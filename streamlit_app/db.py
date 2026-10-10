"""
Database layer for the Smart Document Q&A Assistant (Streamlit version).

Uses a cloud PostgreSQL database (Neon or Supabase) with the pgvector extension:
- app_users      -> accounts (passwords are hashed with bcrypt, never stored as plain text)
- app_documents  -> one row per uploaded document, linked to its owner
- app_chunks     -> text chunks + their 384-dim embeddings (pgvector replaces FAISS)
- app_messages   -> saved chat history per document

Tables use an "app_" prefix so they never clash with the old FastAPI project's tables.
The connection string comes from Streamlit secrets: DATABASE_URL.
"""
import uuid

import bcrypt
import numpy as np
import streamlit as st
from sqlalchemy import create_engine, text

EMBEDDING_DIM = 384

SCHEMA = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    """
    CREATE TABLE IF NOT EXISTS app_users (
        id            SERIAL PRIMARY KEY,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at    TIMESTAMPTZ DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS app_documents (
        id          TEXT PRIMARY KEY,
        user_id     INT NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
        filename    TEXT NOT NULL,
        chunk_count INT NOT NULL,
        uploaded_at TIMESTAMPTZ DEFAULT now()
    )
    """,
    f"""
    CREATE TABLE IF NOT EXISTS app_chunks (
        id          BIGSERIAL PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES app_documents(id) ON DELETE CASCADE,
        chunk_index INT NOT NULL,
        content     TEXT NOT NULL,
        embedding   vector({EMBEDDING_DIM}) NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS app_chunks_document_idx ON app_chunks(document_id)",
    """
    CREATE TABLE IF NOT EXISTS app_messages (
        id          BIGSERIAL PRIMARY KEY,
        document_id TEXT NOT NULL REFERENCES app_documents(id) ON DELETE CASCADE,
        role        TEXT NOT NULL,
        content     TEXT NOT NULL,
        created_at  TIMESTAMPTZ DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS app_messages_document_idx ON app_messages(document_id)",
]


def _normalize_url(url: str) -> str:
    """Neon/Supabase give URLs starting with postgresql:// or postgres://.
    Tell SQLAlchemy to use the psycopg (v3) driver for both."""
    url = url.strip()
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


@st.cache_resource(show_spinner="Connecting to the database…")
def get_engine():
    """Create one shared connection pool and make sure all tables exist."""
    engine = create_engine(
        _normalize_url(st.secrets["DATABASE_URL"]),
        pool_pre_ping=True,   # reconnect automatically if the cloud DB went to sleep
        pool_size=5,
        max_overflow=5,
    )
    with engine.begin() as conn:
        for statement in SCHEMA:
            conn.execute(text(statement))
    return engine


def _to_vector(values) -> str:
    """Convert a list/array of floats into pgvector's text format: [0.1,0.2,...]"""
    return "[" + ",".join(f"{float(v):.6f}" for v in values) + "]"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
def create_user(username: str, password: str) -> bool:
    """Return True if the account was created, False if the username is taken."""
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with get_engine().begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO app_users (username, password_hash) VALUES (:u, :p)
                ON CONFLICT (username) DO NOTHING
            """),
            {"u": username, "p": password_hash},
        )
        return result.rowcount == 1


def check_login(username: str, password: str) -> dict | None:
    """Return {'id', 'username'} if the password is correct, otherwise None."""
    with get_engine().connect() as conn:
        row = conn.execute(
            text("SELECT id, username, password_hash FROM app_users WHERE username = :u"),
            {"u": username},
        ).first()
    if row and bcrypt.checkpw(password.encode(), row.password_hash.encode()):
        return {"id": row.id, "username": row.username}
    return None


# ---------------------------------------------------------------------------
# Documents and chunks
# ---------------------------------------------------------------------------
def add_document(user_id: int, filename: str, chunks: list[str], vectors: np.ndarray) -> str:
    """Save a document and all its chunks + embeddings in one transaction."""
    doc_id = str(uuid.uuid4())
    with get_engine().begin() as conn:
        conn.execute(
            text("""
                INSERT INTO app_documents (id, user_id, filename, chunk_count)
                VALUES (:id, :uid, :name, :n)
            """),
            {"id": doc_id, "uid": user_id, "name": filename, "n": len(chunks)},
        )
        conn.execute(
            text("""
                INSERT INTO app_chunks (document_id, chunk_index, content, embedding)
                VALUES (:doc, :i, :content, CAST(:emb AS vector))
            """),
            [
                {"doc": doc_id, "i": i, "content": chunk, "emb": _to_vector(vec)}
                for i, (chunk, vec) in enumerate(zip(chunks, vectors))
            ],
        )
    return doc_id


def list_documents(user_id: int) -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT id, filename, chunk_count, uploaded_at
                FROM app_documents WHERE user_id = :uid
                ORDER BY uploaded_at
            """),
            {"uid": user_id},
        ).mappings().all()
    return [dict(r) for r in rows]


def delete_document(user_id: int, doc_id: str) -> None:
    """Delete a document; its chunks and messages are removed automatically (ON DELETE CASCADE).
    The user_id check makes sure people can only delete their own documents."""
    with get_engine().begin() as conn:
        conn.execute(
            text("DELETE FROM app_documents WHERE id = :id AND user_id = :uid"),
            {"id": doc_id, "uid": user_id},
        )


def search_chunks(user_id: int, doc_id: str, query_vector, top_k: int) -> list[tuple[str, float]]:
    """Find the chunks most similar to the question (cosine similarity via pgvector's <=> operator)."""
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("""
                SELECT c.content, 1 - (c.embedding <=> CAST(:q AS vector)) AS score
                FROM app_chunks c
                JOIN app_documents d ON d.id = c.document_id
                WHERE c.document_id = :doc AND d.user_id = :uid
                ORDER BY c.embedding <=> CAST(:q AS vector)
                LIMIT :k
            """),
            {"q": _to_vector(query_vector), "doc": doc_id, "uid": user_id, "k": top_k},
        ).all()
    return [(r.content, float(r.score)) for r in rows]


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
def add_message(doc_id: str, role: str, content: str) -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text("INSERT INTO app_messages (document_id, role, content) VALUES (:d, :r, :c)"),
            {"d": doc_id, "r": role, "c": content},
        )


def get_messages(doc_id: str) -> list[dict]:
    with get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT role, content FROM app_messages WHERE document_id = :d ORDER BY id"),
            {"d": doc_id},
        ).mappings().all()
    return [dict(r) for r in rows]
