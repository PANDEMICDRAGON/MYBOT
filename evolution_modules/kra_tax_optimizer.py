import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KRA_Tax_Optimizer:
    """
    A class to optimize and forecast KRA tax liabilities.
    """

    def __init__(self, operator_name: str = "Michael Obiero"):
        self.operator_name = operator_name
        self.tax_rates = {
            "corporate": 0.30,
            "personal": 0.30,
            "vat": 0.16
        }
        self.logger = logging.getLogger(__name__)

    def calculate_tax_liability(self, income: float, tax_type: str = "corporate") -> float:
        """
        Calculate the tax liability based on income and tax type.
        
        Args:
            income (float): The income amount.
            tax_type (str): The type of tax (corporate, personal, vat).
            
        Returns:
            float: The calculated tax liability.
        """
        if tax_type not in self.tax_rates:
            raise ValueError(f"Invalid tax type: {tax_type}")
        
        tax_rate = self.tax_rates[tax_type]
        tax_liability = income * tax_rate
        self.logger.info(f"Calculated {tax_type} tax liability: {tax_liability:.2f}")
        return tax_liability

    def forecast_tax_liability(self, income: float, tax_type: str = "corporate") -> Dict[str, Any]:
        """
        Forecast the tax liability for the next period.
        
        Args:
            income (float): The projected income.
            tax_type (str): The type of tax.
            
        Returns:
            Dict[str, Any]: A dictionary containing the forecasted tax liability.
        """
        tax_liability = self.calculate_tax_liability(income, tax_type)
        return {
            "operator": self.operator_name,
            "income": income,
            "tax_type": tax_type,
            "forecasted_tax_liability": tax_liability,
            "timestamp": datetime.now().isoformat()
        }

    def optimize_tax_strategy(self, income: float, tax_type: str = "corporate") -> Dict[str, Any]:
        """
        Optimize the tax strategy based on income and tax type.
        
        Args:
            income (float): The income amount.
            tax_type (str): The type of tax.
            
        Returns:
            Dict[str, Any]: A dictionary containing the optimized tax strategy.
        """
        tax_liability = self.calculate_tax_liability(income, tax_type)
        optimized_strategy = {
            "operator": self.operator_name,
            "income": income,
            "tax_type": tax_type,
            "current_tax_liability": tax_liability,
            "optimized_tax_liability": tax_liability * 0.9,  # Example optimization
            "savings": tax_liability * 0.1,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"Optimized tax strategy for {self.operator_name}: {optimized_strategy}")
        return optimized_strategy

if __name__ == "__main__":
    optimizer = KRA_Tax_Optimizer()
    income = 100000.0
    tax_type = "corporate"
    
    # Calculate tax liability
    tax_liability = optimizer.calculate_tax_liability(income, tax_type)
    print(f"Tax Liability: {tax_liability:.2f}")
    
    # Forecast tax liability
    forecast = optimizer.forecast_tax_liability(income, tax_type)
    print(f"Forecast: {json.dumps(forecast, indent=2)}")
    
    # Optimize tax strategy
    optimized = optimizer.optimize_tax_strategy(income, tax_type)
    print(f"Optimized Strategy: {json.dumps(optimized, indent=2)}")
