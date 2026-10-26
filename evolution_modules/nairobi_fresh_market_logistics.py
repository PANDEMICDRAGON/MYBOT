"""
Nairobi Fresh Produce Supply Chain Cold-Chain Integrity & Logistics Optimizer
Designed for Michael Obiero in Nairobi, Kenya.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [FRESH_LOGISTICS] [%(levelname)s]: %(message)s')
logger = logging.getLogger("FreshMarketLogistics")

class ColdChainIntegrityAuditor:
    """Monitors IoT temperature/humidity logs from transit crates, flagging spoilage risks."""
    
    MAX_SAFE_TEMP_C = 8.0
    CRITICAL_TEMP_C = 14.0

    def audit_shipment(self, shipment_id: str, produce_type: str, temp_readings: List[float]) -> Dict[str, Any]:
        logger.info(f"Auditing cold-chain for {produce_type} shipment {shipment_id} with {len(temp_readings)} telemetry points.")
        if not temp_readings:
            return {"shipment_id": shipment_id, "status": "UNKNOWN", "risk_score": 1.0}

        max_temp = max(temp_readings)
        avg_temp = sum(temp_readings) / len(temp_readings)
        breaches = sum(1 for t in temp_readings if t > self.MAX_SAFE_TEMP_C)
        critical_breaches = sum(1 for t in temp_readings if t > self.CRITICAL_TEMP_C)

        risk_score = min(1.0, (breaches / len(temp_readings)) * 0.5 + (critical_breaches * 0.5))
        
        status = "OPTIMAL"
        if risk_score > 0.7:
            status = "SPOILED_HIGH_RISK"
        elif risk_score > 0.3:
            status = "WARNING_DEGRADED"

        return {
            "shipment_id": shipment_id,
            "produce_type": produce_type,
            "max_temp": max_temp,
            "avg_temp": avg_temp,
            "breach_count": breaches,
            "risk_score": round(risk_score, 2),
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class NairobiMarketLogisticsRouter:
    """Optimizes delivery drop sequences across Nairobi markets (Wakulima, Gikomba, City Market, Westlands)."""

    MARKET_NODES = {
        "Wakulima": {"lat": -1.2891, "lon": 36.8219},
        "Gikomba": {"lat": -1.2833, "lon": 36.8417},
        "City_Market": {"lat": -1.2825, "lon": 36.8214},
        "Westlands": {"lat": -1.2656, "lon": 36.8028},
        "Kawangware": {"lat": -1.2921, "lon": 36.7562}
    }

    def optimize_route(self, start_hub: str, destination_markets: List[str]) -> List[str]:
        logger.info(f"Optimizing multi-drop route starting from {start_hub} to markets: {destination_markets}")
        # Greedy nearest neighbor route computation for lightweight edge execution
        valid_destinations = [m for m in destination_markets if m in self.MARKET_NODES]
        if start_hub not in self.MARKET_NODES or not valid_destinations:
            return destination_markets

        current_loc = start_hub
        unvisited = list(valid_destinations)
        route = []

        while unvisited:
            # Find nearest unvisited
            curr_coords = self.MARKET_NODES[current_loc]
            next_market = min(
                unvisited,
                key=lambda m: ((self.MARKET_NODES[m]["lat"] - curr_coords["lat"])**2 + (self.MARKET_NODES[m]["lon"] - curr_coords["lon"])**2)
            )
            route.append(next_market)
            unvisited.remove(next_market)
            current_loc = next_market

        return route

class FreshMarketLogisticsEngine:
    """Unified orchestrator for cold-chain audits and Nairobi market distribution."""

    def __init__(self):
        self.auditor = ColdChainIntegrityAuditor()
        self.router = NairobiMarketLogisticsRouter()

    def execute_dispatch_plan(self, shipment_id: str, produce_type: str, start_hub: str, markets: List[str], temperatures: List[float]) -> Dict[str, Any]:
        audit_res = self.auditor.audit_shipment(shipment_id, produce_type, temperatures)
        optimal_route = self.router.optimize_route(start_hub, markets)
        
        return {
            "dispatch_id": shipment_id,
            "cold_chain_audit": audit_res,
            "recommended_routing": optimal_route,
            "operator": "Michael Obiero",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    print("[TEST HARNESS] Initializing Nairobi Fresh Market Logistics Engine...")
    engine = FreshMarketLogisticsEngine()
    sample_temps = [4.2, 5.0, 7.5, 11.2, 13.5, 6.0]
    plan = engine.execute_dispatch_plan(
        shipment_id="SHP-KIAMBU-099",
        produce_type="Fresh Tomatoes & Sukuma Wiki",
        start_hub="Wakulima",
        markets=["Gikomba", "Westlands", "City_Market", "Kawangware"],
        temperatures=sample_temps
    )
    print(json.dumps(plan, indent=2))
    print("[TEST HARNESS] Execution successful.")
