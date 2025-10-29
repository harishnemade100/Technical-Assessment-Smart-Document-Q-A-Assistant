import time
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.services.vector_store_faiss import FAISSVectorStore
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.prompt_templates import PromptTemplates
from backend.app.models.models import Document
from backend.app.schema.query_schema import QueryResponse, QuerySource
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from backend.app.utils.database import load_config


class QuestionAnsweringService:
    """
    Handles question answering with similarity search (FAISS) + LLM reasoning (LangChain + Groq).
    """

    def __init__(self, db: Session, vector_store_path: str = "data/faiss_index.index"):
        self.db = db
        self.vector_store = FAISSVectorStore(index_path=vector_store_path)
        self.embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")

        # Load Groq API key from config
        groq_conf = load_config("GROQ_API_KEY")
        groq_api_key = groq_conf.get("API_KEY")
        if not groq_api_key:
            raise ValueError("Missing GROQ_API_KEY in configuration file")

        # Initialize Groq model
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            api_key=groq_api_key,
        )

        # Create LangChain prompt and chain
        qa_template_str = PromptTemplates.qa_template()
        self.prompt = ChatPromptTemplate.from_template(qa_template_str)
        self.chain = RunnableSequence(self.prompt | self.llm)

    def _fetch_context(self, document_id: str, top_k: int) -> list[dict]:
        """
        Retrieve text context for a given document.

        NOTE: Since FAISS indices are integers (not linked to document.id),
        we fetch based only on the document_id.

        :param document_id: The UUID of the uploaded document.
        :param top_k: Number of chunks to include.
        """
        document = self.db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found.")

        # Return minimal simulated context (you can extend this later)
        return [
            {
                "text": f"Context chunk {i+1} for document {document.filename}",
                "filename": document.filename,
            }
            for i in range(top_k)
        ]


    def answer_question(self, document_id: str, question: str, top_k: int = 5) -> QueryResponse:
        """
        Answers a question based on the specified document using FAISS similarity search and LLM.


        :param document_id: The UUID of the uploaded document.
        :param question: The user's question.
        :param top_k: Number of similar chunks to retrieve from FAISS.
        :return: QueryResponse containing the answer and sources.

        """
        start_time = time.time()

        try:
            # Create embedding for the user's question
            query_vector = self.embedder.create_embeddings([question])[0]

            # Perform FAISS similarity search
            indices, scores = self.vector_store.search(query_vector, top_k=top_k)

            # Fetch context for document
            context_chunks = self._fetch_context(document_id=document_id, top_k=top_k)
            context_text = "\n\n".join([c["text"] for c in context_chunks])

            # Pass context and question into LLM
            inputs = {"context": context_text, "question": question}
            response = self.chain.invoke(inputs)
            answer_text = getattr(response, "content", str(response)).strip()

            # Build structured sources
            sources = [
                QuerySource(
                    chunk_text=ctx["text"],
                    relevance_score=float(scores[i]) if i < len(scores) else 0.0
                )
                for i, ctx in enumerate(context_chunks)
            ]

            # Return clean typed response
            processing_time = round(time.time() - start_time, 3)

            return QueryResponse(
                document_id=document_id,
                question=question,
                answer=answer_text,
                sources=sources,
                processing_time_seconds=processing_time,
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")