import ast
import json
import time
import random
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AcousticSideChannelShield")


class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class AcousticSignature:
    """Represents a captured acoustic fingerprint."""
    timestamp: float
    frequency_spectrum: List[float]
    amplitude_db: float
    entropy_score: float
    source_id: str


@dataclass
class ShieldStatus:
    """Current status of the acoustic shield."""
    is_active: bool
    threat_level: ThreatLevel
    last_scan_time: float
    masked_channels: int
    total_channels: int


class AcousticSideChannelShield:
    """
    Proactively monitors and mitigates acoustic side-channel leakage.
    
    This module simulates the capture of acoustic data from data center
    environments (fans, keyboards, hard drives) and applies noise
    masking or frequency shifting to prevent key extraction via sound.
    """

    def __init__(self, operator_id: str = "Michael Obiero", location: str = "Nairobi, Kenya"):
        self.operator_id = operator_id
        self.location = location
        self.status = ShieldStatus(
            is_active=False,
            threat_level=ThreatLevel.LOW,
            last_scan_time=0.0,
            masked_channels=0,
            total_channels=16
        )
        self.baseline_signatures: List[AcousticSignature] = []
        self._lock = None  # Simulated lock
        logger.info(f"AcousticSideChannelShield initialized for {operator_id} in {location}")

    def _calculate_entropy(self, spectrum: List[float]) -> float:
        """Calculate Shannon entropy of the frequency spectrum."""
        if not spectrum:
            return 0.0
        total = sum(spectrum)
        if total == 0:
            return 0.0
        entropy = 0.0
        for val in spectrum:
            if val > 0:
                p = val / total
                entropy -= p * (p ** 0.5)  # Simplified entropy metric
        return abs(entropy)

    def capture_signature(self, source_id: str) -> AcousticSignature:
        """
        Simulate capturing an acoustic signature from a hardware component.
        In production, this would interface with microphones or vibration sensors.
        """
        # Simulate random acoustic data
        spectrum = [random.uniform(0.1, 10.0) for _ in range(16)]
        amplitude = random.uniform(30.0, 80.0)
        entropy = self._calculate_entropy(spectrum)
        
        sig = AcousticSignature(
            timestamp=time.time(),
            frequency_spectrum=spectrum,
            amplitude_db=amplitude,
            entropy_score=entropy,
            source_id=source_id
        )
        self.baseline_signatures.append(sig)
        return sig

    def detect_anomaly(self, current_sig: AcousticSignature) -> ThreatLevel:
        """
        Compare current signature against baseline to detect anomalies.
        High entropy or sudden amplitude spikes may indicate data leakage.
        """
        if not self.baseline_signatures:
            return ThreatLevel.LOW

        # Calculate average baseline entropy
        avg_entropy = sum(s.entropy_score for s in self.baseline_signatures) / len(self.baseline_signatures)
        
        # Detect deviation
        deviation = abs(current_sig.entropy_score - avg_entropy)
        amplitude_spike = current_sig.amplitude_db > 70.0

        if deviation > 2.0 and amplitude_spike:
            return ThreatLevel.CRITICAL
        elif deviation > 1.0:
            return ThreatLevel.HIGH
        elif amplitude_spike:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def apply_noise_masking(self, threat_level: ThreatLevel) -> int:
        """
        Apply acoustic noise masking to mitigate detected threats.
        Returns the number of channels masked.
        """
        if threat_level == ThreatLevel.LOW:
            return 0
        
        # Simulate masking channels based on threat level
        mask_factor = {
            ThreatLevel.MEDIUM: 4,
            ThreatLevel.HIGH: 8,
            ThreatLevel.CRITICAL: 16
        }
        
        channels_to_mask = mask_factor.get(threat_level, 0)
        self.status.masked_channels = channels_to_mask
        self.status.threat_level = threat_level
        self.status.last_scan_time = time.time()
        
        logger.warning(f"Applied noise masking on {channels_to_mask} channels due to {threat_level.value} threat")
        return channels_to_mask

    def run_scan_cycle(self) -> Dict[str, Any]:
        """
        Execute a full acoustic scan cycle.
        """
        if not self.status.is_active:
            raise RuntimeError("Shield is not active. Call activate() first.")

        # Simulate scanning multiple sources
        sources = ["fan_01", "keyboard_01", "hdd_01", "psu_01"]
        results = []
        max_threat = ThreatLevel.LOW

        for source in sources:
            sig = self.capture_signature(source)
            threat = self.detect_anomaly(sig)
            if threat.value > max_threat.value:
                max_threat = threat
            results.append({
                "source": source,
                "threat": threat.value,
                "entropy": sig.entropy_score
            })

        # Apply mitigation if needed
        masked = self.apply_noise_masking(max_threat)

        return {
            "scan_time": time.time(),
            "max_threat": max_threat.value,
            "masked_channels": masked,
            "details": results
        }

    def activate(self) -> None:
        """Activate the acoustic shield."""
        self.status.is_active = True
        logger.info("AcousticSideChannelShield activated")

    def deactivate(self) -> None:
        """Deactivate the acoustic shield."""
        self.status.is_active = False
        self.status.masked_channels = 0
        logger.info("AcousticSideChannelShield deactivated")

    def get_status(self) -> Dict[str, Any]:
        """Return current shield status."""
        return {
            "is_active": self.status.is_active,
            "threat_level": self.status.threat_level.value,
            "last_scan_time": self.status.last_scan_time,
            "masked_channels": self.status.masked_channels,
            "total_channels": self.status.total_channels,
            "operator": self.operator_id,
            "location": self.location
        }


def main():
    """Test harness for AcousticSideChannelShield."""
    try:
        shield = AcousticSideChannelShield()
        shield.activate()
        
        # Run a scan cycle
        result = shield.run_scan_cycle()
        print(json.dumps(result, indent=2))
        
        # Check status
        status = shield.get_status()
        print(json.dumps(status, indent=2))
        
        shield.deactivate()
        print("Test completed successfully.")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
