"""
production_rag.core.cache - Semantic Response Cache (<10ms Return)
"""

import time
import math
from typing import Optional, Dict
from production_rag.vector_store.embeddings import ResilientEmbeddings

def cosine_similarity(v1, v2) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    return dot / (norm_a * norm_b + 1e-9)

class SemanticCache:
    """Stores query vectors and cached answers to provide instant responses for similar queries."""
    
    def __init__(self, similarity_threshold: float = 0.92):
        self.similarity_threshold = similarity_threshold
        self.embeddings = ResilientEmbeddings()
        self.cache_entries: list = []  # [{query: str, vector: list, answer: str, timestamp: float}]
        
    def get(self, query: str) -> Optional[dict]:
        """Check cache for semantic match."""
        if not self.cache_entries:
            return None
            
        try:
            query_vector = self.embeddings.embed_query(query)
            best_match = None
            highest_sim = -1.0
            
            for entry in self.cache_entries:
                sim = cosine_similarity(query_vector, entry["vector"])
                if sim > highest_sim:
                    highest_sim = sim
                    best_match = entry
                    
            if highest_sim >= self.similarity_threshold and best_match:
                return {
                    "answer": best_match["answer"],
                    "similarity": round(highest_sim, 4),
                    "is_cache_hit": True
                }
        except Exception as e:
            print(f"[Cache Warning] Failed to check semantic cache: {e}")
            
        return None
        
    def set(self, query: str, answer: str):
        """Store query vector and answer in cache."""
        try:
            query_vector = self.embeddings.embed_query(query)
            self.cache_entries.append({
                "query": query,
                "vector": query_vector,
                "answer": answer,
                "timestamp": time.time()
            })
            # Limit cache size to 100 entries
            if len(self.cache_entries) > 100:
                self.cache_entries.pop(0)
        except Exception as e:
            print(f"[Cache Warning] Failed to store in semantic cache: {e}")

semantic_cache = SemanticCache()
