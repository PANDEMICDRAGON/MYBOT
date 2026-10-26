"""
Nairobi Expressway & Major Toll Road Automated RFID/M-Pesa Toll Pass & Cost Minimizer
Designed for Michael Obiero's seamless transit across Nairobi and Kitengela infrastructure.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NairobiTollAutomator")

@dataclass
class TollPlaza:
    name: str
    latitude: float
    longitude: float
    standard_fee_kes: float
    expressway_segment: str

@dataclass
class VehiclePassAccount:
    account_id: str
    operator_name: str
    current_balance_kes: float
    auto_top_up_threshold_kes: float
    top_up_amount_kes: float

class NairobiTollAutomator:
    """
    Manages toll balances, auto-replenishes via M-Pesa API hooks upon geo-fencing entry,
    and calculates time-vs-cost efficiency for Nairobi transport corridors.
    """
    def __init__(self, account: VehiclePassAccount):
        self.account = account
        self.plazas = [
            TollPlaza("Mlolongo (JKIA) Plaza", -1.3533, 36.9555, 300.0, "Southern Segment"),
            TollPlaza("SGR / Syokimau Plaza", -1.3321, 36.9122, 250.0, "Mid Segment"),
            TollPlaza("Nyayo Stadium Plaza", -1.3033, 36.8222, 400.0, "Northern Terminus"),
            TollPlaza("Westlands / Museum Hill Plaza", -1.2655, 36.8022, 500.0, "Western Extension")
        ]
        logger.info(f"Initialized NairobiTollAutomator for account: {self.account.account_id}")

    def check_proximity_and_replenish(self, current_lat: float, current_lon: float) -> Dict[str, Any]:
        """
        Checks if vehicle is approaching any known toll plaza. If balance is below
        threshold, simulates triggering an M-Pesa STK push top-up.
        """
        triggered_action = {"status": "monitoring", "top_up_triggered": False, "nearest_plaza": None}
        
        for plaza in self.plazas:
            # Simple Euclidean check for simulation (In production, use Haversine)
            distance_approx = ((current_lat - plaza.latitude)**2 + (current_lon - plaza.longitude)**2)**0.5
            if distance_approx < 0.02: # Within proximity zone
                triggered_action["nearest_plaza"] = plaza.name
                logger.info(f"Approaching toll plaza: {plaza.name} (Fee: KES {plaza.standard_fee_kes})")
                
                if self.account.current_balance_kes < self.account.auto_top_up_threshold_kes:
                    top_up_success = self._simulate_mpesa_stk_top_up(self.account.top_up_amount_kes)
                    if top_up_success:
                        self.account.current_balance_kes += self.account.top_up_amount_kes
                        triggered_action["top_up_triggered"] = True
                        triggered_action["new_balance"] = self.account.current_balance_kes
                        logger.info(f"Auto-replenished KES {self.account.top_up_amount_kes} via M-Pesa.")
                break
                
        return triggered_action

    def evaluate_route_economics(self, distance_km: float, traffic_delay_minutes: float) -> Dict[str, Any]:
        """
        Calculates whether taking the expressway is economically and temporally optimal
        compared to avoiding tolls (e.g., Mombasa Road normal lanes).
        """
        # Assume normal fuel cost per km is KES 18, value of operator time is KES 500/hour
        value_of_time_per_min = 500.0 / 60.0
        normal_transit_time_mins = (distance_km / 40.0) * 60.0 + traffic_delay_minutes
        expressway_transit_time_mins = (distance_km / 80.0) * 60.0 # Faster average speed
        
        time_saved_mins = normal_transit_time_mins - expressway_transit_time_mins
        time_value_saved_kes = time_saved_mins * value_of_time_per_min
        
        average_toll_cost = 350.0
        net_benefit_kes = time_value_saved_kes - average_toll_cost
        
        recommendation = "EXPRESSWAY" if net_benefit_kes > 0 else "STANDARD_ROAD"
        
        return {
            "recommendation": recommendation,
            "time_saved_minutes": round(time_saved_mins, 1),
            "time_value_saved_kes": round(time_value_saved_kes, 2),
            "toll_cost_kes": average_toll_cost,
            "net_economic_benefit_kes": round(net_benefit_kes, 2)
        }

    def _simulate_mpesa_stk_top_up(self, amount: float) -> bool:
        """Simulates secure M-Pesa STK push for toll pass replenishment."""
        logger.info(f"Initiating M-Pesa STK Push for KES {amount} to Toll Pass Account...")
        return True

if __name__ == "__main__":
    pass_account = VehiclePassAccount(
        account_id="EXPRESS-KE-98421",
        operator_name="Michael Obiero",
        current_balance_kes=150.0,
        auto_top_up_threshold_kes=300.0,
        top_up_amount_kes=1000.0
    )
    
    automator = NairobiTollAutomator(pass_account)
    # Test approaching Mlolongo plaza
    action = automator.check_proximity_and_replenish(-1.3530, 36.9550)
    print("Proximity Action Result:", json.dumps(action, indent=2))
    
    # Test route economics for a 25km trip with 35 min traffic delay
    economics = automator.evaluate_route_economics(25.0, 35.0)
    print("Route Economics Result:", json.dumps(economics, indent=2))
