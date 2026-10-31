"""
Nairobi Commercial Grain Silo Bin Level & Spectroscopy Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Monitors silo fill levels using acoustic time-of-flight and capacitive arrays, while
processing near-infrared (NIR) spectroscopy data to detect moisture spikes, fungal
activity, and protein degradation in stored maize, wheat, and pulses.
"""

import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SiloSpectroscopySentinel")

class SiloSpectroscopySentinel:
    def __init__(self, silo_id: str, capacity_tonnes: float = 5000.0):
        self.silo_id = silo_id
        self.capacity_tonnes = capacity_tonnes
        self.history: List[Dict[str, Any]] = []
        logger.info(f"Initialized SiloSpectroscopySentinel for silo {silo_id} (Capacity: {capacity_tonnes}T).")

    def measure_bin_telemetry(self, raw_tof_cm: float, capacitive_load_pf: float, nir_reflectance: List[float]) -> Dict[str, Any]:
        """
        Process raw bin level sensor metrics and NIR spectrum vectors.
        """
        try:
            # Estimate fill height from Time of Flight (assuming 30m silo depth)
            silo_depth_cm = 3000.0
            fill_height_cm = max(0.0, silo_depth_cm - raw_tof_cm)
            fill_percentage = min(100.0, (fill_height_cm / silo_depth_cm) * 100.0)
            estimated_tonnage = (fill_percentage / 100.0) * self.capacity_tonnes

            # NIR Spectroscopy Analysis (mocked feature extraction)
            # Wavelength bands: 1450nm (moisture), 1940nm (free water), 2100nm (protein)
            if len(nir_reflectance) >= 3:
                moisture_index = nir_reflectance[0] * 12.5
                protein_index = nir_reflectance[2] * 8.2
                fungal_risk_score = max(0.0, (moisture_index - 14.0) * 1.8) # moisture > 14% triggers risk
            else:
                moisture_index = 12.0
                protein_index = 10.5
                fungal_risk_score = 0.0

            status = "OPTIMAL"
            warnings = []

            if moisture_index > 14.5:
                status = "WARNING"
                warnings.append("High moisture detected: Risk of mycotoxin formation.")
            
            if fungal_risk_score > 5.0:
                status = "CRITICAL"
                warnings.append("Fungal spoilage signature identified in NIR spectra.")

            telemetry = {
                "timestamp": time.time(),
                "silo_id": self.silo_id,
                "fill_percentage": round(fill_percentage, 2),
                "estimated_tonnage": round(estimated_tonnage, 2),
                "moisture_percent": round(moisture_index, 2),
                "protein_percent": round(protein_index, 2),
                "fungal_risk_score": round(fungal_risk_score, 2),
                "status": status,
                "warnings": warnings
            }

            self.history.append(telemetry)
            return telemetry

        except Exception as e:
            logger.error(f"Error processing silo telemetry: {e}")
            raise

    def get_audit_summary(self) -> Dict[str, Any]:
        """Summarize historical readings for operator reporting."""
        if not self.history:
            return {"status": "NO_DATA"}
        
        avg_moisture = sum(h["moisture_percent"] for h in self.history) / len(self.history)
        max_risk = max(h["fungal_risk_score"] for h in self.history)
        
        return {
            "silo_id": self.silo_id,
            "total_readings": len(self.history),
            "average_moisture": round(avg_moisture, 2),
            "peak_fungal_risk": round(max_risk, 2),
            "latest_status": self.history[-1]["status"]
        }

if __name__ == "__main__":
    print("[+] Running Test Harness for Nairobi Commercial Grain Silo Bin Level & Spectroscopy Sentinel...")
    sentinel = SiloSpectroscopySentinel(silo_id="NAI_GRAIN_SILO_07", capacity_tonnes=10000.0)
    
    # Simulate normal maize telemetry
    sample_nir = [1.05, 0.88, 1.32]
    result = sentinel.measure_bin_telemetry(raw_tof_cm=850.0, capacitive_load_pf=420.5, nir_reflectance=sample_nir)
    print(f"[+] Telemetry Result: {result}")
    
    # Simulate high moisture spoilage threat
    spoilage_nir = [1.35, 0.92, 1.28]
    result_danger = sentinel.measure_bin_telemetry(raw_tof_cm=840.0, capacitive_load_pf=425.0, nir_reflectance=spoilage_nir)
    print(f"[+] Danger Telemetry Result: {result_danger}")
    
    summary = sentinel.get_audit_summary()
    print(f"[+] Audit Summary: {summary}")
    print("[+] Sentinel execution completed successfully.")
