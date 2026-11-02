"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Shear Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

 Monitors high-frequency electro-acoustic shear wave emissions from roller mill gaps to detect
 micro-abrasions, uneven grain feed distribution, and bearing wear under high-load milling conditions.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapAcousticShearSentinel")

class RollerGapAcousticShearSentinel:
    def __init__(self, mill_id: str, sample_frequency_hz: float = 48000.0):
        self.mill_id = mill_id
        self.sample_frequency_hz = sample_frequency_hz
        self.baseline_shear_db: float = 65.0
        self.shear_threshold_db: float = 88.0
        self.history: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerGapAcousticShearSentinel for Mill ID: {mill_id} at {sample_frequency_hz} Hz")

    def analyze_acoustic_emission(self, raw_audio_rms: float, current_gap_microns: float) -> Dict[str, Any]:
        """
        Analyzes acoustic shear emissions in decibels relative to the roller gap setting.
        """
        # Convert raw RMS to decibel equivalent
        db_level = 20 * math.log10(max(raw_audio_rms, 1e-6)) + 120.0
        
        # Dynamic adjustment based on tight gaps (< 200 microns have higher baseline shear)
        gap_factor = 200.0 / max(current_gap_microns, 50.0)
        adjusted_threshold = self.shear_threshold_db + (gap_factor * 2.5)
        
        anomaly_detected = db_level > adjusted_threshold
        
        telemetry = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "current_gap_microns": current_gap_microns,
            "acoustic_db": round(db_level, 2),
            "threshold_db": round(adjusted_threshold, 2),
            "anomaly_detected": anomaly_detected,
            "mitigation_action": "APPLY_DYNAMIC_GAP_COMPENSATION" if anomaly_detected else "NOMINAL"
        }
        
        self.history.append(telemetry)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        if anomaly_detected:
            logger.warning(f"[{self.mill_id}] ANOMALOUS SHEAR DETECTED: {db_level:.2f} dB (Threshold: {adjusted_threshold:.2f} dB) at gap {current_gap_microns}um")
            
        return telemetry

    def generate_health_report(self) -> Dict[str, Any]:
        if not self.history:
            return {"status": "NO_DATA"}
            
        anomalies = [h for h in self.history if h["anomaly_detected"]]
        return {
            "mill_id": self.mill_id,
            "total_samples": len(self.history),
            "total_anomalies": len(anomalies),
            "anomaly_rate": len(anomalies) / len(self.history),
            "last_status": self.history[-1]
        }

if __name__ == "__main__":
    sentinel = RollerGapAcousticShearSentinel(mill_id="NAIROBI_UNGA_MILL_04")
    
    # Simulate normal and anomalous runs
    for i in range(10):
        rms = random.uniform(0.01, 0.05) if i != 7 else 0.85
        gap = 150.0
        report = sentinel.analyze_acoustic_emission(raw_audio_rms=rms, current_gap_microns=gap)
        print(report)
        
    print("Final Health Report:", sentinel.generate_health_report())
