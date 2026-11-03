"""Nairobi Commercial Biogas Microgrid SCADA Synapse Harmonic Pulse Correlation Sentinel"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("BiogasMicrogridSynapse")

class BiogasMicrogridSynapseSentinel:
    """
    Monitors Nairobi commercial biogas microgrid SCADA telemetry, correlating
    digester pressure pulses, cogeneration engine harmonic loads, and gas desulfurization
    pressures to prevent catastrophic over-pressurization or grid synchronization failure.
    """
    def __init__(self, plant_id: str = "NRB_BIO_KASARANI_01") -> None:
        self.plant_id = plant_id
        self.baseline_harmonic_hz = 50.0  # Standard East African grid frequency
        self.telemetry_history: List[Dict[str, float]] = []
        logger.info(f"Initialized BiogasMicrogridSynapseSentinel for plant: {self.plant_id}")

    def ingest_telemetry(self, digester_pressure_kpa: float, generator_hz: float, 
                         ch4_purity_pct: float, vibration_amplitude_mm_s: float) -> Dict[str, Any]:
        """
        Ingests real-time sensor streams and computes harmonic correlation and anomaly risk score.
        """
        timestamp = time.time()
        frequency_drift = abs(generator_hz - self.baseline_harmonic_hz)
        
        # Synthetic harmonic pulse correlation metric calculation
        pulse_correlation = math.exp(-0.1 * frequency_drift) * (ch4_purity_pct / 100.0)
        
        risk_score = 0.0
        if digester_pressure_kpa > 15.0 or digester_pressure_kpa < 2.0:
            risk_score += 0.4
        if frequency_drift > 0.8:
            risk_score += 0.35
        if vibration_amplitude_mm_s > 4.5:
            risk_score += 0.25
            
        status = "NOMINAL"
        if risk_score >= 0.7:
            status = "CRITICAL_INTERVENTION_REQUIRED"
        elif risk_score >= 0.4:
            status = "WARNING_ELEVATED_STRESS"

        reading = {
            "timestamp": timestamp,
            "digester_pressure_kpa": digester_pressure_kpa,
            "generator_hz": generator_hz,
            "ch4_purity_pct": ch4_purity_pct,
            "vibration_amplitude_mm_s": vibration_amplitude_mm_s,
            "pulse_correlation": pulse_correlation,
            "risk_score": risk_score,
            "status": status
        }
        
        self.telemetry_history.append(reading)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        return reading

    def run_diagnostic_audit(self) -> Dict[str, Any]:
        """
        Performs comprehensive diagnostic audit across recent microgrid cycles.
        """
        if not self.telemetry_history:
            return {"status": "NO_DATA", "recommendation": "Awaiting telemetry stream."}
            
        avg_risk = sum(r["risk_score"] for r in self.telemetry_history) / len(self.telemetry_history)
        latest_status = self.telemetry_history[-1]["status"]
        
        action_plan = "Stable operations. Continue anaerobic digestion monitoring."
        if avg_risk > 0.3:
            action_plan = "Inspect biogas compressor valves and verify microgrid inverter phase synchronization."
            
        return {
            "plant_id": self.plant_id,
            "total_samples": len(self.telemetry_history),
            "average_risk_score": round(avg_risk, 4),
            "current_status": latest_status,
            "operator_action_plan": action_plan
        }

if __name__ == "__main__":
    sentinel = BiogasMicrogridSynapseSentinel("NRB_KASARANI_BIOGAS_04")
    # Simulate normal and aberrant telemetry cycles
    for _ in range(5):
        p = random.uniform(4.0, 12.0)
        hz = random.normalvariate(50.0, 0.1)
        ch4 = random.uniform(60.0, 75.0)
        vib = random.uniform(1.0, 3.0)
        res = sentinel.ingest_telemetry(p, hz, ch4, vib)
        logger.info(f"Telemetry Ingested: {res['status']} (Risk: {res['risk_score']})")
    
    audit = sentinel.run_diagnostic_audit()
    logger.info(f"Diagnostic Audit Result: {audit}")
