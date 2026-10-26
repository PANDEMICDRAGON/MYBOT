"""Nairobi Expressway RFID & ANPR Toll Pass Automated Top-Up and Fleet Balance Sentinel."""

import logging
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("NairobiExpresswaySentinel")

@dataclass
class TollTransaction:
    station_id: str
    timestamp: float
    amount_kes: float
    entry_gate: str
    exit_gate: str
    vehicle_reg: str

@dataclass
class TollAccount:
    account_id: str
    vehicle_reg: str
    rfid_tag: str
    balance_kes: float
    threshold_kes: float
    replenish_amount_kes: float
    auto_topup_enabled: bool = True
    transactions: List[TollTransaction] = field(default_factory=list)

class ExpresswayTollOptimizer:
    """Manages Nairobi Expressway toll balances, auto-topup triggers, and transit analytics."""
    
    STATIONS = {
        "STN_01": "Mlolongo",
        "STN_02": "SGR",
        "STN_03": "JKIA",
        "STN_04": "Imara Daima",
        "STN_05": "Eastern Bypass",
        "STN_06": "Capital Centre",
        "STN_07": "Haile Selassie",
        "STN_08": "Museum Hill",
        "STN_09": "Westlands"
    }

    def __init__(self) -> None:
        self.accounts: Dict[str, TollAccount] = {}
        logger.log(logging.INFO, "ExpresswayTollOptimizer initialized for Nairobi infrastructure.")

    def register_account(self, account_id: str, vehicle_reg: str, rfid_tag: str, initial_balance: float, threshold: float = 300.0, replenish_amt: float = 1000.0) -> TollAccount:
        account = TollAccount(
            account_id=account_id,
            vehicle_reg=vehicle_reg,
            rfid_tag=rfid_tag,
            balance_kes=initial_balance,
            threshold_kes=threshold,
            replenish_amount_kes=replenish_amt
        )
        self.accounts[account_id] = account
        logger.info(f"Registered toll account {account_id} for vehicle {vehicle_reg} with balance KES {initial_balance}")
        return account

    def simulate_transit(self, account_id: str, station_id: str, entry_gate: str, exit_gate: str, cost: float) -> bool:
        if account_id not in self.accounts:
            logger.error(f"Account {account_id} not found.")
            return False

        acc = self.accounts[account_id]
        if acc.balance_kes < cost:
            logger.warning(f"Insufficient balance for {acc.vehicle_reg} at {self.STATIONS.get(station_id, station_id)}. Balance: KES {acc.balance_kes}, Required: KES {cost}")
            if acc.auto_topup_enabled:
                self._trigger_mpesa_topup(acc, cost)
            else:
                return False

        acc.balance_kes -= cost
        tx = TollTransaction(
            station_id=station_id,
            timestamp=time.time(),
            amount_kes=cost,
            entry_gate=entry_gate,
            exit_gate=exit_gate,
            vehicle_reg=acc.vehicle_reg
        )
        acc.transactions.append(tx)
        logger.info(f"Transit approved: {acc.vehicle_reg} passed {self.STATIONS.get(station_id, station_id)}. Deducted KES {cost}. New balance: KES {acc.balance_kes}")

        # Check threshold for replenishment
        if acc.balance_kes <= acc.threshold_kes and acc.auto_topup_enabled:
            self._trigger_mpesa_topup(acc)

        return True

    def _trigger_mpesa_topup(self, acc: TollAccount, target_min: float = 0.0) -> None:
        topup = max(acc.replenish_amount_kes, (target_min - acc.balance_kes) + acc.replenish_amount_kes)
        acc.balance_kes += topup
        logger.info(f"[M-Pesa STK Push] Auto-replenished KES {topup} for account {acc.account_id} ({acc.vehicle_reg}). Updated balance: KES {acc.balance_kes}")

    def get_account_summary(self, account_id: str) -> Optional[Dict]:
        if account_id not in self.accounts:
            return None
        acc = self.accounts[account_id]
        total_spent = sum(t.amount_kes for t in acc.transactions)
        return {
            "account_id": acc.account_id,
            "vehicle_reg": acc.vehicle_reg,
            "current_balance_kes": acc.balance_kes,
            "total_trips": len(acc.transactions),
            "total_spent_kes": total_spent
        }

if __name__ == "__main__":
    print("--- Executing Nairobi Expressway Toll Optimizer Test Harness ---")
    optimizer = ExpresswayTollOptimizer()
    acc = optimizer.register_account(
        account_id="ACC-MO-001",
        vehicle_reg="KDA 888Z",
        rfid_tag="RFID-NBI-99821",
        initial_balance=500.0,
        threshold=250.0,
        replenish_amt=1500.0
    )

    # Simulate transit from Mlolongo to Westlands
    optimizer.simulate_transit("ACC-MO-001", "STN_01", "Mlolongo Entry", "JKIA Exit", 220.0)
    optimizer.simulate_transit(
        account_id="ACC-MO-001",
        station_id="STN_09",
        entry_gate="JKIA Entry",
        exit_gate="Westlands Exit",
        cost=360.0
    )

    summary = optimizer.get_account_summary("ACC-MO-001")
    print(f"Account Summary: {summary}")
    print("--- Nairobi Expressway Toll Optimizer Test Completed Successfully ---")
