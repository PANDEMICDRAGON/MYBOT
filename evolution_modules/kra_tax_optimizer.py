import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KRA_Tax_Optimizer:
    """
    A class to optimize tax calculations and ensure compliance with KRA regulations.
    """

    def __init__(self, operator_name: str = "Michael Obiero"):
        self.operator_name = operator_name
        self.tax_rates = {
            "personal_income_tax": 0.30,  # 30% for high earners
            "corporate_tax": 0.30,  # 30% corporate tax
            "vat": 0.16,  # 16% VAT
            "withholding_tax": 0.5,  # 5% withholding tax
        }
        self.tax_deadlines = {
            "personal_income_tax": "15th of every month",
            "corporate_tax": "15th of every month",
            "vat": "20th of every month",
            "withholding_tax": "15th of every month",
        }

    def calculate_tax(self, income: float, tax_type: str) -> float:
        """
        Calculate tax based on income and tax type.

        Args:
            income (float): The income amount.
            tax_type (str): The type of tax (e.g., 'personal_income_tax', 'corporate_tax').

        Returns:
            float: The calculated tax amount.
        """
        if tax_type not in self.tax_rates:
            raise ValueError(f"Unknown tax type: {tax_type}")

        tax_amount = income * self.tax_rates[tax_type]
        logger.info(f"Calculated {tax_type} for {self.operator_name}: {tax_amount:.2f}")
        return tax_amount

    def check_compliance(self, tax_type: str, due_date: datetime) -> bool:
        """
        Check if the tax is due and compliant.

        Args:
            tax_type (str): The type of tax.
            due_date (datetime): The due date for the tax.

        Returns:
            bool: True if compliant, False otherwise.
        """
        today = datetime.now()
        if due_date < today:
            logger.warning(f"{tax_type} is overdue for {self.operator_name}")
            return False
        else:
            logger.info(f"{tax_type} is compliant for {self.operator_name}")
            return True

    def generate_tax_report(self, income: float, tax_type: str) -> Dict[str, Union[float, str]]:
        """
        Generate a tax report for the given income and tax type.

        Args:
            income (float): The income amount.
            tax_type (str): The type of tax.

        Returns:
            Dict[str, Union[float, str]]: A dictionary containing the tax report.
        """
        tax_amount = self.calculate_tax(income, tax_type)
        report = {
            "operator": self.operator_name,
            "income": income,
            "tax_type": tax_type,
            "tax_amount": tax_amount,
            "due_date": self.tax_deadlines[tax_type],
            "compliant": self.check_compliance(tax_type, datetime.now()),
        }
        logger.info(f"Generated tax report for {self.operator_name}: {report}")
        return report


if __name__ == "__main__":
    optimizer = KRA_Tax_Optimizer()
    income = 100000.0
    tax_type = "personal_income_tax"
    report = optimizer.generate_tax_report(income, tax_type)
    print(json.dumps(report, indent=2))
