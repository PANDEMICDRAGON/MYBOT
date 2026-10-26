import logging
import time
import threading
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KenyaSMSAlerting")


class AlertSeverity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class SMSMessage:
    recipient: str
    body: str
    severity: AlertSeverity = AlertSeverity.INFO
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])


class SMSProvider:
    """Abstract base class for SMS providers."""
    def send(self, message: SMSMessage) -> bool:
        raise NotImplementedError


class MockSMSProvider(SMSProvider):
    """Mock SMS provider for testing and development."""
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.sent_messages: List[SMSMessage] = []
        self._lock = threading.Lock()

    def send(self, message: SMSMessage) -> bool:
        time.sleep(self.delay)
        with self._lock:
            self.sent_messages.append(message)
        logger.info(f"[MOCK] SMS sent to {message.recipient}: {message.body}")
        return True


class KenyaSMSAlerting:
    """
    Resilient SMS alerting system for operator notification in Kenya.
    
    Features:
    - Rate limiting to prevent SMS flooding
    - Severity-based filtering
    - Retry logic with exponential backoff
    - Thread-safe message queue
    - Local message logging for audit
    """

    def __init__(self, provider: SMSProvider, max_rate_per_minute: int = 10, max_retries: int = 3):
        self.provider = provider
        self.max_rate_per_minute = max_rate_per_minute
        self.max_retries = max_retries
        self._message_queue: List[SMSMessage] = []
        self._lock = threading.Lock()
        self._send_times: List[float] = []
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._audit_log: List[Dict[str, Any]] = []

    def _is_rate_limited(self) -> bool:
        now = time.time()
        with self._lock:
            # Remove timestamps older than 60 seconds
            self._send_times = [t for t in self._send_times if now - t < 60]
            return len(self._send_times) >= self.max_rate_per_minute

    def _record_send(self) -> None:
        now = time.time()
        with self._lock:
            self._send_times.append(now)

    def _log_audit(self, message: SMSMessage, success: bool, error: Optional[str] = None) -> None:
        entry = {
            "message_id": message.message_id,
            "recipient": message.recipient,
            "severity": message.severity.value,
            "timestamp": message.timestamp,
            "success": success,
            "error": error
        }
        with self._lock:
            self._audit_log.append(entry)
        logger.info(f"Audit: {entry}")

    def _send_with_retry(self, message: SMSMessage) -> bool:
        for attempt in range(self.max_retries):
            try:
                if self._is_rate_limited():
                    logger.warning(f"Rate limit reached, delaying send for message {message.message_id}")
                    time.sleep(5)
                    continue

                success = self.provider.send(message)
                if success:
                    self._record_send()
                    self._log_audit(message, True)
                    return True
                else:
                    error = "Provider returned False"
                    self._log_audit(message, False, error)
                    logger.warning(f"Send failed for {message.message_id}, attempt {attempt + 1}/{self.max_retries}")
            except Exception as e:
                error = str(e)
                self._log_audit(message, False, error)
                logger.error(f"Exception sending {message.message_id}: {e}, attempt {attempt + 1}/{self.max_retries}")

            # Exponential backoff
            backoff = 2 ** attempt
            time.sleep(backoff)

        return False

    def _worker(self) -> None:
        while self._running:
            with self._lock:
                if not self._message_queue:
                    time.sleep(0.1)
                    continue
                message = self._message_queue.pop(0)

            self._send_with_retry(message)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        logger.info("KenyaSMSAlerting worker started")

    def stop(self) -> None:
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        logger.info("KenyaSMSAlerting worker stopped")

    def send_alert(self, recipient: str, body: str, severity: AlertSeverity = AlertSeverity.INFO) -> bool:
        """Queue an SMS alert for sending."""
        message = SMSMessage(recipient=recipient, body=body, severity=severity)
        with self._lock:
            self._message_queue.append(message)
        logger.info(f"Queued alert {message.message_id} for {recipient} (severity: {severity.value})")
        return True

    def get_audit_log(self) -> List[Dict[str, Any]]:
        with self._lock:
            return self._audit_log.copy()

    def get_queue_size(self) -> int:
        with self._lock:
            return len(self._message_queue)


if __name__ == "__main__":
    # Test harness
    print("Testing KenyaSMSAlerting...")
    provider = MockSMSProvider(delay=0.01)
    alerter = KenyaSMSAlerting(provider, max_rate_per_minute=5, max_retries=2)
    alerter.start()

    # Send test alerts
    alerter.send_alert("+254700000000", "System online", AlertSeverity.INFO)
    alerter.send_alert("+254700000000", "High CPU load detected", AlertSeverity.WARNING)
    alerter.send_alert("+254700000000", "Security breach attempt blocked", AlertSeverity.CRITICAL)

    time.sleep(1)  # Allow time for sending

    alerter.stop()

    # Verify results
    audit_log = alerter.get_audit_log()
    assert len(audit_log) == 3, f"Expected 3 audit entries, got {len(audit_log)}"
    assert all(entry["success"] for entry in audit_log), "All sends should succeed"
    assert len(provider.sent_messages) == 3, f"Expected 3 sent messages, got {len(provider.sent_messages)}"

    print("All tests passed!")
    print(f"Audit log: {audit_log}")