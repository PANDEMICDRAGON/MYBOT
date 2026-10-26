import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KRA_Tax_Optimizer:
    """
    Autonomous KRA Tax Optimization & Compliance Sentinel.
    
    This class proactively calculates optimal tax brackets, identifies deductions,
    and ensures compliance with KRA regulations for operators in Kenya.
    """

    def __init__(self, operator_name: str, location: str):
        self.operator_name = operator_name
        self.location = location
        self.tax_brackets = self._load_tax_brackets()
        self.deductions = self._load_deductions()
        self.compliance_rules = self._load_compliance_rules()
        logger.info(f"KRA_Tax_Optimizer initialized for {operator_name} in {location}")

    def _load_tax_brackets(self) -> List[Dict]:
        """Load current KRA tax brackets."""
        return [
            {"min": 0, "max": 240000, "rate": 0.10},
            {"min": 240001, "max": 400000, "rate": 0.25},
            {"min": 400001, "max": 800000, "rate": 0.30},
            {"min": 800001, "max": 1000000, "rate": 0.325},
            {"min": 1000001, "max": float('inf'), "rate": 0.35}
        ]

    def _load_deductions(self) -> Dict[str, float]:
        """Load standard deductions."""
        return {
            "housing": 0.15,
            "medical": 0.05,
            "education": 0.10
        }

    def _load_compliance_rules(self) -> List[str]:
        """Load compliance rules."""
        return [
            "File returns by 20th of the following month",
            "Maintain records for 5 years",
            "Pay VAT if turnover exceeds 1M KES"
        ]

    def calculate_tax(self, income: float) -> float:
        """
        Calculate tax based on income.
        
        Args:
            income (float): Annual income in KES.
            
        Returns:
            float: Calculated tax amount.
        """
        tax = 0.0
        for bracket in self.tax_brackets:
            if income > bracket["min"]:
                taxable = min(income, bracket["max"]) - bracket["min"]
                tax += taxable * bracket["rate"]
            else:
                break
        return tax

    def optimize_deductions(self, income: float, deductions: Dict[str, float]) -> float:
        """
        Optimize deductions to minimize tax.
        
        Args:
            income (float): Annual income in KES.
            deductions (Dict[str, float]): Available deductions.
            
        Returns:
            float: Optimized tax amount.
        """
        total_deductions = sum(deductions.values())
        taxable_income = max(0, income - total_deductions)
        return self.calculate_tax(taxable_income)

    def check_compliance(self, last_filing_date: datetime) -> bool:
        """
        Check if the operator is compliant with filing deadlines.
        
        Args:
            last_filing_date (datetime): Date of last tax filing.
            
        Returns:
            bool: True if compliant, False otherwise.
        """
        current_date = datetime.now()
        days_since_filing = (current_date - last_filing_date).days
        return days_since_filing <= 30

    def generate_report(self, income: float, deductions: Dict[str, float], last_filing_date: datetime) -> Dict:
        """
        Generate a comprehensive tax report.
        
        Args:
            income (float): Annual income in KES.
            deductions (Dict[str, float]): Available deductions.
            last_filing_date (datetime): Date of last tax filing.
            
        Returns:
            Dict: Comprehensive tax report.
        """
        base_tax = self.calculate_tax(income)
        optimized_tax = self.optimize_deductions(income, deductions)
        savings = base_tax - optimized_tax
        compliant = self.check_compliance(last_filing_date)
        
        return {
            "operator": self.operator_name,
            "location": self.location,
            "income": income,
            "base_tax": base_tax,
            "optimized_tax": optimized_tax,
            "savings": savings,
            "compliant": compliant,
            "recommendations": self._generate_recommendations(savings, compliant)
        }

    def _generate_recommendations(self, savings: float, compliant: bool) -> List[str]:
        """
        Generate recommendations based on tax report.
        
        Args:
            savings (float): Potential tax savings.
            compliant (bool): Compliance status.
            
        Returns:
            List[str]: Recommendations.
        """
        recommendations = []
        if savings > 0:
            recommendations.append(f"Consider optimizing deductions to save {savings:.2f} KES.")
        if not compliant:
            recommendations.append("File your taxes immediately to avoid penalties.")
        return recommendations


if __name__ == "__main__":
    # Test harness
    optimizer = KRA_Tax_Optimizer("Michael Obiero", "Kitengela")
    income = 1200000
    deductions = {"housing": 180000, "medical": 60000, "education": 120000}
    last_filing_date = datetime.now()
    
    report = optimizer.generate_report(income, deductions, last_filing_date)
    print(json.dumps(report, indent=2))
