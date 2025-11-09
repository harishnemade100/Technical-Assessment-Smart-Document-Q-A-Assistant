from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from fastapi import HTTPException
import datetime

from backend.app.utils.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    chunk_count = Column(Integer, default=0)
    extra_metadata = Column(JSON, nullable=True)
    faiss_index_path = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="documents")
 
    @classmethod
    def list_documents(
        cls, 
        db: Session,
        user_id: int)-> list[dict] | None :
        """
        Retrieves all documents with minimal fields for API listing.

        Returns:
            List[dict]: Each record includes document_id, filename, upload time, chunk_count, and FAISS path.
        """
        try:
            docs = db.query(cls).filter(cls.user_id == user_id).all()
            if not docs:
                return []
            return [
                {
                    "document_id": d.id,
                    "filename": d.filename,
                    "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "chunk_count": d.chunk_count,
                    "faiss_index_path": d.faiss_index_path,
                }
                for d in docs
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

  
    @classmethod
    def delete_metadata(cls, db: Session, doc_id: str):
        """
        Deletes a document record from the database by ID.

        Args:
            db (Session): SQLAlchemy session.
            doc_id (str): Document unique ID.

        Returns:
            dict: Confirmation message after successful deletion.
        """
        try:
            doc = db.query(cls).filter(cls.id == doc_id).first()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found.")

            db.delete(doc)
            db.commit()

            print(f"🗑️ Deleted metadata for document '{doc.filename}' (doc_id={doc_id})")
            return {"status": "deleted", "document_id": doc_id}

        except HTTPException:
            # Let FastAPI handle these gracefully
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete metadata: {str(e)}")

    
    @classmethod
    def get_metadata(cls, db: Session, doc_id: str):
        """
        Retrieves metadata for a single document by ID.

        Args:
            db (Session): SQLAlchemy session.
            doc_id (str): Unique document ID.

        Returns:
            Document: SQLAlchemy model instance or raises 404.
        """
        try:
            doc = db.query(cls).filter(cls.id == doc_id).first()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found.")
            return doc
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

