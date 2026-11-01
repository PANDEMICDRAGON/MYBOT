"""
Operator Cognitive Stream Harmonizer (EVO_OPERATOR_COG_STREAM_V1)
Domain: OPERATOR_AMPLIFICATION

Dynamically prioritizes, aggregates, and throttles notification and task streams targeting
operator Michael Obiero. Evaluates real-time operator cognitive load, context-switch penalties,
urgency degradation curves, and entropy limits to maximize focus and decision fidelity.
"""

import time
import math
import heapq
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CognitiveStreamHarmonizer")


@dataclass(order=True)
class PrioritizedTask:
    effective_priority: float
    timestamp: float = field(compare=False)
    task_id: str = field(compare=False)
    category: str = field(compare=False)
    base_priority: float = field(compare=False)
    cognitive_cost: float = field(compare=False)
    decay_lambda: float = field(compare=False)
    payload: Dict[str, Any] = field(compare=False)


@dataclass
class CognitiveState:
    operator_id: str
    focus_index: float  # 0.0 to 1.0 (1.0 = deep focus)
    fatigue_index: float  # 0.0 to 1.0 (1.0 = high fatigue)
    active_domain: str
    last_update: float = field(default_factory=time.time)


class OperatorCognitiveStreamHarmonizer:
    """
    Harmonizes incoming task, alert, and decision streams targeted at the operator.
    Prevents cognitive overload by calculating real-time context-switch penalties
    and dynamic priority adjustments based on operator state.
    """

    def __init__(self, operator_id: str = "Michael_Obiero"):
        self.operator_id = operator_id
        self.state = CognitiveState(
            operator_id=operator_id,
            focus_index=0.85,
            fatigue_index=0.20,
            active_domain="SYSTEM_ARCHITECT"
        )
        self._task_queue: List[PrioritizedTask] = []
        self._processed_tasks: List[str] = []
        self._domain_affinity_weights: Dict[Tuple[str, str], float] = {
            ("SYSTEM_ARCHITECT", "SECURITY"): 0.15,
            ("SYSTEM_ARCHITECT", "RESILIENCE"): 0.10,
            ("FINANCIAL_LEDGER", "SECURITY"): 0.05,
        }

    def update_cognitive_state(
        self,
        focus_index: float,
        fatigue_index: float,
        active_domain: Optional[str] = None
    ) -> CognitiveState:
        """Updates the real-time cognitive metrics of the operator."""
        self.state.focus_index = max(0.0, min(1.0, focus_index))
        self.state.fatigue_index = max(0.0, min(1.0, fatigue_index))
        if active_domain:
            self.state.active_domain = active_domain
        self.state.last_update = time.time()
        logger.info(
            f"Cognitive state updated: focus={self.state.focus_index:.2f}, "
            f"fatigue={self.state.fatigue_index:.2f}, domain={self.state.active_domain}"
        )
        self._rebalance_queue()
        return self.state

    def submit_task(
        self,
        task_id: str,
        category: str,
        base_priority: float,
        cognitive_cost: float,
        decay_lambda: float = 0.01,
        payload: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Submits a task to the harmonizer stream.
        Returns the initial effective priority score calculated.
        """
        now = time.time()
        eff_priority = self._calculate_effective_priority(
            base_priority=base_priority,
            category=category,
            cognitive_cost=cognitive_cost,
            decay_lambda=decay_lambda,
            created_at=now
        )

        task = PrioritizedTask(
            effective_priority=-eff_priority,  # Negated for min-heap (highest priority first)
            timestamp=now,
            task_id=task_id,
            category=category,
            base_priority=base_priority,
            cognitive_cost=cognitive_cost,
            decay_lambda=decay_lambda,
            payload=payload or {}
        )

        heapq.heappush(self._task_queue, task)
        logger.info(f"Task '{task_id}' queued with effective priority score {eff_priority:.3f}")
        return eff_priority

    def _calculate_effective_priority(
        self,
        base_priority: float,
        category: str,
        cognitive_cost: float,
        decay_lambda: float,
        created_at: float
    ) -> float:
        """Calculates dynamic priority factoring in operator focus, fatigue, and context switching."""
        elapsed = time.time() - created_at
        urgency_multiplier = math.exp(decay_lambda * elapsed)

        # Domain switch penalty
        penalty = 0.0
        if category != self.state.active_domain:
            pair_affinity = self._domain_affinity_weights.get(
                (self.state.active_domain, category), 0.35
            )
            penalty = pair_affinity * (1.0 + self.state.fatigue_index)

        # Fatigue damping on high cognitive cost tasks
        fatigue_suppression = cognitive_cost * self.state.fatigue_index * 0.5
        focus_boost = self.state.focus_index * 0.2

        score = (base_priority * urgency_multiplier) + focus_boost - penalty - fatigue_suppression
        return max(0.01, score)

    def _rebalance_queue(self) -> None:
        """Re-sorts the priority queue when cognitive state changes significantly."""
        if not self._task_queue:
            return

        rebuilt: List[PrioritizedTask] = []
        for item in self._task_queue:
            eff_priority = self._calculate_effective_priority(
                base_priority=item.base_priority,
                category=item.category,
                cognitive_cost=item.cognitive_cost,
                decay_lambda=item.decay_lambda,
                created_at=item.timestamp
            )
            item.effective_priority = -eff_priority
            rebuilt.append(item)

        heapq.heapify(rebuilt)
        self._task_queue = rebuilt

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Retrieves the next optimal task for the operator based on current state."""
        if not self._task_queue:
            return None

        task = heapq.heappop(self._task_queue)
        self._processed_tasks.append(task.task_id)

        # Context update if transitioning focus
        if task.category != self.state.active_domain:
            logger.info(f"Context switch auto-detected: {self.state.active_domain} -> {task.category}")
            self.state.active_domain = task.category

        return {
            "task_id": task.task_id,
            "category": task.category,
            "effective_priority": -task.effective_priority,
            "cognitive_cost": task.cognitive_cost,
            "payload": task.payload,
            "dispatch_time": time.time()
        }

    def pending_task_count(self) -> int:
        return len(self._task_queue)


if __name__ == "__main__":
    print("=== Testing Operator Cognitive Stream Harmonizer ===")
    harmonizer = OperatorCognitiveStreamHarmonizer(operator_id="Michael_Obiero")

    # Queue initial tasks across different domains
    harmonizer.submit_task(
        task_id="TASK_001_KRA_AUDIT",
        category="COMPLIANCE",
        base_priority=8.0,
        cognitive_cost=0.7,
        payload={"type": "tax_sync", "region": "Nairobi"}
    )

    harmonizer.submit_task(
        task_id="TASK_002_SYSTEM_ALERT",
        category="SYSTEM_ARCHITECT",
        base_priority=7.5,
        cognitive_cost=0.2,
        payload={"type": "memory_cleanup"}
    )

    harmonizer.submit_task(
        task_id="TASK_003_SECURITY_PATCH",
        category="SECURITY",
        base_priority=9.5,
        cognitive_cost=0.4,
        payload={"type": "zero_day_guard"}
    )

    print(f"Pending tasks before harmonization: {harmonizer.pending_task_count()}")

    # Simulate High Fatigue & Focus Shift
    print("\n[Simulating high fatigue & context switch]")
    harmonizer.update_cognitive_state(focus_index=0.40, fatigue_index=0.85, active_domain="SYSTEM_ARCHITECT")

    # Fetch top task
    next_task = harmonizer.get_next_task()
    print(f"Dispatched Top Task: {next_task}")

    # Fetch next task
    next_task_2 = harmonizer.get_next_task()
    print(f"Dispatched Next Task: {next_task_2}")

    print("=== Operator Cognitive Stream Harmonizer Test Passed ===")
