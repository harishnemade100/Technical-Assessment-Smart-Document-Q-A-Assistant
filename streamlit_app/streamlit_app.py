"""
Smart Document Q&A Assistant — Streamlit version with login and saved documents
===============================================================================
Same RAG pipeline as the FastAPI backend in this repo:
    upload PDF/TXT -> extract text -> split into chunks -> embeddings (all-MiniLM-L6-v2)
    -> similarity search (pgvector in PostgreSQL) -> Groq LLM (llama-3.3-70b-versatile) answer

Runs on Streamlit Community Cloud with a free cloud PostgreSQL database (Neon or Supabase).
Required secrets (Settings -> Secrets):
    GROQ_API_KEY = "gsk_..."
    DATABASE_URL = "postgresql://user:password@host/dbname?sslmode=require"
"""
import re
import time

import numpy as np
import streamlit as st
from fastembed import TextEmbedding
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

import db

# ---------------------------------------------------------------------------
# Settings (same values as backend/app/settings/constants.py)
# ---------------------------------------------------------------------------
def get_setting(name: str, default: str) -> str:
    """Read an optional setting from Streamlit secrets, falling back to a default."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# Groq retires models over time. To switch models, add LLM_MODEL = "model-name" in Secrets.
# Current models: https://console.groq.com/docs/models
LLM_MODEL = get_setting("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = 0.2
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5
MAX_FILE_MB = 10
MAX_DOCS_PER_USER = 20      # keeps the free database from filling up
MAX_QUESTION_CHARS = 1000

st.set_page_config(page_title="Smart Document Q&A", page_icon="📄", layout="wide")


# ---------------------------------------------------------------------------
# Shared resources: loaded once per server and shared by all visitors
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading the embedding model (first time only)…")
def get_embedder() -> TextEmbedding:
    return TextEmbedding(model_name=EMBEDDING_MODEL)


@st.cache_resource
def get_llm() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])


def missing_secrets() -> list[str]:
    try:
        return [name for name in ("GROQ_API_KEY", "DATABASE_URL") if not st.secrets.get(name)]
    except Exception:  # no secrets configured at all
        return ["GROQ_API_KEY", "DATABASE_URL"]


# ---------------------------------------------------------------------------
# RAG pipeline
# ---------------------------------------------------------------------------
def extract_text(uploaded_file) -> str:
    """Step 1: extract text from a PDF or TXT file."""
    if uploaded_file.name.lower().endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return uploaded_file.getvalue().decode("utf-8", errors="ignore")


def embed(texts: list[str]) -> np.ndarray:
    """Turn text into 384-number vectors that capture meaning."""
    return np.array(list(get_embedder().embed(texts)), dtype="float32")


def split_text(text: str) -> list[str]:
    """Step 2: split the text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return [c for c in splitter.split_text(text) if c.strip()]


def answer_question(user_id: int, doc_id: str, question: str):
    """Find the most relevant chunks in the database, then ask the LLM using only those."""
    sources = db.search_chunks(user_id, doc_id, embed([question])[0], TOP_K)
    context = "\n\n---\n\n".join(chunk for chunk, _ in sources)

    response = get_llm().chat.completions.create(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions about a document. "
                    "Use only the provided context. If the answer is not in the context, "
                    "say you couldn't find it in the document."
                ),
            },
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content.strip(), sources


def model_help_message() -> str:
    """Explain how to fix a retired Groq model and list the models this API key can use."""
    text = (
        f"The AI model `{LLM_MODEL}` isn't available on Groq anymore. "
        "Choose a current model and add it to your app's Secrets, for example:\n\n"
        '`LLM_MODEL = "model-name-here"`\n\n'
    )
    try:
        ids = sorted(m.id for m in get_llm().models.list().data)
        skip = ("whisper", "tts", "guard", "playai", "orpheus")
        chat_ids = [i for i in ids if not any(word in i.lower() for word in skip)]
        text += "Models your Groq key can use:\n\n" + "\n".join(f"- `{i}`" for i in chat_ids)
    except Exception:
        text += "See the list of current models at https://console.groq.com/docs/models"
    return text


# ---------------------------------------------------------------------------
# Button callbacks (run before the page redraws, so changes show immediately)
# ---------------------------------------------------------------------------
def do_login():
    username = st.session_state.get("login_username", "").strip().lower()
    password = st.session_state.get("login_password", "")
    user = db.check_login(username, password) if username and password else None
    if user:
        st.session_state.user = user
        st.session_state.auth_error = None
    else:
        st.session_state.auth_error = "Wrong username or password."


def do_register():
    username = st.session_state.get("reg_username", "").strip().lower()
    password = st.session_state.get("reg_password", "")
    confirm = st.session_state.get("reg_confirm", "")
    if not re.fullmatch(r"[a-z0-9_]{3,30}", username):
        st.session_state.auth_error = "Username must be 3–30 characters: letters, numbers or _."
    elif not 6 <= len(password.encode()) <= 72:
        st.session_state.auth_error = "Password must be 6–72 characters."
    elif password != confirm:
        st.session_state.auth_error = "Passwords don't match."
    elif not db.create_user(username, password):
        st.session_state.auth_error = "That username is taken. Choose another one."
    else:
        st.session_state.user = db.check_login(username, password)
        st.session_state.auth_error = None


