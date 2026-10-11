import math
from typing import List, Dict, Any, Tuple
import re

class BM25Indexer:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: List[Dict[str, int]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.idf: Dict[str, float] = {}
        self.num_docs: int = 0
        self.corpus_chunks: List[Dict[str, Any]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Split tokens preserving numbers, percentages, currency (e.g., 7.25%, ₹30, 90%)
        tokens = re.findall(r'\b\w+(?:[\.\%]\w+)*\b', text.lower())
        return tokens

    def index_documents(self, chunks: List[Dict[str, Any]]):
        self.corpus_chunks = chunks
        self.num_docs = len(chunks)
        self.doc_freqs = []
        self.doc_lengths = []
        df: Dict[str, int] = {}

        for chunk in chunks:
            tokens = self._tokenize(chunk["text"])
            self.doc_lengths.append(len(tokens))
            freq_map: Dict[str, int] = {}
            for t in tokens:
                freq_map[t] = freq_map.get(t, 0) + 1
            self.doc_freqs.append(freq_map)
            
            for t in set(tokens):
                df[t] = df.get(t, 0) + 1

        self.avg_doc_len = sum(self.doc_lengths) / self.num_docs if self.num_docs > 0 else 1.0

        # Calculate IDF
        for token, freq in df.items():
            self.idf[token] = math.log((self.num_docs - freq + 0.5) / (freq + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.num_docs

        for token in query_tokens:
            if token not in self.idf:
                continue
            idf_val = self.idf[token]
            for doc_idx, freq_map in enumerate(self.doc_freqs):
                if token in freq_map:
                    tf = freq_map[token]
                    doc_len = self.doc_lengths[doc_idx]
                    num = tf * (self.k1 + 1)
                    denom = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    scores[doc_idx] += idf_val * (num / denom)

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [(idx, score) for idx, score in ranked[:top_k] if score > 0]
