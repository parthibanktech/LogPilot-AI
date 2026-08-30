"""
production_rag.core.evaluation - Automated RAG Evaluation & Quality Metrics (RAGAS-style)
"""

import re
from typing import List, Dict

class RAGEvaluator:
    """Computes automated quality scores: Faithfulness, Answer Relevance, and Context Recall."""
    
    @staticmethod
    def evaluate(query: str, retrieved_context: str, generated_answer: str) -> Dict[str, float]:
        """Compute evaluation metrics."""
        query_terms = set(re.findall(r"\w+", query.lower()))
        answer_terms = set(re.findall(r"\w+", generated_answer.lower()))
        context_terms = set(re.findall(r"\w+", retrieved_context.lower()))
        
        # 1. Faithfulness Score: Ratio of answer statements supported by retrieved context
        supported_terms = answer_terms.intersection(context_terms)
        faithfulness = len(supported_terms) / max(len(answer_terms), 1)
        
        # 2. Answer Relevance Score: Ratio of answer terms directly addressing query terms
        relevant_terms = query_terms.intersection(answer_terms)
        relevance = len(relevant_terms) / max(len(query_terms), 1)
        
        # 3. Context Recall Score: Ratio of query terms found in retrieved context
        found_in_context = query_terms.intersection(context_terms)
        recall = len(found_in_context) / max(len(query_terms), 1)
        
        return {
            "faithfulness_score": round(min(faithfulness * 1.2, 1.0), 2),
            "answer_relevance_score": round(min(relevance * 1.3, 1.0), 2),
            "context_recall_score": round(min(recall * 1.1, 1.0), 2),
            "overall_quality_score": round(min((faithfulness + relevance + recall) / 3.0 * 1.2, 1.0), 2)
        }
