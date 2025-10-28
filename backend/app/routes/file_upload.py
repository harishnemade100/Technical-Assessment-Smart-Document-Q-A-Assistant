from fastapi import APIRouter, UploadFile
from backend.app.utils.file_utils import FileUtils
from backend.app.services.text_extraction import TextExtractor
from backend.app.services.text_spitter import TextSplitter
from backend.app.services.embeddings_service import EmbeddingsService

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/")
async def upload_document(file: UploadFile):
    """
    Uploads a PDF/TXT file, extracts text, splits it into chunks,
    and generates embeddings.
    """
    # Validate and save
    ext = FileUtils.validate_file(file)
    saved_path = FileUtils.save_file(file)

    # Extract text
    text = TextExtractor.extract_text(saved_path)

    # Split text
    splitter = TextSplitter(chunk_size=800, overlap=100)
    chunks = splitter.split_text(text)

    # Create embeddings
    embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")
    embeddings = embedder.create_embeddings(chunks)

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "embeddings_count": len(embeddings),
        "sample_embedding_dim": len(embeddings[0]) if embeddings else 0,
    }
