"""
Nairobi Artisanal Leather Tannery & Effluent Biosafety Sentinel
Designed to monitor chemical parameters, heavy metal run-off (Cr VI), pH levels, 
and curing temperature logs for artisanal leather processors in Nairobi.
"""

import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("LeatherTannerySentinel")

class TanneryBatch:
    def __init__(self, batch_id: str, artisan_group: str, hides_count: int, target_cure_method: str):
        self.batch_id = batch_id
        self.artisan_group = artisan_group
        self.hides_count = hides_count
        self.target_cure_method = target_cure_method
        self.created_at = time.time()
        self.status = "INITIATED"
        self.log_history: List[Dict[str, Any]] = []

class NairobiLeatherTannerySentinel:
    """
    Monitors tanning baths, effluent discharge compliance (NEMA standards),
    and chromium VI safety thresholds for Nairobi artisanal tanneries.
    """
    
    MAX_CHROMIUM_VI_PPM = 0.5  # NEMA effluent discharge limit for Cr(VI)
    IDEAL_PH_RANGE = (8.0, 10.5) # Liming stage pH threshold

    def __init__(self):
        self.active_batches: Dict[str, TanneryBatch] = {}
        logger.info("NairobiLeatherTannerySentinel initialized for environmental & production compliance.")

    def register_batch(self, batch_id: str, artisan_group: str, hides_count: int, target_cure_method: str) -> TanneryBatch:
        batch = TanneryBatch(batch_id, artisan_group, hides_count, target_cure_method)
        self.active_batches[batch_id] = batch
        logger.info(f"Registered tannery batch {batch_id} for group {artisan_group} ({hides_count} hides).")
        return batch

    def audit_tannery_metrics(self, batch_id: str, ph_level: float, chromium_vi_ppm: float, bath_temp_c: float) -> Dict[str, Any]:
        if batch_id not in self.active_batches:
            raise ValueError(f"Batch {batch_id} not found in active registry.")
        
        batch = self.active_batches[batch_id]
        alerts = []
        compliant = True

        # Check pH
        if not (self.IDEAL_PH_RANGE[0] <= ph_level <= self.IDEAL_PH_RANGE[1]):
            compliant = False
            alerts.append(f"pH out of range: {ph_level} (Expected {self.IDEAL_PH_RANGE})")

        # Check Chromium VI effluent toxicity
        if chromium_vi_ppm > self.MAX_CHROMIUM_VI_PPM:
            compliant = False
            alerts.append(f"CRITICAL: Chromium(VI) level {chromium_vi_ppm} ppm exceeds NEMA limit ({self.MAX_CHROMIUM_VI_PPM} ppm).")

        # Temperature check
        if bath_temp_c > 35.0:
            compliant = False
            alerts.append(f"Bath temperature too high: {bath_temp_c}°C (Risk of collagen damage).")

        status = "COMPLIANT" if compliant else "ACTION_REQUIRED"
        batch.status = status

        audit_entry = {
            "timestamp": time.time(),
            "ph_level": ph_level,
            "chromium_vi_ppm": chromium_vi_ppm,
            "bath_temp_c": bath_temp_c,
            "status": status,
            "alerts": alerts
        }
        batch.log_history.append(audit_entry)

        logger.info(f"Audited batch {batch_id}: Status -> {status} | Alerts -> {len(alerts)}")
        return audit_entry

if __name__ == "__main__":
    sentinel = NairobiLeatherTannerySentinel()
    b_id = "KARIOKOR-LT-092"
    sentinel.register_batch(b_id, "Kariokor Artisans Cooperative", 45, "Vegetable & Chrome Tanning")
    
    # Test normal audit
    result_ok = sentinel.audit_tannery_metrics(b_id, ph_level=8.5, chromium_vi_ppm=0.2, bath_temp_c=26.5)
    assert result_ok["status"] == "COMPLIANT"
    
    # Test toxic effluent alert
    result_alert = sentinel.audit_tannery_metrics(b_id, ph_level=11.2, chromium_vi_ppm=1.4, bath_temp_c=38.0)
    assert result_alert["status"] == "ACTION_REQUIRED"
    assert len(result_alert["alerts"]) == 3
    print("NairobiLeatherTannerySentinel module verified successfully.")