def do_logout():
    for key in ("user", "selected_doc", "auth_error"):
        st.session_state.pop(key, None)


def do_delete(doc_id: str):
    db.delete_document(st.session_state.user["id"], doc_id)
    st.session_state.pop("selected_doc", None)


# ---------------------------------------------------------------------------
# Page start: check secrets and database connection
# ---------------------------------------------------------------------------
st.title("Smart Document Q&A Assistant")

if missing := missing_secrets():
    st.error(f"Missing secrets: {', '.join(missing)}. In Streamlit Cloud, open Settings → Secrets and add them.")
    st.stop()

try:
    db.get_engine()
except Exception as e:
    st.error(
        "Couldn't connect to the database. Check that DATABASE_URL in your secrets is correct "
        f"and ends with ?sslmode=require.\n\nDetails: {e}"
    )
    st.stop()

st.session_state.setdefault("uploader_key", 0)

# ---------------------------------------------------------------------------
# Login / create account screen
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.write("Log in or create an account. Your documents and chats are saved to your account.")
    login_tab, register_tab = st.tabs(["Log in", "Create account"])

    with login_tab:
        with st.form("login_form"):
            st.text_input("Username", key="login_username")
            st.text_input("Password", type="password", key="login_password")
            st.form_submit_button("Log in", on_click=do_login, type="primary")

    with register_tab:
        with st.form("register_form"):
            st.text_input("Username", key="reg_username", help="3–30 characters: letters, numbers or _")
            st.text_input("Password", type="password", key="reg_password", help="At least 6 characters")
            st.text_input("Confirm password", type="password", key="reg_confirm")
            st.form_submit_button("Create account", on_click=do_register, type="primary")

    if st.session_state.get("auth_error"):
        st.error(st.session_state.auth_error)
    st.stop()

user = st.session_state.user

# ---------------------------------------------------------------------------
# Sidebar: account, upload, and document list
# ---------------------------------------------------------------------------
with st.sidebar:
    st.write(f"Signed in as **{user['username']}**")
    st.button("Log out", on_click=do_logout)
    st.divider()

    st.header("📄 Your documents")
    documents = db.list_documents(user["id"])

    uploaded = st.file_uploader(
        "Upload a PDF or TXT file",
        type=["pdf", "txt"],
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded is not None:
        if len(documents) >= MAX_DOCS_PER_USER:
            st.error(f"You can keep up to {MAX_DOCS_PER_USER} documents. Delete one to upload another.")
        elif uploaded.size > MAX_FILE_MB * 1024 * 1024:
            st.error(f"This file is larger than {MAX_FILE_MB} MB. Upload a smaller file.")
        else:
            try:
                with st.spinner(f"Processing {uploaded.name}…"):
                    text = extract_text(uploaded)
                    if not text.strip():
                        st.error("No readable text found. Scanned PDFs (images of pages) aren't supported.")
                    else:
                        chunks = split_text(text)
                        doc_id = db.add_document(user["id"], uploaded.name, chunks, embed(chunks))
                        st.session_state.selected_doc = doc_id
                        st.session_state.uploader_key += 1   # clear the uploader
                        documents = db.list_documents(user["id"])
                        st.success(f"{uploaded.name} is ready ({len(chunks)} chunks).")
            except Exception as e:
                st.error(f"Couldn't process this file: {e}")

    if documents:
        names = {d["id"]: f"{d['filename']} ({d['uploaded_at']:%d %b %Y})" for d in documents}
        if st.session_state.get("selected_doc") not in names:
            st.session_state.selected_doc = documents[-1]["id"]
        selected = st.radio(
            "Ask questions about:", list(names), format_func=names.get, key="selected_doc"
        )
        st.button("Delete this document", use_container_width=True, on_click=do_delete, args=(selected,))
    else:
        selected = None

    st.divider()
    st.caption(f"Answers are generated by {LLM_MODEL} via Groq, using only your document.")

# ---------------------------------------------------------------------------
# Main area: chat (history is loaded from the database)
# ---------------------------------------------------------------------------
if not selected:
    st.info("Upload a PDF or TXT file in the sidebar to start asking questions.")
    st.stop()

for msg in db.get_messages(selected):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

selected_name = next(d["filename"] for d in documents if d["id"] == selected)
if question := st.chat_input(f"Ask a question about {selected_name}"):
    question = question[:MAX_QUESTION_CHARS]
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        start = time.time()
        with st.spinner("Searching the document…"):
            try:
                reply, sources = answer_question(user["id"], selected, question)
                failed = False
            except Exception as e:
                message = str(e)
                if "rate" in message.lower() and "limit" in message.lower():
                    reply = "Too many questions right now. Wait a minute and try again."
                elif "model_not_found" in message or "decommissioned" in message:
                    reply = model_help_message()
                else:
                    reply = f"Couldn't get an answer: {message}"
                sources, failed = [], True
        st.markdown(reply)
        if sources:
            with st.expander(f"Sources used ({time.time() - start:.1f}s)"):
                for chunk, score in sources:
                    st.markdown(f"**Relevance: {score:.2f}**")
                    st.text(chunk[:600])

    if not failed:   # only save successful answers to the history
        db.add_message(selected, "user", question)
        db.add_message(selected, "assistant", reply)