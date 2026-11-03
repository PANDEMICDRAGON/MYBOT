import hashlib
import time
import uuid
from typing import Dict, Any, Optional

class KraEinDynamicRotator:
    """
    Autonomous KRA EIN Dynamic Rotator & Compliance Sentinel.
    
    This class manages the dynamic rotation of Electronic Identification Numbers (EINs)
    for KRA (Kenya Revenue Authority) compliance. It ensures that sensitive tax data
    is never exposed to static credentials and proactively detects anomalies in tax
    filing patterns.
    """

    def __init__(self, operator_id: str, initial_ein: str):
        """
        Initialize the KRA EIN Dynamic Rotator.
        
        Args:
            operator_id: The unique identifier for the operator.
            initial_ein: The initial Electronic Identification Number.
        """
        self.operator_id = operator_id
        self.current_ein = initial_ein
        self.rotation_history: list[Dict[str, Any]] = []
        self.last_rotation_time: float = time.time()
        self.rotation_interval: float = 3600.0  # 1 hour
        self.anomaly_threshold: float = 0.8
        self.tax_filing_patterns: list[float] = []

    def rotate_ein(self) -> str:
        """
        Rotate the current EIN to a new one.
        
        Returns:
            The new EIN.
        """
        new_ein = self._generate_new_ein()
        self.rotation_history.append({
            'old_ein': self.current_ein,
            'new_ein': new_ein,
            'timestamp': time.time()
        })
        self.current_ein = new_ein
        self.last_rotation_time = time.time()
        return new_ein

    def _generate_new_ein(self) -> str:
        """
        Generate a new EIN based on the current time and a random UUID.
        
        Returns:
            The new EIN.
        """
        timestamp = int(time.time())
        random_uuid = str(uuid.uuid4())
        combined = f"{self.operator_id}{timestamp}{random_uuid}"
        hashed = hashlib.sha256(combined.encode()).hexdigest()
        return hashed[:16].upper()

    def check_rotation_due(self) -> bool:
        """
        Check if a rotation is due.
        
        Returns:
            True if a rotation is due, False otherwise.
        """
        return (time.time() - self.last_rotation_time) >= self.rotation_interval

    def record_tax_filing(self, amount: float) -> None:
        """
        Record a tax filing amount for anomaly detection.
        
        Args:
            amount: The amount of the tax filing.
        """
        self.tax_filing_patterns.append(amount)
        if len(self.tax_filing_patterns) > 100:
            self.tax_filing_patterns.pop(0)

    def detect_anomalies(self) -> bool:
        """
        Detect anomalies in tax filing patterns.
        
        Returns:
            True if an anomaly is detected, False otherwise.
        """
        if len(self.tax_filing_patterns) < 5:
            return False
        
        mean = sum(self.tax_filing_patterns) / len(self.tax_filing_patterns)
        variance = sum((x - mean) ** 2 for x in self.tax_filing_patterns) / len(self.tax_filing_patterns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return False
        
        z_score = abs(self.tax_filing_patterns[-1] - mean) / std_dev
        return z_score > self.anomaly_threshold

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the rotator.
        
        Returns:
            A dictionary containing the current status.
        """
        return {
            'operator_id': self.operator_id,
            'current_ein': self.current_ein,
            'last_rotation_time': self.last_rotation_time,
            'rotation_interval': self.rotation_interval,
            'anomaly_threshold': self.anomaly_threshold,
            'tax_filing_patterns': self.tax_filing_patterns[-10:],
            'rotation_history': self.rotation_history[-10:]
        }

if __name__ == "__main__":
    rotator = KraEinDynamicRotator("Michael_Obiero", "INITIAL_EIN_12345")
    print("Initial EIN:", rotator.current_ein)
    
    # Simulate tax filings
    for i in range(10):
        rotator.record_tax_filing(1000.0 + (i * 100))
    
    # Check for anomalies
    anomaly_detected = rotator.detect_anomalies()
    print("Anomaly detected:", anomaly_detected)
    
    # Rotate EIN
    new_ein = rotator.rotate_ein()
    print("New EIN:", new_ein)
    
    # Get status
    status = rotator.get_status()
    print("Status:", status)