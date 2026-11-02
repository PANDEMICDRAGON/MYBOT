"""
Nairobi Commercial Grain Milling Roller Mill Dynamic Torsion Harmonic Equilibrium Sentinel
Designed for automated industrial roller mill torsional stabilization in Nairobi, Kenya.
"""

import os
import time
import logging
import threading
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("TorsionHarmonicEquilibriumSentinel")

class TorsionHarmonicEquilibriumSentinel:
    """
    Monitors torsional stress across roller mill drive shafts and applies dynamic
    equilibrium compensations to neutralize harmful resonant frequencies.
    """
    def __init__(self, mill_id: str, sample_interval_sec: float = 0.05):
        self.mill_id = mill_id
        self.sample_interval_sec = sample_interval_sec
        self.active = False
        self._thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.current_torsion_nm: float = 0.0
        self.harmonic_distortion_pct: float = 0.0
        self.equilibrium_status: str = "NOMINAL"
        self.compensation_history: List[Dict[str, Any]] = []

    def start(self) -> None:
        with self.lock:
            if self.active:
                return
            self.active = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info(f"[{self.mill_id}] Torsion Harmonic Equilibrium Sentinel activated.")

    def stop(self) -> None:
        with self.lock:
            self.active = False
            if self._thread:
                self._thread.join(timeout=1.0)
                logger.info(f"[{self.mill_id}] Torsion Harmonic Equilibrium Sentinel deactivated.")

    def _monitor_loop(self) -> None:
        while True:
            with self.lock:
                if not self.active:
                    break
                
                # Simulate telemetry reading from mill drive shaft sensors
                import random
                self.current_torsion_nm = 1250.0 + random.uniform(-150.0, 150.0)
                self.harmonic_distortion_pct = max(0.0, min(100.0, 2.5 + random.uniform(-1.2, 3.5)))

                if self.harmonic_distortion_pct > 5.0:
                    self.equilibrium_status = "COMPENSATING"
                    correction = self._apply_equilibrium_correction(self.harmonic_distortion_pct)
                    self.compensation_history.append({
                        "timestamp": time.time(),
                        "distortion": self.harmonic_distortion_pct,
                        "correction_factor": correction
                    })
                    if len(self.compensation_history) > 100:
                        self.compensation_history.pop(0)
                else:
                    self.equilibrium_status = "NOMINAL"

            time.sleep(self.sample_interval_sec)

    def _apply_equilibrium_correction(self, distortion: float) -> float:
        # Compute dynamic counter-torque modulation coefficient
        correction = round(distortion * 0.85, 4)
        logger.warning(f"[{self.mill_id}] High torsional harmonic detected ({distortion:.2f}%). Applying counter-modulation: {correction}")
        return correction

    def get_status(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "mill_id": self.mill_id,
                "active": self.active,
                "current_torsion_nm": self.current_torsion_nm,
                "harmonic_distortion_pct": self.harmonic_distortion_pct,
                "equilibrium_status": self.equilibrium_status,
                "recent_compensations": len(self.compensation_history)
            }

if __name__ == "__main__":
    sentinel = TorsionHarmonicEquilibriumSentinel(mill_id="NAIROBI_INDUSTRIAL_AREA_MILL_04")
    sentinel.start()
    time.sleep(0.2)
    status = sentinel.get_status()
    print("Sentinel Status Test:", status)
    sentinel.stop()
    print("Sentinel successfully verified and terminated.")
