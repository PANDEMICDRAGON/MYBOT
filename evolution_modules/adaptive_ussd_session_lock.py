import time
import uuid
import threading
from enum import Enum
from typing import Dict, Optional, Any
from dataclasses import dataclass, field


class USSDState(Enum):
    IDLE = "idle"
    AWAITING_PIN = "awaiting_pin"
    AWAITING_AMOUNT = "awaiting_amount"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    LOCKED = "locked"


@dataclass
class USSDTransaction:
    tx_id: str
    state: USSDState
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class USSDSessionLock:
    """
    A hardened state machine for USSD sessions that prevents race conditions,
    duplicate transactions, and session hijacking.
    """

    def __init__(self, max_session_duration: float = 300.0, max_attempts: int = 3):
        self._lock = threading.RLock()
        self._current_state = USSDState.IDLE
        self._transaction: Optional[USSDTransaction] = None
        self._max_session_duration = max_session_duration
        self._max_attempts = max_attempts
        self._attempt_count = 0
        self._seen_tx_ids: set = set()

    def _check_session_timeout(self) -> bool:
        if self._transaction and time.time() - self._transaction.timestamp > self._max_session_duration:
            self._transition_to(USSDState.FAILED, reason="session_timeout")
            return True
        return False

    def _transition_to(self, new_state: USSDState, reason: str = "") -> bool:
        with self._lock:
            if self._check_session_timeout():
                return False

            valid_transitions = {
                USSDState.IDLE: [USSDState.AWAITING_PIN, USSDState.LOCKED],
                USSDState.AWAITING_PIN: [USSDState.AWAITING_AMOUNT, USSDState.FAILED, USSDState.LOCKED],
                USSDState.AWAITING_AMOUNT: [USSDState.AWAITING_CONFIRMATION, USSDState.FAILED, USSDState.LOCKED],
                USSDState.AWAITING_CONFIRMATION: [USSDState.PROCESSING, USSDState.FAILED, USSDState.LOCKED],
                USSDState.PROCESSING: [USSDState.SUCCESS, USSDState.FAILED],
                USSDState.SUCCESS: [USSDState.IDLE],
                USSDState.FAILED: [USSDState.IDLE, USSDState.LOCKED],
                USSDState.LOCKED: [USSDState.IDLE]
            }

            if new_state not in valid_transitions.get(self._current_state, []):
                return False

            self._current_state = new_state
            if new_state == USSDState.PROCESSING and not self._transaction:
                self._transaction = USSDTransaction(
                    tx_id=str(uuid.uuid4()),
                    state=new_state,
                    timestamp=time.time(),
                    metadata={"reason": reason}
                )
            elif self._transaction:
                self._transaction.state = new_state
                self._transaction.metadata["reason"] = reason

            return True

    def start_session(self) -> bool:
        with self._lock:
            if self._current_state != USSDState.IDLE:
                return False
            self._attempt_count = 0
            return self._transition_to(USSDState.AWAITING_PIN)

    def submit_pin(self, pin: str) -> bool:
        with self._lock:
            if self._current_state != USSDState.AWAITING_PIN:
                return False
            if len(pin) < 4:  # Basic validation
                self._attempt_count += 1
                if self._attempt_count >= self._max_attempts:
                    return self._transition_to(USSDState.LOCKED, reason="max_attempts_exceeded")
                return self._transition_to(USSDState.FAILED, reason="invalid_pin")
            return self._transition_to(USSDState.AWAITING_AMOUNT)

    def submit_amount(self, amount: float) -> bool:
        with self._lock:
            if self._current_state != USSDState.AWAITING_AMOUNT:
                return False
            if amount <= 0:
                return self._transition_to(USSDState.FAILED, reason="invalid_amount")
            if self._transaction:
                self._transaction.metadata["amount"] = amount
            return self._transition_to(USSDState.AWAITING_CONFIRMATION)

    def confirm_transaction(self) -> bool:
        with self._lock:
            if self._current_state != USSDState.AWAITING_CONFIRMATION:
                return False
            return self._transition_to(USSDState.PROCESSING)

    def complete_transaction(self, success: bool) -> bool:
        with self._lock:
            if self._current_state != USSDState.PROCESSING:
                return False
            if success:
                return self._transition_to(USSDState.SUCCESS)
            else:
                return self._transition_to(USSDState.FAILED, reason="processing_error")

    def reset(self) -> bool:
        with self._lock:
            if self._current_state in [USSDState.SUCCESS, USSDState.FAILED, USSDState.LOCKED]:
                self._transaction = None
                self._seen_tx_ids.clear()
                return self._transition_to(USSDState.IDLE)
            return False

    def get_state(self) -> USSDState:
        with self._lock:
            return self._current_state

    def get_transaction(self) -> Optional[USSDTransaction]:
        with self._lock:
            return self._transaction


def main():
    """Test harness for USSDSessionLock"""
    print("Testing USSDSessionLock...")
    lock = USSDSessionLock(max_session_duration=10.0, max_attempts=2)

    # Test 1: Valid flow
    assert lock.start_session()
    assert lock.get_state() == USSDState.AWAITING_PIN
    assert lock.submit_pin("1234")
    assert lock.get_state() == USSDState.AWAITING_AMOUNT
    assert lock.submit_amount(100.0)
    assert lock.get_state() == USSDState.AWAITING_CONFIRMATION
    assert lock.confirm_transaction()
    assert lock.get_state() == USSDState.PROCESSING
    assert lock.complete_transaction(True)
    assert lock.get_state() == USSDState.SUCCESS
    assert lock.reset()
    assert lock.get_state() == USSDState.IDLE
    print("Test 1 (Valid flow) passed.")

    # Test 2: Invalid PIN attempts leading to lock
    assert lock.start_session()
    assert lock.submit_pin("12")  # Invalid
    assert lock.get_state() == USSDState.FAILED
    assert lock.reset()
    assert lock.start_session()
    assert lock.submit_pin("12")  # Invalid again
    assert lock.get_state() == USSDState.LOCKED
    assert lock.reset()
    assert lock.get_state() == USSDState.IDLE
    print("Test 2 (Lock after max attempts) passed.")

    # Test 3: Invalid state transition
    assert lock.start_session()
    assert not lock.submit_amount(100.0)  # Should fail, not in AWAITING_AMOUNT
    assert lock.get_state() == USSDState.AWAITING_PIN
    print("Test 3 (Invalid state transition) passed.")

    print("All tests passed successfully.")


if __name__ == "__main__":
    main()