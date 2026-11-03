import time
import threading
import logging
from enum import Enum
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USSDState(Enum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    TERMINATED = "TERMINATED"

class AdaptiveUSSDSessionLock:
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.state = USSDState.IDLE
        self.timeout = timeout
        self.max_retries = max_retries
        self._lock = threading.Lock()
        self._last_activity = time.time()
        self._retries = 0

    def _update_activity(self):
        self._last_activity = time.time()

    def _check_timeout(self) -> bool:
        return (time.time() - self._last_activity) > self.timeout

    def start_session(self) -> bool:
        with self._lock:
            if self.state != USSDState.IDLE:
                logger.warning("Session already active or locked.")
                return False
            self.state = USSDState.ACTIVE
            self._update_activity()
            logger.info("USSD session started.")
            return True

    def send_command(self, command: str) -> bool:
        with self._lock:
            if self.state != USSDState.ACTIVE:
                logger.error("Cannot send command in state: %s", self.state)
                return False
            if self._check_timeout():
                self._handle_timeout()
                return False
            self._update_activity()
            logger.info("Command sent: %s", command)
            return True

    def _handle_timeout(self):
        self._retries += 1
        if self._retries >= self.max_retries:
            self.state = USSDState.TERMINATED
            logger.error("Max retries exceeded. Session terminated.")
        else:
            self.state = USSDState.LOCKED
            logger.warning("Session locked due to timeout. Retry %d/%d", self._retries, self.max_retries)

    def unlock_session(self) -> bool:
        with self._lock:
            if self.state != USSDState.LOCKED:
                logger.warning("Session is not locked.")
                return False
            self.state = USSDState.ACTIVE
            self._update_activity()
            self._retries = 0
            logger.info("Session unlocked.")
            return True

    def terminate_session(self):
        with self._lock:
            self.state = USSDState.TERMINATED
            logger.info("Session terminated.")

    def get_state(self) -> USSDState:
        return self.state

if __name__ == "__main__":
    session = AdaptiveUSSDSessionLock(timeout=5.0, max_retries=2)
    assert session.start_session() == True
    assert session.send_command("*123#") == True
    time.sleep(6)
    assert session.send_command("*456#") == False
    assert session.get_state() == USSDState.LOCKED
    assert session.unlock_session() == True
    assert session.send_command("*789#") == True
    session.terminate_session()
    assert session.get_state() == USSDState.TERMINATED
    logger.info("All tests passed.")