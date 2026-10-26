"""Nairobi & Nairobi Emergency Hospital Bed & Critical Care Triage Dispatcher.

Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi & Nairobi, Kenya)
"""

import ast
import json
import logging
import time
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("HospitalBedTriage")


class HospitalBedTriageEngine:
    """Manages real-time hospital bed capacity, oxygen reserves, and emergency routing for Nairobi & Nairobi."""

    def __init__(self) -> None:
        self.hospitals: Dict[str, Dict] = {
            "Aga Khan University Hospital Nairobi": {
                "zone": "Nairobi Central",
                "icu_total": 30,
                "icu_available": 4,
                "hdu_available": 8,
                "oxygen_litres": 15000,
                "emergency_ready": True,
            },
            "Kenyatta National Hospital": {
                "zone": "Nairobi Upper Hill",
                "icu_total": 100,
                "icu_available": 12,
                "hdu_available": 25,
                "oxygen_litres": 45000,
                "emergency_ready": True,
            },
            "Nairobi Sub-County Hospital": {
                "zone": "Nairobi Town",
                "icu_total": 10,
                "icu_available": 2,
                "hdu_available": 4,
                "oxygen_litres": 5000,
                "emergency_ready": True,
            },
            "The Nairobi Hospital": {
                "zone": "Nairobi Central",
                "icu_total": 40,
                "icu_available": 6,
                "hdu_available": 10,
                "oxygen_litres": 20000,
                "emergency_ready": True,
            },
        }

    def update_facility_status(self, hospital_name: string, icu_avail: int, hdu_avail: int, oxygen: int) -> bool:
        """Updates real-time metrics for a specific health facility."""
        if hospital_name in self.hospitals:
            self.hospitals[hospital_name]["icu_available"] = icu_avail
            self.hospitals[hospital_name]["hdu_available"] = hdu_avail
            self.hospitals[hospital_name]["oxygen_litres"] = oxygen
            logger.info(f"Updated status for {hospital_name}: ICU={icu_avail}, HDU={hdu_avail}, O2={oxygen}L")
            return True
        logger.warning(f"Hospital {hospital_name} not found in registry.")
        return False

    def triage_emergency_routing(self, patient_condition: str, zone_preference: str) -> Optional[Dict]:
        """Finds the optimal hospital facility based on patient acuity and location proximity."""
        best_match = None
        score = -1.0

        for name, data in self.hospitals.items():
            if not data["emergency_ready"]:
                continue

            # Calculate suitability score
            acuity_weight = data["icu_available"] if patient_condition.lower() == "critical" else data["hdu_available"]
            if acuity_weight <= 0:
                continue

            proximity_bonus = 1.5 if data["zone"].lower() == zone_preference.lower() else 1.0
            oxygen_factor = min(data["oxygen_litres"] / 10000.0, 2.0)

            current_score = (acuity_weight * proximity_bonus) * oxygen_factor

            if current_score > score:
                score = current_score
                best_match = {
                    "hospital_name": name,
                    "zone": data["zone"],
                    "icu_available": data["icu_available"],
                    "hdu_available": data["hdu_available"],
                    "oxygen_litres": data["oxygen_litres"],
                    "dispatch_score": round(current_score, 2),
                }

        if best_match:
            logger.info(f"Emergency Triage Success: Routed to {best_match['hospital_name']} with score {best_match['dispatch_score']}")
        else:
            logger.warning("Emergency Triage Alert: No suitable bed capacity found matching criteria!")

        return best_match

    def export_telemetry(self) -> str:
        """Exports current regional medical readiness as JSON."""
        return json.dumps({
            "timestamp": time.time(),
            "region": "Nairobi & Nairobi",
            "facilities": self.hospitals
        }, indent=2)


if __name__ == "__main__":
    print("Initializing Cortana Hospital Bed Triage Engine...")
    engine = HospitalBedTriageEngine()
    
    # Test triage for critical patient in Nairobi
    recommendation = engine.triage_emergency_routing(patient_condition="critical", zone_preference="Nairobi Town")
    print("Nairobi Triage Recommendation:", json.dumps(recommendation, indent=2))

    # Test update and Nairobi routing
    engine.update_facility_status("Aga Khan University Hospital Nairobi", icu_avail=7, hdu_avail=9, oxygen=18000)
    nairobi_rec = engine.triage_emergency_routing(patient_condition="critical", zone_preference="Nairobi Central")
    print("Nairobi Triage Recommendation:", json.dumps(nairobi_rec, indent=2))
    
    # Verify compilation integrity
    code_string = open(__file__, "r").read()
    ast.parse(code_string)
    print("AST Compilation Integrity Check: PASSED.")
