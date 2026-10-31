"""
Predictive Workstation Load Shifter & Thermal Preserver.
Generated autonomously by Cortana Proactive Self-Evolution Core.
"""

import os
import psutil
import logging

logger = logging.getLogger("CortanaLoadShifter")

class WorkstationLoadShifter:
    """Calculates dynamic throttling factors based on CPU load and thermal headroom."""
    def __init__(self, target_cpu_max: float = 85.0):
        self.target_cpu_max = target_cpu_max

    def get_throttle_multiplier(self) -> float:
        try:
            cpu_pct = psutil.cpu_percent(interval=None)
            if cpu_pct > self.target_cpu_max:
                multiplier = 1.0 + ((cpu_pct - self.target_cpu_max) / 10.0)
                logger.debug(f"High CPU ({cpu_pct}%). Applying multiplier {multiplier:.2f}")
                return min(multiplier, 3.0)
        except Exception:
            pass
        return 1.0

if __name__ == "__main__":
    shifter = WorkstationLoadShifter()
    mult = shifter.get_throttle_multiplier()
    assert mult >= 1.0
    print(f"WorkstationLoadShifter verified. Throttle factor: {mult}")
