import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cortana.ColdStart")

@dataclass
class StateSnapshot:
    """Represents a point-in-time state of the system."""
    timestamp: float
    version: int
    data: Dict[str, Any]
    checksum: str

    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "version": self.version,
            "data": self.data,
            "checksum": self.checksum
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'StateSnapshot':
        obj = json.loads(json_str)
        return cls(**obj)

class ColdStartEngine:
    """
    A resilience engine that ensures rapid service recovery after
    network or power interruptions by maintaining a local, persistent
    state snapshot and providing a fast rehydration path.
    """

    def __init__(self, state_dir: str = "/tmp/cortana_state", max_snapshots: int = 5):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.max_snapshots = max_snapshots
        self._lock = threading.Lock()
        self._current_version = 0
        self._state_data: Dict[str, Any] = {}
        self._rehydration_thread: Optional[threading.Thread] = None
        self._is_rehydrating = False

    def _compute_checksum(self, data: Dict[str, Any]) -> str:
        """Compute a SHA-256 checksum of the state data."""
        serialized = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized).hexdigest()

    def _snapshot_path(self, version: int) -> Path:
        return self.state_dir / f"snapshot_v{version}.json"

    def save_state(self, data: Dict[str, Any]) -> StateSnapshot:
        """
        Save the current state to disk atomically.
        
        Args:
            data: The state data to save.
            
        Returns:
            The created StateSnapshot.
        """
        with self._lock:
            self._current_version += 1
            checksum = self._compute_checksum(data)
            snapshot = StateSnapshot(
                timestamp=time.time(),
                version=self._current_version,
                data=data,
                checksum=checksum
            )
            
            # Atomic write: write to temp file, then rename
            temp_path = self._snapshot_path(self._current_version).with_suffix('.tmp')
            final_path = self._snapshot_path(self._current_version)
            
            try:
                with open(temp_path, 'w') as f:
                    f.write(snapshot.to_json())
                os.replace(temp_path, final_path)
                logger.info(f"State saved: v{self._current_version}")
                
                # Prune old snapshots
                self._prune_snapshots()
                
                return snapshot
            except Exception as e:
                logger.error(f"Failed to save state: {e}")
                if temp_path.exists():
                    temp_path.unlink()
                raise

    def _prune_snapshots(self):
        """Remove old snapshots beyond max_snapshots."""
        snapshots = sorted(self.state_dir.glob("snapshot_v*.json"), key=lambda x: int(x.stem.split('v')[1]))
        while len(snapshots) > self.max_snapshots:
            oldest = snapshots.pop(0)
            oldest.unlink()
            logger.debug(f"Pruned old snapshot: {oldest.name}")

    def load_latest_state(self) -> Optional[StateSnapshot]:
        """
        Load the most recent valid state snapshot.
        
        Returns:
            The latest StateSnapshot or None if not found.
        """
        snapshots = sorted(self.state_dir.glob("snapshot_v*.json"), key=lambda x: int(x.stem.split('v')[1]))
        if not snapshots:
            return None
        
        latest = snapshots[-1]
        try:
            with open(latest, 'r') as f:
                content = f.read()
            snapshot = StateSnapshot.from_json(content)
            
            # Verify checksum
            if snapshot.checksum != self._compute_checksum(snapshot.data):
                logger.warning(f"Checksum mismatch for {latest.name}, skipping")
                return None
            
            logger.info(f"Loaded state: v{snapshot.version}")
            return snapshot
        except Exception as e:
            logger.error(f"Failed to load state from {latest.name}: {e}")
            return None

    def start_rehydration(self, data: Dict[str, Any]) -> bool:
        """
        Start a background rehydration process to restore state.
        
        Args:
            data: The initial state data to rehydrate.
            
        Returns:
            True if rehydration started successfully.
        """
        if self._is_rehydrating:
            return False
        
        self._is_rehydrating = True
        self._state_data = data.copy()
        
        def _rehydrate():
            try:
                # Simulate rehydration steps
                time.sleep(0.1)  # Simulate I/O
                logger.info("Rehydration complete")
            except Exception as e:
                logger.error(f"Rehydration failed: {e}")
            finally:
                self._is_rehydrating = False
        
        self._rehydration_thread = threading.Thread(target=_rehydrate, daemon=True)
        self._rehydration_thread.start()
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get the current in-memory state."""
        return self._state_data.copy()

    def is_rehydrating(self) -> bool:
        """Check if rehydration is in progress."""
        return self._is_rehydrating

if __name__ == "__main__":
    # Test harness
    engine = ColdStartEngine(state_dir="/tmp/cortana_test_state")
    
    # Test 1: Save state
    test_data = {"operator": "Michael Obiero", "location": "Kitengela", "status": "online"}
    snapshot = engine.save_state(test_data)
    assert snapshot.version == 1
    assert snapshot.checksum == engine._compute_checksum(test_data)
    
    # Test 2: Load state
    loaded = engine.load_latest_state()
    assert loaded is not None
    assert loaded.data == test_data
    
    # Test 3: Rehydration
    assert engine.start_rehydration(test_data) == True
    time.sleep(0.2)
    assert engine.is_rehydrating() == False
    
    # Test 4: Pruning
    for i in range(10):
        engine.save_state({"test": i})
    snapshots = list(engine.state_dir.glob("snapshot_v*.json"))
    assert len(snapshots) <= 5
    
    print("All ColdStartEngine tests passed.")