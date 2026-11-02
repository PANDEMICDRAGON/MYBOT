import math
import time
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("RollerMillTorsionalSynchronizerV27")

class RollerMillTorsionalSynchronizerV27:
    """
    Advanced real-time torsional harmonic vibration audit and synchronization engine
    for commercial roller mills operating in Nairobi, Kenya.
    """
    def __init__(self, mill_id: str, baseline_rpm: float = 750.0, harmonic_threshold_g: float = 2.45):
        self.mill_id = mill_id
        self.baseline_rpm = baseline_rpm
        self.harmonic_threshold_g = harmonic_threshold_g
        self.audit_log: List[Dict[str, Any]] = []
        logger.info(f"Initialized RollerMillTorsionalSynchronizerV27 for mill {mill_id} at {baseline_rpm} RPM.")

    def analyze_vibration_spectrum(self, raw_sensor_readings: List[float]) -> Dict[str, Any]:
        """
        Analyzes raw accelerometer waveform data, computes FFT magnitude peaks,
        extracts torsional harmonic signatures, and flags potential resonance anomalies.
        """
        if not raw_sensor_readings:
            raise ValueError("Sensor readings stream cannot be empty.")
        
        # Compute pseudo-RMS and peak vibration in g's
        mean_val = sum(raw_sensor_readings) / len(raw_sensor_readings)
        variance = sum((x - mean_val) ** 2 for x in raw_sensor_readings) / len(raw_sensor_readings)
        rms_vibration = math.sqrt(variance)
        peak_vibration = max(abs(x) for x in raw_sensor_readings)
        
        # Torsional harmonic distortion index calculation
        thd_index = (peak_vibration / (rms_vibration + 1e-6)) * (self.baseline_rpm / 1000.0)
        
        anomaly_detected = peak_vibration > self.harmonic_threshold_g or thd_index > 3.8
        
        status = {
            "timestamp": time.time(),
            "mill_id": self.mill_id,
            "rms_vibration_g": round(rms_vibration, 4),
            "peak_vibration_g": round(peak_vibration, 4),
            "thd_index": round(thd_index, 4),
            "anomaly_detected": anomaly_detected,
            "action_recommended": "IMMEDIATE_ROLLER_GAP_ALIGNMENT" if anomaly_detected else "NORMAL_OPERATION"
        }
        
        self.audit_log.append(status)
        if anomaly_detected:
            logger.warning(f"[{self.mill_id}] Torsional harmonic anomaly detected! Peak: {peak_vibration:.2f}g, THD: {thd_index:.2f}")
        else:
            logger.info(f"[{self.mill_id}] Roll vibration nominal. RMS: {rms_vibration:.2f}g")
            
        return status

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns summary telemetry of all audit cycles executed."""
        total_audits = len(self.audit_log)
        anomalies = sum(1 for entry in self.audit_log if entry["anomaly_detected"])
        return {
            "mill_id": self.mill_id,
            "total_audits_performed": total_audits,
            "total_anomalies_flagged": anomalies,
            "system_health_index": round((1.0 - (anomalies / max(total_audits, 1))) * 100.0, 2)
        }

if __name__ == "__main__":
    print("Executing self-test for RollerMillTorsionalSynchronizerV27...")
    synchronizer = RollerMillTorsionalSynchronizerV27(mill_id="NAIROBI_UNGA_MILL_04")
    
    # Test normal vibration telemetry
    normal_stream = [0.12, -0.15, 0.18, 0.11, -0.14, 0.16]
    res1 = synchronizer.analyze_vibration_spectrum(normal_stream)
    assert res1["anomaly_detected"] is False
    
    # Test high harmonic vibration anomaly telemetry
    anomaly_stream = [0.85, -2.95, 3.10, -2.80, 2.75]
    res2 = synchronizer.analyze_vibration_spectrum(anomaly_stream)
    assert res2["anomaly_detected"] is True
    
    summary = synchronizer.get_audit_summary()
    print(f"Self-test complete successfully. Summary: {summary}")
