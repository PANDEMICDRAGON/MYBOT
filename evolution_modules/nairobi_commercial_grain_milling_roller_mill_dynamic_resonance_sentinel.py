"""Nairobi Commercial Grain Milling Roller Mill Dynamic Resonance Sentinel.

Provides real-time telemetry analysis, structural resonance tracking, harmonic distortion
monitoring, and automated emergency dampening recommendations for roller mills operating in Nairobi.
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillDynamicResonanceSentinel")


class RollerMillDynamicResonanceSentinel:
    """Monitors mechanical vibration spectra and structural resonance in commercial roller mills."""

    def __init__(self, mill_id: str, natural_frequency_hz: float = 48.5, warning_threshold_g: float = 2.5):
        self.mill_id = mill_id
        self.natural_frequency_hz = natural_frequency_hz
        self.warning_threshold_g = warning_threshold_g
        self.telemetry_history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillDynamicResonanceSentinel for mill {mill_id} [NatFreq: {natural_frequency_hz}Hz]")

    def analyze_spectrum(self, dominant_frequency_hz: float, peak_amplitude_g: float, harmonic_distortion_pct: float) -> Dict[str, Any]:
        """Analyze incoming vibration spectrum telemetry for resonance lock and excessive g-force."""
        timestamp = time.time()
        
        # Calculate proximity to structural natural frequency
        freq_delta = abs(dominant_frequency_hz - self.natural_frequency_hz)
        resonance_lock = freq_delta < 1.5  # Within 1.5 Hz of natural frequency
        
        status = "NOMINAL"
        action_required = "NONE"
        
        if peak_amplitude_g >= self.warning_threshold_g and resonance_lock:
            status = "CRITICAL_RESONANCE_WARNING"
            action_required = "IMMEDIATE_FEED_REDUCTION_AND_SPEED_SHIFT"
            logger.error(f"CRITICAL: Mill {self.mill_id} experiencing structural resonance lock at {dominant_frequency_hz}Hz ({peak_amplitude_g}g)!")
        elif peak_amplitude_g >= self.warning_threshold_g:
            status = "ELEVATED_VIBRATION"
            action_required = "INSPECT_DRIVE_AND_BEARINGS"
            logger.warning(f"WARNING: High vibration on mill {self.mill_id}: {peak_amplitude_g}g at {dominant_frequency_hz}Hz")
        elif resonance_lock:
            status = "NEAR_RESONANCE"
            action_required = "MONITOR_CLOSELY"
            logger.warning(f"CAUTION: Mill {self.mill_id} operating near natural frequency ({dominant_frequency_hz}Hz)")

        record = {
            "timestamp": timestamp,
            "dominant_frequency_hz": dominant_frequency_hz,
            "peak_amplitude_g": peak_amplitude_g,
            "harmonic_distortion_pct": harmonic_distortion_pct,
            "freq_delta": freq_delta,
            "resonance_lock": resonance_lock,
            "status": status,
            "action_required": action_required
        }
        
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return record

    def get_health_summary(self) -> Dict[str, Any]:
        """Summarize recent operational health and resonance telemetry."""
        if not self.telemetry_history:
            return {"mill_id": self.mill_id, "status": "NO_DATA"}
            
        recent = self.telemetry_history[-1]
        critical_events = sum(1 for r in self.telemetry_history if r["status"] == "CRITICAL_RESONANCE_WARNING")
        
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.telemetry_history),
            "latest_status": recent["status"],
            "latest_amplitude_g": recent["peak_amplitude_g"],
            "critical_event_count": critical_events,
            "natural_frequency_hz": self.natural_frequency_hz
        }


if __name__ == "__main__":
    print("Executing RollerMillDynamicResonanceSentinel Self-Test...")
    sentinel = RollerMillDynamicResonanceSentinel(mill_id="NAI_MILL_04", natural_frequency_hz=50.0, warning_threshold_g=2.0)
    
    # Test normal reading
    res1 = sentinel.analyze_spectrum(dominant_frequency_hz=35.2, peak_amplitude_g=0.8, harmonic_distortion_pct=3.2)
    assert res1["status"] == "NOMINAL", f"Expected NOMINAL, got {res1['status']}"
    
    # Test resonance critical reading
    res2 = sentinel.analyze_spectrum(dominant_frequency_hz=49.8, peak_amplitude_g=2.9, harmonic_distortion_pct=14.5)
    assert res2["status"] == "CRITICAL_RESONANCE_WARNING", f"Expected CRITICAL, got {res2['status']}"
    
    summary = sentinel.get_health_summary()
    print(f"Test Passed. Health Summary: {summary}")
