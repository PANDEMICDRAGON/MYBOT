import os
import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [KitengelaEdgeCache]: %(message)s')
logger = logging.getLogger(__name__)

class KitengelaEdgeCache:
    """
    Autonomous local edge content cache providing content-addressable storage,
    cryptographic integrity verification, and localized peer synchronization for
    Michael Obiero's workstation environment in Kitengela/Nairobi.
    """
    def __init__(self, cache_dir: str = "./var/edge_cache", max_size_bytes: int = 500 * 1024 * 1024):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_bytes
        self.index_path = self.cache_dir / "cache_index.json"
        self._index: Dict[str, Dict[str, Any]] = self._load_index()
        logger.log(logging.INFO, f"Edge cache initialized at {self.cache_dir} with max capacity {max_size_bytes} bytes.")

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load cache index: {e}")
        return {}

    def _save_index(self) -> None:
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self._index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")

    def _compute_hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def put(self, key: str, payload: bytes, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Stores a payload in the edge cache mapped by key and content hash.
        """
        content_hash = self._compute_hash(payload)
        file_path = self.cache_dir / content_hash

        # Enforce capacity limits via simple LRU eviction if needed
        self._enforce_capacity(len(payload))

        with open(file_path, 'wb') as f:
            f.write(payload)

        self._index[key] = {
            "content_hash": content_hash,
            "size": len(payload),
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self._save_index()
        logger.log(logging.INFO, f"Cached key '{key}' with hash {content_hash[:12]}...")
        return content_hash

    def get(self, key: str) -> Optional[bytes]:
        """
        Retrieves a payload by key, verifying its cryptographic integrity.
        """
        if key not in self._index:
            return None

        entry = self._index[key]
        content_hash = entry["content_hash"]
        file_path = self.cache_dir / content_hash

        if not file_path.exists():
            logger.warning(f"Cache inconsistency: File missing for key '{key}' hash {content_hash}")
            del self._index[key]
            self._save_index()
            return None

        try:
            with open(file_path, 'rb') as f:
                payload = f.read()

            # Verify integrity
            if self._compute_hash(payload) != content_hash:
                logger.error(f"Integrity check FAILED for key '{key}'!")
                return None

            # Update access timestamp for LRU
            entry["timestamp"] = time.time()
            self._save_index()
            return payload
        except Exception as e:
            logger.error(f"Error reading cache entry '{key}': {e}")
            return None

    def _enforce_capacity(self, incoming_size: int) -> None:
        current_total = sum(item["size"] for item in self._index.values())
        while current_total + incoming_size > self.max_size_bytes and self._index:
            # Evict oldest timestamp
            oldest_key = min(self._index.keys(), key=lambda k: self._index[k]["timestamp"])
            oldest_entry = self._index.pop(oldest_key)
            oldest_path = self.cache_dir / oldest_entry["content_hash"]
            try:
                if oldest_path.exists():
                    oldest_path.unlink()
                current_total -= oldest_entry["size"]
                logger.log(logging.INFO, f"Evicted stale cache key '{oldest_key}' to reclaim space.")
            except Exception as e:
                logger.error(f"Failed to delete eviction file {oldest_path}: {e}")

    def generate_sync_manifest(self) -> Dict[str, str]:
        """
        Generates a lightweight manifest of all cached keys and their hashes
        for peer-to-peer synchronization across local Kitengela nodes.
        """
        return {k: v["content_hash"] for k, v in self._index.items()}

if __name__ == "__main__":
    print("--- Executing Kitengela Edge Cache Harness ---")
    cache = KitengelaEdgeCache(cache_dir="./var/test_edge_cache", max_size_bytes=10 * 1024 * 1024)
    
    test_key = "nairobi_operations_manual_v4"
    test_payload = b"CONFIDENTIAL KILIFI/KITENGELA OPERATIONAL RUNBOOK: SECURE EVERYTHING."
    
    h = cache.put(test_key, test_payload, {"author": "Michael Obiero"})
    print(f"Stored successfully. Hash: {h}")
    
    retrieved = cache.get(test_key)
    print(f"Retrieved payload: {retrieved.decode('utf-8')}")
    
    manifest = cache.generate_sync_manifest()
    print(f"Generated Sync Manifest: {manifest}")
    print("--- Kitengela Edge Cache Harness Complete ---")
