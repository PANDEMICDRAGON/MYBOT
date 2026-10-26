import os
import json
import time
import threading
import requests
from pathlib import Path

# Configuration
SYNC_INTERVAL = 60  # seconds
MAX_QUEUE_SIZE = 1000
API_ENDPOINT = os.getenv("CLOUD_SYNC_ENDPOINT", "https://api.mycloud.com/sync")
API_KEY = os.getenv("CLOUD_SYNC_KEY")
LOCAL_LOG_DIR = Path("/var/log/mysystem")
QUEUE_FILE = Path("/tmp/kenya_sync_queue.json")

# Simple in-memory queue with persistence
class SyncQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self._load()

    def _load(self):
        if QUEUE_FILE.exists():
            try:
                with QUEUE_FILE.open("r", encoding="utf-8") as f:
                    self.queue = json.load(f)
            except Exception:
                self.queue = []

    def _save(self):
        with QUEUE_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.queue, f)

    def add(self, item):
        with self.lock:
            if len(self.queue) < MAX_QUEUE_SIZE:
                self.queue.append(item)
                self._save()

    def pop_all(self):
        with self.lock:
            items = self.queue[:]
            self.queue = []
            self._save()
            return items

queue = SyncQueue()

# Monitor log directory for new files
def monitor_logs():
    seen = set()
    while True:
        for log_file in LOCAL_LOG_DIR.glob("*.log"):
            if log_file not in seen:
                seen.add(log_file)
                try:
                    with log_file.open("r", encoding="utf-8") as f:
                        data = f.read()
                    queue.add({"path": str(log_file), "content": data, "timestamp": time.time()})
                except Exception:
                    pass
        time.sleep(5)

# Sync thread
def sync_worker():
    while True:
        items = queue.pop_all()
        if items:
            try:
                headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
                resp = requests.post(API_ENDPOINT, headers=headers, json={"logs": items}, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                # Requeue on failure
                for item in items:
                    queue.add(item)
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=monitor_logs, daemon=True).start()
    threading.Thread(target=sync_worker, daemon=True).start()
    while True:
        time.sleep(3600)
