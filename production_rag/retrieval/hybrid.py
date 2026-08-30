"""
production_rag.retrieval.hybrid - Hybrid Search Engine (BM25 + FAISS via Reciprocal Rank Fusion)
"""

from typing import List, Dict
from langchain_core.documents import Document
from production_rag.retrieval.bm25 import BM25SearchEngine
from production_rag.vector_store.faiss_store import FAISSVectorStore

class HybridSearchEngine:
    """Combines Dense Vector Search (FAISS) and Sparse Keyword Search (BM25) using RRF."""
    
    def __init__(self, vector_store: FAISSVectorStore, documents: List[Document], rrf_k: int = 60):
        self.vector_store = vector_store
        self.documents = documents
        self.rrf_k = rrf_k
        self.bm25_engine = BM25SearchEngine()
        self.bm25_engine.index_documents(documents)
        
    def search(self, query: str, top_k: int = 10) -> List[Document]:
        """
        Perform hybrid search using Reciprocal Rank Fusion (RRF).
        RRF_Score(doc) = 1 / (k + rank_dense) + 1 / (k + rank_sparse)
        """
        # 1. Fetch dense candidates from FAISS
        dense_docs = self.vector_store.search(query, k=top_k * 2)
        
        # 2. Fetch sparse candidates from BM25
        sparse_docs = self.bm25_engine.search(query, k=top_k * 2)
        
        # 3. Calculate Reciprocal Rank Fusion (RRF) scores
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}
        
        for rank, doc in enumerate(dense_docs):
            doc_id = doc.page_content[:100]  # Use content snippet as unique key
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (self.rrf_k + rank + 1)
            
        for rank, doc in enumerate(sparse_docs):
            doc_id = doc.page_content[:100]
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (self.rrf_k + rank + 1)
            
        # 4. Sort documents by merged RRF score
        sorted_doc_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        return [doc_map[doc_id] for doc_id in sorted_doc_ids[:top_k]]
