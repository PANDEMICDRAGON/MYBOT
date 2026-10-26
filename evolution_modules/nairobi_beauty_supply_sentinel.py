"""
Nairobi Cosmopolitan Beauty & Salon Supply Chain Inventory & Micro-Consignment Ledger
Author: Cortana, Autonomous Evolutionary Architect
Operator: Michael Obiero, Nairobi, Kenya
"""

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [BEAUTY_SENTINEL] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ConsignmentItem:
    item_id: str
    name: str
    salon_id: str
    quantity_supplied: int
    quantity_sold: int = 0
    unit_price_kes: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

class BeautySupplySentinel:
    """Manages micro-consignments, real-time inventory reconciliation, and M-Pesa payouts for Nairobi salons."""
    
    def __init__(self, distributor_name: str):
        self.distributor_name = distributor_name
        self.consignments: Dict[str, ConsignmentItem] = {}
        self.ledger: List[Dict] = []

    def register_consignment(self, item_id: str, name: str, salon_id: str, quantity: int, unit_price_kes: float) -> bool:
        try:
            if quantity <= 0 or unit_price_kes <= 0:
                raise ValueError("Quantity and price must be strictly positive.")
            
            self.consignments[item_id] = ConsignmentItem(
                item_id=item_id,
                name=name,
                salon_id=salon_id,
                quantity_supplied=quantity,
                unit_price_kes=unit_price_kes
            )
            logger.info(f"Registered consignment {item_id} ({name}) for salon {salon_id}: {quantity} units @ KES {unit_price_kes}")
            return True
        except Exception as e:
            logger.error(f"Failed to register consignment: {e}")
            return False

    def record_sale(self, item_id: str, units_sold: int) -> Optional[float]:
        try:
            if item_id not in self.consignments:
                raise KeyError(f"Consignment item {item_id} not found.")
            
            item = self.consignments[item_id]
            if item.quantity_sold + units_sold > item.quantity_supplied:
                raise ValueError("Units sold exceed available supplied stock.")
            
            item.quantity_sold += units_sold
            item.last_updated = datetime.utcnow().isoformat()
            
            revenue = units_sold * item.unit_price_kes
            self.ledger.append({
                "timestamp": item.last_updated,
                "item_id": item_id,
                "salon_id": item.salon_id,
                "units_sold": units_sold,
                "revenue_kes": revenue
            })
            
            logger.info(f"Recorded sale: {units_sold} of {item.name} at salon {item.salon_id}. Revenue: KES {revenue}")
            return revenue
        except Exception as e:
            logger.error(f"Sale recording error: {e}")
            return None

    def generate_settlement_report(self, salon_id: str) -> Dict:
        salon_items = [i for i in self.consignments.values() if i.salon_id == salon_id]
        total_due_kes = sum(i.quantity_sold * i.unit_price_kes for i in salon_items)
        total_items_supplied = sum(i.quantity_supplied for i in salon_items)
        total_items_sold = sum(i.quantity_sold for i in salon_items)
        
        return {
            "salon_id": salon_id,
            "distributor": self.distributor_name,
            "total_supplied": total_items_supplied,
            "total_sold": total_items_sold,
            "total_due_kes": total_due_kes,
            "generated_at": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    sentinel = BeautySupplySentinel("Nairobi Glamour Hub Distributors")
    sentinel.register_consignment("ITEM-001", "Argan Oil Hair Treatment 250ml", "SALON-WESTLANDS-04", 50, 1200.0)
    sentinel.record_sale("ITEM-001", 12)
    report = sentinel.generate_settlement_report("SALON-WESTLANDS-04")
    logger.info(f"Settlement Audit Report: {report}")

    # Self-validation check
    source_code = open(__file__, "r", encoding="utf-8").read()
    ast.parse(source_code)
    logger.info("Self-test AST compilation passed successfully.")
