"""
Nairobi Municipal Water Treatment Coagulant Dosage Harmonic Sentinel

Audits and synchronizes polyaluminum chloride (PAC) dosing rates against real-time
turbidity, pH, and flow rate telemetry at Nairobi water treatment intakes (e.g., Ngethu and Sasumua),
protecting municipal water purity and optimizing chemical usage.
"""

import time
import math
import statistics
from typing import Dict, List, Any, Optional


class WaterTreatmentDosageSentinel:
    """
    Monitors water intake telemetry and computes optimal coagulant dosing adjustments
    using a harmonic feedback loop designed for Kenyan municipal water infrastructure.
    """

    def __init__(self, target_turbidity_nephelometric: float = 1.0):
        self.target_turbidity = target_turbidity_nephelometric
        self.telemetry_history: List[Dict[str, float]] = []
        self.dosing_adjustments: List[Dict[str, Any]] = []

    def ingest_telemetry(self, flow_rate_m3_h: float, raw_turbidity_ntu: float, ph_level: float) -> Dict[str, Any]:
        """
        Ingests raw sensor telemetry from the water treatment intake.
        """
        record = {
            "timestamp": time.time(),
            "flow_rate": flow_rate_m3_h,
            "turbidity": raw_turbidity_ntu,
            "ph": ph_level
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
        
        return self._compute_optimal_dosage(record)

    def _compute_optimal_dosage(self, current: Dict[str, float]) -> Dict[str, Any]:
        """
        Computes optimal PAC dosage (mg/L) based on turbidity deviation and pH correction factor.
        """
        turbidity_delta = current["turbidity"] - self.target_turbidity
        
        # Base coagulant dosage coefficient (mg/L per NTU)
        base_coefficient = 3.5
        
        # pH adjustment penalty (optimal coagulation pH is typically 6.8 - 7.5)
        ph = current["ph"]
        ph_correction = 1.0
        if ph < 6.5 or ph > 8.0:
            ph_correction = 1.25

        raw_dose = max(2.0, (current["turbidity"] * base_coefficient) * ph_correction)
        total_pac_kg_h = (raw_dose * current["flow_rate"]) / 1000.0

        status = "OPTIMAL"
        if current["turbidity"] > 25.0:
            status = "HIGH_TURBIDITY_SURGE_DETECTED"
        elif ph < 6.0 or ph > 8.5:
            status = "PH_OUT_OF_BOUNDS_WARNING"

        adjustment = {
            "timestamp": current["timestamp"],
            "recommended_pac_mg_l": round(raw_dose, 2),
            "total_pac_feed_kg_h": round(total_pac_kg_h, 3),
            "status": status,
            "turbidity_delta": round(turbidity_delta, 2)
        }
        self.dosing_adjustments.append(adjustment)
        return adjustment

    def generate_audit_report(self) -> Dict[str, Any]:
        """
        Generates summary statistics of water treatment dosing performance.
        """
        if not self.dosing_adjustments:
            return {"status": "NO_DATA"}

        doses = [d["recommended_pac_mg_l"] for d in self.dosing_adjustments]
        flows = [t["flow_rate"] for t in self.telemetry_history]

        return {
            "records_analyzed": len(self.dosing_adjustments),
            "mean_pac_dosage_mg_l": round(statistics.mean(doses), 2),
            "peak_pac_dosage_mg_l": round(max(doses), 2),
            "mean_flow_rate_m3_h": round(statistics.mean(flows), 2) if flows else 0.0,
            "sentinel_status": "ACTIVE_MONITORING"
        }


if __name__ == "__main__":
    sentinel = WaterTreatmentDosageSentinel(target_turbidity_nephelometric=1.2)
    # Simulate morning raw water surge from Aberdare catchment
    telemetry_sample = sentinel.ingest_telemetry(flow_rate_m3_h=4500.0, raw_turbidity_ntu=32.5, ph_level=7.1)
    print("Test Telemetry Ingest Result:", telemetry_sample)
    print("Audit Report:", sentinel.generate_audit_report())
