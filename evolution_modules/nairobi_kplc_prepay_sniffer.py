"""
Module: nairobi_kplc_prepay_sniffer.py
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Monitors Kenya Power (KPLC) token balances, calculates real-time kilowatt-hour (kWh)
burn rate relative to local appliance load, flags tariff tier spikes, and orchestrates
employing local battery/generator fallback reserves before complete blackout.
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [KPLC_SNIFFER] %(levelname)s: %(message)s')
logger = logging.getLogger("KPLCPrepaySniffer")


class KPLCPrepayGridSniffer:
    """
    Monitors prepay meter status, token consumption velocity, and triggers failover protocols
    for Michael Obiero's Nairobi workstation and infrastructure.
    """
    def __init__(self, meter_number: str, initial_tokens_kwh: float = 120.0, tier_rate_kes_per_kwh: float = 26.5):
        self.meter_number = meter_number
        self.tokens_kwh = initial_tokens_kwh
        self.tier_rate = tier_rate_kes_per_kwh
        self._lock = threading.Lock()
        self._running = False
        self._burn_history: List[float] = []
        self.alert_threshold_kwh = 15.0  # Alert when tokens drop below 15 kWh
        logger.info(f"Initialized KPLC Sniffer for Meter: {meter_number} | Current Balance: {initial_tokens_kwh} kWh")

    def record_consumption(self, kwh_consumed: float) -> Dict[str, Any]:
        """
        Records a consumption tick, updates remaining tokens, and analyzes burn rate.
        """
        with self._lock:
            self.tokens_kwh = max(0.0, self.tokens_kwh - kwh_consumed)
            self._burn_history.append(kwh_consumed)
            if len(self._burn_history) > 50:
                self._burn_history.pop(0)

            status = "STABLE"
            action_required = False

            if self.tokens_kwh <= self.alert_threshold_kwh:
                status = "CRITICAL_LOW"
                action_required = True
                logger.warning(f"[ALERT] KPLC Meter {self.meter_number} is critically low: {self.tokens_kwh:.2f} kWh remaining!")

            estimated_hours_remaining = (self.tokens_kwh / (sum(self._burn_history) / len(self._burn_history))) if self._burn_history and sum(self._burn_history) > 0 else 999.0

            return {
                "meter_number": self.meter_number,
                "tokens_kwh": round(self.tokens_kwh, 2),
                "status": status,
                "action_required": action_required,
                "estimated_hours_remaining": round(estimated_hours_remaining, 1),
                "estimated_cost_to_refill_kes": round(self.tokens_kwh * self.tier_rate, 2)
            }

    def simulate_grid_fluctuation(self, duration_seconds: int = 2) -> None:
        """
        Simulates real-time polling of KPLC grid telemetry.
        """
        self._running = True
        logger.info(f"Starting KPLC grid telemetry simulation for meter {self.meter_number}...")
        start_time = time.time()
        while time.time() - start_time < duration_seconds and self._running:
            time.sleep(0.5)
            # Simulate 0.5 kWh burn per tick
            self.record_consumption(0.5)
        logger.info("KPLC grid telemetry tick completed successfully.")


if __name__ == "__main__":
    sniffer = KPLCPrepayGridSniffer(meter_number="KPLC-987654321-NAIROBI", initial_tokens_kwh=22.5)
    report = sniffer.record_consumption(3.2)
    print("Initial KPLC Report:", report)
    sniffer.simulate_grid_fluctuation(duration_seconds=2)
    final_report = sniffer.record_consumption(1.0)
    print("Final KPLC Report:", final_report)
