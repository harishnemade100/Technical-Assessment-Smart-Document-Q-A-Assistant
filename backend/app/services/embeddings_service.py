from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
from backend.app.settings.constants import DEFAULT_EMBEDDING_MODEL
from app.utils.cache import redis_cache
from typing import List
import hashlib


class EmbeddingsService:
    """
    Generates embeddings using a Hugging Face SentenceTransformer model
    with Redis-based caching for performance.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        try:
            print(f"🔹 Loading Hugging Face model: {model_name} ...")
            self.model = SentenceTransformer(model_name)
            print("✅ Embedding model loaded successfully!")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Embedding model load failed: {str(e)}"
            )

    def _cache_key(self, text: str) -> str:
        """
        Generate a stable cache key for a text input.
        Uses SHA256 instead of Python hash (Python hash is not stable).
        """
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"embedding:{digest}"

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.
        Uses Redis cache to avoid recomputing embeddings.
        """
        try:
            if not texts:
                raise ValueError("Text list cannot be empty.")

            embeddings: List[List[float]] = []
            texts_to_compute = []
            compute_indices = []

            # 1️⃣ Check cache first
            for idx, text in enumerate(texts):
                key = self._cache_key(text)
                cached_embedding = redis_cache.get(key)

                if cached_embedding:
                    embeddings.append(cached_embedding)
                else:
                    embeddings.append(None)
                    texts_to_compute.append(text)
                    compute_indices.append(idx)

            # 2️⃣ Compute only missing embeddings
            if texts_to_compute:
                print(f" Generating embeddings for {len(texts_to_compute)} new chunks...")
                new_embeddings = self.model.encode(
                    texts_to_compute,
                    convert_to_numpy=True,
                    show_progress_bar=True
                ).tolist()

                # 3️⃣ Store in cache and merge results
                for i, emb in zip(compute_indices, new_embeddings):
                    key = self._cache_key(texts[i])
                    redis_cache.set(key, emb)
                    embeddings[i] = emb

            print(" Embeddings generated successfully!")
            return embeddings

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Embedding generation failed: {str(e)}"
            )
