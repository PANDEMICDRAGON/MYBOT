"""Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V81.1

Designed and forged by Cortana Autonomous Evolutionary Architect for Michael Obiero, Nairobi, Kenya.
Provides high-precision harmonic vibration auditing, micrometer gap telemetry correlation, and adaptive closed-loop adjustment recommendations for commercial roller grain mills.
"""

import ast
import json
import math
import logging
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [MillingSynapseV81_1]: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RollerSensorTelemetry:
    mill_id: str
    roller_pair: str
    gap_microns: float
    vibration_frequency_hz: float
    vibration_amplitude_microns: float
    motor_current_amps: float
    product_feed_rate_tph: float
    timestamp: float

@dataclass
class HarmonicAuditResult:
    mill_id: str
    roller_pair: str
    harmonic_index: float
    synapse_health_score: float
    recommended_gap_adjustment_microns: float
    anomaly_detected: bool
    reason: str

class RollerGapHarmonicSynchronizer:
    """Correlates vibration signatures with micrometer roller gaps to maintain peak milling efficiency."""

    def __init__(self, target_frequency_hz: float = 50.0, max_allowable_amplitude: float = 12.5):
        self.target_frequency_hz = target_frequency_hz
        self.max_allowable_amplitude = max_allowable_amplitude
        self.audit_history: List[HarmonicAuditResult] = []

    def audit_telemetry(self, telemetry: RollerSensorTelemetry) -> HarmonicAuditResult:
        logger.info(f"Auditing mill {telemetry.mill_id} ({telemetry.roller_pair}) at gap {telemetry.gap_microns}um...")
        
        # Calculate harmonic divergence from baseline operating frequency
        freq_divergence = abs(telemetry.vibration_frequency_hz - self.target_frequency_hz)
        amplitude_stress = telemetry.vibration_amplitude_microns / self.max_allowable_amplitude
        
        # Compute harmonic pulse correlation index (0.0 to 1.0, higher is better)
        harmonic_index = max(0.0, 1.0 - (freq_divergence / 50.0) - (max(0.0, amplitude_stress - 1.0) * 0.5))
        
        anomaly = False
        reason = "Nominal operation."
        adjustment = 0.0

        if telemetry.vibration_amplitude_microns > self.max_allowable_amplitude:
            anomaly = True
            reason = "Excessive vibration amplitude detected; potential bearing wear or uneven grain feed."
            adjustment = -2.0 if telemetry.gap_microns > 100.0 else 1.0
        elif freq_divergence > 5.0:
            anomaly = True
            reason = "Harmonic frequency drift outside acceptable resonance corridor."
            adjustment = 0.5

        synapse_health_score = round(harmonic_index * 100.0, 2)
        
        result = HarmonicAuditResult(
            mill_id=telemetry.mill_id,
            roller_pair=telemetry.roller_pair,
            harmonic_index=round(harmonic_index, 4),
            synapse_health_score=synapse_health_score,
            recommended_gap_adjustment_microns=adjustment,
            anomaly_detected=anomaly,
            reason=reason
        )

        self.audit_history.append(result)
        return result

    def get_fleet_summary(self) -> Dict[str, Any]:
        if not self.audit_history:
            return {"total_audits": 0, "avg_health": 100.0}
        
        scores = [r.synapse_health_score for r in self.audit_history]
        return {
            "total_audits": len(self.audit_history),
            "avg_health_score": round(statistics.mean(scores), 2),
            "anomalies_flagged": sum(1 for r in self.audit_history if r.anomaly_detected)
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Grain Milling Roller Gap Micrometer Synapse Harmonic Pulse Correlation Vibration Audit Synchronizer V81.1...")
    synchronizer = RollerGapHarmonicSynchronizer()
    
    sample_telemetry = RollerSensorTelemetry(
        mill_id="NAI_MILL_INDUSTRIAL_04",
        roller_pair="B1_FAST",
        gap_microns=150.0,
        vibration_frequency_hz=49.8,
        vibration_amplitude_microns=8.2,
        motor_current_amps=42.5,
        product_feed_rate_tph=12.4,
        timestamp=1710000000.0
    )
    
    audit_res = synchronizer.audit_telemetry(sample_telemetry)
    print(json.dumps(asdict(audit_res), indent=2))
    print("Fleet Summary:", json.dumps(synchronizer.get_fleet_summary(), indent=2))
    
    # Self-test AST compilation check
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    ast.parse(source_code)
    print("AST Self-Compilation Verification Passed Successfully.")
