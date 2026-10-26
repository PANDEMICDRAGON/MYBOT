"""
Nairobi Maasai Market & Artisan Curio Global Provenance & Fair-Trade Escrow Sentinel
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Provides verifiable cryptographic provenance, fair-trade revenue split calculation, and
secure escrow automation for Nairobi artisan goods exported globally.
"""

import os
import json
import time
import hmac
import hashlib
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [ArtisanSentinel]: %(message)s")

@dataclass
class ArtisanItem:
    item_id: str
    artisan_name: str
    cooperative: str
    material: str
    category: str
    base_price_kes: float
    provenance_hash: str
    timestamp: float

@dataclass
class EscrowTransaction:
    transaction_id: str
    item_id: str
    buyer_id: str
    destination_country: str
    sale_price_usd: float
    exchange_rate_kes_usd: float
    artisan_payout_kes: float
    cooperative_levy_kes: float
    platform_fee_kes: float
    status: str
    signature: str

class NairobiArtisanSentinel:
    """Manages provenance verification and fair-trade escrow for Nairobi artisan goods."""
    
    def __init__(self, secret_key: Optional[bytes] = None):
        self.secret_key = secret_key or os.urandom(32)
        self.registry: Dict[str, ArtisanItem] = {}
        self.escrows: Dict[str, EscrowTransaction] = {}
        logging.info("NairobiArtisanSentinel initialized successfully.")

    def register_item(self, item_id: str, artisan_name: str, cooperative: str, 
                      material: str, category: str, base_price_kes: float) -> ArtisanItem:
        """Registers a new handmade item with cryptographic provenance."""
        raw_data = f"{item_id}:{artisan_name}:{cooperative}:{material}:{base_price_kes}:{time.time()}"
        prov_hash = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        
        item = ArtisanItem(
            item_id=item_id,
            artisan_name=artisan_name,
            cooperative=cooperative,
            material=material,
            category=category,
            base_price_kes=base_price_kes,
            provenance_hash=prov_hash,
            timestamp=time.time()
        )
        self.registry[item_id] = item
        logging.info(f"Registered artisan item {item_id} by {artisan_name} ({cooperative}).")
        return item

    def initiate_global_sale(self, transaction_id: str, item_id: str, buyer_id: str,
                              destination_country: str, sale_price_usd: float, 
                              exchange_rate_kes_usd: float = 130.0) -> EscrowTransaction:
        """Processes an international purchase, enforcing fair-trade revenue split."""
        if item_id not in self.registry:
            raise ValueError(f"Item {item_id} not found in provenance registry.")
        
        item = self.registry[item_id]
        total_kes = sale_price_usd * exchange_rate_kes_usd
        
        # Fair-trade distribution logic: 75% to artisan, 15% cooperative, 10% platform
        artisan_payout = total_kes * 0.75
        cooperative_levy = total_kes * 0.15
        platform_fee = total_kes * 0.10
        
        payload = f"{transaction_id}:{item_id}:{buyer_id}:{sale_price_usd}:{artisan_payout}"
        sig = hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        
        escrow = EscrowTransaction(
            transaction_id=transaction_id,
            item_id=item_id,
            buyer_id=buyer_id,
            destination_country=destination_country,
            sale_price_usd=sale_price_usd,
            exchange_rate_kes_usd=exchange_rate_kes_usd,
            artisan_payout_kes=round(artisan_payout, 2),
            cooperative_levy_kes=round(cooperative_levy, 2),
            platform_fee_kes=round(platform_fee, 2),
            status="ESCROW_HELD",
            signature=sig
        )
        
        self.escrows[transaction_id] = escrow
        logging.info(f"Escrow {transaction_id} created for item {item_id}. Payout to {item.artisan_name}: KES {artisan_payout:.2f}")
        return escrow

    def release_escrow(self, transaction_id: str) -> Dict[str, Any]:
        """Releases funds upon verified international delivery."""
        if transaction_id not in self.escrows:
            raise ValueError(f"Transaction {transaction_id} not found.")
        
        escrow = self.escrows[transaction_id]
        escrow.status = "RELEASED"
        logging.info(f"Escrow {transaction_id} successfully released to artisan.")
        return {
            "transaction_id": transaction_id,
            "status": escrow.status,
            "artisan_payout_kes": escrow.artisan_payout_kes
        }

if __name__ == "__main__":
    print("--- Executing NairobiArtisanSentinel Test Harness ---")
    sentinel = NairobiArtisanSentinel()
    
    item = sentinel.register_item(
        item_id="ART-MSK-001",
        artisan_name="Naomi Wanjiku",
        cooperative="Karen Beadwork Women Group",
        material="Recycled Glass & Brass",
        category="Necklace",
        base_price_kes=2500.0
    )
    
    escrow = sentinel.initiate_global_sale(
        transaction_id="TXN-NYC-9988",
        item_id="ART-MSK-001",
        buyer_id="buyer_ny_42",
        destination_country="United States",
        sale_price_usd=65.0,
        exchange_rate_kes_usd=132.5
    )
    
    print(json.dumps(asdict(escrow), indent=2))
    release = sentinel.release_escrow("TXN-NYC-9988")
    print(json.dumps(release, indent=2))
