import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class TaxAuditSimulator:
    """
    Simulates KRA tax liabilities and audit risks for Nairobi-based operators.
    """
    
    def __init__(self, operator_id: str, ein: str):
        self.operator_id = operator_id
        self.ein = ein
        self.audit_risk_score = 0.0
        self.estimated_liability = 0.0
        
    def calculate_vat_liability(self, sales: float, purchases: float) -> float:
        """
        Calculate VAT liability based on sales and purchases.
        """
        if sales < 0 or purchases < 0:
            raise ValueError("Sales and purchases must be non-negative")
        
        vat_on_sales = sales * 0.16
        vat_on_purchases = purchases * 0.16
        liability = vat_on_sales - vat_on_purchases
        return max(0, liability)
    
    def calculate_income_tax(self, profit: float) -> float:
        """
        Calculate income tax based on profit using KRA tax brackets.
        """
        if profit < 0:
            return 0.0
        
        # Simplified KRA tax brackets for individuals
        if profit <= 240000:
            return profit * 0.10
        elif profit <= 480000:
            return 24000 + (profit - 240000) * 0.25
        elif profit <= 840000:
            return 84000 + (profit - 480000) * 0.30
        elif profit <= 1200000:
            return 192000 + (profit - 840000) * 0.325
        else:
            return 309000 + (profit - 1200000) * 0.35
    
    def assess_audit_risk(self, compliance_score: float, transaction_volume: float) -> float:
        """
        Assess audit risk based on compliance score and transaction volume.
        """
        if not 0 <= compliance_score <= 1:
            raise ValueError("Compliance score must be between 0 and 1")
        if transaction_volume < 0:
            raise ValueError("Transaction volume must be non-negative")
        
        # Higher compliance and lower volume reduce risk
        risk = (1 - compliance_score) * 0.5 + (transaction_volume / 1000000) * 0.5
        return min(1.0, risk)
    
    def simulate_audit(self, sales: float, purchases: float, profit: float, compliance_score: float) -> Dict:
        """
        Simulate a full tax audit scenario.
        """
        vat_liability = self.calculate_vat_liability(sales, purchases)
        income_tax = self.calculate_income_tax(profit)
        total_liability = vat_liability + income_tax
        
        audit_risk = self.assess_audit_risk(compliance_score, sales + purchases)
        
        return {
            "operator_id": self.operator_id,
            "ein": self.ein,
            "vat_liability": vat_liability,
            "income_tax": income_tax,
            "total_liability": total_liability,
            "audit_risk_score": audit_risk,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    simulator = TaxAuditSimulator("Michael Obiero", "EIN123456789")
    result = simulator.simulate_audit(
        sales=1000000,
        purchases=500000,
        profit=300000,
        compliance_score=0.95
    )
    print(json.dumps(result, indent=2))
