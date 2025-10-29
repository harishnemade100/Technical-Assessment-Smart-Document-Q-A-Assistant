from typing import List, Dict
import os
from sqlalchemy.orm import Session
from backend.app.services.vector_store_faiss import FAISSVectorStore
from backend.app.services.embeddings_service import EmbeddingsService
from backend.app.services.prompt_templates import PromptTemplates
from backend.app.models.models import DocumentChunk
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from backend.app.utils.database import load_config


BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
CONFIG_DIR: str = os.path.join(BASE_DIR, "config")


class QuestionAnsweringService:
    """
    Handles similarity search and LLM-based question answering using LangChain Runnable API.
    """

    def __init__(self, db: Session, vector_store_path: str = "data/faiss_index.index"):
        self.db = db
        self.vector_store = FAISSVectorStore(index_path=vector_store_path)
        self.embedder = EmbeddingsService(model_name="all-MiniLM-L6-v2")

        groq_conf = load_config("GEOQ_API_KEY")
        groq_api_key = groq_conf.get("API_KEY")

        if not groq_api_key:
            raise ValueError(" GROQ_API_KEY missing in local.yml → GROQ_CONFIG.API_KEY")

        # ✅ Initialize Groq LLM
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0.2,
            api_key=groq_api_key)

        # ✅ Get template string (make sure PromptTemplates.qa_template() returns a STRING)
        qa_template_str = PromptTemplates.qa_template()

        # ✅ Convert the string into a ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_template(qa_template_str)

        # ✅ Build the chain (Prompt → LLM)
        self.chain = RunnableSequence(self.prompt | self.llm)

    def _fetch_context(self, indices: List[int], limit: int = 5) -> List[Dict]:
        """
        Retrieve metadata for the top-matched chunks from PostgreSQL.
        """
        results = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.id.in_(indices[:limit]))
            .all()
        )
        return [
            {
                "page": r.page,
                "chunk_id": r.chunk_id,
                "text": r.text,
                "filename": r.filename,
            }
            for r in results
        ]

    def answer_question(self, query: str, top_k: int = 5) -> Dict:
        """
        Performs: FAISS search → Build context → LLM reasoning → Return answer + sources.
        """
        # Step 1: Embed the query
        query_vector = self.embedder.create_embeddings([query])[0]

        # Step 2: FAISS similarity search
        indices, distances = self.vector_store.search(query_vector, top_k=top_k)

        # Step 3: Fetch context text from DB
        context_chunks = self._fetch_context(indices, limit=top_k)
        context_text = "\n\n".join([c["text"] for c in context_chunks])

        # Step 4: Generate the answer using LangChain Runnable
        inputs = {"context": context_text, "question": query}
        response = self.chain.invoke(inputs)

        # Step 5: Extract text content (ChatGroq returns `AIMessage`)
        answer_text = getattr(response, "content", str(response))

        # Step 6: Build citations
        sources = [
            f"{c['filename']} (Chunk {c['chunk_id']}, Page {c.get('page', 'N/A')})"
            for c in context_chunks
        ]

        return {
            "question": query,
            "answer": answer_text.strip(),
            "sources": sources,
        }