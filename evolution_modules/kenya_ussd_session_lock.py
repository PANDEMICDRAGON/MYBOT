import threading
import time
import logging
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum

# Configure logging for the USSD Lock module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KenyaUSSDLock')


class LockState(Enum):
    """Enumeration of possible states for the USSD session lock."""
    IDLE = "idle"
    ACQUIRED = "acquired"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class LockAcquisition:
    """Represents a successful acquisition of the USSD lock."""
    token: str
    acquired_at: float
    timeout: float


class KenyaUSSDSessionLock:
    """
    A specialized mutex for USSD sessions in Kenyan mobile networks.
    
    This class prevents concurrent USSD session initiation which can lead to
    'session busy' errors or transaction failures on M-Pesa and other STK services.
    It includes a timeout mechanism to prevent deadlocks if a session hangs.
    """

    def __init__(self, default_timeout: float = 30.0, max_waiters: int = 5):
        """
        Initialize the USSD Session Lock.

        Args:
            default_timeout: Default timeout in seconds for lock acquisition.
            max_waiters: Maximum number of threads allowed to wait for the lock.
        """
        self._lock = threading.Lock()
        self._state = LockState.IDLE
        self._current_holder: Optional[str] = None
        self._waiters = 0
        self._max_waiters = max_waiters
        self._default_timeout = default_timeout
        self._condition = threading.Condition(self._lock)

    def acquire(self, timeout: Optional[float] = None, holder_id: str = "unknown") -> Optional[LockAcquisition]:
        """
        Attempt to acquire the USSD session lock.

        Args:
            timeout: Time in seconds to wait for the lock. Defaults to self._default_timeout.
            holder_id: Identifier for the thread/process acquiring the lock.

        Returns:
            LockAcquisition object if successful, None if timeout or error.
        """
        if timeout is None:
            timeout = self._default_timeout

        start_time = time.time()
        
        with self._condition:
            # Check if max waiters exceeded
            if self._waiters >= self._max_waiters:
                logger.warning(f"Max waiters ({self._max_waiters}) exceeded. Rejecting acquisition for {holder_id}.")
                return None

            self._waiters += 1
            self._state = LockState.WAITING

            try:
                # Wait for the lock to become available
                acquired = self._condition.wait_for(
                    lambda: self._state == LockState.IDLE,
                    timeout=timeout
                )

                if not acquired:
                    logger.warning(f"Timeout waiting for USSD lock for {holder_id}.")
                    return None

                # Acquire the lock
                self._state = LockState.ACQUIRED
                self._current_holder = holder_id
                token = f"USSD_LOCK_{time.time_ns()}"
                logger.info(f"USSD lock acquired by {holder_id} (token: {token}).")
                return LockAcquisition(token=token, acquired_at=time.time(), timeout=timeout)

            finally:
                self._waiters -= 1
                if self._waiters == 0:
                    self._state = LockState.IDLE

    def release(self, acquisition: Optional[LockAcquisition]) -> bool:
        """
        Release the USSD session lock.

        Args:
            acquisition: The LockAcquisition object obtained from acquire().

        Returns:
            True if released successfully, False otherwise.
        """
        if acquisition is None:
            logger.error("Attempted to release a None acquisition.")
            return False

        with self._condition:
            if self._current_holder is None:
                logger.error("Attempted to release a lock that is not held.")
                return False

            # In a real scenario, we might verify the token matches the holder
            # For simplicity, we assume the holder releases their own lock
            self._state = LockState.IDLE
            self._current_holder = None
            self._condition.notify_all()
            logger.info(f"USSD lock released.")
            return True

    def get_status(self) -> dict:
        """
        Get the current status of the USSD lock.

        Returns:
            Dictionary containing state, holder, and waiters count.
        """
        with self._lock:
            return {
                "state": self._state.value,
                "current_holder": self._current_holder,
                "waiters": self._waiters
            }


class USSDTransactionContext:
    """
    Context manager for USSD transactions.
    Ensures the lock is acquired and released properly.
    """

    def __init__(self, lock: KenyaUSSDSessionLock, holder_id: str, timeout: Optional[float] = None):
        self._lock = lock
        self._holder_id = holder_id
        self._timeout = timeout
        self._acquisition: Optional[LockAcquisition] = None

    def __enter__(self) -> 'USSDTransactionContext':
        self._acquisition = self._lock.acquire(timeout=self._timeout, holder_id=self._holder_id)
        if self._acquisition is None:
            raise RuntimeError(f"Failed to acquire USSD lock for {self._holder_id}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._acquisition:
            self._lock.release(self._acquisition)
        return False


if __name__ == "__main__":
    # Test Harness
    print("Starting Kenya USSD Session Lock Test Harness...")
    
    lock = KenyaUSSDSessionLock(default_timeout=5.0)
    
    def simulate_ussd_session(thread_id: int, duration: float):
        try:
            with USSDTransactionContext(lock, holder_id=f"Thread-{thread_id}"):
                print(f"Thread-{thread_id}: USSD session started.")
                time.sleep(duration)  # Simulate USSD interaction
                print(f"Thread-{thread_id}: USSD session completed.")
        except RuntimeError as e:
            print(f"Thread-{thread_id}: {e}")

    # Test 1: Sequential acquisition
    print("\nTest 1: Sequential Acquisition")
    simulate_ussd_session(1, 1.0)
    simulate_ussd_session(2, 1.0)

    # Test 2: Concurrent acquisition (should queue)
    print("\nTest 2: Concurrent Acquisition")
    threads = []
    for i in range(3):
        t = threading.Thread(target=simulate_ussd_session, args=(i+10, 0.5))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

    print("\nTest Harness Complete.")
