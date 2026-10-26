"""
Nairobi JamboJet & Regional Domestic Airline Dynamic Seat Inventory & Price Surge Automator
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [JamboJetSentinel] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DomesticFlightSentinel:
    """
    Monitors regional domestic flight routes out of Nairobi (JKIA / Wilson), tracking
    seat availability, price velocity, and triggering automated booking locks when fares
    dip below historical volatility thresholds.
    """

    SUPPORTED_ROUTES = [
        {"origin": "NBO", "destination": "MBA", "name": "Nairobi to Mombasa"},
        {"origin": "NBO", "destination": "KIS", "name": "Nairobi to Kisumu"},
        {"origin": "NBO", "destination": "EDL", "name": "Nairobi to Eldoret"},
        {"origin": "NBO", "destination": "UKA", "name": "Nairobi to Ukunda/Diani"}
    ]

    def __init__(self, budget_ceiling_kes: float = 8500.0):
        self.budget_ceiling_kes = budget_ceiling_kes
        self.tracked_inventories: Dict[str, List[Dict[str, Any]]] = {}
        self.watchlist: List[Dict[str, Any]] = []
        logger.info("DomesticFlightSentinel initialized with KES %.2f budget ceiling.", self.budget_ceiling_kes)

    def add_to_watchlist(self, origin: str, destination: str, target_date: str) -> str:
        """Add a specific route and travel date to the automated surveillance watchlist."""
        route_key = f"{origin.upper()}-{destination.upper()}-{target_date}"
        watch_item = {
            "id": hashlib.sha256(route_key.encode()).hexdigest()[:12],
            "origin": origin.upper(),
            "destination": destination.upper(),
            "target_date": target_date,
            "added_at": datetime.utcnow().isoformat(),
            "status": "ACTIVE"
        }
        self.watchlist.append(watch_item)
        logger.info("Added watchlist item for route %s on %s", route_key, target_date)
        return watch_item["id"]

    def simulate_price_polling(self, item_id: str, current_fare_kes: float, seats_remaining: int) -> Dict[str, Any]:
        """
        Simulates polling airline APIs (JamboJet, Skyward, Fly540) for live inventory.
        Evaluates if fare is optimal for instant booking execution.
        """
        item = next((w for w in self.watchlist if w["id"] == item_id), None)
        if not item:
            raise ValueError(f"Watchlist item {item_id} not found.")

        timestamp = datetime.utcnow().isoformat()
        record = {
            "timestamp": timestamp,
            "fare_kes": current_fare_kes,
            "seats_remaining": seats_remaining,
            "surge_detected": current_fare_kes > self.budget_ceiling_kes
        }

        if item_id not in self.tracked_inventories:
            self.tracked_inventories[item_id] = []
        self.tracked_inventories[item_id].append(record)

        decision = "HOLD"
        if current_fare_kes <= self.budget_ceiling_kes and seats_remaining <= 5:
            decision = "EXECUTE_URGENT_BOOKING"
        elif current_fare_kes <= self.budget_ceiling_kes:
            decision = "EXECUTE_BOOKING"
        elif current_fare_kes > self.budget_ceiling_kes * 1.25:
            decision = "SURGE_WARNING_WAIT"

        logger.info(
            "Polled Route %s-%s (%s): KES %.2f | Seats: %d | Decision: %s",
            item["origin"], item["destination"], item["target_date"],
            current_fare_kes, seats_remaining, decision
        )

        return {
            "watchlist_id": item_id,
            "fare_kes": current_fare_kes,
            "seats_remaining": seats_remaining,
            "decision": decision,
            "timestamp": timestamp
        }

    def get_market_analytics(self, item_id: str) -> Dict[str, Any]:
        """Computes rolling price averages and volatility metrics."""
        history = self.tracked_inventories.get(item_id, [])
        if not history:
            return {"status": "no_data"}

        fares = [h["fare_kes"] for h in history]
        return {
            "total_polls": len(history),
            "min_fare": min(fares),
            "max_fare": max(fares),
            "average_fare": sum(fares) / len(fares),
            "latest_fare": fares[-1]
        }


if __name__ == "__main__":
    print("=== TESTING NAIROBI JAMBOJET & REGIONAL FLIGHT SENTINEL ===")
    sentinel = DomesticFlightSentinel(budget_ceiling_kes=7500.0)
    
    # Register upcoming flight to Mombasa (MBA)
    flight_date = (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d")
    watch_id = sentinel.add_to_watchlist("NBO", "MBA", flight_date)
    
    # Simulate polling ticks
    res1 = sentinel.simulate_price_polling(watch_id, 8200.0, 12)
    res2 = sentinel.simulate_price_polling(watch_id, 7100.0, 4)
    
    analytics = sentinel.get_market_analytics(watch_id)
    print("Market Analytics:", json.dumps(analytics, indent=2))
    print("Test Execution Complete.")
