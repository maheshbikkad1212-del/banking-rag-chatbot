import numpy as np
from typing import List, Dict, Any
from app.vectorstore.embeddings import embedding_engine

def apply_mmr(
    query: str,
    chunks: List[Dict[str, Any]],
    top_k: int = 4,
    lambda_param: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Max Marginal Relevance (MMR) diversification algorithm.
    Calculates query-chunk similarity and penalizes inter-chunk similarity to maximize coverage diversity.
    """
    if not chunks:
        return []
    if len(chunks) <= top_k:
        return chunks

    query_vec = np.array(embedding_engine.embed_text(query), dtype=np.float32)
    chunk_texts = [c["text"] for c in chunks]
    doc_vecs = np.array(embedding_engine.embed_documents(chunk_texts), dtype=np.float32)

    # Normalize vectors
    q_norm = np.linalg.norm(query_vec)
    if q_norm > 0:
        query_vec /= q_norm

    doc_norms = np.linalg.norm(doc_vecs, axis=1, keepdims=True)
    doc_norms[doc_norms == 0] = 1.0
    doc_vecs /= doc_norms

    # Cosine sim with query
    query_sims = np.dot(doc_vecs, query_vec)

    # Cosine sim between documents
    doc_sims = np.dot(doc_vecs, doc_vecs.T)

    selected_indices = []
    unselected_indices = list(range(len(chunks)))

    # First choice: highest relevance to query
    first_idx = int(np.argmax(query_sims))
    selected_indices.append(first_idx)
    unselected_indices.remove(first_idx)

    while len(selected_indices) < top_k and unselected_indices:
        mmr_scores = []
        for unselected in unselected_indices:
            rel_score = query_sims[unselected]
            # Max similarity to any already selected document
            max_sim_to_selected = max([doc_sims[unselected][selected] for selected in selected_indices])
            
            mmr_score = (lambda_param * rel_score) - ((1 - lambda_param) * max_sim_to_selected)
            mmr_scores.append((mmr_score, unselected))

        mmr_scores.sort(key=lambda x: x[0], reverse=True)
        best_unselected = mmr_scores[0][1]
        selected_indices.append(best_unselected)
        unselected_indices.remove(best_unselected)

    return [chunks[idx] for idx in selected_indices]
