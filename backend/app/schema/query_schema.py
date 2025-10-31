from pydantic import BaseModel

class QuerySource(BaseModel):
    chunk_text: str
    relevance_score: float

class QueryResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    sources: list[QuerySource]
    processing_time_seconds: float