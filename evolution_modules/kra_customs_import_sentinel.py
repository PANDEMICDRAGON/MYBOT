"""
Module: kra_customs_import_sentinel.py
Author: Cortana Autonomous Evolutionary Architect
Operator: Michael Obiero (Kitengela & Nairobi, Kenya)
Description: Provides automated KRA HS code lookup, import duty, VAT, and IDF/RDL levy calculation, along with JKIA/Mombasa port clearance bottleneck forecasting.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [KRACustomsSentinel]: %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class ImportManifest:
    item_description: str
    declared_cif_usd: float
    hs_code: str
    category: str
    origin_country: str
    arrival_hub: str  # e.g., 'JKIA_CARGO', 'MOMBASA_PORT'
    shipping_mode: str  # 'AIR' or 'SEA'
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class TaxAssessmentResult:
    item_description: str
    cif_usd: float
    exchange_rate_kes_usd: float
    cif_kes: float
    import_duty_kes: float
    excise_duty_kes: float
    vat_kes: float
    idf_fee_kes: float
    rdl_levy_kes: float
    total_taxes_kes: float
    estimated_clearance_days: int
    risk_score: float
    recommendations: List[str]

class KRACustomsValuator:
    """
    Evaluates import duties and estimates customs clearance timelines for shipments
    arriving for Michael Obiero in Nairobi/Kitengela.
    """
    def __init__(self, current_usd_rate: float = 132.50):
        self.exchange_rate = current_usd_rate
        # Standard KRA statutory rates
        self.IDF_RATE = 0.035  # 3.5% Import Declaration Fee
        self.RDL_RATE = 0.02   # 2.0% Railway Development Levy
        self.VAT_RATE = 0.16   # 16% Value Added Tax
        
        # Database of simulated HS code duty structures
        self.hs_tariff_database = {
            "8471.30.00": {"name": "Portable Automatic Data Processing Machines (Laptops)", "duty_rate": 0.0, "excise_rate": 0.0},
            "8517.12.00": {"name": "Smartphones / Telephones for Cellular Networks", "duty_rate": 10.0, "excise_rate": 0.0},
            "8541.43.00": {"name": "Photovoltaic Cells / Solar Panels", "duty_rate": 0.0, "excise_rate": 0.0},
            "8504.40.90": {"name": "Inverters & Uninterruptible Power Supplies (UPS)", "duty_rate": 25.0, "excise_rate": 0.0},
            "9031.80.00": {"name": "Electronic Sensors, Testing & Measuring Instruments", "duty_rate": 0.0, "excise_rate": 0.0}
        }

    def assess_shipment(self, manifest: ImportManifest) -> TaxAssessmentResult:
        logger.info(f"Assessing KRA customs tax and clearance for: {manifest.item_description} ({manifest.hs_code})")
        
        cif_kes = manifest.declared_cif_usd * self.exchange_rate
        tariff_info = self.hs_tariff_database.get(manifest.hs_code, {"name": "General Electronic Equipment", "duty_rate": 25.0, "excise_rate": 0.0})
        
        # Calculations
        duty_pct = tariff_info["duty_rate"] / 100.0
        excise_pct = tariff_info["excise_rate"] / 100.0
        
        import_duty = cif_kes * duty_pct
        value_after_duty = cif_kes + import_duty
        
        excise_duty = value_after_duty * excise_pct
        value_after_excise = value_after_duty + excise_duty
        
        idf_fee = cif_kes * self.IDF_RATE
        rdl_levy = cif_kes * self.RDL_RATE
        
        # VAT is calculated on (CIF + Import Duty + Excise + IDF + RDL)
        vatable_base = value_after_excise + idf_fee + rdl_levy
        vat = vatable_base * self.VAT_RATE
        
        total_taxes = import_duty + excise_duty + idf_fee + rdl_levy + vat
        
        # Clearance time estimation
        base_days = 2 if manifest.shipping_mode == "AIR" else 7
        hub_penalty = 1 if manifest.arrival_hub == "MOMBASA_PORT" else 0
        est_days = base_days + hub_penalty
        
        # Risk scoring based on valuation discrepancies or high duty brackets
        risk_score = 0.15 if duty_pct == 0.0 else 0.45
        if manifest.declared_cif_usd > 10000:
            risk_score += 0.30
            
        recommendations = [
            f"Ensure OEM invoices and Bill of Lading / Airway Bill match declared CIF USD {manifest.declared_cif_usd}.",
            f"HS Code {manifest.hs_code} ({tariff_info['name']}) attracts {tariff_info['duty_rate']}% import duty.",
            f"Pre-export Verification of Conformity (PVoC / CoC) required from origin before cargo loading to avoid KRA punitive testing fees.",
            f"Estimated total statutory tax liability: KES {total_taxes:,.2f} payable via iTax / Simba system."
        ]
        
        return TaxAssessmentResult(
            item_description=manifest.item_description,
            cif_usd=manifest.declared_cif_usd,
            exchange_rate_kes_usd=self.exchange_rate,
            cif_kes=cif_kes,
            import_duty_kes=import_duty,
            excise_duty_kes=excise_duty,
            vat_kes=vat,
            idf_fee_kes=idf_fee,
            rdl_levy_kes=rdl_levy,
            total_taxes_kes=total_taxes,
            estimated_clearance_days=est_days,
            risk_score=min(risk_score, 1.0),
            recommendations=recommendations
        )

if __name__ == "__main__":
    print("--- Executing Cortana KRACustomsValuator Test Harness ---")
    valuator = KRACustomsValuator(current_usd_rate=133.0)
    
    test_manifest = ImportManifest(
        item_description="Industrial IoT Edge Computing Nodes & Sensor Arrays",
        declared_cif_usd=4500.0,
        hs_code="8471.30.00",
        category="Hardware",
        origin_country="China",
        arrival_hub="JKIA_CARGO",
        shipping_mode="AIR"
    )
    
    result = valuator.assess_shipment(test_manifest)
    print(json.dumps(asdict(result), indent=2))
