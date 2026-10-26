"""
Nairobi Commercial Laundry & Water Recycling Biosafety Sentinel
Autonomous Evolutionary Architecture Module v1

Monitors commercial laundry washwater parameters, chemical dosing, filtration health,
and UV disinfection efficacy for urban water recirculation systems.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LaundrySentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger("NairobiCommercialLaundrySentinel")

class CommercialLaundrySentinel:
    """
    Monitors, evaluates, and regulates commercial laundry greywater reclamation
    units to ensure safe reuse or compliant municipal discharge.
    """
    
    def __init__(self, facility_id: str, target_capacity_liters: float = 10000.0):
        self.facility_id = facility_id
        self.target_capacity_liters = target_capacity_liters
        self.total_processed_liters = 0.0
        self.recycled_liters = 0.0
        self.alert_log: List[str] = []
        logger.info(f"Initialized CommercialLaundrySentinel for facility {facility_id} (Capacity: {target_capacity_liters}L)")

    def evaluate_washwater_batch(self, batch_id: str, turbidity_ntu: float, 
                                ph_level: float, cod_mg_l: float, 
                                residual_chlorine_ppm: float) -> Dict[str, Any]:
        """
        Evaluates incoming greywater parameters against NEMA effluent discharge
        and internal membrane bioreactor (MBR) tolerance thresholds.
        """
        status = "APPROVED_FOR_RECYCLE"
        reasons = []
        
        # Turbidity check (NTU)
        if turbidity_ntu > 5.0:
            reasons.append(f"High turbidity ({turbidity_ntu} NTU). Requires coagulant dosing.")
            status = "REQUIRES_PRETREATMENT"
            
        # pH check
        if not (6.5 <= ph_level <= 8.5):
            reasons.append(f"pH out of range ({ph_level}). Acid/base neutralization required.")
            status = "REMEDIATION_REQUIRED"
            
        # Chemical Oxygen Demand (COD) check
        if cod_mg_l > 50.0:
            reasons.append(f"Elevated COD ({cod_mg_l} mg/L). Extended aeration needed.")
            status = "REQUIRES_PRETREATMENT"
            
        # Residual Chlorine check
        if residual_chlorine_ppm < 0.2:
            reasons.append(f"Low residual chlorine ({residual_chlorine_ppm} ppm). UV/Chlorine boost required.")
            if status == "APPROVED_FOR_RECYCLE":
                status = "DISINFECTION_BOOST"

        evaluation = {
            "batch_id": batch_id,
            "timestamp": time.time(),
            "status": status,
            "metrics": {
                "turbidity_ntu": turbidity_ntu,
                "ph_level": ph_level,
                "cod_mg_l": cod_mg_l,
                "residual_chlorine_ppm": residual_chlorine_ppm
            },
            "actions_required": reasons
        }
        
        if status != "APPROVED_FOR_RECYCLE":
            self.alert_log.append(f"Batch {batch_id} flagged: {reasons}")
            logger.warning(f"Water batch {batch_id} status: {status}. Reasons: {reasons}")
        else:
            logger.info(f"Water batch {batch_id} successfully cleared for ultrafiltration and recycling.")
            
        return evaluation

    def process_filtration_cycle(self, batch_id: str, volume_liters: float, success: bool) -> None:
        """Tracks throughput and recycling yield."""
        self.total_processed_liters += volume_liters
        if success:
            self.recycled_liters += volume_liters
            logger.info(f"Successfully recycled {volume_liters}L from batch {batch_id}.")
        else:
            logger.error(f"Filtration cycle failed for batch {batch_id}. Volume diverted to sewer line.")

    def get_audit_summary(self) -> Dict[str, Any]:
        """Returns operational water recovery efficiency."""
        efficiency = (self.recycled_liters / self.total_processed_liters * 100.0) if self.total_processed_liters > 0 else 0.0
        return {
            "facility_id": self.facility_id,
            "total_processed_liters": self.total_processed_liters,
            "recycled_liters": self.recycled_liters,
            "recovery_efficiency_percent": round(efficiency, 2),
            "total_alerts": len(self.alert_log)
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for CommercialLaundrySentinel...")
    sentinel = CommercialLaundrySentinel(facility_id="NAI_LAUNDRY_01", target_capacity_liters=15000.0)
    
    eval_res = sentinel.evaluate_washwater_batch(
        batch_id="BATCH-2023-11A",
        turbidity_ntu=3.2,
        ph_level=7.2,
        cod_mg_l=35.0,
        residual_chlorine_ppm=0.5
    )
    assert eval_res["status"] == "APPROVED_FOR_RECYCLE"
    
    sentinel.process_filtration_cycle("BATCH-2023-11A", 2500.0, True)
    summary = sentinel.get_audit_summary()
    assert summary["recycled_liters"] == 2500.0
    logger.info("Commercial Laundry Sentinel self-test passed successfully.")
