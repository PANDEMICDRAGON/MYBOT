"""
Nairobi Municipal Bamboo Afforestation & Carbon Sequestration Credit Sentinel
Autonomous Evolutionary Architecture for Cortana
Written for Michael Obiero in Nairobi, Kenya
"""

import json
import time
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class BambooGroveTelemetry:
    grove_id: str
    location_zone: str
    species_name: str
    hectares: float
    stem_count: int
    average_height_meters: float
    soil_moisture_pct: float
    ambient_temp_c: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class CarbonCreditRecord:
    credit_id: str
    grove_id: str
    metric_tons_co2_sequestered: float
    estimated_value_kes: float
    verification_status: str
    issued_at: float = field(default_factory=time.time)

class BambooCarbonSentinel:
    """
    Monitors urban bamboo growth metrics, computes biomass accumulation via allometric equations,
    and estimates verified carbon offsets for Nairobi environmental programs.
    """
    def __init__(self, baseline_sequestration_rate_per_hectare_ton: float = 35.0):
        # Bambusa vulgaris / Dendrocalamus giganteus average ~30-40 tons CO2/ha/year under tropical highland conditions
        self.annual_rate = baseline_sequestration_rate_per_hectare_ton
        self.groves: Dict[str, BambooGroveTelemetry] = {}
        self.ledger: List[CarbonCreditRecord] = []

    def register_grove(self, telemetry: BambooGroveTelemetry) -> None:
        if telemetry.hectares <= 0 or telemetry.stem_count <= 0:
            raise ValueError("Invalid grove parameters: hectares and stem count must be positive.")
        self.groves[telemetry.grove_id] = telemetry

    def compute_daily_sequestration(self, grove_id: str) -> CarbonCreditRecord:
        if grove_id not in self.groves:
            raise KeyError(f"Grove {grove_id} not registered in telemetry grid.")
        
        grove = self.groves[grove_id]
        
        # Growth multiplier based on soil moisture (optimum 40-70%) and height factor
        moisture_factor = 1.0
        if grove.soil_moisture_pct < 30.0:
            moisture_factor = 0.7
        elif grove.soil_moisture_pct > 80.0:
            moisture_factor = 0.85
            
        height_multiplier = grove.average_height_meters / 15.0 if grove.average_height_meters > 0 else 0.5
        
        daily_rate_per_ha = (self.annual_rate / 365.0) * moisture_factor * height_multiplier
        total_daily_tons = daily_rate_per_ha * grove.hectares
        
        # Current market valuation assumption: ~1,500 KES per metric ton of certified African carbon offset
        kes_per_ton = 1500.0
        estimated_value = total_daily_tons * kes_per_ton
        
        credit_id = f"CRD-{grove_id}-{int(time.time())}"
        record = CarbonCreditRecord(
            credit_id=credit_id,
            grove_id=grove_id,
            metric_tons_co2_sequestered=round(total_daily_tons, 4),
            estimated_value_kes=round(estimated_value, 2),
            verification_status="PENDING_BLOCKCHAIN_ANCHOR"
        )
        self.ledger.append(record)
        return record

    def generate_audit_summary(self) -> Dict[str, Any]:
        total_hectares = sum(g.hectares for g in self.groves.values())
        total_sequestered = sum(r.metric_tons_co2_sequestered for r in self.ledger)
        total_kes_value = sum(r.estimated_value_kes for r in self.ledger)
        return {
            "active_groves_monitored": len(self.groves),
            "total_hectares_under_management": round(total_hectares, 2),
            "cumulative_co2_offset_tons": round(total_sequestered, 4),
            "total_estimated_value_kes": round(total_kes_value, 2),
            "operator": "Michael Obiero (Nairobi, Kenya)"
        }

if __name__ == "__main__":
    sentinel = BambooCarbonSentinel()
    
    test_grove = BambooGroveTelemetry(
        grove_id="KARURA-BAMBOO-01",
        location_zone="Karura Forest Buffer Zone C",
        species_name="Dendrocalamus giganteus",
        hectares=12.5,
        stem_count=18500,
        average_height_meters=18.2,
        soil_moisture_pct=55.0,
        ambient_temp_c=22.4
    )
    
    sentinel.register_grove(test_grove)
    credit = sentinel.compute_daily_sequestration("KARURA-BAMBOO-01")
    summary = sentinel.generate_audit_summary()
    
    print("--- NAIROBI BAMBOO CARBON CREDIT SENTINEL TEST ---")
    print(json.dumps({"credit_generated": credit.__dict__, "audit_summary": summary}, indent=2))
