import numpy as np
from typing import List, Union

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.use_fallback = False
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print(f"[EmbeddingEngine] Successfully loaded sentence-transformer: {self.model_name}")
        except Exception as e:
            print(f"[EmbeddingEngine] Warning: Could not load sentence-transformers ({e}). Using deterministic semantic vectorizer fallback.")
            self.use_fallback = True

    def embed_text(self, text: str) -> List[float]:
        if not self.use_fallback and self.model:
            vec = self.model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        else:
            return self._fallback_embed(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.use_fallback and self.model:
            vecs = self.model.encode(texts, convert_to_numpy=True)
            return vecs.tolist()
        else:
            return [self._fallback_embed(t) for t in texts]

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """Deterministic hash-based TF frequency embedding vectorizer."""
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for word in words:
            # Simple hash bin mapping
            h = hash(word) % dim
            vec[h] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

embedding_engine = EmbeddingEngine()
