import os
import faiss
import numpy as np
from typing import List


class FAISSVectorStore:
    """
    Handles creation, storage, and retrieval of embeddings using FAISS.
    """

    def __init__(self, index_path: str = "data/faiss_index.index", embedding_dim: int = 1536):
        self.index_path = index_path
        self.embedding_dim = embedding_dim
        self.index = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            print(f"📂 Loading FAISS index from {self.index_path}")
            self.index = faiss.read_index(self.index_path)
        else:
            print(f"🆕 Creating new FAISS index (dim={self.embedding_dim})")
            self.index = faiss.IndexFlatL2(self.embedding_dim)

    def add_embeddings(self, embeddings: List[List[float]]) -> List[int]:
        vectors = np.array(embeddings).astype("float32")
        start_id = self.index.ntotal
        self.index.add(vectors)
        self.save_index()
        return list(range(start_id, self.index.ntotal))

    def save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        print(f"💾 Saved FAISS index → {self.index_path}")

    def search(self, query_vector: List[float], top_k: int = 5):
        if self.index is None:
            raise ValueError("FAISS index not loaded.")
        query = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(query, top_k)
        return indices[0].tolist(), distances[0].tolist()
