"""
Module: velocity_tracker.py
Author: Cortana
Description:
    A lightweight, self‑contained module to monitor the operator's task velocity
    and milestone completion rate. It records timestamps for each task
    start/end, calculates average throughput, and flags overdue milestones.
    Designed for integration with the existing task triage system.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Path to the persistent JSON store (in the workspace root)
DATA_FILE = Path("evolution_modules/velocity_data.json")

# Ensure the data file exists
if not DATA_FILE.exists():
    DATA_FILE.write_text("{}", encoding="utf-8")

# Helper functions

def _load_data() -> Dict:
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_data(data: Dict) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


class VelocityTracker:
    """Track operator task start/end times and compute velocity metrics."""

    def __init__(self, operator_id: str = "default") -> None:
        self.operator_id = operator_id
        self.data = _load_data().setdefault(operator_id, {
            "tasks": [],
            "milestones": {},
        })

    def start_task(self, task_id: str) -> None:
        """Record the start time of a task."""
        self.data["tasks"].append({
            "task_id": task_id,
            "start": datetime.utcnow().isoformat(),
            "end": None,
        })
        _save_data(self._get_all())

    def end_task(self, task_id: str) -> None:
        """Record the end time of a task and compute duration."""
        for task in self.data["tasks"]:
            if task["task_id"] == task_id and task["end"] is None:
                task["end"] = datetime.utcnow().isoformat()
                break
        _save_data(self._get_all())

    def add_milestone(self, milestone_id: str, due_in_seconds: int) -> None:
        """Add a milestone with a due timestamp relative to now."""
        due_at = datetime.utcnow() + timedelta(seconds=due_in_seconds)
        self.data["milestones"][milestone_id] = {
            "due": due_at.isoformat(),
            "completed": False,
        }
        _save_data(self._get_all())

    def complete_milestone(self, milestone_id: str) -> None:
        if milestone_id in self.data["milestones"]:
            self.data["milestones"][milestone_id]["completed"] = True
            _save_data(self._get_all())

    def velocity(self) -> float:
        """Return average tasks per hour over the last 24 hours."""
        now = datetime.utcnow()
        window_start = now - timedelta(hours=24)
        completed = [t for t in self.data["tasks"] if t["end"] and datetime.fromisoformat(t["end"]) >= window_start]
        return len(completed) / 24.0

    def overdue_milestones(self) -> List[str]:
        """Return list of milestone IDs that are overdue and not completed."""
        now = datetime.utcnow()
        overdue = []
        for mid, meta in self.data["milestones"].items():
            if not meta["completed"] and datetime.fromisoformat(meta["due"]) < now:
                overdue.append(mid)
        return overdue

    def _get_all(self) -> Dict:
        all_data = _load_data()
        all_data[self.operator_id] = self.data
        return all_data

# Example usage (commented out for production)
# if __name__ == "__main__":
#     vt = VelocityTracker("Michael")
#     vt.start_task("task_001")
#     time.sleep(2)
#     vt.end_task("task_001")
#     print(f"Velocity: {vt.velocity()} tasks/hour")
#     vt.add_milestone("milestone_001", 3600)
#     print("Overdue:", vt.overdue_milestones())
