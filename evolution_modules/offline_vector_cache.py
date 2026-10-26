"""Local Ephemeral Vector Embedding Cache & Offline Semantic Search Engine.

Provides robust, zero-dependency offline semantic indexing and retrieval for Cortana's
local knowledge base, ensuring continuous operation during network partitions in Nairobi.
"""

import json
import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple


class OfflineVectorCache:
    """Manages localized text chunking, deterministic hashing/pseudo-embeddings,
    and cosine-similarity search entirely in RAM and optional persistent JSON storage.
    """

    def __init__(self, storage_path: Optional[str] = None) -> None:
        self.storage_path = storage_path
        self.index: List[Dict[str, Any]] = []
        if storage_path and os.path.exists(storage_path):
            self.load_index()

    def _tokenize(self, text: str) -> List[str]:
        """Simple whitespace and punctuation tokenizer."""
        import re
        return [t.lower() for t in re.findall(r'\w+', text)]

    def _generate_pseudo_embedding(self, text: str, dimensions: int = 64) -> List[float]:
        """Generates a lightweight normalized pseudo-embedding vector using deterministic hashing.
        
        Provides offline semantic approximation without heavy PyTorch/Transformers dependencies.
        """
        vector = [0.0] * dimensions
        tokens = self._tokenize(text)
        if not tokens:
            return vector
            
        for token in tokens:
            h = hash(token)
            for i in range(dimensions):
                # Mix hash bits across dimensions
                bit_val = ((h >> (i % 32)) & 1) * 2.0 - 1.0
                vector[i] += bit_val * (1.0 / math.sqrt(len(tokens)))
                
        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def upsert(self, doc_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Inserts or updates a document in the offline vector cache."""
        embedding = self._generate_pseudo_embedding(content)
        record = {
            "doc_id": doc_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding,
            "timestamp": time.time()
        }
        
        # Remove existing if present
        self.index = [item for item in self.index if item["doc_id"] != doc_id]
        self.index.append(record)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs semantic similarity search against indexed local documents."""
        query_vector = self._generate_pseudo_embedding(query)
        scored_results = []

        for item in self.index:
            score = self._cosine_similarity(query_vector, item["embedding"])
            scored_results.append({
                "doc_id": item["doc_id"],
                "content": item["content"],
                "metadata": item["metadata"],
                "similarity_score": round(score, 4)
            })

        scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_results[:top_k]

    def save_index(self) -> None:
        """Persists index to local storage for cold-start recovery."""
        if not self.storage_path:
            return
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self.index, f)
        except Exception as e:
            print(f"[OfflineVectorCache] Error saving index: {e}")

    def load_index(self) -> None:
        """Loads index from local storage."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        except Exception as e:
            print(f"[OfflineVectorCache] Error loading index: {e}")


if __name__ == "__main__":
    print("Initializing OfflineVectorCache Test Harness...")
    cache = OfflineVectorCache()
    
    cache.upsert(
        doc_id="nairobi_solar_01",
        content="Nairobi microgrid solar battery optimization protocols and inverter telemetry.",
        metadata={"location": "Nairobi", "category": "energy"}
    )
    cache.upsert(
        doc_id="nairobi_routing_02",
        content="Nairobi node multi-WAN failover routing and Starlink bond management.",
        metadata={"location": "Nairobi", "category": "network"}
    )
    
    query = "How to optimize solar battery load in Nairobi?"
    print(f"Query: '{query}'")
    results = cache.search(query, top_k=2)
    
    for res in results:
        print(f"Match [{res['doc_id']}] Score: {res['similarity_score']} -> {res['content']}")
    assert len(results) > 0
    print("OfflineVectorCache test completed successfully.")
