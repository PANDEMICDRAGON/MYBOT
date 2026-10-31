import time
import math
import random
import logging
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger("FlourSifterVibrationSentinel")

class FlourSifterVibrationSentinel:
    """
    Monitors multi-axis vibration signatures, eccentric drive frequencies, and thermal loads
    on commercial flour sifter decks in Nairobi industrial milling units to detect bearing wear,
    unbalanced sieve frames, and structural fatigue before catastrophic failure occurs.
    """
    def __init__(self, sifter_id: str, rated_rpm: float = 520.0, warning_threshold_g: float = 3.5):
        self.sifter_id = sifter_id
        self.rated_rpm = rated_rpm
        self.warning_threshold_g = warning_threshold_g
        self.telemetry_history: List[Dict[str, Any]] = []
        self.anomaly_count = 0
        self.status = "NORMAL"

    def ingest_telemetry(self, axial_vibe_g: float, radial_vibe_g: float, bearing_temp_c: float, current_draw_a: float) -> Dict[str, Any]:
        """
        Ingests real-time vibration metrics in G-force, bearing temperature, and motor current draw.
        Calculates total harmonic vibration composite index.
        """
        composite_vibe = math.sqrt(axial_vibe_g**2 + radial_vibe_g**2)
        
        timestamp = time.time()
        record = {
            "timestamp": timestamp,
            "sifter_id": self.sifter_id,
            "axial_vibe_g": axial_vibe_g,
            "radial_vibe_g": radial_vibe_g,
            "composite_vibe": composite_vibe,
            "bearing_temp_c": bearing_temp_c,
            "current_draw_a": current_draw_a
        }
        self.telemetry_history.append(record);
        if len(self.telemetry_history) > 1000:
            self.telemetry_history.pop(0)
            
        assessment = self._evaluate_health(record)
        return assessment

    def _evaluate_health(self, record: Dict[str, Any]) -> Dict[str, Any]:
        comp = record["composite_vibe"]
        temp = record["bearing_temp_c"]
        current = record["current_draw_a"]
        
        recommendation = "All sifter decks operating within nominal harmonic parameters."
        self.status = "NORMAL"

        if comp > self.warning_threshold_g or temp > 75.0:
            self.status = "CRITICAL_ATTENTION_REQUIRED"
            self.anomaly_count += 1
            recommendation = (
                f"ALERT: Sifter {self.sifter_id} exhibiting excessive vibration ({comp:.2f}G) "
                f"or bearing temperature ({temp:.1f}C). Inspect eccentric drive counterweights, "
                f"rubber suspension bushings, and spherical roller bearings immediately."
            )
            logger.warning(recommendation)
        elif comp > (self.warning_threshold_g * 0.75) or temp > 68.0:
            self.status = "WARNING"
            recommendation = (
                f"CAUTION: Sifter {self.sifter_id} vibration rising ({comp:.2f}G). "
                f"Schedule preventative lubrication and sieve cloth tension check during next shift change."
            )
            logger.info(recommendation)

        return {
            "sifter_id": self.sifter_id,
            "status": self.status,
            "composite_vibe_g": comp,
            "bearing_temp_c": temp,
            "current_draw_a": current,
            "anomaly_count": self.anomaly_count,
            "recommendation": recommendation
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "sifter_id": self.sifter_id,
            "rated_rpm": self.rated_rpm,
            "total_records": len(self.telemetry_history),
            "lifetime_anomalies": self.anomaly_count,
            "current_status": self.status
        }

if __name__ == "__main__":
    print("Initializing Nairobi Commercial Flour Sifter & Vibration Harmonization Sentinel...")
    sentinel = FlourSifterVibrationSentinel(sifter_id="SIFTER-IND-AREA-04")
    
    # Simulate nominal run
    res1 = sentinel.ingest_telemetry(axial_vibe_g=1.2, radial_vibe_g=1.5, bearing_temp_c=58.2, current_draw_a=24.5)
    print(f"Test Run 1 Status: {res1['status']} | Composite Vibe: {res1['composite_vibe_g']:.2f}G")
    
    # Simulate anomalous out-of-balance sieve deck
    res2 = sentinel.ingest_telemetry(axial_vibe_g=3.8, radial_vibe_g=4.1, bearing_temp_c=78.9, current_draw_a=32.1)
    print(f"Test Run 2 Status: {res2['status']} | Recommendation: {res2['recommendation']}")
    
    print("Diagnostics:", sentinel.get_diagnostics())
    print("Flour Sifter Vibration Sentinel operational verification complete.")
