"""
Module: nairobi_rooftop_solar_exchange.py
Description: Decentralized P2P rooftop solar energy exchange, microgrid wheelage fee
             calculator, and automated settlement ledger tailored for Nairobi estates.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import ast
import json
import hashlib
import time
from typing import Dict, List, Optional, Any


class SolarNode:
    """Represents a solar prosumer or consumer node within a Nairobi estate microgrid."""

    def __init__(self, node_id: str, location: str, capacity_kwh: float, is_prosumer: bool):
        self.node_id = node_id
        self.location = location
        self.capacity_kwh = capacity_kwh
        self.is_prosumer = is_prosumer
        self.current_generation_kwh = 0.0
        self.current_consumption_kwh = 0.0
        self.credit_balance_kes = 0.0

    def update_metrics(self, generation: float, consumption: float) -> None:
        self.current_generation_kwh = max(0.0, generation)
        self.current_consumption_kwh = max(0.0, consumption)

    @property
    def net_surplus_kwh(self) -> float:
        return self.current_generation_kwh - self.current_consumption_kwh


class RooftopSolarExchangeEngine:
    """Manages P2P energy matching, dynamic wheelage calculation, and ledger settlement."""

    def __init__(self, base_tariff_kes_per_kwh: float = 24.50, wheelage_fee_pct: float = 0.03):
        self.base_tariff = base_tariff_kes_per_kwh
        self.wheelage_fee_pct = wheelage_fee_pct
        self.nodes: Dict[str, SolarNode] = {}
        self.ledger: List[Dict[str, Any]] = []

    def register_node(self, node_id: str, location: str, capacity_kwh: float, is_prosumer: bool) -> SolarNode:
        node = SolarNode(node_id, location, capacity_kwh, is_prosumer)
        self.nodes[node_id] = node
        return node

    def calculate_wheelage_fee(self, energy_kwh: float, distance_km: float) -> float:
        """Calculates local microgrid wheelage fee based on transmission distance."""
        base_cost = energy_kwh * self.base_tariff
        distance_factor = 1.0 + (distance_km * 0.02)
        return round(base_cost * self.wheelage_fee_pct * distance_factor, 2)

    def execute_p2p_clearing(self, estate_name: str) -> Dict[str, Any]:
        """Matches surplus producers with deficit consumers within the estate."""
        producers = [n for n in self.nodes.values() if n.net_surplus_kwh > 0]
        consumers = [n for n in self.nodes.values() if n.net_surplus_kwh < 0]

        transactions: List[Dict[str, Any]] = []
        total_traded_kwh = 0.0
        total_value_kes = 0.0

        for consumer in consumers:
            deficit = abs(consumer.net_surplus_kwh)
            for producer in producers:
                if producer.net_surplus_kwh <= 0 or deficit <= 0:
                    continue

                transfer_amt = min(deficit, producer.net_surplus_kwh)
                # P2P discount rate: 85% of standard KPLC tariff
                p2p_price_per_kwh = self.base_tariff * 0.85
                gross_cost = transfer_amt * p2p_price_per_kwh
                wheelage = self.calculate_wheelage_fee(transfer_amt, distance_km=1.5)
                total_cost = gross_cost + wheelage

                # Update local balances
                producer.current_generation_kwh -= transfer_amt
                consumer.current_consumption_kwh -= transfer_amt
                deficit -= transfer_amt

                producer.credit_balance_kes += gross_cost
                consumer.credit_balance_kes -= total_cost

                tx_record = {
                    "timestamp": time.time(),
                    "estate": estate_name,
                    "producer_id": producer.node_id,
                    "consumer_id": consumer.node_id,
                    "energy_kwh": round(transfer_amt, 3),
                    "gross_cost_kes": round(gross_cost, 2),
                    "wheelage_fee_kes": round(wheelage, 2),
                    "total_settlement_kes": round(total_cost, 2)
                }
                tx_hash = hashlib.sha256(json.dumps(tx_record, sort_keys=True).encode()).hexdigest()
                tx_record["tx_hash"] = tx_hash

                transactions.append(tx_record)
                self.ledger.append(tx_record)
                total_traded_kwh += transfer_amt
                total_value_kes += total_cost

        return {
            "estate": estate_name,
            "transactions_executed": len(transactions),
            "total_traded_kwh": round(total_traded_kwh, 3),
            "total_value_kes": round(total_value_kes, 2),
            "transactions": transactions
        }


if __name__ == "__main__":
    engine = RooftopSolarExchangeEngine()
    # Register nodes in Kilimani Estate
    p1 = engine.register_node("KILIMANI_SOLAR_01", "Argwings Kodhek Rd", 10.0, True)
    c1 = engine.register_node("KILIMANI_HOME_05", "Lenana Rd", 3.0, False)

    # Simulate generation and consumption
    p1.update_metrics(generation=8.5, consumption=1.2)  # Net surplus: 7.3 kWh
    c1.update_metrics(generation=0.5, consumption=4.5)  # Net deficit: 4.0 kWh

    clearing_result = engine.execute_p2p_clearing("Kilimani Microgrid")
    assert clearing_result["transactions_executed"] == 1
    print("Nairobi Rooftop Solar Exchange Test Passed Successfully.")
