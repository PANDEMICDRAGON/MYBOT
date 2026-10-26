import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KRA_Tax_Optimizer:
    """
    A class to optimize tax payments and ensure compliance with Kenyan Revenue Authority (KRA) regulations.
    """
    
    def __init__(self, tax_year: int = 2024):
        self.tax_year = tax_year
        self.tax_brackets = self._get_tax_brackets()
        self.deductions = self._get_deductions()
        
    def _get_tax_brackets(self) -> List[Dict[str, float]]:
        """
        Retrieve the current tax brackets for the specified tax year.
        """
        # Example tax brackets for Kenya (2024)
        return [
            {"min_income": 0, "max_income": 240000, "rate": 0.10},
            {"min_income": 240001, "max_income": 400000, "rate": 0.25},
            {"min_income": 400001, "max_income": 800000, "rate": 0.30},
            {"min_income": 800001, "max_income": float('inf'), "rate": 0.35}
        ]
    
    def _get_deductions(self) -> Dict[str, float]:
        """
        Retrieve the current deductions for the specified tax year.
        """
        # Example deductions for Kenya (2024)
        return {
            "personal_relief": 2400,
            "pension_contribution": 0.05,  # 5% of gross income
            "insurance_premium": 0.02,  # 2% of gross income
            "medical_expenses": 0.01  # 1% of gross income
        }
    
    def calculate_tax(self, gross_income: float) -> Dict[str, float]:
        """
        Calculate the tax payable based on the gross income.
        
        Args:
            gross_income (float): The gross income for the tax year.
            
        Returns:
            Dict[str, float]: A dictionary containing the calculated tax details.
        """
        if gross_income < 0:
            raise ValueError("Gross income cannot be negative.")
            
        tax_payable = 0.0
        for bracket in self.tax_brackets:
            if gross_income > bracket["min_income"]:
                taxable_amount = min(gross_income, bracket["max_income"]) - bracket["min_income"]
                tax_payable += taxable_amount * bracket["rate"]
            else:
                break
        
        # Apply deductions
        deductions = self.deductions
        total_deductions = deductions["personal_relief"] + \
                           (gross_income * deductions["pension_contribution"]) + \
                           (gross_income * deductions["insurance_premium"]) + \
                           (gross_income * deductions["medical_expenses"])
        
        net_tax = max(0, tax_payable - total_deductions)
        
        return {
            "gross_income": gross_income,
            "tax_payable": tax_payable,
            "total_deductions": total_deductions,
            "net_tax": net_tax
        }
    
    def suggest_optimization(self, gross_income: float) -> Dict[str, float]:
        """
        Suggest tax optimization strategies based on the gross income.
        
        Args:
            gross_income (float): The gross income for the tax year.
            
        Returns:
            Dict[str, float]: A dictionary containing the suggested optimization details.
        """
        tax_details = self.calculate_tax(gross_income)
        
        # Suggest increasing pension contributions if possible
        suggested_pension_contribution = min(gross_income * 0.05, gross_income * 0.10)
        
        return {
            "current_net_tax": tax_details["net_tax"],
            "suggested_pension_contribution": suggested_pension_contribution,
            "potential_tax_savings": suggested_pension_contribution * 0.35  # Assuming top tax rate
        }

if __name__ == "__main__":
    optimizer = KRA_Tax_Optimizer()
    
    # Test case 1
    gross_income_1 = 500000
    tax_details_1 = optimizer.calculate_tax(gross_income_1)
    print(f"Tax Details for {gross_income_1}: {tax_details_1}")
    
    # Test case 2
    gross_income_2 = 1000000
    tax_details_2 = optimizer.calculate_tax(gross_income_2)
    print(f"Tax Details for {gross_income_2}: {tax_details_2}")
    
    # Suggest optimization
    optimization_1 = optimizer.suggest_optimization(gross_income_1)
    print(f"Optimization Suggestion for {gross_income_1}: {optimization_1}")
    
    optimization_2 = optimizer.suggest_optimization(gross_income_2)
    print(f"Optimization Suggestion for {gross_income_2}: {optimization_2}")