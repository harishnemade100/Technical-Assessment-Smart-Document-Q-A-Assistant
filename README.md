# 🧠 Smart Document Q&A Assistant

A mini-project built using **FastAPI**, **Next.js**, **LangChain**, **FAISS**, and **PostgreSQL** that allows users to **upload documents (PDF/TXT)** and **ask AI questions** directly from their content.

This project demonstrates a complete **Retrieval-Augmented Generation (RAG)** pipeline — combining document retrieval with AI models to produce accurate, document-based answers.

---
🎥 Demo Video: https://drive.google.com/file/d/1ygtesu6QX_bHRywi9_rcBRMsXwIpw3zY/view?usp=drive_link

## 🚀 Features
- 🔑 Login & Registration with 🛡️ **JWT-based Authorization**  
- 📤 Upload PDF or TXT documents
- 🧠 Generate embeddings using Hugging Face or OpenAI
- 💾 Store embeddings in **FAISS** for similarity search
- 🗃️ Save document metadata in **PostgreSQL**
- ❓ Ask questions and get AI answers with references
- 💻 Responsive frontend built with **Next.js + Tailwind CSS**

---

## 🏗️ System Architecture
login page -- > 

<img width="1867" height="932" alt="login apge" src="https://github.com/user-attachments/assets/7099de28-4885-4439-bc58-f278b903864d" />


Frontend --- >
<img width="1490" height="816" alt="fornted" src="https://github.com/user-attachments/assets/a3b2bc95-ce86-41c0-b8ae-c0eddf8117c8" />

Backend --- >

<img width="1871" height="1023" alt="new_swagger" src="https://github.com/user-attachments/assets/6be4161d-09f7-43cd-8362-04c89efa6a54" />

🏗️ Project Architecture
# 🎨 Design Pattern

The project follows a **Layered Architecture** combined with a **Pipeline Pattern**:

## 1️⃣ Layered Architecture

- **Presentation Layer (Frontend)**  
  - **Next.js** handles user interactions, document upload, and displaying answers.
  
- **Application/Service Layer (Backend)**  
  - **FastAPI** orchestrates the workflow: document processing, embedding generation, vector storage, and question answering.

- **Data Layer**  
  - **PostgreSQL** stores document metadata.  
  - **FAISS** stores vector embeddings for efficient similarity search.

---

## 2️⃣ Pipeline Pattern
Each document uploaded flows through a **pipeline of processing steps**:

1. **Upload Document** → Frontend triggers backend API  
2. **Extract Text** → PyPDF2 parses document content  
3. **Store Metadata** → PostgreSQL stores document info  
4. **Generate Embeddings** → Hugging Face embeddings model  
5. **Store Vectors** → FAISS index for semantic search  

Similarly, **user questions** flow through a mini pipeline:

1. **Ask Question** → Frontend sends to backend  
2. **Retrieve Chunks** → FAISS searches relevant text vectors  
3. **LLM Answer** → Large language model generates answer  
4. **Display Answer** → Frontend renders response

---

## ✅ Benefits

- **Separation of Concerns**: Each layer has a single responsibility  
- **Scalability**: Can easily add new processing steps or LLM models  
- **Reusability**: Pipeline steps can be reused for different document types  
- **Maintainability**: Clear structure makes debugging and extending the system easier

  
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

<img width="346" height="852" alt="image" src="https://github.com/user-attachments/assets/753b2109-0ebf-4383-9453-9f44faf9e699" />


## 🔑📝 Local Setup & Configuration

Create a `.env` file inside your `backend/` folder:

```bash
This project uses:

All sensitive data and environment-specific settings are stored in a **`LOCAL.yml`** file so they can be easily managed without hardcoding them in your application.

- **PostgreSQL** for database storage
- **JWT Authentication** for login & registration
- Optional **GROQ API** for advanced data queries
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
pip install pipenv
pipenv install
cd ..

RUN Backend -- > 
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000                                                                                                   

3️⃣ Frontend Setup
cd frontend
npm install react-hot-toast  
npm install

RUN Frontend -->
npm run dev

Backend runs on http://localhost:8000

Frontend runs on http://localhost:3000

```

```
## 🐍 Python Environment

This project uses **Pipenv** instead of `requirements.txt` for easier dependency management:

- Creates an **isolated virtual environment** 🌱  
- Locks package versions with `Pipfile.lock` 🔒  
- Install dependencies with:  
  ```bash
  pipenv install

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

```
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
