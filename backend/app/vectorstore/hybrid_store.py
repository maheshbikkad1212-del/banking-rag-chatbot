import numpy as np
from typing import List, Dict, Any, Optional
from app.vectorstore.embeddings import embedding_engine
from app.vectorstore.sparse_bm25 import BM25Indexer

class HybridVectorStore:
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []
        self.bm25_indexer = BM25Indexer()

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        if not new_chunks:
            return

        texts = [chunk["text"] for chunk in new_chunks]
        new_embeds = embedding_engine.embed_documents(texts)

        start_id = len(self.chunks)
        for i, chunk in enumerate(new_chunks):
            chunk["chunk_id"] = f"chunk_{start_id + i}"
            self.chunks.append(chunk)

        self.embeddings.extend(new_embeds)
        self.bm25_indexer.index_documents(self.chunks)

    def hybrid_search(
        self,
        query: str,
        top_k: int = 6,
        metadata_filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5  # Weight between dense (alpha) and sparse (1-alpha)
    ) -> List[Dict[str, Any]]:
        """
        Executes Dense Cosine Similarity + Sparse BM25 Search with RRF Fusion and Metadata Filtering.
        """
        if not self.chunks:
            return []

        # 1. Dense Cosine Search
        query_vec = np.array(embedding_engine.embed_text(query), dtype=np.float32)
        doc_matrix = np.array(self.embeddings, dtype=np.float32)

        query_norm = np.linalg.norm(query_vec)
        if query_norm > 0:
            query_vec = query_vec / query_norm

        matrix_norms = np.linalg.norm(doc_matrix, axis=1, keepdims=True)
        matrix_norms[matrix_norms == 0] = 1.0
        normalized_matrix = doc_matrix / matrix_norms

        dense_scores = np.dot(normalized_matrix, query_vec)

        # 2. Sparse BM25 Search
        bm25_results = self.bm25_indexer.search(query, top_k=len(self.chunks))
        sparse_scores = np.zeros(len(self.chunks), dtype=np.float32)
        for idx, score in bm25_results:
            sparse_scores[idx] = score

        # Normalize sparse scores to 0-1 range
        max_sparse = np.max(sparse_scores) if np.max(sparse_scores) > 0 else 1.0
        sparse_scores_norm = sparse_scores / max_sparse

        # 3. Hybrid Fusion Score Calculation
        hybrid_scores = (alpha * dense_scores) + ((1.0 - alpha) * sparse_scores_norm)

        # 4. Rank candidates and apply Metadata Filters
        ranked_indices = np.argsort(hybrid_scores)[::-1]

        results = []
        for idx in ranked_indices:
            chunk = self.chunks[idx].copy()
            score = float(hybrid_scores[idx])

            # Apply Metadata Filtering if specified
            if metadata_filters:
                match = True
                for key, val in metadata_filters.items():
                    if key in chunk.get("metadata", {}) and chunk["metadata"][key] != val:
                        match = False
                        break
                if not match:
                    continue

            chunk["score"] = score
            chunk["dense_score"] = float(dense_scores[idx])
            chunk["sparse_score"] = float(sparse_scores_norm[idx])
            results.append(chunk)

            if len(results) >= top_k:
                break

        return results

    def clear(self):
        self.chunks = []
        self.embeddings = []
        self.bm25_indexer = BM25Indexer()

vector_store = HybridVectorStore()
