from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.utils.database import get_db
from backend.app.services.question_answering import QuestionAnsweringService
from backend.app.schema.query_schema import QueryResponse

router = APIRouter(prefix="/api/documents", tags=["Question Answering"])


@router.post("/query", response_model=QueryResponse)
async def ask_question(
    document_id: str = Query(..., description="UUID of the uploaded document"),
    question: str = Query(..., description="User's natural language question"),
    db: Session = Depends(get_db),
):
    """
    Ask a question about an uploaded document using the RAG pipeline.

    Flow:
    1. Create embedding for the user's question.
    2. Perform FAISS similarity search to find relevant document chunks.
    3. Fetch context for the document.
    4. Pass context and question into LLM for answer generation.
    5. Build structured sources from retrieved chunks.
    6. Return a clean typed response with the answer and sources.

    :param document_id: UUID of the uploaded document.
    :param question: User's natural language question.
    :param db: Database session dependency.
    :return: QueryResponse containing the answer and sources.

    :raises HTTPException: If any step in the pipeline fails.
    """
    try:
        # Initialize service
        qa_service = QuestionAnsweringService(db=db)

        # Set internal default for top_k
        top_k = 5  # Default number of top chunks to retrieve

        # Run full pipeline
        response = qa_service.answer_question(
            document_id=document_id,
            question=question,
            top_k=top_k,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")