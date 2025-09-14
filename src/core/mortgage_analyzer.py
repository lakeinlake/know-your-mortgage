"""
Mortgage Analysis Engine

This module contains the core MortgageAnalyzer class that performs
comprehensive mortgage scenario analysis and financial calculations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from .scenario import MortgageScenario


class MortgageAnalyzer:
    """Comprehensive mortgage analysis tool for comparing different financing scenarios."""

    def __init__(self, home_price: float = 500000, emergency_fund: float = 50000):
        """
        Initialize the mortgage analyzer with base parameters.

        Args:
            home_price: Price of the home
            emergency_fund: Amount to keep as emergency fund (not invested)
        """
        self.home_price = home_price
        self.emergency_fund = emergency_fund
        self.analysis_period = 30  # Years to analyze

    def calculate_monthly_payment(self, loan_amount: float, annual_rate: float, years: int) -> float:
        """
        Calculate monthly mortgage payment using standard amortization formula.

        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate (as decimal)
            years: Loan term in years

        Returns:
            Monthly payment amount
        """
        if loan_amount <= 0:
            return 0

        monthly_rate = annual_rate / 12
        n_payments = years * 12

        if monthly_rate == 0:
            return loan_amount / n_payments

        payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                  ((1 + monthly_rate)**n_payments - 1)
        return payment

    def calculate_amortization_schedule(self, loan_amount: float, annual_rate: float,
                                      years: int) -> pd.DataFrame:
        """
        Generate complete amortization schedule for a mortgage.

        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate (as decimal)
            years: Loan term in years

        Returns:
            DataFrame with payment schedule details
        """
        if loan_amount <= 0:
            return pd.DataFrame()

        monthly_payment = self.calculate_monthly_payment(loan_amount, annual_rate, years)
        monthly_rate = annual_rate / 12
        n_payments = years * 12

        schedule = []
        balance = loan_amount

        for month in range(1, n_payments + 1):
            interest_payment = balance * monthly_rate
            principal_payment = monthly_payment - interest_payment
            balance -= principal_payment

            schedule.append({
                'Month': month,
                'Payment': monthly_payment,
                'Principal': principal_payment,
                'Interest': interest_payment,
                'Balance': max(0, balance)
            })

        return pd.DataFrame(schedule)

    def calculate_investment_growth(self, initial_amount: float, monthly_contribution: float,
                                  annual_return: float, years: int) -> float:
        """
        Calculate future value of investments with compound growth.

        Args:
            initial_amount: Initial investment amount
            monthly_contribution: Monthly addition to investment
            annual_return: Expected annual return rate
            years: Investment period in years

        Returns:
            Future value of investment
        """
        monthly_return = annual_return / 12
        n_months = years * 12

        # Future value of initial amount
        fv_initial = initial_amount * (1 + monthly_return)**n_months

        # Future value of monthly contributions
        if monthly_return > 0:
            fv_contributions = monthly_contribution * \
                              (((1 + monthly_return)**n_months - 1) / monthly_return)
        else:
            fv_contributions = monthly_contribution * n_months

        return fv_initial + fv_contributions

    def adjust_for_inflation(self, amount: float, years: int, inflation_rate: float) -> float:
        """
        Adjust future value to present value accounting for inflation.

        Args:
            amount: Future nominal amount
            years: Number of years in the future
            inflation_rate: Annual inflation rate

        Returns:
            Present value in today's dollars
        """
        return amount / (1 + inflation_rate)**years

    def calculate_tax_deduction(self, interest_paid: float, tax_rate: float) -> float:
        """
        Calculate tax savings from mortgage interest deduction.

        Args:
            interest_paid: Annual interest paid
            tax_rate: Marginal tax rate

        Returns:
            Tax savings amount
        """
        return interest_paid * tax_rate

    def analyze_scenario(self, scenario: MortgageScenario) -> Dict:
        """
        Perform comprehensive analysis of a single mortgage scenario.

        Args:
            scenario: MortgageScenario object with all parameters

        Returns:
            Dictionary containing all analysis results
        """
        results = {
            'name': scenario.name,
            'home_price': scenario.home_price,
            'down_payment': scenario.down_payment,
            'loan_amount': scenario.loan_amount,
            'monthly_payment': 0,
            'total_interest_paid': 0,
            'total_payments': 0,
            'yearly_data': [],
            'final_net_worth': 0,
            'final_net_worth_adjusted': 0
        }

        # Handle cash purchase scenario
        if scenario.loan_amount <= 0:
            results['monthly_payment'] = 0
            initial_investment = self.home_price - scenario.down_payment

            for year in range(1, self.analysis_period + 1):
                home_value = self.home_price * (1 + scenario.home_appreciation_rate)**year
                property_tax = home_value * scenario.property_tax_rate

                # All extra money is invested
                investment_value = self.calculate_investment_growth(
                    initial_investment,
                    0,  # No monthly contributions for cash purchase
                    scenario.stock_return,
                    year
                )

                net_worth = home_value + investment_value + self.emergency_fund
                net_worth_adjusted = self.adjust_for_inflation(
                    net_worth, year, scenario.inflation_rate
                )

                results['yearly_data'].append({
                    'year': year,
                    'home_value': home_value,
                    'loan_balance': 0,
                    'home_equity': home_value,
                    'investment_value': investment_value,
                    'property_tax': property_tax,
                    'net_worth': net_worth,
                    'net_worth_adjusted': net_worth_adjusted
                })

            results['final_net_worth'] = results['yearly_data'][-1]['net_worth']
            results['final_net_worth_adjusted'] = results['yearly_data'][-1]['net_worth_adjusted']

            return results

        # Calculate mortgage payments
        monthly_payment = self.calculate_monthly_payment(
            scenario.loan_amount, scenario.interest_rate, scenario.term_years
        )
        results['monthly_payment'] = monthly_payment

        # Generate amortization schedule
        amortization = self.calculate_amortization_schedule(
            scenario.loan_amount, scenario.interest_rate, scenario.term_years
        )

        # Calculate totals
        results['total_payments'] = monthly_payment * scenario.term_years * 12
        results['total_interest_paid'] = results['total_payments'] - scenario.loan_amount

        # Calculate available money for investment
        # Assume baseline is 30-year mortgage with $100K down
        baseline_payment = self.calculate_monthly_payment(
            self.home_price - 100000, 0.061, 30
        )

        # Money available for investment after down payment
        initial_investment = max(0, 300000 - scenario.down_payment - self.emergency_fund)

        # Monthly investment (difference from baseline payment)
        monthly_investment = max(0, baseline_payment - monthly_payment)

        # Year-by-year analysis
        for year in range(1, self.analysis_period + 1):
            month_end = min(year * 12, len(amortization))

            # Home value with appreciation
            home_value = self.home_price * (1 + scenario.home_appreciation_rate)**year

            # Loan balance
            if month_end < len(amortization):
                loan_balance = amortization.iloc[month_end - 1]['Balance']
            elif year <= scenario.term_years:
                loan_balance = amortization.iloc[-1]['Balance']
            else:
                loan_balance = 0

            # Home equity
            home_equity = home_value - loan_balance

            # Calculate interest paid this year for tax deduction
            year_start_month = (year - 1) * 12
            year_end_month = min(year * 12, len(amortization))

            if year_start_month < len(amortization):
                yearly_interest = amortization.iloc[year_start_month:year_end_month]['Interest'].sum()
                tax_savings = self.calculate_tax_deduction(yearly_interest, scenario.tax_rate)
            else:
                yearly_interest = 0
                tax_savings = 0

            # Investment calculations
            # After mortgage is paid off, invest the payment amount
            if year > scenario.term_years:
                monthly_investment_current = monthly_payment + monthly_investment
            else:
                monthly_investment_current = monthly_investment

            investment_value = self.calculate_investment_growth(
                initial_investment,
                monthly_investment_current + (tax_savings / 12),
                scenario.stock_return,
                year
            )

            # Property tax
            property_tax = home_value * scenario.property_tax_rate

            # Net worth calculation
            net_worth = home_equity + investment_value + self.emergency_fund
            net_worth_adjusted = self.adjust_for_inflation(net_worth, year, scenario.inflation_rate)

            results['yearly_data'].append({
                'year': year,
                'home_value': home_value,
                'loan_balance': loan_balance,
                'home_equity': home_equity,
                'investment_value': investment_value,
                'yearly_interest': yearly_interest,
                'tax_savings': tax_savings,
                'property_tax': property_tax,
                'net_worth': net_worth,
                'net_worth_adjusted': net_worth_adjusted
            })

        results['final_net_worth'] = results['yearly_data'][-1]['net_worth']
        results['final_net_worth_adjusted'] = results['yearly_data'][-1]['net_worth_adjusted']

        return results

    def create_scenarios(self, home_price: float, rate_15yr: float = 0.056,
                        rate_30yr: float = 0.061, stock_return: float = 0.08,
                        inflation: float = 0.03) -> List[MortgageScenario]:
        """
        Create standard comparison scenarios.

        Args:
            home_price: Price of the home
            rate_15yr: Interest rate for 15-year mortgage
            rate_30yr: Interest rate for 30-year mortgage
            stock_return: Expected stock market return
            inflation: Expected inflation rate

        Returns:
            List of MortgageScenario objects
        """
        scenarios = [
            MortgageScenario(
                name="30-Year, $100K Down",
                home_price=home_price,
                down_payment=100000,
                loan_amount=home_price - 100000,
                interest_rate=rate_30yr,
                term_years=30,
                stock_return=stock_return,
                inflation_rate=inflation
            ),
            MortgageScenario(
                name="15-Year, $100K Down",
                home_price=home_price,
                down_payment=100000,
                loan_amount=home_price - 100000,
                interest_rate=rate_15yr,
                term_years=15,
                stock_return=stock_return,
                inflation_rate=inflation
            ),
            MortgageScenario(
                name="15-Year, $200K Down",
                home_price=home_price,
                down_payment=200000,
                loan_amount=home_price - 200000,
                interest_rate=rate_15yr,
                term_years=15,
                stock_return=stock_return,
                inflation_rate=inflation
            ),
            MortgageScenario(
                name="Cash Purchase",
                home_price=home_price,
                down_payment=home_price,
                loan_amount=0,
                interest_rate=0,
                term_years=0,
                stock_return=stock_return,
                inflation_rate=inflation
            )
        ]

        return scenarios

    def compare_scenarios(self, scenarios: List[MortgageScenario]) -> pd.DataFrame:
        """
        Compare multiple mortgage scenarios side by side.

        Args:
            scenarios: List of MortgageScenario objects to compare

        Returns:
            DataFrame with comparison results
        """
        comparisons = []

        for scenario in scenarios:
            results = self.analyze_scenario(scenario)

            comparison = {
                'Scenario': scenario.name,
                'Down Payment': f"${scenario.down_payment:,.0f}",
                'Loan Amount': f"${scenario.loan_amount:,.0f}",
                'Monthly Payment': f"${results['monthly_payment']:,.0f}",
                'Total Interest': f"${results['total_interest_paid']:,.0f}",
                'Final Net Worth (Nominal)': f"${results['final_net_worth']:,.0f}",
                'Final Net Worth (Real)': f"${results['final_net_worth_adjusted']:,.0f}",
                'Rank': 0
            }
            comparisons.append(comparison)

        df = pd.DataFrame(comparisons)

        # Rank scenarios by final net worth (real)
        net_worth_values = [float(nw.replace('$', '').replace(',', ''))
                           for nw in df['Final Net Worth (Real)']]
        df['Rank'] = pd.Series(net_worth_values).rank(ascending=False, method='min').astype(int)
        df = df.sort_values('Rank')

        return df

    def get_summary_statistics(self, scenarios: List[MortgageScenario]) -> Dict:
        """
        Calculate summary statistics across all scenarios.

        Args:
            scenarios: List of scenarios to analyze

        Returns:
            Dictionary with summary statistics
        """
        stats = {
            'best_scenario': None,
            'worst_scenario': None,
            'max_final_wealth': 0,
            'min_final_wealth': float('inf'),
            'scenarios_analyzed': len(scenarios)
        }

        for scenario in scenarios:
            results = self.analyze_scenario(scenario)
            final_wealth = results['final_net_worth_adjusted']

            if final_wealth > stats['max_final_wealth']:
                stats['max_final_wealth'] = final_wealth
                stats['best_scenario'] = scenario.name

            if final_wealth < stats['min_final_wealth']:
                stats['min_final_wealth'] = final_wealth
                stats['worst_scenario'] = scenario.name

        stats['wealth_difference'] = stats['max_final_wealth'] - stats['min_final_wealth']
        stats['wealth_difference_pct'] = (stats['wealth_difference'] / stats['min_final_wealth']) * 100

        return stats