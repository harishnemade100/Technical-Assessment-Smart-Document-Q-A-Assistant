import uuid
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.utils.database import get_db
from backend.app.utils.file_utils import FileUtils
from backend.app.services.text_extraction import TextExtractor
from backend.app.services.text_spitter import  TextSplitter
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.vector_store_faiss import FAISSVectorStore
from backend.app.services.metadata_service import MetadataService

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    """
    Upload a PDF/TXT file → extract text → split into chunks →
    generate embeddings → save metadata in PostgreSQL + vectors in FAISS.
    """
    try:
        # --- 1️⃣ Validate and save file locally ---
        ext = FileUtils.validate_file(file)
        saved_path = FileUtils.save_file(file)
        filename = file.filename
        doc_id = str(uuid.uuid4())

        # --- 2️⃣ Extract text ---
        text = TextExtractor.extract_text(saved_path)
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="File text extraction failed or file is empty.")

        # --- 3️⃣ Split text into chunks ---
        splitter = TextSplitter(chunk_size=800, overlap=100)
        chunks = splitter.split_text(text)

        # --- 4️⃣ Generate embeddings using sentence-transformers ---
        embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")
        embeddings = embedder.create_embeddings(chunks)

        # --- 5️⃣ Store embeddings in FAISS ---
        vector_store = FAISSVectorStore(embedding_dim=len(embeddings[0]))
        vector_ids = vector_store.add_embeddings(embeddings)

        # --- 6️⃣ Save document + chunk metadata in PostgreSQL ---
        metadata_service = MetadataService()
        metadata_service.save_metadata(
            db=db,
            doc_id=doc_id,
            filename=filename,
            chunks=chunks,
            embedding_dim=len(embeddings[0])
        )


        # --- 7️⃣ Return response summary ---
        return {
            "doc_id": doc_id,
            "filename": filename,
            "chunks_processed": len(chunks),
            "vectors_indexed": len(vector_ids),
            "db_status": "✅ Metadata saved to PostgreSQL",
            "faiss_status": "✅ Vectors indexed in FAISS"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
