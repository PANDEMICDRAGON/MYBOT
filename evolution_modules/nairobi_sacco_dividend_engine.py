"""
Module: nairobi_sacco_dividend_engine.py
Description: Automated dividend clearinghouse and sinking fund calculator for Nairobi Matatu SACCOs.
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SaccoDividendEngine")

@dataclass
class VehicleLedgerEntry:
    plate_number: str
    route_name: str
    daily_gross_ksh: float
    fuel_cost_ksh: float
    crew_wages_ksh: float
    maintenance_reserve_ksh: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class DividendDistributionReport:
    plate_number: str
    route_name: str
    net_operating_profit_ksh: float
    sacco_levy_ksh: float
    owner_dividend_ksh: float
    sinking_fund_allocation_ksh: float
    status: str
    timestamp: str

class SaccoDividendEngine:
    """
    Computes net distributable dividends for matatu owners and SACCO administrators in Nairobi,
    ensuring transparent deduction of operating expenses, levies, and long-term asset reserves.
    """
    def __init__(self, sacco_levy_percentage: float = 8.5, sinking_fund_percentage: float = 12.0):
        self.sacco_levy_percentage = sacco_levy_percentage
        self.sinking_fund_percentage = sinking_fund_percentage
        self._ledgers: List[VehicleLedgerEntry] = []

    def record_daily_operation(self, entry: VehicleLedgerEntry) -> None:
        if entry.daily_gross_ksh < 0:
            raise ValueError("Gross revenue cannot be negative.")
        self._ledgers.append(entry)
        logger.info(f"Recorded daily operations for matatu {entry.plate_number} on route {entry.route_name}.")

    def compute_dividend(self, plate_number: str) -> Optional[DividendDistributionReport]:
        vehicle_entries = [e for e in self._ledgers if e.plate_number == plate_number]
        if not vehicle_entries:
            logger.warning(f"No ledger entries found for plate {plate_number}")
            return None

        total_gross = sum(e.daily_gross_ksh for e in vehicle_entries)
        total_fuel = sum(e.fuel_cost_ksh for e in vehicle_entries)
        total_wages = sum(e.crew_wages_ksh for e in vehicle_entries)
        total_maintenance = sum(e.maintenance_reserve_ksh for e in vehicle_entries)

        net_operating_profit = total_gross - (total_fuel + total_wages + total_maintenance)
        if net_operating_profit < 0:
            net_operating_profit = 0.0

        sacco_levy = net_operating_profit * (self.sacco_levy_percentage / 100.0)
        sinking_allocation = net_operating_profit * (self.sinking_fund_percentage / 100.0)
        owner_dividend = net_operating_profit - (sacco_levy + sinking_allocation)

        report = DividendDistributionReport(
            plate_number=plate_number,
            route_name=vehicle_entries[-1].route_name,
            net_operating_profit_ksh=round(net_operating_profit, 2),
            sacco_levy_ksh=round(sacco_levy, 2),
            owner_dividend_ksh=round(owner_dividend, 2),
            sinking_fund_allocation_ksh=round(sinking_allocation, 2),
            status="SUCCESS",
            timestamp=datetime.utcnow().isoformat()
        )
        return report

if __name__ == "__main__":
    print("Initializing Nairobi Matatu SACCO Dividend Engine Test Harness...")
    engine = SaccoDividendEngine(sacco_levy_percentage=10.0, sinking_fund_percentage=15.0)
    
    entry1 = VehicleLedgerEntry(
        plate_number="KDA 456Z",
        route_name="Route 23 (Town - Buruburu)",
        daily_gross_ksh=14500.0,
        fuel_cost_ksh=4500.0,
        crew_wages_ksh=3000.0,
        maintenance_reserve_ksh=1500.0
    )
    
    engine.record_daily_operation(entry1)
    report = engine.compute_dividend("KDA 456Z")
    print(json.dumps(asdict(report), indent=2))
    print("Test Harness Complete. Module operational.")
