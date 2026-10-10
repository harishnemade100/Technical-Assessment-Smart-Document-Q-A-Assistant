# Smart Document Q&A Assistant

An AI-powered assistant that lets you upload PDF or text documents and ask questions about them in plain language. Answers are generated only from the content of your document, and each answer shows the exact passages it was based on.

**Live demo:** https://your-app-name.streamlit.app <!-- replace with your Streamlit link -->

The project uses **Retrieval-Augmented Generation (RAG)**: instead of asking an AI model to answer from memory, the app first finds the most relevant parts of your document and then asks the model to answer using only those parts. This keeps answers grounded in your document and reduces made-up information.

---

## Table of contents

- [Features](#features)
- [How it works](#how-it-works)
- [Project versions](#project-versions)
- [Tech stack](#tech-stack)
- [Repository structure](#repository-structure)
- [Database design](#database-design)
- [Getting started (Streamlit version)](#getting-started-streamlit-version)
- [Deploying to Streamlit Community Cloud](#deploying-to-streamlit-community-cloud)
- [Configuration](#configuration)
- [Original FastAPI + Next.js version](#original-fastapi--nextjs-version)
- [Project journey: what was done](#project-journey-what-was-done)
- [Known limitations](#known-limitations)
- [Roadmap: future updates](#roadmap-future-updates)
- [Troubleshooting](#troubleshooting)

---

## Features

- **User accounts:** sign up and log in; passwords are stored as secure bcrypt hashes.
- **Document upload:** PDF and TXT files up to 10 MB.
- **Ask questions in a chat:** natural-language questions about any uploaded document.
- **Grounded answers with sources:** every answer shows the document passages it used, with relevance scores.
- **Saved history:** documents and chat history are stored in the database and are still there the next time you log in.
- **Private by design:** each user can only see, search and delete their own documents.
- **Swappable AI model:** the Groq model is set in configuration, so it can be changed without touching code.

---

## How it works

### Uploading a document

```mermaid
flowchart LR
    A[PDF / TXT upload] --> B[Extract text<br/>pypdf]
    B --> C[Split into chunks<br/>800 chars, 150 overlap]
    C --> D[Create embeddings<br/>all-MiniLM-L6-v2]
    D --> E[(PostgreSQL + pgvector<br/>Neon)]
```

1. **Extract:** text is pulled out of the PDF page by page.
2. **Chunk:** the text is split into overlapping pieces of about 800 characters, so each piece is small enough to search precisely while the overlap keeps sentences from being cut off.
3. **Embed:** each chunk is converted into a list of 384 numbers (an *embedding*) that represents its meaning. Texts with similar meaning get similar numbers.
4. **Store:** the chunks and their embeddings are saved in PostgreSQL using the pgvector extension.

### Asking a question

```mermaid
flowchart LR
    Q[User question] --> E[Embed question]
    E --> S[pgvector search<br/>top 5 closest chunks]
    S --> L[Groq LLM<br/>question + 5 chunks]
    L --> A[Answer + sources]
    A --> H[(Save to chat history)]
```

1. The question is converted into an embedding with the same model.
2. pgvector finds the 5 chunks whose embeddings are closest to the question (cosine similarity).
3. The question and those 5 chunks are sent to a Groq-hosted LLM with an instruction to answer only from that context.
4. The answer and its source chunks are shown and saved to the chat history.

Groq is called only when a question is asked. Uploading, logging in and viewing history do not use Groq.

---

## Project versions

This repository contains two implementations of the same idea:

| | Streamlit version (`streamlit_app/`) | Original version (`backend/` + `frontend/`) |
|---|---|---|
| Status | **Active, deployed** | Legacy, kept for reference |
| Frontend | Streamlit | Next.js (React, TypeScript, Tailwind) |
| Backend | Same Python app | FastAPI REST API |
| Vector search | pgvector inside PostgreSQL | FAISS index files on disk |
| Database | Cloud PostgreSQL (Neon) | Local PostgreSQL |
| Auth | Username + bcrypt password | JWT tokens |
| Hosting | Streamlit Community Cloud | Runs locally |

The Streamlit version was created so the project could be hosted publicly for free. Streamlit Community Cloud can only run Streamlit apps, and its disk is reset on every restart, so the FastAPI + Next.js version and its on-disk FAISS files could not be deployed there as-is.

---

## Tech stack

| Area | Technology |
|---|---|
| UI and app server | [Streamlit](https://streamlit.io) |
| Text extraction | [pypdf](https://pypdf.readthedocs.io) |
| Chunking | [LangChain text splitters](https://python.langchain.com) (`RecursiveCharacterTextSplitter`) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` via [fastembed](https://github.com/qdrant/fastembed) (ONNX, no PyTorch needed) |
| Vector search | [pgvector](https://github.com/pgvector/pgvector) |
| Database | PostgreSQL on [Neon](https://neon.tech) (serverless, free tier) |
| Database access | SQLAlchemy 2 + psycopg 3 |
| LLM | [Groq](https://groq.com) API (default model configurable, e.g. `openai/gpt-oss-120b`) |
| Password hashing | bcrypt |
| Hosting | [Streamlit Community Cloud](https://streamlit.io/cloud) |

---

## Repository structure

```
Technical-Assessment-Smart-Document-Q-A-Assistant/
├── streamlit_app/                 ← Active Streamlit version
│   ├── streamlit_app.py           # UI: login, upload, document list, chat, RAG pipeline
│   ├── db.py                      # Database: tables, users, documents, chunks, messages
│   ├── requirements.txt           # Python dependencies for Streamlit Cloud
│   └── README.md                  # Short deployment notes
│
├── backend/                       ← Original FastAPI backend (legacy)
│   └── app/
│       ├── main.py                # FastAPI app and router registration
│       ├── routes/                # auth, upload, list, delete, Q&A endpoints
│       ├── services/              # text extraction, chunking, embeddings, FAISS, Q&A
│       ├── models/                # SQLAlchemy models (users, documents)
│       ├── schema/                # Pydantic request/response schemas
│       ├── settings/constants.py  # Model names, chunk sizes, limits
│       └── utils/                 # Database connection, JWT, file helpers
│
├── frontend/                      ← Original Next.js frontend (legacy)
│   ├── app/                       # Pages and layout
│   ├── components/                # Upload box, document list, Q&A, auth modals
│   └── lib/api.ts                 # API client
│
├── .gitignore
└── README.md                      # This file
```

---

## Database design

Tables are created automatically the first time the Streamlit app starts. They use an `app_` prefix so they never clash with tables from the original version.

```mermaid
erDiagram
    app_users ||--o{ app_documents : owns
    app_documents ||--o{ app_chunks : "split into"
    app_documents ||--o{ app_messages : "has chat"

    app_users {
        int id PK
        text username UK
        text password_hash
        timestamptz created_at
    }
    app_documents {
        text id PK
        int user_id FK
        text filename
        int chunk_count
        timestamptz uploaded_at
    }
    app_chunks {
        bigint id PK
        text document_id FK
        int chunk_index
        text content
        vector embedding "384 dimensions"
    }
    app_messages {
        bigint id PK
        text document_id FK
        text role "user or assistant"
        text content
        timestamptz created_at
    }
```

Deleting a document automatically deletes its chunks and messages (`ON DELETE CASCADE`).

---

## Getting started (Streamlit version)

### Prerequisites

- Python 3.11 or 3.12
- A free [Groq API key](https://console.groq.com)
- A free [Neon](https://neon.tech) PostgreSQL database (copy its connection string)

### Run locally

```bash
cd streamlit_app
pip install -r requirements.txt
```

Create `streamlit_app/.streamlit/secrets.toml` (this file is git-ignored and must never be committed):

```toml
GROQ_API_KEY = "gsk_your_key_here"
DATABASE_URL = "postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require"
LLM_MODEL = "openai/gpt-oss-120b"
```

Start the app:

```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501, create an account, upload a document and start asking questions.

---

## Deploying to Streamlit Community Cloud

1. Push the repository to GitHub (make sure no secrets are committed).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **Create app** and set:
   - **Repository:** this repository
   - **Branch:** `main`
   - **Main file path:** `streamlit_app/streamlit_app.py`
   - **App URL:** any name (note: subdomains can't contain `qa`)
4. Under **Advanced settings**, choose Python 3.12 and paste the same three lines from `secrets.toml` into **Secrets**.
5. Click **Deploy**. The first build takes a few minutes.

After deployment, every push to the selected branch updates the live app automatically.

---

## Configuration

| Setting | Where | Required | Description |
|---|---|---|---|
| `GROQ_API_KEY` | Secrets | Yes | Groq API key |
| `DATABASE_URL` | Secrets | Yes | PostgreSQL connection string (Neon or Supabase) |
| `LLM_MODEL` | Secrets | Recommended | Groq model name; if the model is retired, the app lists the models your key can use |
| `CHUNK_SIZE`, `CHUNK_OVERLAP` | `streamlit_app.py` | No | Chunking settings (default 800 / 150) |
| `TOP_K` | `streamlit_app.py` | No | Number of chunks sent to the LLM per question (default 5) |
| `MAX_FILE_MB` | `streamlit_app.py` | No | Upload size limit (default 10 MB) |
| `MAX_DOCS_PER_USER` | `streamlit_app.py` | No | Documents per account (default 20) |

---

## Original FastAPI + Next.js version

The original implementation is kept in `backend/` and `frontend/` for reference.

**API endpoints**

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Log in and receive a JWT |
| POST | `/api/documents/upload` | Upload and process a document |
| GET | `/api/documents/` | List the user's documents |
| DELETE | `/api/documents/{document_id}` | Delete a document |
| POST | `/api/qa/query` | Ask a question about a document |

**Status:** this version has known issues that are not yet fixed: the upload route imports functions that were renamed, the Q&A service uses placeholder context instead of the stored document text, all documents share a single FAISS index, and some dependencies are missing from the Pipfile. These are listed in the roadmap below. Configuration that used to live in `backend/LOCAL.yml` should now be supplied through environment variables (`backend/.env`, git-ignored).

---

## Project journey: what was done

1. **Built the original app** with a FastAPI backend, Next.js frontend, local PostgreSQL, FAISS vector search and Groq for answers.
2. **Reviewed the project for public deployment** and found that Streamlit Community Cloud cannot host FastAPI or Next.js, cannot reach a local database, and wipes its disk on restart.
3. **Rebuilt the app in Streamlit**, reusing the same RAG pipeline (pypdf, LangChain splitter, all-MiniLM-L6-v2, Groq) in a single Python app.
4. **Switched embeddings to fastembed**, which runs the same model through ONNX and avoids installing PyTorch, keeping the app within the free hosting memory limit.
5. **Moved data to a cloud database:** Neon PostgreSQL with pgvector now stores users, documents, embeddings and chat history, replacing local Postgres and FAISS files.
6. **Added accounts with secure passwords** (bcrypt hashing) and per-user data isolation.
7. **Fixed a real retrieval gap:** the new version sends the actual stored chunks to the LLM, so answers come from the document.
8. **Improved security:** removed `backend/LOCAL.yml` from the repository (any credentials it contained should be treated as exposed and changed), expanded `.gitignore`, and moved all keys to Streamlit Secrets. GitHub push protection was used to block a commit containing an API key.
9. **Made the LLM configurable:** when Groq retired `llama-3.3-70b-versatile`, the app was updated to read `LLM_MODEL` from Secrets and to list available models automatically.
10. **Deployed the app publicly** on Streamlit Community Cloud.

---

## Known limitations

- **Scanned PDFs** (images of pages) contain no extractable text and are not supported yet.
- **Login does not survive a page refresh:** users must log in again, although their documents remain saved.
- **Whole-document summaries** are based on the 5 most relevant chunks, so very long documents may be summarized only partially.
- **Free-tier sleep:** the Streamlit app and the Neon database sleep when unused; the first visit after a break takes a little longer.
- **Rate limits:** Groq's free tier limits how many questions can be answered per minute.
- **File types:** only PDF and TXT are supported.

---

## Roadmap: future updates

### Short term
- [ ] **Persistent login** with secure cookies or Streamlit's built-in OpenID Connect login (Google sign-in).
- [ ] **Better summaries:** a dedicated "Summarize document" button that summarizes chunk groups and then combines them (map-reduce), so long documents are fully covered.
- [ ] **More file types:** DOCX, Markdown and CSV.
- [ ] **Streaming answers** so text appears word by word.
- [ ] **Password change and account deletion.**

### Medium term
- [ ] **OCR for scanned PDFs** (e.g. Tesseract) so image-based documents can be searched.
- [ ] **Ask across multiple documents** at once, with sources labeled by document.
- [ ] **Page numbers in sources** so users can jump to the exact page.
- [ ] **Conversation memory:** include recent chat turns so follow-up questions ("what about the second point?") work naturally.
- [ ] **Hybrid search:** combine keyword (full-text) search with vector search for better retrieval of names, codes and numbers.
- [ ] **Usage limits per user** to protect the Groq quota on a public deployment.

### Long term
- [ ] **Fix and modernize the FastAPI + Next.js version** (repair upload and Q&A, per-document indexes, pgvector, environment-based config) and deploy it on Render/Railway + Vercel.
- [ ] **Automated tests and CI** with GitHub Actions.
- [ ] **Answer quality evaluation** with a small set of test questions and expected answers.
- [ ] **Docker setup** for one-command local development.
- [ ] **Admin dashboard** with usage statistics.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Missing secrets: GROQ_API_KEY, DATABASE_URL` | Add them in **Settings → Secrets** (or `streamlit_app/.streamlit/secrets.toml` locally). |
| `Couldn't connect to the database` | Recopy the Neon connection string exactly, inside quotes, including `?sslmode=require`. |
| Message saying the AI model isn't available | Pick a model from the list the app shows and set `LLM_MODEL` in Secrets. |
| `Username must be 3–30 characters` | Use only letters, numbers and `_` (no spaces, hyphens or email addresses). |
| `No readable text found` | The PDF is scanned; try a PDF with selectable text. |
| `Too many questions right now` | Groq rate limit reached; wait a minute and try again. |
| App shows "gone to sleep" | Click the wake-up button and wait about a minute. |

---

## Author

**Harish Nemade** · [GitHub](https://github.com/harishnemade100)
