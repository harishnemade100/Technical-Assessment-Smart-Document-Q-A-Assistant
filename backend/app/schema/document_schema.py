from pydantic import BaseModel


class DocumentOut(BaseModel):
    """
    Response model when listing or fetching documents.
    """
    document_id: str
    filename: str
    uploaded_at: str
    chunk_count: int


class UploadResponse(BaseModel):
    """
    Response model after uploading a document.
    """
    document_id: str
    filename: str
    status: str
    chunks_created: int
    uploaded_at: str
