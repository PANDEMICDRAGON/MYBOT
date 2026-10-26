"""
Module: nairobi_power_token_sentinel.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Kitengela & Nairobi, Kenya)
Description: Predicts KPLC prepaid token depletion, correlates grid stability with local microclimate/solar status, and manages automated emergency top-up alerts.
"""

import time
import logging
import json
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [PowerTokenSentinel]: %(message)s')

class PowerTokenSentinel:
    """
    Monitors, forecasts, and manages prepaid KPLC smart meter tokens for residences in Kitengela and Nairobi.
    """
    def __init__(self, meter_number: str, initial_tokens_kwh: float, burn_rate_kwh_per_hour: float):
        self.meter_number = meter_number
        self.tokens_kwh = initial_tokens_kwh
        self.burn_rate = burn_rate_kwh_per_hour
        self.last_sync_timestamp = time.time()
        self.alert_threshold_kwh = 15.0  # Alert if tokens drop below 15 kWh (~24 hours remaining)

    def update_consumption(self, elapsed_hours: float, solar_offset_kwh: float = 0.0) -> float:
        """
        Updates remaining token count factoring in solar offset.
        """
        net_burn = max(0.0, (self.burn_rate * elapsed_hours) - solar_offset_kwh)
        self.tokens_kwh = max(0.0, self.tokens_kwh - net_burn)
        self.last_sync_timestamp = time.time()
        logging.info(f"Meter {self.meter_number}: Updated tokens -> {self.tokens_kwh:.2f} kWh remaining.")
        return self.tokens_kwh

    def predict_depletion_hours(self) -> float:
        """
        Calculates exact hours until complete blackout based on current burn rate.
        """
        if self.burn_rate <= 0:
            return float('inf')
        return self.tokens_kwh / self.burn_rate

    def evaluate_status(self) -> Dict[str, Any]:
        """
        Evaluates token health and returns actionable emergency triggers for Michael Obiero.
        """
        hours_left = self.predict_depletion_hours()
        critical_state = self.tokens_kwh <= self.alert_threshold_kwh

        status = {
            "meter_number": self.meter_number,
            "tokens_kwh": round(self.tokens_kwh, 2),
            "hours_until_blackout": round(hours_left, 2),
            "critical_alert": critical_state,
            "recommended_action": "INITIATE_MPESA_KPLC_STK" if critical_state else "NORMAL_OPERATION"
        }

        if critical_state:
            logging.warning(f"CRITICAL KPLC TOKEN WARNING! Meter {self.meter_number} has ~{hours_left:.1f} hours left!")
        else:
            logging.info(f"Power token status nominal. ~{hours_left:.1f} hours remaining.")

        return status

if __name__ == "__main__":
    print("[+] Initializing Nairobi Power Token Sentinel Test Harness...")
    sentinel = PowerTokenSentinel(meter_number="01928374650", initial_tokens_kwh=22.5, burn_rate_kwh_per_hour=0.8)
    
    # Simulate 12 hours passing with minor solar offset
    sentinel.update_consumption(elapsed_hours=12.0, solar_offset_kwh=3.5)
    report = sentinel.evaluate_status()
    print(json.dumps(report, indent=2))
