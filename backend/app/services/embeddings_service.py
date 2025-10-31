from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
from constants import DEFAULT_EMBEDDING_MODEL


class EmbeddingsService:
    """
    Generates embeddings using a Hugging Face SentenceTransformer model.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        try:
            print(f"🔹 Loading Hugging Face model: {model_name} ...")
            self.model = SentenceTransformer(model_name)
            print("✅ Embedding model loaded successfully!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Embedding model load failed: {str(e)}")

    def create_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of text chunks.
        """
        try:
            if not texts:
                raise ValueError("Text list cannot be empty.")

            print(f"🧠 Generating embeddings for {len(texts)} chunks...")
            embeddings = self.model.encode(
                texts, convert_to_numpy=True, show_progress_bar=True
            )
            print("✅ Embeddings generated successfully!")
            return embeddings.tolist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")
