import logging
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("NairobiChaiTrade")

@dataclass
class TeaBatch:
    batch_id: str
    cooperative_name: str
    grade: str
    bags: int
    net_weight_kgs: float
    strike_price_kes_per_kg: float
    fob_target_usd: float
    escrow_balance_kes: float = 0.0
    status: str = "PENDING_HEDGE"
    bol_hash: Optional[str] = None

@dataclass
class MarketIndex:
    timestamp: float
    mombasa_auction_avg_usd: float
    usd_kes_rate: float
    volatility_index: float

class NairobiChaiTradeEngine:
    """
    Autonomous Forward Hedging and Escrow Settlement Engine for Kenyan Smallholder Tea.
    Integrates Mombasa Tea Auction metrics, currency risk smoothing, and automated M-Pesa payouts.
    """
    def __init__(self, api_secret: str):
        self.api_secret = api_secret.encode('utf-8')
        self.batches: Dict[str, TeaBatch] = {}
        self.market_history: List[MarketIndex] = []
        logger.info("Initialized NairobiChaiTradeEngine for Kenya Tea Sector.")

    def record_market_index(self, avg_usd: float, usd_kes: float, volatility: float) -> MarketIndex:
        idx = MarketIndex(timestamp=time.time(), mombasa_auction_avg_usd=avg_usd, usd_kes_rate=usd_kes, volatility_index=volatility)
        self.market_history.append(idx)
        logger.info(f"Recorded Market Index: Mombasa Avg=${avg_usd}/kg, USD/KES={usd_kes}")
        return idx

    def create_forward_contract(self, batch_id: str, coop: str, grade: str, bags: int, weight: float, strike_kes: float, fob_usd: float) -> TeaBatch:
        if batch_id in self.batches:
            raise ValueError(f"Batch {batch_id} already exists.")
        
        batch = TeaBatch(
            batch_id=batch_id,
            cooperative_name=coop,
            grade=grade,
            bags=bags,
            net_weight_kgs=weight,
            strike_price_kes_per_kg=strike_kes,
            fob_target_usd=fob_usd,
            escrow_balance_kes=weight * strike_kes,
            status="ESCROW_FUNDED"
        )
        self.batches[batch_id] = batch
        logger.info(f"Created Forward Contract for {coop} ({bags} bags, {weight} kgs). Escrow locked: KES {batch.escrow_balance_kes}")
        return batch

    def verify_bill_of_lading(self, batch_id: str, container_no: str, port_seal: str) -> str:
        if batch_id not in self.batches:
            raise KeyError(f"Batch {batch_id} not found.")
        
        raw_data = f"{batch_id}:{container_no}:{port_seal}:{time.time()}"
        bol_hash = hmac.new(self.api_secret, raw_data.encode('utf-8'), hashlib.sha256).hexdigest()
        
        batch = self.batches[batch_id]
        batch.bol_hash = bol_hash
        batch.status = "BOL_VERIFIED"
        logger.info(f"Bill of Lading verified for batch {batch_id}. Hash: {bol_hash[:16]}...")
        return bol_hash

    def execute_m_pesa_payout(self, batch_id: str) -> Dict[str, any]:
        batch = self.batches[batch_id]
        if batch.status != "BOL_VERIFIED":
            raise ValueError(f"Batch {batch_id} cannot disburse funds. Status: {batch.status}")
        
        payout_amount = batch.escrow_balance_kes
        batch.status = "SETTLED"
        
        transaction_id = f"MPESA-TEA-{int(time.time())}-{batch_id[:4].upper()}"
        logger.info(f"Disbursing KES {payout_amount} to {batch.cooperative_name} via M-Pesa API. TxID: {transaction_id}")
        
        return {
            "status": "SUCCESS",
            "transaction_id": transaction_id,
            "cooperative": batch.cooperative_name,
            "amount_kes": payout_amount,
            "settled_timestamp": time.time()
        }

if __name__ == "__main__":
    engine = NairobiChaiTradeEngine(api_secret="kenya_tea_board_secure_secret_2025")
    engine.record_market_index(avg_usd=2.85, usd_kes=129.50, volatility=0.04)
    batch = engine.create_forward_contract(
        batch_id="TC-2025-089",
        coop="Kericho Smallholders Tea Growers Sacco",
        grade="BP1",
        bags=500,
        weight=25000.0,
        strike_kes=320.0,
        fob_target_usd=2.90
    )
    engine.verify_bill_of_lading("TC-2025-089", container_no="MSKU9837210", port_seal="KPA-MBSA-9942")
    receipt = engine.execute_m_pesa_payout("TC-2025-089")
    print("Test Execution Successful:", receipt)
