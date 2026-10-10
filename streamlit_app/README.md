# Smart Document Q&A Assistant — Streamlit version (with login and saved documents)

Upload PDF or TXT files and ask questions about them. Answers come only from the document's content.
Users create an account, and their documents and chat history are saved in a PostgreSQL database.

**Pipeline:** PDF/TXT → text extraction (pypdf) → chunking (LangChain text splitter)
→ embeddings (all-MiniLM-L6-v2 via fastembed) → similarity search (pgvector in PostgreSQL)
→ answer from Groq LLM (llama-3.3-70b-versatile)

## Files

| File | What it does |
|------|--------------|
| `streamlit_app.py` | The app: login screen, upload, document list, chat |
| `db.py` | All database code: creates tables, saves users, documents, chunks and messages |
| `requirements.txt` | Python packages Streamlit Cloud installs |

## Database tables (created automatically on first run)

| Table | Stores |
|-------|--------|
| `app_users` | Usernames and bcrypt-hashed passwords |
| `app_documents` | Each uploaded document and its owner |
| `app_chunks` | Text chunks and their 384-dimension embeddings (pgvector) |
| `app_messages` | Chat history for each document |

## Deploy on Streamlit Community Cloud

1. **Groq key:** create one at https://console.groq.com (API Keys → Create API Key).
2. **Database:** create a free project at https://neon.tech and copy its connection string
   (it looks like `postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require`).
3. Go to https://share.streamlit.io, click **Create app**, and choose:
   - Repository: this repo
   - Branch: `main`
   - Main file path: `streamlit_app/streamlit_app.py`
4. Open **Advanced settings**, choose Python 3.12, and paste into **Secrets**:
   ```toml
   GROQ_API_KEY = "gsk_your_key_here"
   DATABASE_URL = "postgresql://user:password@ep-xxxx.neon.tech/neondb?sslmode=require"
   ```
5. Click **Deploy**.

## Run locally

```bash
cd streamlit_app
pip install -r requirements.txt
mkdir .streamlit
# create .streamlit/secrets.toml with the same two lines as above
streamlit run streamlit_app.py
```

## Limits

- Scanned PDFs (images of pages) have no text and aren't supported.
- Files up to 10 MB; up to 20 documents per user.
- Users need to log in again after refreshing the page; their documents stay saved.
- On the free plan the app sleeps when unused; click the wake-up button to restart it.
