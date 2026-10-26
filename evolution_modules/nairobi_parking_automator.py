"""
Module: nairobi_parking_automator.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Kitengela & Nairobi)
Description: Autonomous Nairobi County & Kajiado County parking fee calculator,
             e-Citizen ticket generation scheduler, M-Pesa toll integration stub,
             and clamp-prevention countdown sentinel.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [PARKING_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger("NairobiParkingAutomator")

class NairobiParkingAutomator:
    """Manages municipal parking zones, fee schedules, and automated STK payment triggers for Nairobi and Kitengela."""

    ZONE_FEES = {
        "NAIROBI_CBD": 200.0,
        "NAIROBI_ZONED_ANNEX": 100.0,
        "KITENGELA_MUNICIPAL": 50.0,
        "OUTER_COUNTY_ZONE": 40.0
    }

    def __init__(self, vehicle_reg: str, default_zone: str = "NAIROBI_CBD") -> None:
        self.vehicle_reg = vehicle_reg.upper()
        self.current_zone = default_zone
        self.active_ticket: Optional[Dict[str, Any]] = None
        logger.info(f"Initialized Parking Automator for Vehicle [{self.vehicle_reg}] in Zone [{self.current_zone}]")

    def calculate_fee(self, zone: str, duration_hours: int = 1) -> float:
        """Calculates parking fees based on municipal tariff structures."""
        rate = self.ZONE_FEES.get(zone, 100.0)
        total = rate * max(1, duration_hours)
        logger.info(f"Calculated fee for {zone}: KES {total} for {duration_hours} hour(s).")
        return total

    def acquire_parking_ticket(self, phone_number: str, duration_hours: int = 1) -> Dict[str, Any]:
        """Simulates e-Citizen / County API handshake and M-Pesa STK push for parking."""
        fee = self.calculate_fee(self.current_zone, duration_hours)
        
        ticket_id = f"NBI-PRK-{int(time.time())}-{self.vehicle_reg}"
        expiry_time = datetime.now() + timedelta(hours=duration_hours)

        self.active_ticket = {
            "ticket_id": ticket_id,
            "vehicle_reg": self.vehicle_reg,
            "zone": self.current_zone,
            "fee_paid_kes": fee,
            "phone_number": phone_number,
            "issued_at": datetime.now().isoformat(),
            "expires_at": expiry_time.isoformat(),
            "status": "ACTIVE"
        }

        logger.info(f"SUCCESS: Parking ticket {ticket_id} acquired for {self.vehicle_reg}. Valid until {expiry_time.strftime('%H:%M:%S')}.")
        return self.active_ticket

    def check_ticket_status(self) -> Dict[str, Any]:
        """Monitors active ticket time-to-live and flags impending clamp risk."""
        if not self.active_ticket:
            return {"status": "NO_ACTIVE_TICKET", "risk": "HIGH_CLAMP_WARNING"}

        expiry = datetime.fromisoformat(self.active_ticket["expires_at"])
        remaining_seconds = (expiry - datetime.now()).total_seconds()

        if remaining_seconds <= 0:
            self.active_ticket["status"] = "EXPIRED"
            logger.warning(f"WARNING: Parking ticket for {self.vehicle_reg} has EXPIRED! Clamp risk imminent!")
            return {"status": "EXPIRED", "risk": "CRITICAL_CLAMP_RISK", "ticket": self.active_ticket}
        
        minutes_left = int(remaining_seconds // 60)
        logger.info(f"Ticket {self.active_ticket['ticket_id']} valid. Remaining time: {minutes_left} minutes.")
        return {
            "status": "VALID",
            "minutes_remaining": minutes_left,
            "risk": "LOW" if minutes_left > 15 else "MODERATE_RENEWAL_RECOMMENDED"
        }

if __name__ == "__main__":
    logger.info("Executing NairobiParkingAutomator self-test sequence...")
    automator = NairobiParkingAutomator(vehicle_reg="KDD 456Z", default_zone="NAIROBI_CBD")
    ticket = automator.acquire_parking_ticket(phone_number="254712345678", duration_hours=2)
    print(json.dumps(ticket, indent=2))
    status = automator.check_ticket_status()
    print(json.dumps(status, indent=2))
