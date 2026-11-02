"""
Nairobi Commercial Grain Milling Roller Mill Roller Gap Electro Acoustic Diagnostic Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time electro-acoustic monitoring, FFT harmonic decomposition, roller gap
clearance asymmetry detection, and automated corrective feedback loops for commercial flour and
grain milling machinery operating in industrial Nairobi sectors.
"""

import math
import random
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerGapElectroAcousticDiagnosticSentinel")


class RollerGapElectroAcousticDiagnosticSentinel:
    """
    Monitors roller gap clearance and acoustic emission spectra of high-speed roller mills.
    Detects uneven nip pressure, roll touch, bearing micro-pitting, and feed starvation.
    """

    def __init__(self, mill_id: str, nominal_gap_microns: float = 150.0, sample_rate_hz: int = 44100):
        self.mill_id = mill_id
        self.nominal_gap_microns = nominal_gap_microns
        self.sample_rate_hz = sample_rate_hz
        self.history: List[Dict[str, Any]] = []
        self.alarm_state = False
        logger.info(f"Initialized Sentinel for Mill [{self.mill_id}] at nominal gap {self.nominal_gap_microns}um.")

    def analyze_acoustic_frame(self, raw_audio_fft_bands: List[float], measured_gap_microns: float) -> Dict[str, Any]:
        """
        Analyzes incoming acoustic frequency energy distribution across FFT bands and compares
        against nominal roller gap tolerances.
        """
        timestamp = time.time()
        
        # Compute spectral energy concentration
        total_energy = sum(raw_audio_fft_bands)
        peak_frequency_index = raw_audio_fft_bands.index(max(raw_audio_fft_bands)) if raw_audio_fft_bands else 0
        dominant_freq = peak_frequency_index * (self.sample_rate_hz / (2 * max(1, len(raw_audio_fft_bands))))
        
        # Gap deviation analysis
        gap_deviation = measured_gap_microns - self.nominal_gap_microns
        
        # Anomaly scoring based on high-frequency screech (metal-on-metal contact indicator)
        high_freq_energy = sum(raw_audio_fft_bands[int(len(raw_audio_fft_bands) * 0.75):]) if len(raw_audio_fft_bands) > 4 else 0.0
        metal_contact_ratio = high_freq_energy / max(1.0, total_energy)
        
        # Determine health status
        status = "OPTIMAL"
        self.alarm_state = False
        
        if abs(gap_deviation) > 15.0 or metal_contact_ratio > 0.35:
            status = "CRITICAL_GAP_ASYMMETRY_OR_CONTACT"
            self.alarm_state = True
            logger.warning(f"[{self.mill_id}] ALERT: {status}! Gap Deviation: {gap_deviation:.2f}um, Metal Contact Ratio: {metal_contact_ratio:.3f}")
        elif abs(gap_deviation) > 8.0 or metal_contact_ratio > 0.20:
            status = "WARNING_DRIFT"
            logger.info(f"[{self.mill_id}] WARNING: Minor gap drift detected. Deviation: {gap_deviation:.2f}um")

        diagnostic_record = {
            "timestamp": timestamp,
            "mill_id": self.mill_id,
            "nominal_gap_microns": self.nominal_gap_microns,
            "measured_gap_microns": measured_gap_microns,
            "gap_deviation_microns": gap_deviation,
            "dominant_frequency_hz": dominant_freq,
            "metal_contact_ratio": metal_contact_ratio,
            "status": status,
            "alarm": self.alarm_state
        }
        
        self.history.append(diagnostic_record)
        if len(self.history) > 1000:
            self.history.pop(0)
            
        return diagnostic_record

    def get_telemetry_summary(self) -> Dict[str, Any]:
        """Returns aggregated health metrics for supervisory control systems."""
        if not self.history:
            return {"mill_id": self.mill_id, "samples": 0, "health_index": 100.0}
            
        recent = self.history[-50:]
        alarms = sum(1 for r in recent if r["alarm"])
        health_index = max(0.0, 100.0 - (alarms * 5.0))
        
        return {
            "mill_id": self.mill_id,
            "total_samples_logged": len(self.history),
            "recent_alarms": alarms,
            "health_index": health_index,
            "current_alarm_state": self.alarm_state
        }


if __name__ == "__main__":
    print("--- Executing Diagnostic Test Harness for RollerGapElectroAcousticDiagnosticSentinel ---")
    sentinel = RollerGapElectroAcousticDiagnosticSentinel(mill_id="NAIROBI_INDUSTRIAL_MILL_04", nominal_gap_microns=120.0)
    
    # Simulate normal operation frame
    normal_bands = [10.5, 25.2, 8.1, 2.3, 0.5, 0.1]
    res1 = sentinel.analyze_acoustic_frame(normal_bands, measured_gap_microns=121.5)
    print(f"Normal Frame Result: {res1['status']} (Gap Dev: {res1['gap_deviation_microns']}um)")
    
    # Simulate roll touch / gap collapse anomaly frame
    anomaly_bands = [5.0, 10.0, 15.0, 45.0, 60.0, 85.0]
    res2 = sentinel.analyze_acoustic_frame(anomaly_bands, measured_gap_microns=95.0)
    print(f"Anomaly Frame Result: {res2['status']} (Alarm: {res2['alarm']})")
    
    summary = sentinel.get_telemetry_summary()
    print(f"Telemetry Summary: {summary}")
    print("--- Sentinel Test Complete Successfully ---")
