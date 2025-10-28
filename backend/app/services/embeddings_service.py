from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingsService:
    """Service to generate embeddings using Hugging Face SentenceTransformer."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.

        Args:
            model_name (str): Hugging Face model name. Default is 'all-MiniLM-L6-v2'.
        """
        print(f"🔹 Loading Hugging Face model: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded successfully!")

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.

        Args:
            texts (List[str]): List of text strings (chunks or sentences).

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        if not texts:
            raise ValueError("Text list cannot be empty")

        print(f"🧠 Generating embeddings for {len(texts)} text chunks...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        print("✅ Embeddings generated successfully!")
        return embeddings.tolist()
