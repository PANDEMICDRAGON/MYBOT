"""
Autonomous Adaptive Circuit Breaker & API Cascade Isolator.
Generated autonomously by Cortana Proactive Self-Evolution Core.
"""

import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger("CortanaCircuitBreaker")

class CircuitBreakerOpenException(Exception):
    """Raised when an external resource request is blocked due to open circuit."""
    pass

class AdaptiveCircuitBreaker:
    """Monitors external endpoint failures and automatically sheds traffic during degradation."""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker tripped to OPEN (Failures: {self.failure_count})")

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN trial.")
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False

if __name__ == "__main__":
    cb = AdaptiveCircuitBreaker(failure_threshold=3, recovery_timeout=2.0)
    assert cb.can_execute() is True
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == "OPEN"
    print("AdaptiveCircuitBreaker verified and functional.")
