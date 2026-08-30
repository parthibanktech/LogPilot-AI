"""
production_rag.retrieval.bm25 - BM25 Sparse Keyword Search Indexer
"""

import math
import re
from collections import Counter
from typing import List
from langchain_core.documents import Document

class BM25SearchEngine:
    """BM25 Inverted Index for exact keyword, IP address, and error code matching."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: List[Document] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_lens: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Counter = Counter()
        self.idf: dict = {}
        
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenize string into lowercase alphanumeric and symbol terms (IPs, hex IDs)."""
        return re.findall(r"\w+|[\d\.]+", text.lower())
        
    def index_documents(self, documents: List[Document]):
        """Build BM25 index over document corpus."""
        self.documents = documents
        self.doc_tokens = [self._tokenize(doc.page_content) for doc in documents]
        self.doc_lens = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_len = sum(self.doc_lens) / max(len(self.doc_lens), 1)
        
        # Calculate document frequencies
        df = Counter()
        for tokens in self.doc_tokens:
            unique_terms = set(tokens)
            for term in unique_terms:
                df[term] += 1
        self.doc_freqs = df
        
        # Calculate Inverse Document Frequency (IDF)
        num_docs = len(documents)
        for term, freq in df.items():
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1.0)
            
    def search(self, query: str, k: int = 5) -> List[Document]:
        """Search corpus using BM25 scoring algorithm."""
        if not self.documents:
            return []
            
        query_tokens = self._tokenize(query)
        scores = [0.0] * len(self.documents)
        
        for idx, tokens in enumerate(self.doc_tokens):
            token_counts = Counter(tokens)
            doc_len = self.doc_lens[idx]
            
            for q_term in query_tokens:
                if q_term in token_counts:
                    tf = token_counts[q_term]
                    idf_score = self.idf.get(q_term, 0.0)
                    # BM25 term weighting formula
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(self.avg_doc_len, 1.0)))
                    scores[idx] += idf_score * (numerator / denominator)
                    
        # Rank documents by BM25 score
        scored_docs = sorted(zip(scores, self.documents), key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:k] if score > 0]
