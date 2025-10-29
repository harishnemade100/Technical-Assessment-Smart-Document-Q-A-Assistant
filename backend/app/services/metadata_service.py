from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.models.models import Document
import datetime


class MetadataService:
    """
    Handles saving and retrieving metadata about documents in PostgreSQL.
    """

    @staticmethod
    def save_metadata(
        db: Session,
        doc_id: str,
        filename: str,
        chunks: list[str],
        embedding_dim: int,
        faiss_index_path: str = "data/faiss_index.index",
    ):
        """
        Saves document metadata after upload and processing.

        Args:
            db (Session): SQLAlchemy session.
            doc_id (str): Unique document ID (UUID).
            filename (str): Original filename.
            chunks (list[str]): List of text chunks.
            embedding_dim (int): Embedding dimension size.
            faiss_index_path (str): Path to FAISS index file.

        Returns:
            Document: The saved Document record.
        """
        try:
            if not chunks:
                raise ValueError("No text chunks found to save metadata.")

            document = Document(
                id=doc_id,
                filename=filename,
                uploaded_at=datetime.datetime.utcnow(),
                chunk_count=len(chunks),
                metadata={
                    "embedding_dim": embedding_dim,
                    "total_chunks": len(chunks),
                },
                faiss_index_path=faiss_index_path,
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            print(f"✅ Metadata saved for '{filename}' (doc_id={doc_id})")
            return document

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save metadata: {str(e)}")