from sqlalchemy.orm import Session
from backend.app.models.models import DocumentChunk

class MetadataService:
    """
    Handles saving and retrieving metadata from PostgreSQL.
    """

    @staticmethod
    def save_metadata(
        db: Session,
        doc_id: str,
        filename: str,
        chunks: list[str],
        embedding_dim: int,
    ):
        """
        Store chunk metadata and embedding info.
        """
        for i, chunk_text in enumerate(chunks):
            record = DocumentChunk(
                doc_id=doc_id,
                filename=filename,
                chunk_id=i,
                page=None,
                text=chunk_text,
                embedding_dim=embedding_dim,
                extra_metadata={"embedding_index": i},
            )
            db.add(record)

        db.commit()
        print(f"✅ Stored {len(chunks)} metadata entries for {filename}")

    @staticmethod
    def get_metadata(db: Session, doc_id: str):
        return db.query(DocumentChunk).filter(DocumentChunk.doc_id == doc_id).all()
