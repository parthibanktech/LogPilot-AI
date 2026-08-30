"""
production_rag.core.knowledge_graph - Multi-Hop GraphRAG Knowledge Graph Engine
"""

from typing import List, Dict, Set

class ServiceKnowledgeGraph:
    """
    Graph-Augmented RAG (GraphRAG) Engine.
    Builds an explicit Architecture Dependency Graph (Nodes = Microservices, Edges = Downstream Dependencies)
    and executes multi-hop Graph Traversal (BFS) to perform root-cause dependency analysis.
    """
    
    # Directed Graph: Service -> List of Downstream Dependent Infrastructure
    GRAPH_EDGES = {
        "gateway-proxy": ["auth-service", "payment-gateway-service", "api-gateway"],
        "auth-service": ["postgres-primary", "redis-cluster"],
        "payment-gateway-service": ["kafka-broker-1", "postgres-primary", "redis-cluster"],
        "kafka-broker-1": ["zookeeper-cluster", "disk-storage-node"],
        "postgres-primary": ["database-pool", "pvc-storage-volume"],
        "elasticsearch": ["cloudwatch-agent", "fluentd-collector"]
    }
    
    @classmethod
    def traverse_graph_multi_hop(cls, start_service: str, max_depth: int = 2) -> Dict[str, List[str]]:
        """Perform Breadth-First Search (BFS) graph traversal to uncover 2-hop upstream and downstream dependencies."""
        visited: Set[str] = set()
        queue: List[tuple] = [(start_service.lower(), 0)]
        traversal_results: Dict[str, List[str]] = {}
        
        while queue:
            node, depth = queue.pop(0)
            if node in visited or depth > max_depth:
                continue
            visited.add(node)
            
            neighbors = cls.GRAPH_EDGES.get(node, [])
            if neighbors:
                traversal_results[node] = neighbors
                for neighbor in neighbors:
                    queue.append((neighbor, depth + 1))
                    
        return traversal_results
        
    @classmethod
    def format_graph_context(cls, service_name: str) -> str:
        """Format Multi-Hop GraphRAG context for LLM prompt grounding."""
        traversal = cls.traverse_graph_multi_hop(service_name, max_depth=2)
        if not traversal:
            return ""
            
        lines = [f"\n[GRAPHRAG ARCHITECTURE DEPENDENCY MATRIX for '{service_name}']:"]
        for parent, children in traversal.items():
            lines.append(f"  • Node '{parent}' connects to downstream nodes: [{', '.join(children)}]")
            
        lines.append("  • Incident Impact Analysis: Failures in downstream nodes directly cause cascading errors in upstream services.\n")
        return "\n".join(lines)
