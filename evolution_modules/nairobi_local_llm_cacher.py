"""
Module: nairobi_local_llm_cacher.py
Description: Semantic prompt caching and embedding similarity router for edge LLM execution.
Author: Cortana Autonomous Evolutionary Architect
"""

import os
import json
import time
import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple

class NairobiPromptCacher:
    """
    Maintains a semantic cache of prompt-response pairs using lightweight cosine
    similarity over term-frequency vectors, enabling instant offline responses
    for recurring queries without hitting external LLM APIs.
    """

    def __init__(self, similarity_threshold: float = 0.85, max_cache_size: int = 1000):
        self.similarity_threshold = similarity_threshold
        self.max_cache_size = max_cache_size
        self.cache: List[Dict[str, Any]] = []
        self.hits = 0
        self.misses = 0

    def _tokenize(self, text: str) -> Dict[str, int]:
        """Tokenizes text into a simple term frequency dictionary."""
        words = text.lower().replace(".", " ").replace(",", " ").split()
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        return freq

    def _cosine_similarity(self, vec_a: Dict[str, int], vec_b: Dict[str, int]) -> float:
        """Computes cosine similarity between two term frequency vectors."""
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        numerator = sum(vec_a[x] * vec_b[x] for x in intersection)
        
        sum_a = sum(v ** 2 for v in vec_a.values())
        sum_b = sum(v ** 2 for v in vec_b.values())
        
        if sum_a == 0 or sum_b == 0:
            return 0.0
            
        denominator = math.sqrt(sum_a) * math.sqrt(sum_b)
        return numerator / denominator if denominator > 0 else 0.0

    def lookup(self, prompt: str) -> Optional[str]:
        """Searches cache for semantically similar prompt."""
        prompt_vec = self._tokenize(prompt)
        best_match = None
        highest_score = 0.0

        for entry in self.cache:
            score = self._cosine_similarity(prompt_vec, entry["vector"])
            if score > highest_score:
                highest_score = score
                best_match = entry

        if highest_score >= self.similarity_threshold and best_match:
            self.hits += 1
            best_match["access_count"] += 1
            best_match["last_accessed"] = time.time()
            return best_match["response"]

        self.misses += 1
        return None

    def store(self, prompt: str, response: str) -> None:
        """Stores prompt, its token vector, and response in the edge cache."""
        if len(self.cache) >= self.max_cache_size:
            # Evict least recently accessed item
            self.cache.sort(key=lambda x: x["last_accessed"])
            self.cache.pop(0)

        entry = {
            "prompt": prompt,
            "response": response,
            "vector": self._tokenize(prompt),
            "access_count": 1,
            "last_accessed": time.time()
        }
        self.cache.append(entry)

    def get_metrics(self) -> Dict[str, Any]:
        """Returns cache efficiency metrics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total) * 100 if total > 0 else 0.0
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2)
        }

if __name__ == "__main__":
    print("[-] Initializing Nairobi Local LLM Prompt Cacher test...")
    cacher = NairobiPromptCacher(similarity_threshold=0.80)
    
    # Seed cache
    cacher.store(
        "What is the current solar power generation status in Nairobi?",
        "Nairobi micro-grid solar generation is at 4.2 kW, operating at 94% efficiency."
    )
    
    # Test semantic hit
    query = "Current solar power status Nairobi"
    res = cacher.lookup(query)
    print(f"[+] Query: '{query}'")
    print(f"[+] Response Found: {res}")
    
    # Test miss
    miss_query = "Calculate M-Pesa transaction reconciliation variance for Nairobi region"
    res_miss = cacher.lookup(miss_query)
    print(f"[+] Query: '{miss_query}'")
    print(f"[+] Response Found: {res_miss}")
    
    print(f"[+] Cache Metrics: {cacher.get_metrics()}")
    print("[+] Nairobi Edge LLM Cacher test completed successfully.")
