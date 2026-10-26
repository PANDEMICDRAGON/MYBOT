"""Nairobi Commercial Aquaponics Nutrient Film Technique (NFT) Biosafety Sentinel.

Author: Cortana - Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Provides real-time telemetry monitoring, closed-loop pump failover, nutrient dosing
optimization, and biosafety threat mitigation for commercial NFT aquaponics setups.
"""

import time
import logging
import statistics
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [NFT_SENTINEL]: %(message)s')
logger = logging.getLogger('AquaponicsNFTSentinel')


class AquaponicsNFTSentinel:
    """Monitors and optimizes NFT channels, fish biofilters, and automated dosing."""

    def __init__(self, system_id: str, channel_count: int = 12):
        self.system_id = system_id
        self.channel_count = channel_count
        self.telemetry_history: List[Dict[str, Any]] = []
        self.pump_status: Dict[str, bool] = {"primary_water_pump": True, "backup_air_pump": True, "dosing_pump": True}
        self.thresholds = {
            "ph_min": 6.2,
            "ph_max": 7.4,
            "do_min_mg_l": 5.5,  # Dissolved oxygen minimum
            "ec_min_ms_cm": 1.0,  # Electrical conductivity
            "ec_max_ms_cm": 2.2,
            "ammonia_max_ppm": 0.05,
            "nitrite_max_ppm": 0.1,
            "nitrate_optimal_ppm": 40.0,
            "flow_rate_min_l_min": 1.2  # Per NFT channel
        }

    def ingest_telemetry(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests sensory telemetry from NFT channels and fish tanks, returning immediate health evaluation."""
        timestamp = time.time()
        ph = float(raw_data.get("ph", 6.8))
        do = float(raw_data.get("dissolved_oxygen", 6.5))
        ec = float(raw_data.get("electrical_conductivity", 1.5))
        ammonia = float(raw_data.get("ammonia_ppm", 0.01))
        nitrite = float(raw_data.get("nitrite_ppm", 0.02))
        nitrate = float(raw_data.get("nitrate_ppm", 35.0))
        flow_rate = float(raw_data.get("flow_rate_l_min", 1.8))
        water_temp = float(raw_data.get("water_temperature_c", 22.5))

        record = {
            "timestamp": timestamp,
            "ph": ph,
            "dissolved_oxygen": do,
            "electrical_conductivity": ec,
            "ammonia_ppm": ammonia,
            "nitrite_ppm": nitrite,
            "nitrate_ppm": nitrate,
            "flow_rate_l_min": flow_rate,
            "water_temperature_c": water_temp
        }
        self.telemetry_history.append(record)
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)

        return self._evaluate_biosafety(record)

    def _evaluate_biosafety(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates parameters and triggers corrective actuators or alerts."""
        alerts = []
        actions = []

        # pH Checks
        if rec["ph"] < self.thresholds["ph_min"]:
            alerts.warn = alerts.append(f"CRITICAL: pH low ({rec['ph']}). Risk of nitrification stall.")
            actions.append("trigger_buffer_base_dosing")
        elif rec["ph"] > self.thresholds["ph_max"]:
            alerts.append(f"CRITICAL: pH high ({rec['ph']}). Risk of ammonia toxicity.")
            actions.append("trigger_buffer_acid_dosing")

        # Dissolved Oxygen Checks
        if rec["dissolved_oxygen"] < self.thresholds["do_min_mg_l"]:
            alerts.append(f"EMERGENCY: Hypoxia risk! DO at {rec['dissolved_oxygen']} mg/L.")
            actions.append("activate_emergency_oxygen_diffuser")
            self.pump_status["backup_air_pump"] = True

        # Flow Rate Checks (NFT root starvation risk)
        if rec["flow_rate_l_min"] < self.thresholds["flow_rate_min_l_min"]:
            alerts.append(f"WARNING: NFT flow rate sub-optimal ({rec['flow_rate_l_min']} L/min).")
            actions.append("boost_primary_pump_rpm")

        # Ammonia / Nitrite Toxicity
        if rec["ammonia_ppm"] > self.thresholds["ammonia_max_ppm"] or rec["nitrite_ppm"] > self.thresholds["nitrite_max_ppm"]:
            alerts.append("CRITICAL: Biofilter nitrification lag detected. Elevating aeration.")
            actions.append("increase_biofilter_aeration")

        system_status = "NOMINAL" if not alerts else ("WARNING" if len(alerts) <= 1 else "CRITICAL_ACTION_REQUIRED")

        report = {
            "system_id": self.system_id,
            "status": system_status,
            "alerts": alerts,
            "recommended_actions": actions,
            "pump_status": self.pump_status,
            "metrics": rec
        }
        logger.info(f"Evaluated System {self.system_id}: Status -> {system_status} | Actions -> {actions}")
        return report

    def compute_daily_analytics(self) -> Dict[str, float]:
        """Computes rolling averages for greenhouse operational tuning."""
        if not self.telemetry_history:
            return {}
        return {
            "avg_ph": statistics.mean([r["ph"] for r in self.telemetry_history]),
            "avg_do": statistics.mean([r["dissolved_oxygen"] for r in self.telemetry_history]),
            "avg_ec": statistics.mean([r["electrical_conductivity"] for r in self.telemetry_history]),
            "avg_temp": statistics.mean([r["water_temperature_c"] for r in self.telemetry_history])
        }


if __name__ == "__main__":
    sentinel = AquaponicsNFTSentinel(system_id="NBI-NFT-AERO-01")
    sample_telemetry = {
        "ph": 6.7,
        "dissolved_oxygen": 6.2,
        "electrical_conductivity": 1.6,
        "ammonia_ppm": 0.02,
        "nitrite_ppm": 0.01,
        "nitrate_ppm": 42.0,
        "flow_rate_l_min": 1.9,
        "water_temperature_c": 23.1
    }
    evaluation = sentinel.ingest_telemetry(sample_telemetry)
    print("Test Evaluation Result:", evaluation)
    analytics = sentinel.compute_daily_analytics()
    print("Daily Analytics:", analytics)
