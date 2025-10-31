import os
import faiss
import numpy as np
from fastapi import HTTPException


class FAISSVectorStore:
    """
    Handles FAISS index creation, storage, and retrieval of embeddings.
    Responsible ONLY for vector operations — not database writes.
    """

    def __init__(self, index_path: str = "data/faiss_index.index", embedding_dim: int = 384):
        """
        Initialize FAISS vector store.
        If index exists → load it, else create a new one.
        """
        self.index_path = index_path
        self.embedding_dim = embedding_dim
        self.index = None
        self._load_or_create_index()

    def _load_or_create_index(self):
        """Load existing FAISS index or create a new one."""
        try:
            if os.path.exists(self.index_path):
                print(f"📂 Loading FAISS index from {self.index_path}")
                self.index = faiss.read_index(self.index_path)
            else:
                print(f"🆕 Creating new FAISS index (dim={self.embedding_dim})")
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                self.index = faiss.IndexFlatL2(self.embedding_dim)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"FAISS index load/create failed: {str(e)}")


    def add_embeddings(self, embeddings: list[list[float]]) -> list[int]:
        """
        Add embeddings to the FAISS index and persist the index to disk.
        """
        try:
            if not embeddings:
                raise ValueError("No embeddings provided to add to FAISS index.")

            vectors = np.array(embeddings).astype("float32")
            start_id = self.index.ntotal
            self.index.add(vectors)
            self.save_index()
            print(f"✅ Added {len(embeddings)} vectors. Total vectors: {self.index.ntotal}")
            return list(range(start_id, self.index.ntotal))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add embeddings: {str(e)}")

    def search(self, query_vector: list[float], top_k: int = 5):
        """
        Search the FAISS index for the nearest embeddings.
        Returns (indices, distances).
        """
        try:
            if self.index is None:
                raise ValueError("FAISS index not loaded.")
            query = np.array([query_vector]).astype("float32")
            distances, indices = self.index.search(query, top_k)
            return indices[0].tolist(), distances[0].tolist()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"FAISS search failed: {str(e)}")

    def save_index(self):
        """
        Save the FAISS index to disk.
        """
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)
            print(f"💾 Saved FAISS index → {self.index_path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"FAISS index save failed: {str(e)}")


    @staticmethod
    def create_new_index(embeddings: list[list[float]], output_path: str, dimension: int | None = None) -> str:
        """
        Create and save a NEW FAISS index from embeddings (without touching global index).
        Useful for per-document indexing if desired.
        """
        try:
            if not embeddings:
                raise ValueError("No embeddings provided to create FAISS index.")

            dimension = dimension or len(embeddings[0])
            vectors = np.array(embeddings).astype("float32")

            index = faiss.IndexFlatL2(dimension)
            index.add(vectors)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            faiss.write_index(index, output_path)
            print(f"📘 Created new FAISS index → {output_path}")
            return output_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"FAISS index creation failed: {str(e)}")
