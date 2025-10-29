from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from backend.app.utils.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, index=True)       # Unique document ID
    filename = Column(String, nullable=False)      # Original file name
    chunk_id = Column(Integer, nullable=False)     # Chunk index
    page = Column(Integer, nullable=True)          # Page number (if PDF)
    text = Column(String, nullable=False)          # Extracted text
    embedding_dim = Column(Integer, nullable=True) # Embedding vector dimension
    extra_metadata = Column(JSON, nullable=True)       # Extra metadata
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
