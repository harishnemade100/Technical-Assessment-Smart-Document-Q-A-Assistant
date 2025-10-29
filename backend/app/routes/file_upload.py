import uuid
import traceback
from fastapi import APIRouter, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.utils.database import get_db
from backend.app.utils.file_utils import FileUtils
from backend.app.services.text_extraction import TextExtractor
from backend.app.services.text_spitter import TextSplitter
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.vector_store_faiss import FAISSVectorStore
from backend.app.schema.document_schema import UploadResponse
from backend.app.services.metadata_service import MetadataService


router = APIRouter(prefix="/api/documents", tags=["File Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    """
    Upload and process a document (PDF/TXT) for semantic retrieval and Q&A.

    This endpoint accepts a document upload, extracts its text content,
    splits it into manageable chunks, generates embeddings, and stores
    both the embeddings (in FAISS) and metadata (in PostgreSQL).
    : Workflow:
    1. Validate and save the uploaded file.
    2. Extract text content from the file.
    3. Split the text into smaller overlapping chunks.
    4. Generate sentence embeddings for each chunk.
    5. Persist the FAISS index to disk.
    6. Save document metadata (e.g., FAISS path, upload time) in PostgreSQL.


    :param file: Uploaded file (PDF or TXT).
    :param db: Database session dependency.
    :return: UploadResponse with document details and upload status.
    :raises HTTPException: If validation, extraction, embedding, or storage fails.
    """
    try:
        # Validate file extension
        ext = FileUtils.validate_file(file)
        if not ext:
            raise HTTPException(status_code=400, detail="Invalid or missing file extension.")

        # Save file locally
        saved_path = FileUtils.save_file(file)
        filename = file.filename
        document_id = str(uuid.uuid4())

        # Extract text from file
        try:
            text = TextExtractor.extract_text(saved_path)
            if not text or not text.strip():
                raise HTTPException(status_code=400, detail="No readable text found in document.")
        except Exception as extract_err:
            print(f" Text extraction failed: {extract_err}")
            raise HTTPException(status_code=400, detail=f"Text extraction error: {extract_err}")

        # Split text into chunks
        splitter = TextSplitter(chunk_size=800, overlap=100)
        chunks = splitter.split_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="Text splitting produced no chunks.")

        # Generate embeddings
        embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")
        embeddings = embedder.create_embeddings(chunks)
        if not embeddings:
            raise HTTPException(status_code=400, detail="Embedding generation failed.")
        print(f" Generated {len(embeddings)} embeddings (dim={len(embeddings[0])}).")

        try:
            vector_store = FAISSVectorStore(embedding_dim=len(embeddings[0]))
            vector_ids = vector_store.add_embeddings(embeddings)

            metadata_service = MetadataService()
            document = metadata_service.save_metadata(
                db=db,
                doc_id=document_id,
                filename=filename,
                chunks=chunks,
                embedding_dim=len(embeddings[0]),
                faiss_index_path=vector_store.index_path,
            )

            print(f" Stored {document_id} vectors in FAISS.")
        except Exception as faiss_err:
            print(f"❌ FAISS indexing failed: {faiss_err}")
            raise HTTPException(status_code=500, detail=f"FAISS indexing failed: {faiss_err}")

        return UploadResponse(
            document_id=document_id,
            filename=filename,
            status="Uploaded and processed successfully",
            chunks_created=len(chunks),
            uploaded_at=document.uploaded_at.isoformat(),
        )

    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected upload error: {str(e)}",
        )