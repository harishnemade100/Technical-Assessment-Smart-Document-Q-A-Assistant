import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.doc_models import Document
from backend.app.utils.database import get_db
from backend.app.services.auth.auth_service import get_current_user

router = APIRouter(tags=["Delete Document"])


@router.delete("/{document_id}", status_code=200)
def delete_document(
    document_id: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # ensures user is authenticated
):
    """
    Delete a document and its associated metadata and FAISS files.
    Only the owner of the document can delete it.

    :param document_id: ID of the document to delete.
    :param db: Database session.
    :param current_user: Logged-in user from JWT token.
    :return: Status message indicating deletion success.
    :raises HTTPException: If document not found or user is not authorized.
    """
    try:
        # Retrieve document metadata
        document = Document.get_metadata(db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found.")

        # Ensure the current user is the owner
        if document.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this document.")

        # Delete FAISS index files if they exist
        if document.faiss_index_path:
            faiss_path = Path(document.faiss_index_path)
            if faiss_path.exists() and faiss_path.is_dir():
                shutil.rmtree(faiss_path)
                print(f"Deleted FAISS index at {faiss_path}")

        # Delete document metadata from DB
        result = Document.delete_metadata(db, document_id)

        return {"status": "success", "message": f"Document {document_id} deleted successfully."}
    
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )
