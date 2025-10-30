import shutil
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.models import Document
from pathlib import Path

from backend.app.utils.database import get_db

router = APIRouter(tags=["Delete Document"])



@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete a document and its associated metadata and files.
    :param document_id: ID of the document to delete.
    :param db: Database session (injected via dependency).
    :return: Status message indicating deletion success.

    """
    try:
        # Retrieve document metadata
        document = Document.get_metadata(db, document_id)

        # Delete FAISS index files
        if document.faiss_index_path:
            faiss_path = Path(document.faiss_index_path)
            if faiss_path.exists() and faiss_path.is_dir():
                shutil.rmtree(faiss_path)
                print(f" Deleted FAISS index at {faiss_path}")

        # Delete document metadata from DB
        result = Document.delete_metadata(db, document_id)

        return result
    
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    