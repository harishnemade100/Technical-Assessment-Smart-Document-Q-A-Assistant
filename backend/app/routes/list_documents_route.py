from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.schema.document_schema import DocumentOut
from backend.app.models.models import Document

from backend.app.utils.database import get_db

router = APIRouter(prefix="/upload", tags=["File list"])


@router.get("/", response_model=list[DocumentOut])
def get_all_documents(db: Session = Depends(get_db)):
    """
    Retrieve all uploaded documents from the database.

    :param db: Database session dependency.
    :return: List of DocumentOut objects containing document details.
    :raises HTTPException: If no documents are found or database retrieval fails.

    """
    try:
        documents = Document.list_documents(db)
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found.")

        return documents
        
    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        print(f" Error retrieving documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving documents: {str(e)}",
        )