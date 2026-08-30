"""
production_rag.retrieval.reranker - Two-Stage Contextual Re-Ranker
"""

import re
from typing import List
from langchain_core.documents import Document

class ContextualReranker:
    """Re-ranks first-stage hybrid retrieval candidates using token overlap and query relevance density."""
    
    @staticmethod
    def rerank(query: str, candidate_docs: List[Document], top_n: int = 5) -> List[Document]:
        """Score candidate documents against query using token density and exact term matching."""
        if not candidate_docs:
            return []
            
        query_terms = set(re.findall(r"\w+", query.lower()))
        scores = []
        
        for doc in candidate_docs:
            doc_text_lower = doc.page_content.lower()
            doc_terms = set(re.findall(r"\w+", doc_text_lower))
            
            # 1. Term overlap ratio
            matched_terms = query_terms.intersection(doc_terms)
            overlap_score = len(matched_terms) / max(len(query_terms), 1)
            
            # 2. Metadata weight (SOPs given higher priority for resolution steps)
            metadata_bonus = 0.2 if doc.metadata.get("source_type") == "sop" else 0.1
            
            # 3. Critical severity bonus
            severity_bonus = 0.15 if any(lvl in doc_text_lower for lvl in ["critical", "error", "oomkilled"]) else 0.0
            
            final_score = (overlap_score * 0.65) + metadata_bonus + severity_bonus
            scores.append((final_score, doc))
            
        # Sort candidates by final rerank score
        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scores[:top_n]]
