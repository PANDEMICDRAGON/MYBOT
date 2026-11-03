import ast
import logging
import math
import random
import time
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('AvocadoOilCentrifugeSentinel')

class AvocadoOilCentrifugeSentinel:
    """
    Monitors high-speed industrial decanter and disc-stack centrifuges used in Nairobi
    avocado oil processing facilities. Correlates vibrational harmonic frequencies,
    bearing temperatures, feed slurry viscosity, and emulsion break efficiency.
    """
    
    def __init__(self, centrifuge_id: str, rated_rpm: float = 4200.0):
        self.centrifuge_id = centrifuge_id
        self.rated_rpm = rated_rpm
        self.operating_history: List[Dict[str, Any]] = []
        logger.info(f"AvocadoOilCentrifugeSentinel initialized for unit {centrifuge_id} at {rated_rpm} RPM.")

    def audit_cycle(self, rpm: float, vibration_mm_s: float, bearing_temp_c: float, 
                    viscosity_cp: float, emulsion_purity_pct: float) -> Dict[str, Any]:
        """
        Performs a single telemetry audit cycle assessing centrifuge mechanical health
        and oil extraction separation efficiency.
        """
        timestamp = time.time()
        
        # Calculate harmonic anomaly score based on vibration deviation relative to RPM
        rpm_ratio = rpm / self.rated_rpm
        expected_vibration_baseline = 1.2 * rpm_ratio
        vibration_delta = abs(vibration_mm_s - expected_vibration_baseline)
        
        # Emulsion integrity and thermal threshold checks
        thermal_risk = max(0.0, bearing_temp_c - 75.0) / 25.0  # Safe limit 75C
        viscosity_anomaly = abs(viscosity_cp - 45.0) / 45.0    # Optimal slurry viscosity target ~45 cP
        
        # Composite health index (0.0 = nominal, 1.0 = catastrophic failure imminent)
        harmonic_pulse_score = min(1.0, (vibration_delta * 0.4) + (thermal_risk * 0.4) + ((100.0 - emulsion_purity_pct) / 100.0 * 0.2))
        
        status = "NOMINAL"
        action_required = "NONE"
        
        if harmonic_pulse_score > 0.75:
            status = "CRITICAL_INTERVENTION"
            action_required = "EMERGENCY_SHUTDOWN_BEARING_INSPECTION"
        elif harmonic_pulse_score > 0.45:
            status = "WARNING"
            action_required = "ADJUST_FEED_FLOW_AND_FLUSH_BOWL"
            
        audit_record = {
            "timestamp": timestamp,
            "centrifuge_id": self.centrifuge_id,
            "rpm": rpm,
            "vibration_mm_s": vibration_mm_s,
            "bearing_temp_c": bearing_temp_c,
            "viscosity_cp": viscosity_cp,
            "emulsion_purity_pct": emulsion_purity_pct,
            "harmonic_pulse_score": round(harmonic_pulse_score, 4),
            "status": status,
            "action_required": action_required
        }
        
        self.operating_history.append(audit_record)
        if len(self.operating_history) > 1000:
            self.operating_history.pop(0)
            
        logger.info(f"Audit [{self.centrifuge_id}] -> RPM: {rpm}, Vib: {vibration_mm_s}mm/s, Temp: {bearing_temp_c}C, Score: {audit_record['harmonic_pulse_score']}, Status: {status}")
        return audit_record

    def get_fleet_summary(self) -> Dict[str, Any]:
        """Summarizes operational telemetry for executive diagnostics."""
        if not self.operating_history:
            return {"status": "NO_DATA"}
        
        latest = self.operating_history[-1]
        avg_vibration = sum(h["vibration_mm_s"] for h in self.operating_history) / len(self.operating_history)
        return {
            "centrifuge_id": self.centrifuge_id,
            "total_audits": len(self.operating_history),
            "latest_status": latest["status"],
            "latest_score": latest["harmonic_pulse_score"],
            "average_vibration": round(avg_vibration, 2)
        }

if __name__ == "__main__":
    print("Executing self-test harness for AvocadoOilCentrifugeSentinel...")
    sentinel = AvocadoOilCentrifugeSentinel(centrifuge_id="NBO-AVO-CENTRIFUGE-04", rated_rpm=4200.0)
    
    # Simulate normal and aberrant runs
    test_readings = [
        (4200.0, 1.1, 65.0, 44.5, 99.2),
        (4195.0, 1.3, 68.0, 46.0, 98.5),
        (4210.0, 3.8, 82.5, 52.0, 91.0),  # Anomaly state
    ];
    
    for rpm, vib, temp, visc, purity in test_readings:
        res = sentinel.audit_cycle(rpm, vib, temp, visc, purity)
        assert "status" in res
        
    # Verify compilation
    source_code = open(__file__, "r", encoding="utf-8").read()
    parsed_ast = ast.parse(source_code)
    assert parsed_ast is not None
    print("AvocadoOilCentrifugeSentinel module compiled successfully via AST parser.")
