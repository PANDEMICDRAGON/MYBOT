import time
import random
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class AcousticState(Enum):
    """Enum representing the current acoustic stealth state."""
    IDLE = "idle"
    MASKING = "masking"
    ALERT = "alert"
    DAMPED = "damped"


@dataclass
class AcousticProfile:
    """Represents a specific acoustic/vibration signature."""
    frequency_hz: float
    amplitude_db: float
    duration_ms: float
    signature_hash: str = field(default="", init=False)

    def __post_init__(self):
        """Compute the unique hash of the acoustic signature."""
        raw = f"{self.frequency_hz}:{self.amplitude_db}:{self.duration_ms}"
        self.signature_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]


class AcousticStealthSentinel:
    """
    Nairobi Acoustic Stealth & Vibration Dampening Sentinel.
    
    This module monitors and manipulates the acoustic and vibrational environment
    of a server room or critical infrastructure to prevent side-channel attacks.
    It generates masking noise to obscure operational patterns and detects
    anomalous vibrations that may indicate physical tampering.
    """

    def __init__(self, location: str = "Nairobi Data Center", sensitivity: float = 0.5):
        """
        Initialize the Acoustic Stealth Sentinel.

        Args:
            location: The physical location of the monitored area.
            sensitivity: Threshold for anomaly detection (0.0 to 1.0).
        """
        self.location = location
        self.sensitivity = sensitivity
        self.state = AcousticState.IDLE
        self.masking_profiles: List[AcousticProfile] = []
        self.anomaly_log: List[Dict] = []
        self._active_mask: Optional[AcousticProfile] = None
        self._vibration_baseline: float = 0.0
        self._last_check: float = time.time()

    def calibrate_baseline(self, vibration_data: List[float]) -> None:
        """
        Calibrate the baseline vibration level.

        Args:
            vibration_data: List of vibration measurements in mm/s.
        """
        if not vibration_data:
            raise ValueError("Vibration data cannot be empty")
        self._vibration_baseline = sum(vibration_data) / len(vibration_data)
        self.state = AcousticState.IDLE

    def generate_masking_profile(self, target_frequency: float, duration_ms: float) -> AcousticProfile:
        """
        Generate a masking acoustic profile to obscure a specific operational signature.

        Args:
            target_frequency: The frequency to mask (Hz).
            duration_ms: Duration of the masking signal (ms).

        Returns:
            AcousticProfile: The generated masking profile.
        """
        # Add slight randomization to avoid predictable patterns
        randomized_freq = target_frequency + random.uniform(-5, 5)
        amplitude = random.uniform(30, 60)  # dB
        profile = AcousticProfile(
            frequency_hz=randomized_freq,
            amplitude_db=amplitude,
            duration_ms=duration_ms
        )
        self.masking_profiles.append(profile)
        return profile

    def activate_masking(self, profile: AcousticProfile) -> bool:
        """
        Activate an acoustic masking profile.

        Args:
            profile: The acoustic profile to activate.

        Returns:
            bool: True if masking was successfully activated.
        """
        if self.state == AcousticState.ALERT:
            return False
        self._active_mask = profile
        self.state = AcousticState.MASKING
        return True

    def deactivate_masking(self) -> None:
        """Deactivate the current acoustic masking profile."""
        self._active_mask = None
        if self.state == AcousticState.MASKING:
            self.state = AcousticState.IDLE

    def check_vibration_anomaly(self, current_vibration: float) -> Optional[Dict]:
        """
        Check for vibration anomalies that may indicate tampering.

        Args:
            current_vibration: Current vibration measurement in mm/s.

        Returns:
            Optional[Dict]: Anomaly details if detected, None otherwise.
        """
        if self._vibration_baseline == 0.0:
            return None

        deviation = abs(current_vibration - self._vibration_baseline)
        threshold = self._vibration_baseline * self.sensitivity

        if deviation > threshold:
            anomaly = {
                "timestamp": time.time(),
                "current_vibration": current_vibration,
                "baseline": self._vibration_baseline,
                "deviation": deviation,
                "severity": "HIGH" if deviation > threshold * 2 else "MEDIUM"
            }
            self.anomaly_log.append(anomaly)
            self.state = AcousticState.ALERT
            return anomaly

        return None

    def get_stealth_status(self) -> Dict:
        """
        Get the current stealth status.

        Returns:
            Dict: Current status including state, active mask, and anomaly count.
        """
        return {
            "location": self.location,
            "state": self.state.value,
            "active_mask": self._active_mask.signature_hash if self._active_mask else None,
            "anomaly_count": len(self.anomaly_log),
            "baseline_vibration": self._vibration_baseline,
            "sensitivity": self.sensitivity
        }

    def reset_alerts(self) -> None:
        """Reset all alerts and return to idle state."""
        self.anomaly_log.clear()
        self.state = AcousticState.IDLE


def main():
    """Test harness for the Acoustic Stealth Sentinel."""
    print("Initializing Nairobi Acoustic Stealth Sentinel...")
    sentinel = AcousticStealthSentinel(location="Nairobi Data Center", sensitivity=0.3)

    # Calibrate baseline
    vibration_data = [0.5, 0.6, 0.55, 0.52, 0.58]
    sentinel.calibrate_baseline(vibration_data)
    print(f"Baseline calibrated: {sentinel._vibration_baseline} mm/s")

    # Generate and activate masking profile
    mask_profile = sentinel.generate_masking_profile(target_frequency=100.0, duration_ms=500)
    print(f"Generated masking profile: {mask_profile.signature_hash}")
    success = sentinel.activate_masking(mask_profile)
    print(f"Masking activated: {success}")
    print(f"Status: {sentinel.get_stealth_status()}")

    # Simulate normal vibration
    normal_vibration = 0.55
    anomaly = sentinel.check_vibration_anomaly(normal_vibration)
    print(f"Normal vibration check: {anomaly}")

    # Simulate tampering attempt
    tamper_vibration = 2.5
    anomaly = sentinel.check_vibration_anomaly(tamper_vibration)
    print(f"Tampering detected: {anomaly}")
    print(f"Status after tamper: {sentinel.get_stealth_status()}")

    # Reset alerts
    sentinel.reset_alerts()
    print(f"Status after reset: {sentinel.get_stealth_status()}")

    print("Acoustic Stealth Sentinel test completed successfully.")


if __name__ == "__main__":
    main()