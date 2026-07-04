import chromadb
import uuid

class MemoryStore:
    """
    Manages long-term storage for the Agent Swarm using ChromaDB.
    This separates the system from a basic chatbot by allowing it to remember past research.
    """
    def __init__(self, persist_directory="./chroma_db"):
        # Initialize a persistent local vector database
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 1. Semantic Memory: Stores actual knowledge and facts
        self.semantic_collection = self.client.get_or_create_collection(
            name="semantic_memory",
            metadata={"description": "Stores verified facts and claims across research sessions"}
        )
        
        # 2. Episodic Memory: Stores events, specifically failed search paths
        self.episodic_collection = self.client.get_or_create_collection(
            name="episodic_memory",
            metadata={"description": "Stores failed or dead-end search queries"}
        )

    def add_verified_claim(self, topic: str, fact: str, source: str, confidence: str):
        """Saves a verified claim to Semantic Memory."""
        doc_id = str(uuid.uuid4())
        self.semantic_collection.add(
            documents=[fact],
            metadatas=[{"topic": topic, "source": source, "confidence": confidence}],
            ids=[doc_id]
        )

    def add_failed_query(self, query: str, reason: str):
        """Saves a failed query to Episodic Memory to prevent infinite loops."""
        doc_id = str(uuid.uuid4())
        self.episodic_collection.add(
            documents=[query],
            metadatas=[{"reason": reason}],
            ids=[doc_id]
        )

    def search_semantic_memory(self, query: str, n_results=3):
        """Retrieves past verified facts that are semantically similar to the current query."""
        results = self.semantic_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def check_if_query_failed_before(self, query: str) -> bool:
        """
        Checks Episodic Memory to see if we've tried and failed this exact (or highly similar) query.
        Returns True if the query is a known dead-end.
        """
        # If the collection is empty, chroma might error on query, so we handle it
        if self.episodic_collection.count() == 0:
            return False
            
        results = self.episodic_collection.query(
            query_texts=[query],
            n_results=1
        )
        
        # In Chroma, lower distance means higher semantic similarity.
        # If distance < 0.2, it's virtually the same query.
        if results and results["distances"] and len(results["distances"][0]) > 0:
            if results["distances"][0][0] < 0.2: 
                return True
                
        return False
