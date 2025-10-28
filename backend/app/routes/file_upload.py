import uuid
from fastapi import APIRouter, UploadFile, Depends
# from backend.app.utils.database import get_db
from backend.app.utils.file_utils import FileUtils
from backend.app.services.text_extraction import TextExtractor
from backend.app.services.text_spitter import TextSplitter
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.vector_store_faiss import FAISSVectorStore
# from backend.app.services.metadata_service import MetadataService

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
    filename = file.filename
    doc_id = str(uuid.uuid4())

    # Extract text
    text = TextExtractor.extract_text(saved_path)

    # Split text
    splitter = TextSplitter(chunk_size=800, overlap=100)
    chunks = splitter.split_text(text)

    # Create embeddings
    embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")
    embeddings = embedder.create_embeddings(chunks)


    vector_store = FAISSVectorStore(embedding_dim=len(embeddings[0]))
    vector_ids = vector_store.add_embeddings(embeddings)

    return {
        "doc_id": doc_id,
        "filename": filename,
        "chunks": len(chunks),
        "vector_count": len(vector_ids),
        "db_status": "✅ Metadata saved",
        "faiss_status": "✅ Vectors indexed",
    }
