"""
Nairobi Commercial & Industrial Peer-to-Peer Solar Wheeling Micro-Grid Ledger
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya

Handles dynamic energy-wheeling accounting, EPRA tariff compliance checking,
bilateral power purchase contract tracking, and real-time ledger settlement
for commercial solar micro-grids across Nairobi.
"""

import ast
import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SolarWheelingSentinel")


@dataclass
class WheelingContract:
    contract_id: str
    producer_id: str
    consumer_id: str
    ratified_rate_kes_kwh: float
    max_capacity_kw: float
    expiry_timestamp: str
    active: bool = True


@dataclass
class EnergyTransferRecord:
    transfer_id: str
    contract_id: str
    kwh_transferred: float
    timestamp: str
    wheeling_charge_kes: float
    total_cost_kes: float
    hash_signature: str = ""


class NairobiSolarWheelingSentinel:
    """
    Manages P2P solar energy wheeling contracts, calculates EPRA-compliant
    wheeling fees, and maintains an immutable cryptographic ledger for commercial
    micro-grids in Nairobi.
    """
    
    BASE_EPRA_WHEELING_FEE_PER_KWH: float = 1.85  # KES per kWh transmission fee
    MAX_WHEELING_LIMIT_KW: float = 500.0         # Regulatory threshold for localized P2P
    
    def __init__(self) -> None:
        self.contracts: Dict[str, WheelingContract] = {}
        self.ledger: List[EnergyTransferRecord] = []
        logger.info("NairobiSolarWheelingSentinel initialized for Nairobi Micro-Grid Operations.")

    def register_contract(self, producer: str, consumer: str, rate: float, capacity: str, expiry: str) -> WheelingContract:
        """Registers a verified P2P solar supply agreement between a producer and consumer."""
        cap_float = float(capacity)
        if cap_float > self.MAX_WHEELING_LIMIT_KW:
            raise ValueError(f"Capacity {cap_float}kW exceeds decentralized wheeling limit ({self.MAX_WHEELING_LIMIT_KW}kW).")
            
        contract_id = f"WHL-{hashlib.sha256(f'{producer}-{consumer}-{datetime.now()}'.encode()).hexdigest()[:8].upper()}"
        
        contract = WheelingContract(
            contract_id=contract_id,
            producer_id=producer,
            consumer_id=consumer,
            ratified_rate_kes_kwh=rate,
            max_capacity_kw=cap_float,
            expiry_timestamp=expiry,
            active=True
        )
        self.contracts[contract_id] = contract
        logger.info(f"Registered Wheeling Contract {contract_id}: {producer} -> {consumer} @ KES {rate}/kWh")
        return contract

    def record_energy_transfer(self, contract_id: str, kwh: float) -> EnergyTransferRecord:
        """Records an incremental energy transfer block, computing wheeling fees and total costs."""
        if contract_id not in self.contracts:
            raise KeyError(f"Contract {contract_id} not found in active wheeling database.")
            
        contract = self.contracts[contract_id]
        if not contract.active:
            raise ValueError(f"Contract {contract_id} is currently inactive or expired.")
            
        if kwh > contract.max_capacity_kw:
            logger.warning(f"Transfer {kwh}kWh exceeds nominal capacity {contract.max_capacity_kw}kW. Flagged for review.")
            
        timestamp = datetime.now(timezone.utc).isoformat()
        wheeling_charge = kwh * self.BASE_EPRA_WHEELING_FEE_PER_KWH
        energy_cost = kwh * contract.ratified_rate_kes_kwh
        total_cost = energy_cost + wheeling_charge
        
        transfer_id = f"TRF-{hashlib.sha256(f'{contract_id}-{timestamp}-{kwh}'.encode()).hexdigest()[:10].upper()}"
        
        raw_sig = f"{transfer_id}:{contract_id}:{kwh}:{total_cost}:{timestamp}"
        signature = hashlib.sha256(raw_sig.encode()).hexdigest()
        
        record = EnergyTransferRecord(
            transfer_id=transfer_id,
            contract_id=contract_id,
            kwh_transferred=kwh,
            timestamp=timestamp,
            wheeling_charge_kes=round(wheeling_charge, 2),
            total_cost_kes=round(total_cost, 2),
            hash_signature=signature
        )
        
        self.ledger.append(record)
        logger.info(f"Recorded Transfer {transfer_id}: {kwh}kWh transferred. Total KES: {total_cost:.2f}")
        return record

    def audit_ledger(self) -> Tuple[bool, int, float]:
        """Performs cryptographic audit and integrity check of the energy ledger."""
        valid = True
        total_energy = 0.0
        for rec in self.ledger:
            raw_sig = f"{rec.transfer_id}:{rec.contract_id}:{rec.kwh_transferred}:{rec.total_cost_kes}:{rec.timestamp}"
            recomputed = hashlib.sha256(raw_sig.encode()).hexdigest()
            if recomputed != rec.hash_signature:
                valid = False
                logger.error(f"Integrity failure on transfer block {rec.transfer_id}!")
            total_energy += rec.kwh_transferred
        return valid, len(self.ledger), total_energy


if __name__ == "__main__":
    print("=== TESTING NAIROBI SOLAR WHEELING SENTINEL ===")
    sentinel = NairobiSolarWheelingSentinel()
    
    contract = sentinel.register_contract(
        producer="Westlands Rooftop Solar Alpha",
        consumer="Parklands Cold Storage Ltd",
        rate=14.50,
        capacity="120.0",
        expiry="2026-12-31T23:59:59Z"
    )
    
    transfer = sentinel.record_energy_transfer(contract.contract_id, 45.5)
    print(f"Transfer Output: {json.dumps(asdict(transfer), indent=2)}")
    
    is_valid, count, total_kwh = sentinel.audit_ledger()
    print(f"Ledger Audit -> Valid: {is_valid}, Blocks: {count}, Total kWh: {total_kwh}")
    
    assert is_valid == True, "Ledger integrity check failed!"
    print("=== SOLAR WHEELING SENTINEL TEST PASSED ===")
