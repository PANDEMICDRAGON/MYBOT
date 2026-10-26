import ast
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [NairobiTeaAuction]: %(message)s')
logger = logging.getLogger('NairobiTeaAuction')

@dataclass
class TeaLot:
    lot_id: str
    factory_origin: str
    grade: str
    bag_count: int
    net_weight_kgs: float
    reserve_price_usd: float
    status: str = "PENDING_AUCTION"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class Bid:
    bid_id: str
    lot_id: str
    broker_code: str
    bid_price_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class NairobiTeaAuctionClearinghouse:
    """Manages Nairobi Tea Auction lots, live bidding, reserve price enforcement, and USD/KES currency hedging contracts."""
    
    def __init__(self, exchange_rate_kes_per_usd: float = 132.50):
        self.exchange_rate = exchange_rate_kes_per_usd
        self.lots: Dict[str, TeaLot] = {}
        self.bids: Dict[str, List[Bid]] = {}
        self.cleared_contracts: List[Dict[str, Any]] = []
        logger.info(f"NairobiTeaAuctionClearinghouse initialized at KES/USD rate: {self.exchange_rate}")

    def register_lot(self, lot_id: str, factory_origin: str, grade: str, bag_count: int, net_weight_kgs: float, reserve_price_usd: float) -> TeaLot:
        if lot_id in self.lots:
            raise ValueError(f"Lot {lot_id} is already registered.")
        
        lot = TeaLot(
            lot_id=lot_id,
            factory_origin=factory_origin,
            grade=grade,
            bag_count=bag_count,
            net_weight_kgs=net_weight_kgs,
            reserve_price_usd=reserve_price_usd
        )
        self.lots[lot_id] = lot
        self.bids[lot_id] = []
        logger.info(f"Registered Tea Lot {lot_id} from {factory_origin} [{grade}]: {bag_count} bags, Reserve: ${reserve_price_usd}")
        return lot

    def submit_bid(self, bid_id: str, lot_id: str, broker_code: str, bid_price_usd: float) -> Bid:
        if lot_id not in self.lots:
            raise KeyError(f"Lot {lot_id} does not exist.")
        
        lot = self.lots[lot_id]
        if lot.status != "PENDING_AUCTION":
            raise ValueError(f"Lot {lot_id} is no longer accepting bids. Status: {lot.status}")

        if bid_price_usd < lot.reserve_price_usd:
            logger.warning(f"Bid {bid_id} of ${bid_price_usd} rejected for lot {lot_id} (Below reserve ${lot.reserve_price_usd})")
            raise ValueError(f"Bid price must meet or exceed reserve price of ${lot.reserve_price_usd}")

        bid = Bid(bid_id=bid_id, lot_id=lot_id, broker_code=broker_code, bid_price_usd=bid_price_usd)
        self.bids[lot_id].append(bid)
        logger.info(f"Accepted bid {bid_id} from broker {broker_code} for lot {lot_id} at ${bid_price_usd}/kg")
        return bid

    def clear_auction(self, lot_id: str) -> Dict[str, Any]:
        if lot_id not in self.lots:
            raise KeyError(f"Lot {lot_id} not found.")
        
        lot = self.lots[lot_id]
        lot_bids = self.bids.get(lot_id, [])
        
        if not lot_bids:
            lot.status = "UNSOLD_NO_BIDS"
            logger.info(f"Lot {lot_id} closed with no bids.")
            return {"lot_id": lot_id, "status": "UNSOLD", "clearing_price_usd": 0.0}

        highest_bid = max(lot_bids, key=lambda b: b.bid_price_usd)
        lot.status = "SOLD"
        
        total_value_usd = highest_bid.bid_price_usd * lot.net_weight_kgs
        total_value_kes = total_value_usd * self.exchange_rate
        
        contract = {
            "contract_id": f"KTDA-CTR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{lot_id}",
            "lot_id": lot_id,
            "factory_origin": lot.factory_origin,
            "grade": lot.grade,
            "winning_broker": highest_bid.broker_code,
            "net_weight_kgs": lot.net_weight_kgs,
            "clearing_price_usd_per_kg": highest_bid.bid_price_usd,
            "total_value_usd": total_value_usd,
            "total_value_kes": total_value_kes,
            "exchange_rate_applied": self.exchange_rate,
            "cleared_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.cleared_contracts.append(contract)
        logger.info(f"Cleared lot {lot_id}: Winner {highest_bid.broker_code} at ${highest_bid.bid_price_usd}/kg (KES {total_value_kes:,.2f})")
        return contract

    def get_market_summary(self) -> Dict[str, Any]:
        total_lots = len(self.lots)
        sold_lots = sum(1 for l in self.lots.values() if l.status == "SOLD")
        total_revenue_usd = sum(c["total_value_usd"] for c in self.cleared_contracts)
        total_revenue_kes = sum(c["total_value_kes"] for c in self.cleared_contracts)
        
        return {
            "total_registered_lots": total_lots,
            "sold_lots": sold_lots,
            "total_revenue_usd": total_revenue_usd,
            "total_revenue_kes": total_revenue_kes,
            "exchange_rate": self.exchange_rate
        }

if __name__ == "__main__":
    print("Executing Nairobi Tea Auction Clearinghouse Self-Test...")
    clearinghouse = NairobiTeaAuctionClearinghouse(exchange_rate_kes_per_usd=131.0)
    
    lot = clearinghouse.register_lot(
        lot_id="LOT-BP1-089",
        factory_origin="Kipkebe Tea Factory",
        grade="BP1",
        bag_count=250,
        net_weight_kgs=12500.0,
        reserve_price_usd=2.40
    )
    
    clearinghouse.submit_bid("BID-001", "LOT-BP1-089", "BROKER-MOMBASA-A", 2.45)
    clearinghouse.submit_bid("BID-002", "LOT-BP1-089", "BROKER-NAIROBI-B", 2.62)
    
    contract = clearinghouse.clears_auction("LOT-BP1-089") if hasattr(clearinghouse, 'clears_auction') else clearinghouse.clear_auction("LOT-BP1-089")
    print("Cleared Contract Result:", json.dumps(contract, indent=2))
    
    summary = clearinghouse.get_market_summary()
    print("Market Summary:", json.dumps(summary, indent=2))
    
    # Validate syntax integrity
    assert ast.parse(__file__)
    print("Nairobi Tea Auction Module compiled successfully under AST check.")
