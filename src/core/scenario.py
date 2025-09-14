"""
Mortgage Scenario Data Class

This module contains the MortgageScenario dataclass that defines
the parameters for mortgage analysis scenarios.
"""

from dataclasses import dataclass


@dataclass
class MortgageScenario:
    """Data class for mortgage scenario parameters."""
    name: str
    home_price: float
    down_payment: float
    loan_amount: float
    interest_rate: float
    term_years: int
    property_tax_rate: float = 0.02
    home_appreciation_rate: float = 0.05
    tax_rate: float = 0.26
    stock_return: float = 0.10
    inflation_rate: float = 0.03

    def __post_init__(self):
        """Validate scenario parameters."""
        if self.home_price <= 0:
            raise ValueError("Home price must be positive")
        if self.down_payment < 0:
            raise ValueError("Down payment cannot be negative")
        if self.loan_amount < 0:
            raise ValueError("Loan amount cannot be negative")
        if self.interest_rate < 0 or self.interest_rate > 1:
            raise ValueError("Interest rate must be between 0 and 1")
        if self.term_years <= 0:
            raise ValueError("Term years must be positive")