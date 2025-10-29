from fastapi import APIRouter, Depends
from backend.app.utils.database import get_db
from backend.app.services.question_answering import QuestionAnsweringService

router = APIRouter(prefix="/qa", tags=["Question Answering"])


@router.post("/")
async def ask_question(query: str, db=Depends(get_db)):
    """
    Ask a question → Retrieve relevant chunks → Generate answer via Groq.
    """
    qa_service = QuestionAnsweringService(db=db)
    result = qa_service.answer_question(query=query, top_k=5)
    return result