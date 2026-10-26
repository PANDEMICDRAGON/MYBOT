"""
Dynamic Operator Velocity Index & Milestone Tracker.
Generated autonomously by Cortana Proactive Self-Evolution Core.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger("CortanaVelocityTracker")

class OperatorVelocityTracker:
    """Calculates task velocity metrics and flags impending bottlenecks for Michael."""
    @staticmethod
    def calculate_velocity(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get("completed"))
        pending = total - completed
        rate = (completed / total * 100.0) if total > 0 else 100.0
        return {
            "total_tasks": total,
            "completed": completed,
            "pending": pending,
            "completion_rate_pct": round(rate, 1),
            "status": "ACCELERATING" if rate > 70 else "NOMINAL"
        }

if __name__ == "__main__":
    mock_tasks = [{"title": "Deploy Vercel", "completed": True}, {"title": "Code Evolution", "completed": False}]
    res = OperatorVelocityTracker.calculate_velocity(mock_tasks)
    assert res["pending"] == 1
    print(f"OperatorVelocityTracker verified: {res}")
