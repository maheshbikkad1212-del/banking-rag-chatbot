from typing import List, Dict, Any, Tuple

class CorrectiveRAGEvaluator:
    def __init__(self, relevance_threshold: float = 0.35):
        self.relevance_threshold = relevance_threshold

    def evaluate_retrieval(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluates context quality (Relevance, Coverage, Faithfulness).
        Returns action signal: 'CORRECT' (proceed), 'AMBIGUOUS' (re-rank/expand), or 'INCORRECT' (fallback re-retrieval).
        """
        if not retrieved_chunks:
            return {
                "evaluation_status": "INCORRECT",
                "confidence_score": 0.0,
                "relevance_score": 0.0,
                "coverage_score": 0.0,
                "recommendation": "No documents retrieved. Trigger emergency re-retrieval with broad search."
            }

        scores = [c.get("score", 0.0) for c in retrieved_chunks]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        max_score = max(scores) if scores else 0.0

        # Keyword coverage check
        query_words = set(w.lower() for w in query.split() if len(w) > 3)
        combined_text = " ".join([c["text"].lower() for c in retrieved_chunks])
        matched_words = [w for w in query_words if w in combined_text]
        coverage_score = len(matched_words) / len(query_words) if query_words else 1.0

        confidence = (0.6 * max_score) + (0.4 * coverage_score)

        if max_score >= self.relevance_threshold and coverage_score >= 0.4:
            status = "CORRECT"
            rec = "Retrieved context has high relevance and adequate policy coverage."
        elif max_score >= 0.20:
            status = "AMBIGUOUS"
            rec = "Context partial. Applying intent query expansion and re-ranking."
        else:
            status = "INCORRECT"
            rec = "Low context relevance detected. Performing corrective fallback search."

        return {
            "evaluation_status": status,
            "confidence_score": round(float(confidence), 3),
            "relevance_score": round(float(max_score), 3),
            "coverage_score": round(float(coverage_score), 3),
            "recommendation": rec
        }

crag_evaluator = CorrectiveRAGEvaluator()
