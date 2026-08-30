"""
production_rag.app.service - Main Service Orchestrator (v5.3)
"""

import os
import re
import time
from typing import List, Dict, Generator

from production_rag.config.settings import settings
from production_rag.data_ingestion.processor import IngestionPipeline
from production_rag.vector_store.faiss_store import FAISSVectorStore
from production_rag.retrieval.hybrid import HybridSearchEngine
from production_rag.retrieval.reranker import ContextualReranker
from production_rag.retrieval.filter import MetadataFilterEngine
from production_rag.retrieval.engine import RetrievalEngine
from production_rag.core.agent_router import AgentQueryRouter
from production_rag.core.query_rewriter import MultiTurnQueryRewriter
from production_rag.core.knowledge_graph import ServiceKnowledgeGraph
from production_rag.core.cache import semantic_cache
from production_rag.core.guardrail import SafetyGuardian
from production_rag.core.telemetry import telemetry
from production_rag.core.evaluation import RAGEvaluator
from production_rag.llm.client import LLMFactory
from production_rag.llm.prompts import sysops_prompt

class SysOpsRAGService:
    """Enterprise RAG Service Orchestrator v5.3."""
    
    def __init__(self):
        print("[Service Init] Loading documents and initializing Enterprise RAG Service v5.3 Engine...")
        self.pipeline = IngestionPipeline()
        self.documents = self.pipeline.run()
        
        self.vector_store = FAISSVectorStore()
        self.vector_store.build_from_documents(self.documents)
        
        self.hybrid_engine = HybridSearchEngine(self.vector_store, self.documents)
        self.model = LLMFactory.get_model(temperature=0.0, max_tokens=3000)
        print("[Service Init] Enterprise RAG Service v5.3 initialized successfully.")
        
    def process_query(self, query: str, chat_history: List[Dict[str, str]] = None, service_filter: str = None) -> dict:
        """Process query through Agentic Router, Multi-Turn Context, GraphRAG, Hybrid Search, Live Log Injection, Reranking, Evaluation, and Cache."""
        start_time = time.time()
        
        # Clear cache entries when dynamic log filtering is requested to prevent stale log user IDs
        if service_filter and service_filter != "all":
            semantic_cache.cache_entries.clear()
            
        # 1. Agentic Query Intent Classification & Routing
        route_decision = AgentQueryRouter.route_query(query)
        
        # 2. Multi-Turn Conversational Query Rewriting
        contextual_query = MultiTurnQueryRewriter.contextualize_query(query, chat_history or [])
        
        # 3. Check Semantic Cache (<10ms return) - Only for static SOP queries, bypass for live log filtering
        cached_result = None
        if not service_filter or service_filter == "all":
            cached_result = semantic_cache.get(contextual_query)
            
        if cached_result:
            latency_ms = (time.time() - start_time) * 1000
            telemetry.log_query_event(query, latency_ms, 5, "CACHE_HIT", False)
            return {
                "success": True,
                "answer": cached_result["answer"] + f"\n\n*(⚡ Sub-10ms Semantic Cache Hit - Similarity: {cached_result['similarity']})*",
                "latency_ms": latency_ms,
                "guardrail_triggered": False,
                "is_cache_hit": True,
                "route_info": route_decision
            }
            
        # 4. Pre-Query Guardrail Check
        input_check = SafetyGuardian.inspect_input(contextual_query)
        if not input_check["is_safe"]:
            latency_ms = (time.time() - start_time) * 1000
            telemetry.log_query_event(query, latency_ms, 0, "BLOCKED_INPUT", True)
            return {
                "success": False,
                "answer": f"❌ **SECURITY GUARDRAIL REJECTION**: {input_check['reason']}",
                "latency_ms": latency_ms,
                "guardrail_triggered": True,
                "is_cache_hit": False,
                "route_info": route_decision
            }
            
        # 5. GraphRAG Service Dependency Injection
        graph_context = ""
        for s_name in ["gateway-proxy", "auth-service", "payment-gateway-service", "postgres-primary", "kafka-broker-1"]:
            if s_name in contextual_query.lower():
                graph_context += ServiceKnowledgeGraph.format_graph_context(s_name)
                
        # 6. Hybrid Search (BM25 + FAISS via RRF) with Metadata Filtering
        try:
            candidates = self.hybrid_engine.search(contextual_query, top_k=15)
            
            # Determine target service domain from query or explicit dropdown
            query_lower = contextual_query.lower()
            
            # 7. Cross-Encoder Re-Ranking (Top 5 chunks)
            top_chunks = ContextualReranker.rerank(contextual_query, candidates, top_n=5)
            
            # Identify relevant service categories from top chunks & query
            relevant_services = set()
            for chunk in top_chunks:
                src = chunk.metadata.get("source", "").lower()
                svc = chunk.metadata.get("service", "").lower()
                if src: relevant_services.add(src)
                if svc: relevant_services.add(svc)
                
            # 8. Live Realtime Log Tail Injection (Strictly scoped to query-relevant services)
            live_log_context = ""
            if os.path.exists(settings.LOG_DIR):
                target_service = service_filter.lower() if service_filter and service_filter != "all" else ""
                
                for root, _, files in os.walk(settings.LOG_DIR):
                    for file in files:
                        if file.endswith(".log") or file.endswith(".txt"):
                            rel_path = os.path.relpath(os.path.join(root, file), start=settings.LOG_DIR).replace("\\", "/")
                            rel_lower = rel_path.lower()
                            
                            # Ensure live log stream is relevant to the query or explicitly requested service
                            is_explicit_match = target_service and target_service in rel_lower
                            is_topic_match = any(rel_tok in query_lower for rel_tok in rel_lower.split("/")) or \
                                             any(s_name in rel_lower for s_name in relevant_services if s_name != "sop")
                                             
                            if (is_explicit_match and is_topic_match) or (not target_service and is_topic_match):
                                try:
                                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                                        lines = f.readlines()
                                        live_log_context += f"\n=== REALTIME LIVE LOG STREAM ({rel_path} - Last 40 Lines) ===\n" + "".join(lines[-40:])
                                except Exception:
                                    pass

            formatted_context = RetrievalEngine.format_context_documents(top_chunks)
            if live_log_context:
                formatted_context += "\n" + live_log_context
            if graph_context:
                formatted_context += "\n" + graph_context
            
            # 9. LLM Generation
            prompt_value = sysops_prompt.format(context=formatted_context, question=contextual_query)
            raw_response = self.model.invoke(prompt_value).content
            latency_ms = (time.time() - start_time) * 1000
            
            # 10. Post-Output Guardrail Check
            output_check = SafetyGuardian.inspect_output(raw_response)
            final_answer = output_check["sanitized_output"]
            guardrail_triggered = not output_check["is_safe"]
            
            # 11. RAGAS Quality Evaluation
            eval_metrics = RAGEvaluator.evaluate(contextual_query, formatted_context, final_answer)
            
            # 12. Store in Semantic Cache (Only if no specific service filter was requested)
            if not guardrail_triggered and (not service_filter or service_filter == "all"):
                semantic_cache.set(contextual_query, final_answer)
            telemetry.log_query_event(query, latency_ms, 5, "SUCCESS", guardrail_triggered)
            
            return {
                "success": True,
                "answer": final_answer,
                "latency_ms": latency_ms,
                "guardrail_triggered": guardrail_triggered,
                "is_cache_hit": False,
                "route_info": route_decision,
                "eval_metrics": eval_metrics
            }
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            telemetry.log_query_event(query, latency_ms, 0, "ERROR", False)
            return {
                "success": False,
                "answer": f"⚠️ **RAG EXECUTION FAILURE**: {str(e)}",
                "latency_ms": latency_ms,
                "guardrail_triggered": False,
                "is_cache_hit": False,
                "route_info": route_decision
            }
            
    def stream_query_tokens(self, query: str, chat_history: List[Dict[str, str]] = None) -> Generator[str, None, None]:
        """Real-time token stream generator."""
        contextual_query = MultiTurnQueryRewriter.contextualize_query(query, chat_history or [])
        candidates = self.hybrid_engine.search(contextual_query, top_k=15)
        top_chunks = ContextualReranker.rerank(contextual_query, candidates, top_n=5)
        formatted_context = RetrievalEngine.format_context_documents(top_chunks)
        prompt_value = sysops_prompt.format(context=formatted_context, question=contextual_query)
        
        for chunk in self.model.stream(prompt_value):
            yield chunk.content
