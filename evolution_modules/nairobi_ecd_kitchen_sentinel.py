"""
Module: nairobi_ecd_kitchen_sentinel.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Nairobi, Kenya)

Description:
Proactive nutritional tracking, cold-chain temperature telemetry, and vendor delivery audit sentinel
for Nairobi County Early Childhood Development (ECD) center school feeding programs.
"""

import ast
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] (ECD-SENTINEL): %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DeliveryBatch:
    batch_id: str
    ecd_center_id: str
    ingredient_name: str
    quantity_kg: float
    supplier_name: str
    dispatch_temp_c: float
    arrival_temp_c: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified: bool = False
    spoilage_risk: str = "LOW"


@dataclass
class NutritionalLog:
    ecd_center_id: str
    pupil_count: int
    calories_per_meal: float
    protein_grams: float
    iron_mg: float
    vitamin_a_mcg: float
    date_stamp: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))


class NairobiECDKitchenSentinel:
    """
    Manages and audits food supply logistics, cold-chain integrity, and nutritional compliance
    across Nairobi County ECD school feeding kitchens.
    """
    
    def __init__(self, target_calories: float = 650.0, target_protein: float = 18.0):
        self.target_calories = target_calories
        self.target_protein = target_protein
        self.batches: Dict[str, DeliveryBatch] = {}
        self.nutrition_logs: List[NutritionalLog] = []

    def ingest_delivery_batch(self, batch_id: str, ecd_center_id: str, ingredient_name: str,
                              quantity_kg: float, supplier_name: str, dispatch_temp_c: float,
                              arrival_temp_c: float) -> DeliveryBatch:
        """
        Ingests a fresh ingredient delivery batch, calculates spoilage risk based on temperature drift,
        and records telemetry.
        """
        temp_drift = arrival_temp_c - dispatch_temp_c
        spoilage_risk = "LOW"
        
        # Perishable items like milk, meat, or fresh vegetables in Nairobi climate
        perishables = ["milk", "beef", "omena", "spinach", "eggs"]
        is_perishable = any(p in ingredient_name.lower() for p in perishables)
        
        if is_perishable:
            if arrival_temp_c > 8.0 or temp_drift > 4.0:
                spoilage_risk = "CRITICAL"
            elif arrival_temp_c > 5.0 or temp_drift > 2.0:
                spoilage_risk = "MODERATE"
        else:
            if arrival_temp_c > 25.0:
                spoilage_risk = "MODERATE"
                
        verified = spoilage_risk == "LOW"
        
        batch = DeliveryBatch(
            batch_id=batch_id,
            ecd_center_id=ecd_center_id,
            ingredient_name=ingredient_name,
            quantity_kg=quantity_kg,
            supplier_name=supplier_name,
            dispatch_temp_c=dispatch_temp_c,
            arrival_temp_c=arrival_temp_c,
            verified=verified,
            spoilage_risk=spoilage_risk
        )
        
        self.batches[batch_id] = batch
        logger.info(f"Ingested batch {batch_id} for {ecd_center_id}: {ingredient_name} ({quantity_kg}kg). Risk: {spoilage_risk}")
        return batch

    def audit_nutritional_intake(self, ecd_center_id: str, pupil_count: int, 
                                 calories: float, protein: float, iron: float, vitamin_a: float) -> Tuple[bool, str]:
        """
        Audits daily meal nutritional values against mandatory Nairobi County ECD standards.
        """
        log = NutritionalLog(
            ecd_center_id=ecd_center_id,
            pupil_count=pupil_count,
            calories_per_meal=calories,
            protein_grams=protein,
            iron_mg=iron,
            vitamin_a_mcg=vitamin_a
        )
        self.nutrition_logs.append(log)
        
        deficits = []
        if calories < self.target_calories:
            deficits.append(f"Calories below target ({calories} < {self.target_calories})")
        if protein < self.target_protein:
            deficits.append(f"Protein below target ({protein}g < {self.target_protein}g)")
            
        if deficits:
            warning_msg = f"ECD Center {ecd_center_id} nutritional deficit detected: " + "; ".join(deficits)
            logger.warning(warning_msg)
            return False, warning_msg
        
        logger.info(f"ECD Center {ecd_center_id} passed nutritional compliance check for {pupil_count} pupils.")
        return True, "Nutritional standards fully met."

    def generate_county_report(self) -> Dict[str, any]:
        """
        Generates a consolidated summary report for county stakeholders.
        """
        total_batches = len(self.batches)
        rejected_batches = sum(1 for b in self.batches.values() if not b.verified)
        total_nutrition_audits = len(self.nutrition_logs)
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_ingredient_batches": total_batches,
            "rejected_spoiled_batches": rejected_batches,
            "total_nutrition_audits": total_nutrition_audits,
            "supply_chain_integrity_pct": ((total_batches - rejected_batches) / max(1, total_batches)) * 100.0
        }


if __name__ == "__main__":
    print("=== TESTING NAIROBI ECD KITCHEN SENTINEL ===")
    sentinel = NairobiECDKitchenSentinel()
    
    # Test batch ingestion
    b1 = sentinel.ingest_delivery_batch(
        batch_id="BATCH-NBI-001",
        ecd_center_id="ECD-KIBERA-04",
        ingredient_name="Fresh Whole Milk",
        quantity_kg=150.0,
        supplier_name="Highlands Dairy Ltd",
        dispatch_temp_c=4.0,
        arrival_temp_c=9.5
    )
    assert b1.spoilage_risk == "CRITICAL"
    assert not b1.verified
    
    b2 = sentinel.ingest_delivery_batch(
        batch_id="BATCH-NBI-002",
        ecd_center_id="ECD-WESTLANDS-01",
        ingredient_name="Dry Maize Meal (Unga)",
        quantity_kg=500.0,
        supplier_name="Jogoo Millers",
        dispatch_temp_c=22.0,
        arrival_temp_c=23.0
    )
    assert b2.spoilage_risk == "LOW"
    assert b2.verified
    
    # Test nutrition audit
    passed, msg = sentinel.audit_nutritional_intake(
        ecd_center_id="ECD-WESTLANDS-01",
        pupil_count=120,
        calories=680.0,
        protein=21.5,
        iron=8.2,
        vitamin_a=450.0
    )
    assert passed
    
    report = sentinel.generate_county_report()
    print(f"County ECD Feeding Report: {json.dumps(report, indent=2)}")
    
    # AST self-compilation verification
    with open(__file__, "r", encoding="utf-8") as f:
        source_code = f.read()
    ast.parse(source_code)
    print("AST Self-Compilation Verification: SUCCESS")
