from typing import List, Dict, Any
import re

def rerank_chunks(
    chunks: List[Dict[str, Any]],
    query: str
) -> List[Dict[str, Any]]:
    """
    Re-ranks candidate chunks by scoring query keyword match density, authority level, and version recency.
    """
    if not chunks:
        return []

    query_words = set(re.findall(r'\w+', query.lower()))
    stop_words = {"what", "is", "a", "an", "the", "for", "of", "and", "or", "in", "on", "to", "with", "are", "how", "do", "does"}
    query_keywords = {w for w in query_words if w not in stop_words and len(w) > 1}

    reranked = []
    for chunk in chunks:
        score = chunk.get("score", 0.5)
        text_lower = chunk["text"].lower()

        # Query Keyword Match Boost (Top priority for accurate retrieval)
        if query_keywords:
            matched_kws = sum(1 for kw in query_keywords if kw in text_lower)
            match_ratio = matched_kws / len(query_keywords)
            score += (match_ratio * 0.30)  # Strong boost for matching user query keywords

        # Authority & Recency Boost
        meta = chunk.get("metadata", {})
        auth = meta.get("authority", "").lower()
        if "reserve bank of india" in auth or "rbi" in auth:
            score += 0.05
        
        eff_date = meta.get("effective_date", "")
        if "2025" in eff_date or "2026" in eff_date:
            score += 0.05

        # Numerical & Currency Query Boost
        q_has_numbers = any(char.isdigit() for char in query)
        text_has_numbers = any(char.isdigit() for char in chunk["text"])
        if q_has_numbers and text_has_numbers:
            score += 0.10

        item = chunk.copy()
        item["reranked_score"] = round(float(score), 4)
        reranked.append(item)

    reranked.sort(key=lambda x: x["reranked_score"], reverse=True)
    return reranked

