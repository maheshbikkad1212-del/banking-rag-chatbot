import hashlib
from typing import Optional, Dict, Any

class MultiLevelCache:
    """
    Multi-level Caching Strategy:
    - L1: Normalized Query Cache (exact query string normalization lookup)
    - L2: Retrieval Results Cache (pre-retrieved hybrid document chunks)
    - L3: Final Answer Cache (synthesized responses with verified numeric guardrails)
    """
    def __init__(self):
        self.l1_normalized_queries: Dict[str, str] = {}
        self.l2_retrieval_cache: Dict[str, Any] = {}
        self.l3_response_cache: Dict[str, Any] = {}
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "misses": 0
        }

    def _hash_query(self, query: str) -> str:
        norm = query.strip().lower()
        return hashlib.sha256(norm.encode('utf-8')).hexdigest()

    def get_l3_response(self, query: str) -> Optional[Dict[str, Any]]:
        q_hash = self._hash_query(query)
        if q_hash in self.l3_response_cache:
            self.stats["l3_hits"] += 1
            return self.l3_response_cache[q_hash]
        return None

    def set_l3_response(self, query: str, response_data: Dict[str, Any]):
        q_hash = self._hash_query(query)
        self.l3_response_cache[q_hash] = response_data

    def get_l2_retrieval(self, query: str) -> Optional[Any]:
        q_hash = self._hash_query(query)
        if q_hash in self.l2_retrieval_cache:
            self.stats["l2_hits"] += 1
            return self.l2_retrieval_cache[q_hash]
        return None

    def set_l2_retrieval(self, query: str, chunks: Any):
        q_hash = self._hash_query(query)
        self.l2_retrieval_cache[q_hash] = chunks

    def clear(self):
        self.l1_normalized_queries.clear()
        self.l2_retrieval_cache.clear()
        self.l3_response_cache.clear()
        self.stats = {"l1_hits": 0, "l2_hits": 0, "l3_hits": 0, "misses": 0}

cache_system = MultiLevelCache()
