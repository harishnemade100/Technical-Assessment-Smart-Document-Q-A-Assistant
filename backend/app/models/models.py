# from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, func
# from backend.app.utils.database import Base


# class DocumentChunk(Base):
#     __tablename__ = "document_chunks"

#     id = Column(Integer, primary_key=True, index=True)
#     doc_id = Column(String, index=True)
#     filename = Column(String, nullable=False)
#     chunk_id = Column(Integer, nullable=False)
#     page = Column(Integer, nullable=True)
#     text = Column(String, nullable=False)
#     embedding_dim = Column(Integer)
#     metadata = Column(JSON)
#     uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
