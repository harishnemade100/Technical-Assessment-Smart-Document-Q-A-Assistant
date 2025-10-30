# 🧠 Smart Document Q&A Assistant

A mini-project built using **FastAPI**, **Next.js**, **LangChain**, **FAISS**, and **PostgreSQL** that allows users to **upload documents (PDF/TXT)** and **ask AI questions** directly from their content.

This project demonstrates a complete **Retrieval-Augmented Generation (RAG)** pipeline — combining document retrieval with AI models to produce accurate, document-based answers.

---
🎥 Demo Video: https://drive.google.com/file/d/1ygtesu6QX_bHRywi9_rcBRMsXwIpw3zY/view?usp=drive_link

## 🚀 Features

- 📤 Upload PDF or TXT documents
- 🧠 Generate embeddings using Hugging Face or OpenAI
- 💾 Store embeddings in **FAISS** for similarity search
- 🗃️ Save document metadata in **PostgreSQL**
- ❓ Ask questions and get AI answers with references
- 💻 Responsive frontend built with **Next.js + Tailwind CSS**

---

## 🏗️ System Architecture

Frontend --- >
<img width="1490" height="816" alt="fornted" src="https://github.com/user-attachments/assets/a3b2bc95-ce86-41c0-b8ae-c0eddf8117c8" />

Backend --- >

<img width="1865" height="927" alt="full fastapi sceen" src="https://github.com/user-attachments/assets/4cb292ba-1552-4d9a-969a-b40d8ba99e8d" />

🏗️ Project Architecture
User → Next.js Frontend → FastAPI Backend
        ↓                       ↓
  Upload Document       Extract Text (PyPDF2)
        ↓                       ↓
  Store Metadata (PostgreSQL)
        ↓                       ↓
  Generate Embeddings (Hugging Face)
        ↓                       ↓
  Store Vectors in FAISS
        ↓                       ↓
  Ask Question → Retrieve Chunks → LLM Answer
        ↓
  Display Answer on Frontend

  
## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Next.js, React, Tailwind CSS, Axios |
| **Backend** | FastAPI, LangChain |
| **AI Models** | Hugging Face / OpenAI |
| **Vector Database** | FAISS |
| **Metadata Storage** | PostgreSQL |
| **Text Extraction** | PyPDF2 |


📁 Folder Structure
smart-document-qa-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── routes/                 # Upload & Query APIs
│   │   ├── services/               # RAG logic (embeddings, FAISS)
│   │   ├── database.py             # PostgreSQL connection
│   │   └── models/                 # SQLAlchemy models
│   └── requirements.txt
│
├── frontend/
│   ├── app/                        # Next.js routes
│   │   ├── page.tsx                # Upload page
│   │   └── qa/page.tsx             # Q&A page
│   ├── components/                 # UI components
│   ├── lib/api.ts                  # Axios API functions
│   └── package.json
│
├── sample_docs/                    # Example test documents
├── .env.example                    # Environment variables template
└── README.md

## 🔑 Environment Variables

Create a `.env` file inside your `backend/` folder:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/qa_assistant
FAISS_INDEX_PATH=./data/faiss_index
UPLOAD_FOLDER=./uploads
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional if using OpenAI
OPENAI_API_KEY=your_openai_api_key_here

(Optional for OpenAI)

OPENAI_API_KEY=your_openai_api_key_here

🧠 How the RAG Flow Works

Upload document → Extract text using PyPDF2

Split text into chunks (500–1000 characters)

Generate embeddings using Hugging Face

Store embeddings in FAISS

Save file details in PostgreSQL

Ask question → Convert to embedding → Retrieve top chunks from FAISS

Send context to AI → Generate and return answer
```
```bash
⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/<your-username>/smart-document-qa-assistant.git
cd smart-document-qa-assistant
```

```bash

2️⃣ Backend Setup
cd backend
python -m venv venv
source venv/bin/activate    # (venv\Scripts\activate on Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload

3️⃣ Frontend Setup
cd frontend
npm install
npm run dev

Backend runs on http://localhost:8000

Frontend runs on http://localhost:3000

```

🧩 Example API
📤 Upload a Document

Your FastAPI application should implement the following endpoints:
1. POST /api/documents/upload - Accept document upload (PDF or TXT format)
   <img width="1534" height="862" alt="response of file upload" src="https://github.com/user-attachments/assets/41ac42f8-b9fe-4b3b-a327-6f3caf776199" />

3. GET /api/documents - Retrieve list of all uploaded documents
   
   <img width="1220" height="704" alt="respnce of list of document" src="https://github.com/user-attachments/assets/642bf8ae-caba-4ac0-8136-64f5a462cb7f" />

5. POST /api/documents/query - Ask questions about a specific document

    <img width="1534" height="862" alt="response of asking question" src="https://github.com/user-attachments/assets/ef05ea70-0890-4840-b35a-586c79bb817e" />

7. DELETE /api/documents/{document_id} - Delete a document

   <img width="1408" height="788" alt="responce of delete the file" src="https://github.com/user-attachments/assets/6242d4ef-40f3-4e0c-b0b5-1637eee1ccf7" />

```bash
Example Script:

“This project is a Smart Document Q&A Assistant.
When I upload a document, the backend extracts and processes the text, stores embeddings in FAISS, and metadata in PostgreSQL.
When I ask a question, it retrieves similar text parts and uses AI to generate an answer.
It’s built using FastAPI, Next.js, LangChain, and FAISS.”

🌟 Future Improvements

Support DOCX and Markdown files

Add user authentication

Add chat history

Deploy full project (Vercel + Render)

Stream answers in real time

```

👨‍💻 Author

Name: [Your Full Name]
Email: [Your Email]
LinkedIn: [Your LinkedIn Profile]
GitHub: [Your GitHub Profile]

```
```bash 
🏁 Conclusion

This project demonstrates how AI + Vector Databases + FastAPI can make documents searchable and interactive.
It’s a practical mini-project showcasing real-world concepts like RAG, FAISS similarity search, and AI-powered question answering.
```
