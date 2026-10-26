"""
High-Throughput Asynchronous Priority Event Bus.
Generated autonomously by Cortana Continuous Self-Evolution Core.
"""

import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger("CortanaEventBus")

class AsyncPriorityEventBus:
    """Decoupled in-memory publish/subscribe event bus with priority dispatching."""
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = asyncio.PriorityQueue()

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, payload: Any, priority: int = 10):
        await self._queue.put((priority, event_type, payload))
        await self._process_one()

    async def _process_one(self):
        if self._queue.empty():
            return
        priority, event_type, payload = await self._queue.get()
        handlers = self._subscribers.get(event_type, [])
        for h in handlers:
            try:
                if asyncio.iscoroutinefunction(h):
                    await h(payload)
                else:
                    h(payload)
            except Exception as e:
                logger.error(f"[EventBus Handler Error]: {e}")
        self._queue.task_done()

if __name__ == "__main__":
    bus = AsyncPriorityEventBus()
    received = []
    bus.subscribe("TELEMETRY", lambda p: received.append(p))
    asyncio.run(bus.publish("TELEMETRY", {"status": "nominal"}))
    assert len(received) == 1
    print("AsyncPriorityEventBus verified.")
