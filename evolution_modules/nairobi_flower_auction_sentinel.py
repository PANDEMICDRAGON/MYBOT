"""
Module: nairobi_flower_auction_sentinel.py
Description: Monitors floriculture cold-chain IoT telemetry from Naivasha greenhouses to JKIA cargo flights,
             and hedges currency exchange exposure (KES/EUR) for export settlements.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import os
import ast
import json
import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [FlowerSentinel]: %(message)s")
logger = logging.getLogger(__name__)

class FloricultureColdChainSentinel:
    """
    Tracks temperature and humidity thresholds for cut-flower exports and calculates
    instantaneous KES/EUR foreign exchange risk mitigation parameters.
    """
    def __init__(self, max_temp_celsius: float = 4.0, min_temp_celsius: float = 1.0):
        self.max_temp = max_temp_celsius
        self.min_temp = min_temp_celsius
        self.telemetry_logs: List[Dict[str, Any]] = []

    def ingest_sensor_packet(self, batch_id: str, temp: float, humidity: float, location: str) -> Dict[str, Any]:
        """Ingests IoT telemetry from transit containers."""
        status = "OPTIMAL"
        alert_triggered = False
        if temp > self.max_temp or temp < self.min_temp:
            status = "EXCURSION_RISK"
            alert_triggered = True
            logger.warning(f"[ALERT] Batch {batch_id} at {location} recorded impermissible temperature: {temp}C!")
        
        packet = {
            "batch_id": batch_id,
            "timestamp": time.time(),
            "temperature": temp,
            "humidity": humidity,
            "location": location,
            "status": status,
            "alert": alert_triggered
        }
        self.telemetry_logs.append(packet)
        return packet

    def calculate_hedge_requirement(self, export_value_eur: float, current_kes_eur_rate: float, volatility_index: float) -> Dict[str, Any]:
        """
        Calculates optimal forward cover requirements based on exchange rate and volatility.
        """
        hedged_ratio = 0.50
        if volatility_index > 0.15:
            hedged_ratio = 0.85
        elif volatility_index < 0.05:
            hedged_ratio = 0.25

        hedged_amount_eur = export_value_eur * hedged_ratio
        unhedged_amount_eur = export_value_eur - hedged_amount_eur
        estimated_kes_yield = (hedged_amount_eur * current_kes_eur_rate) + (unhedged_amount_eur * current_kes_eur_rate)

        return {
            "export_value_eur": export_value_eur,
            "kes_eur_rate": current_kes_eur_rate,
            "volatility_index": volatility_index,
            "recommended_hedge_ratio": hedged_ratio,
            "hedged_eur": hedged_amount_eur,
            "unhedged_eur": unhedged_amount_eur,
            "projected_kes_revenue": estimated_kes_yield
        }

if __name__ == "__main__":
    logger.info("Executing self-test harness for FloricultureColdChainSentinel...")
    sentinel = FloricultureColdChainSentinel()
    
    # Test telemetry ingestion
    pkt1 = sentinel.ingest_sensor_packet("NAI-ROSE-8821", 2.5, 88.5, "Naivasha Sorting Hub")
    pkt2 = sentinel.ingest_sensor_packet("NAI-ROSE-8822", 5.8, 91.0, "JKIA Cargo Terminal Alpha")
    
    assert pkt1["status"] == "OPTIMAL"
    assert pkt2["status"] == "EXCURSION_RISK"
    assert pkt2["alert"] is True

    # Test hedging calc
    hedge_rec = sentinel.calculate_hedge_requirement(50000.0, 142.50, 0.18)
    assert hedge_rec["recommended_hedge_ratio"] == 0.85
    
    logger.info("All FloricultureColdChainSentinel checks passed successfully.")
