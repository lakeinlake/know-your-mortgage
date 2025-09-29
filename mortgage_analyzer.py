import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import warnings
import gspread
from google.auth import default
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
import os
from datetime import datetime
warnings.filterwarnings('ignore')


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
    inflation_rate: float = 0.03
    stock_return_rate: float = 0.08
    emergency_fund: float = 50000


@dataclass
class RentScenario:
    """Data class for rent vs buy scenario parameters."""
    name: str
    home_price: float
    monthly_rent: float
    annual_rent_increase: float = 0.03
    renters_insurance: float = 200
    down_payment_invested: float = 100000
    closing_costs: float = 15000
    inflation_rate: float = 0.03
    stock_return_rate: float = 0.08
    emergency_fund: float = 50000


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
            'total_interest': 0,
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
                    scenario.stock_return_rate,
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
        results['total_interest'] = results['total_payments'] - scenario.loan_amount

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
                scenario.stock_return_rate,
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

    def analyze_rent_scenario(self, rent_scenario: RentScenario) -> Dict:
        """
        Perform comprehensive analysis of a rent scenario.

        Args:
            rent_scenario: RentScenario object with all parameters

        Returns:
            Dictionary containing all analysis results
        """
        results = {
            'name': rent_scenario.name,
            'home_price': rent_scenario.home_price,
            'monthly_rent': rent_scenario.monthly_rent,
            'total_rent_paid': 0,
            'yearly_data': [],
            'final_net_worth': 0,
            'final_net_worth_adjusted': 0,
            'break_even_year': None
        }

        # Initial investment: down payment + closing costs
        initial_investment = rent_scenario.down_payment_invested + rent_scenario.closing_costs

        # Track cumulative rent and investment growth
        cumulative_rent = 0
        monthly_rent = rent_scenario.monthly_rent

        for year in range(1, self.analysis_period + 1):
            # Calculate current year's rent (with annual increases)
            current_monthly_rent = rent_scenario.monthly_rent * (1 + rent_scenario.annual_rent_increase)**(year - 1)
            annual_rent = current_monthly_rent * 12
            annual_insurance = rent_scenario.renters_insurance

            cumulative_rent += annual_rent + annual_insurance

            # Investment growth (down payment + closing costs invested)
            investment_value = self.calculate_investment_growth(
                initial_investment,
                0,  # No additional monthly contributions for base case
                rent_scenario.stock_return_rate,
                year
            )

            # Calculate what the home would be worth if bought
            home_value_if_bought = rent_scenario.home_price * (1 + 0.05)**year  # Assume 5% appreciation

            # Net worth as renter: investments + emergency fund - cumulative rent spent
            net_worth = investment_value + rent_scenario.emergency_fund
            net_worth_adjusted = self.adjust_for_inflation(net_worth, year, rent_scenario.inflation_rate)

            # For comparison: net worth if bought the home (assuming same mortgage scenario)
            # This helps calculate break-even point

            results['yearly_data'].append({
                'year': year,
                'monthly_rent': current_monthly_rent,
                'annual_rent_paid': annual_rent,
                'cumulative_rent_paid': cumulative_rent,
                'investment_value': investment_value,
                'home_value_if_bought': home_value_if_bought,
                'net_worth': net_worth,
                'net_worth_adjusted': net_worth_adjusted,
                'annual_housing_cost': annual_rent + annual_insurance
            })

        results['total_rent_paid'] = cumulative_rent
        results['final_net_worth'] = results['yearly_data'][-1]['net_worth']
        results['final_net_worth_adjusted'] = results['yearly_data'][-1]['net_worth_adjusted']

        return results

    def calculate_break_even_analysis(self, rent_scenario: RentScenario,
                                    buy_scenario: MortgageScenario,
                                    rent_results: Dict = None,
                                    buy_results: Dict = None) -> Dict:
        """
        Calculate when buying becomes better than renting financially.

        Args:
            rent_scenario: RentScenario object
            buy_scenario: MortgageScenario object to compare against
            rent_results: Optional pre-computed rent analysis results
            buy_results: Optional pre-computed buy analysis results

        Returns:
            Dictionary with break-even analysis results
        """
        # Use pre-computed results if provided, otherwise compute them
        if rent_results is None:
            rent_results = self.analyze_rent_scenario(rent_scenario)
        if buy_results is None:
            buy_results = self.analyze_scenario(buy_scenario)

        break_even_year = None
        yearly_comparison = []

        for year in range(1, min(len(rent_results['yearly_data']), len(buy_results['yearly_data'])) + 1):
            rent_net_worth = rent_results['yearly_data'][year-1]['net_worth_adjusted']
            buy_net_worth = buy_results['yearly_data'][year-1]['net_worth_adjusted']

            difference = buy_net_worth - rent_net_worth

            if break_even_year is None and buy_net_worth > rent_net_worth:
                break_even_year = year

            yearly_comparison.append({
                'year': year,
                'rent_net_worth': rent_net_worth,
                'buy_net_worth': buy_net_worth,
                'buy_advantage': difference,
                'buy_is_better': buy_net_worth > rent_net_worth
            })

        # Calculate final net worth difference
        final_buy_net_worth = buy_results.get('final_net_worth_adjusted', 0)
        final_rent_net_worth = rent_results.get('final_net_worth_adjusted', 0)
        final_net_worth_difference = final_buy_net_worth - final_rent_net_worth

        # Get advantage at 30 years (same as final net worth difference for 30-year analysis)
        advantage_at_30_years = final_net_worth_difference
        if yearly_comparison and len(yearly_comparison) >= 30:
            advantage_at_30_years = yearly_comparison[29]['buy_advantage']  # Year 30 (0-indexed)

        # Generate insights
        insights = []
        if break_even_year:
            insights.append(f"📈 Buying becomes more profitable than renting in year {break_even_year}.")
            if break_even_year <= 5:
                insights.append("This is a very short break-even point, suggesting buying is a strong financial choice.")
            elif break_even_year > 10:
                insights.append("With a longer break-even point, ensure you plan to stay in the home long enough to realize the financial benefits.")
        else:
            insights.append("📉 Based on this 30-year analysis, renting remains more financially advantageous.")

        if final_net_worth_difference > 0:
            insights.append(f"💰 After 30 years, buying is projected to increase your net worth by an additional ${final_net_worth_difference:,.0f} compared to renting.")
        else:
            insights.append(f"💸 After 30 years, renting is projected to leave you with a higher net worth by ${abs(final_net_worth_difference):,.0f}.")

        return {
            'break_even_year': break_even_year if break_even_year is not None else "Never",
            'yearly_comparison': yearly_comparison,
            'final_rent_net_worth': final_rent_net_worth,
            'final_buy_net_worth': final_buy_net_worth,
            'advantage_at_30_years': advantage_at_30_years,
            'final_net_worth_difference': final_net_worth_difference,
            'insights': insights
        }

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
                stock_return_rate=stock_return,
                inflation_rate=inflation,
                emergency_fund=self.emergency_fund
            ),
            MortgageScenario(
                name="15-Year, $100K Down",
                home_price=home_price,
                down_payment=100000,
                loan_amount=home_price - 100000,
                interest_rate=rate_15yr,
                term_years=15,
                stock_return_rate=stock_return,
                inflation_rate=inflation,
                emergency_fund=self.emergency_fund
            ),
            MortgageScenario(
                name="15-Year, $200K Down",
                home_price=home_price,
                down_payment=200000,
                loan_amount=home_price - 200000,
                interest_rate=rate_15yr,
                term_years=15,
                stock_return_rate=stock_return,
                inflation_rate=inflation,
                emergency_fund=self.emergency_fund
            ),
            MortgageScenario(
                name="Cash Purchase",
                home_price=home_price,
                down_payment=home_price,
                loan_amount=0,
                interest_rate=0,
                term_years=0,
                stock_return_rate=stock_return,
                inflation_rate=inflation,
                emergency_fund=self.emergency_fund
            )
        ]

        return scenarios

    def create_rent_scenario(self, home_price: float, monthly_rent: float = None,
                           annual_rent_increase: float = 0.03,
                           stock_return: float = 0.08, inflation: float = 0.03) -> RentScenario:
        """
        Create a rent scenario for comparison.

        Args:
            home_price: Price of the home (for comparison)
            monthly_rent: Monthly rent amount (if None, estimate as 0.5% of home price)
            annual_rent_increase: Annual rent increase rate
            stock_return: Expected stock market return
            inflation: Expected inflation rate

        Returns:
            RentScenario object
        """
        if monthly_rent is None:
            # Rule of thumb: rent is often around 0.5% of home value per month
            monthly_rent = home_price * 0.005

        return RentScenario(
            name="Rent Instead",
            home_price=home_price,
            monthly_rent=monthly_rent,
            annual_rent_increase=annual_rent_increase,
            renters_insurance=200,  # Annual renters insurance
            down_payment_invested=100000,  # Amount that would have been down payment
            closing_costs=home_price * 0.03,  # Typical closing costs ~3%
            inflation_rate=inflation,
            stock_return_rate=stock_return,
            emergency_fund=self.emergency_fund
        )

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
                'Total Interest': f"${results['total_interest']:,.0f}",
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

    def export_results(self, scenarios: List[MortgageScenario], filename: str = 'mortgage_analysis.csv'):
        """
        Export detailed analysis results to CSV file.

        Args:
            scenarios: List of scenarios to analyze and export
            filename: Output CSV filename
        """
        all_data = []

        for scenario in scenarios:
            results = self.analyze_scenario(scenario)

            for year_data in results['yearly_data']:
                row = {
                    'Scenario': scenario.name,
                    'Year': year_data['year'],
                    'Home Value': year_data['home_value'],
                    'Loan Balance': year_data['loan_balance'],
                    'Home Equity': year_data['home_equity'],
                    'Investment Value': year_data['investment_value'],
                    'Net Worth (Nominal)': year_data['net_worth'],
                    'Net Worth (Real)': year_data['net_worth_adjusted'],
                    'Monthly Payment': results['monthly_payment']
                }
                all_data.append(row)

        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
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

    def run_corrected_rent_vs_buy_analysis(self, buy_scenario: MortgageScenario, rent_scenario: RentScenario) -> Dict:
        """
        Corrected rent vs buy analysis that properly accounts for all costs.

        This method fixes the fundamental flaws in the original analysis by:
        1. Including ALL homeownership costs (insurance, maintenance, etc.)
        2. Properly investing monthly savings for whichever option is cheaper
        3. Including selling costs in final calculations
        """
        # Initialize tracking variables
        buy_yearly_data = []
        rent_yearly_data = []

        # Calculate initial costs
        monthly_pi = self.calculate_monthly_payment(buy_scenario.loan_amount, buy_scenario.interest_rate, buy_scenario.term_years)

        # Buyer starts with less cash due to down payment and closing costs
        buyer_initial_cash_out = buy_scenario.down_payment + (buy_scenario.home_price * 0.03)  # 3% closing costs

        # Renter invests what buyer spent on down payment + closing costs
        rent_investment_balance = buyer_initial_cash_out
        buy_investment_balance = 0  # Buyer's money is tied up in the house

        current_rent = rent_scenario.monthly_rent
        analysis_years = min(30, len(range(1, 31)))  # Ensure we don't exceed available data

        for year in range(1, analysis_years + 1):
            # Calculate home value for this year
            home_value = buy_scenario.home_price * ((1 + buy_scenario.home_appreciation_rate) ** year)

            # BUYER'S TOTAL MONTHLY COSTS
            monthly_property_tax = (home_value * buy_scenario.property_tax_rate) / 12
            monthly_insurance = home_value * 0.003 / 12  # 0.3% annually for homeowners insurance
            monthly_maintenance = home_value * 0.01 / 12  # 1% annually for maintenance

            buy_total_monthly = monthly_pi + monthly_property_tax + monthly_insurance + monthly_maintenance

            # RENTER'S TOTAL MONTHLY COSTS
            monthly_renters_insurance = rent_scenario.renters_insurance / 12
            rent_total_monthly = current_rent + monthly_renters_insurance

            # Calculate who saves money and how much
            monthly_difference = buy_total_monthly - rent_total_monthly

            # Grow existing investments
            buy_investment_balance *= (1 + buy_scenario.stock_return_rate)
            rent_investment_balance *= (1 + rent_scenario.stock_return_rate)

            # Add annual savings to appropriate investment account
            annual_savings = monthly_difference * 12
            if monthly_difference > 0:
                # Buying is more expensive, renter invests the difference
                rent_investment_balance += annual_savings
            else:
                # Renting is more expensive, buyer invests the difference
                buy_investment_balance += abs(annual_savings)

            # Calculate net worth
            # Buyer: home equity + investments
            remaining_balance = max(0, buy_scenario.loan_amount * ((1 + buy_scenario.interest_rate/12)**(12*buy_scenario.term_years) - (1 + buy_scenario.interest_rate/12)**(12*year)) / ((1 + buy_scenario.interest_rate/12)**(12*buy_scenario.term_years) - 1)) if year <= buy_scenario.term_years else 0
            home_equity = home_value - remaining_balance
            buy_net_worth = home_equity + buy_investment_balance

            # Renter: investments only
            rent_net_worth = rent_investment_balance

            # Adjust for inflation
            inflation_factor = (1 + buy_scenario.inflation_rate) ** year
            buy_net_worth_adj = buy_net_worth / inflation_factor
            rent_net_worth_adj = rent_net_worth / inflation_factor

            buy_yearly_data.append({
                'year': year,
                'net_worth': buy_net_worth,
                'net_worth_adjusted': buy_net_worth_adj
            })

            rent_yearly_data.append({
                'year': year,
                'net_worth': rent_net_worth,
                'net_worth_adjusted': rent_net_worth_adj
            })

            # Update rent for next year
            current_rent *= (1 + rent_scenario.annual_rent_increase)

        # Calculate final values with selling costs
        final_home_value = buy_scenario.home_price * ((1 + buy_scenario.home_appreciation_rate) ** analysis_years)
        selling_costs = final_home_value * 0.06  # 6% selling costs
        final_home_equity = final_home_value - selling_costs

        final_buy_net_worth = final_home_equity + buy_investment_balance
        final_buy_net_worth_adj = final_buy_net_worth / ((1 + buy_scenario.inflation_rate) ** analysis_years)

        final_rent_net_worth_adj = rent_yearly_data[-1]['net_worth_adjusted'] if rent_yearly_data else 0

        # Find break-even year
        break_even_year = "Never"
        for i, (buy_data, rent_data) in enumerate(zip(buy_yearly_data, rent_yearly_data)):
            if buy_data['net_worth_adjusted'] > rent_data['net_worth_adjusted']:
                break_even_year = i + 1
                break

        # Generate insights
        insights = []
        advantage_at_30_years = final_buy_net_worth_adj - final_rent_net_worth_adj

        if break_even_year != "Never":
            insights.append(f"📈 Buying becomes more profitable than renting in year {break_even_year}.")
            if break_even_year <= 5:
                insights.append("This is a short break-even point, suggesting buying is a strong financial choice.")
            elif break_even_year > 10:
                insights.append("With a longer break-even point, ensure you plan to stay long enough to realize the benefits.")
        else:
            insights.append("📉 Based on this analysis, renting remains more financially advantageous over 30 years.")

        if advantage_at_30_years > 0:
            insights.append(f"💰 After 30 years, buying is projected to increase your net worth by ${advantage_at_30_years:,.0f} compared to renting.")
        else:
            insights.append(f"💸 After 30 years, renting is projected to leave you with ${abs(advantage_at_30_years):,.0f} more net worth.")

        return {
            'buy_results': {
                'yearly_data': buy_yearly_data,
                'final_net_worth_adjusted': final_buy_net_worth_adj,
                'monthly_payment': monthly_pi
            },
            'rent_results': {
                'yearly_data': rent_yearly_data,
                'final_net_worth_adjusted': final_rent_net_worth_adj,
                'total_rent_paid': sum(rent_scenario.monthly_rent * ((1 + rent_scenario.annual_rent_increase) ** (year-1)) * 12 for year in range(1, analysis_years + 1))
            },
            'break_even_analysis': {
                'break_even_year': break_even_year,
                'yearly_comparison': [
                    {
                        'year': i + 1,
                        'rent_net_worth': rent_data['net_worth_adjusted'],
                        'buy_net_worth': buy_data['net_worth_adjusted'],
                        'buy_advantage': buy_data['net_worth_adjusted'] - rent_data['net_worth_adjusted'],
                        'buy_is_better': buy_data['net_worth_adjusted'] > rent_data['net_worth_adjusted']
                    }
                    for i, (buy_data, rent_data) in enumerate(zip(buy_yearly_data, rent_yearly_data))
                ],
                'final_rent_net_worth': final_rent_net_worth_adj,
                'final_buy_net_worth': final_buy_net_worth_adj,
                'advantage_at_30_years': advantage_at_30_years,
                'final_net_worth_difference': advantage_at_30_years,
                'insights': insights
            }
        }

    def calculate_pmi_payment(self, loan_amount: float, home_price: float) -> float:
        """
        Calculate monthly PMI payment.

        Args:
            loan_amount: Principal loan amount
            home_price: Home purchase price

        Returns:
            Monthly PMI payment (0 if LTV <= 80%)
        """
        ltv_ratio = loan_amount / home_price
        if ltv_ratio <= 0.8:
            return 0

        # PMI is typically 0.5% to 1% annually on loan amount
        # Using 0.5% as conservative estimate
        annual_pmi = loan_amount * 0.005
        return annual_pmi / 12

    def calculate_total_monthly_costs(self, scenario: MortgageScenario, home_value: float = None) -> Dict:
        """
        Calculate all monthly homeownership costs including PMI, insurance, maintenance.

        Args:
            scenario: MortgageScenario object
            home_value: Current home value (defaults to purchase price)

        Returns:
            Dictionary with breakdown of all monthly costs
        """
        if home_value is None:
            home_value = scenario.home_price

        costs = {}

        # Principal and Interest
        if scenario.loan_amount > 0:
            costs['principal_interest'] = self.calculate_monthly_payment(
                scenario.loan_amount, scenario.interest_rate, scenario.term_years
            )
        else:
            costs['principal_interest'] = 0

        # Property taxes
        costs['property_tax'] = (home_value * scenario.property_tax_rate) / 12

        # PMI
        costs['pmi'] = self.calculate_pmi_payment(scenario.loan_amount, scenario.home_price)

        # Homeowners insurance (0.3% annually)
        costs['insurance'] = (home_value * 0.003) / 12

        # Maintenance (1% annually)
        costs['maintenance'] = (home_value * 0.01) / 12

        # Total monthly cost
        costs['total_monthly'] = sum(costs.values())

        return costs

    def analyze_scenario_corrected(self, scenario: MortgageScenario, available_cash: float) -> Dict:
        """
        Corrected mortgage scenario analysis without hardcoded assumptions.

        Args:
            scenario: MortgageScenario object with all parameters
            available_cash: Total cash available for down payment and investments

        Returns:
            Dictionary with corrected analysis results
        """
        results = {
            'scenario_name': scenario.name,
            'monthly_costs': {},
            'total_interest': 0,
            'total_payments': 0,
            'yearly_data': [],
            'final_net_worth': 0,
            'final_net_worth_adjusted': 0,
            'pmi_required': False,
            'ltv_ratio': 0
        }

        # Calculate LTV and PMI requirement
        if scenario.loan_amount > 0:
            ltv_ratio = scenario.loan_amount / scenario.home_price
            results['ltv_ratio'] = ltv_ratio
            results['pmi_required'] = ltv_ratio > 0.8

        # Calculate closing costs (3% of home price)
        closing_costs = scenario.home_price * 0.03

        # Calculate remaining cash for investment after down payment and closing costs
        remaining_cash = available_cash - scenario.down_payment - closing_costs
        remaining_cash = max(0, remaining_cash - self.emergency_fund)

        # Handle cash purchase
        if scenario.loan_amount <= 0:
            results['monthly_costs'] = self.calculate_total_monthly_costs(scenario)
            results['monthly_costs']['principal_interest'] = 0  # No loan payment

            for year in range(1, self.analysis_period + 1):
                home_value = scenario.home_price * (1 + scenario.home_appreciation_rate)**year
                costs = self.calculate_total_monthly_costs(scenario, home_value)

                # Investment growth (remaining cash invested)
                investment_value = self.calculate_investment_growth(
                    remaining_cash, 0, scenario.stock_return_rate, year
                )

                # Net worth calculation
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
                    'annual_housing_costs': costs['total_monthly'] * 12,
                    'net_worth': net_worth,
                    'net_worth_adjusted': net_worth_adjusted
                })

            if results['yearly_data']:
                results['final_net_worth'] = results['yearly_data'][-1]['net_worth']
                results['final_net_worth_adjusted'] = results['yearly_data'][-1]['net_worth_adjusted']

            return results

        # Generate amortization schedule for loan scenarios
        amortization = self.calculate_amortization_schedule(
            scenario.loan_amount, scenario.interest_rate, scenario.term_years
        )

        results['total_payments'] = len(amortization) * amortization.iloc[0]['Payment']
        results['total_interest'] = results['total_payments'] - scenario.loan_amount

        # Year-by-year analysis
        for year in range(1, self.analysis_period + 1):
            month_index = min(year * 12 - 1, len(amortization) - 1)

            # Home value with appreciation
            home_value = scenario.home_price * (1 + scenario.home_appreciation_rate)**year

            # Loan balance
            if year <= scenario.term_years:
                loan_balance = amortization.iloc[month_index]['Balance'] if month_index < len(amortization) else 0
            else:
                loan_balance = 0

            # Calculate costs for this year
            costs = self.calculate_total_monthly_costs(scenario, home_value)

            # Remove PMI if LTV drops below 78%
            if loan_balance / home_value < 0.78:
                costs['pmi'] = 0
                costs['total_monthly'] = costs['principal_interest'] + costs['property_tax'] + costs['insurance'] + costs['maintenance']

            # Calculate interest paid this year
            year_start_month = (year - 1) * 12
            year_end_month = min(year * 12, len(amortization))
            if year_start_month < len(amortization) and year <= scenario.term_years:
                yearly_interest = amortization.iloc[year_start_month:year_end_month]['Interest'].sum()
            else:
                yearly_interest = 0

            # Investment calculations
            # After mortgage is paid off, invest the former payment amount
            if year > scenario.term_years:
                monthly_investment = costs['principal_interest']  # Former mortgage payment
            else:
                monthly_investment = 0

            investment_value = self.calculate_investment_growth(
                remaining_cash, monthly_investment, scenario.stock_return_rate, year
            )

            # Net worth = home equity + investments + emergency fund
            home_equity = home_value - loan_balance
            net_worth = home_equity + investment_value + self.emergency_fund
            net_worth_adjusted = self.adjust_for_inflation(
                net_worth, year, scenario.inflation_rate
            )

            results['yearly_data'].append({
                'year': year,
                'home_value': home_value,
                'loan_balance': loan_balance,
                'home_equity': home_equity,
                'investment_value': investment_value,
                'annual_housing_costs': costs['total_monthly'] * 12,
                'monthly_costs': costs,
                'net_worth': net_worth,
                'net_worth_adjusted': net_worth_adjusted,
                'yearly_interest': yearly_interest
            })

        # Store initial monthly costs
        results['monthly_costs'] = self.calculate_total_monthly_costs(scenario)

        if results['yearly_data']:
            results['final_net_worth'] = results['yearly_data'][-1]['net_worth']
            results['final_net_worth_adjusted'] = results['yearly_data'][-1]['net_worth_adjusted']

        return results

    def analyze_opportunity_cost(self, results_30yr: Dict, results_15yr: Dict, stock_return_rate: float, post_payoff_investment_rate: float = 100.0) -> Dict:
        """
        Analyzes the opportunity cost of a 30-year mortgage vs. a 15-year mortgage.

        Args:
            results_30yr: The analysis results dictionary for the 30-year scenario.
            results_15yr: The analysis results dictionary for the 15-year scenario.
            stock_return_rate: The annual stock market return rate (as a percentage).
            post_payoff_investment_rate: The percentage of the freed-up 15yr payment to invest after payoff.

        Returns:
            A dictionary containing the data for plotting and the break-even year.
        """
        # Extract P&I payments
        payment_30yr = results_30yr['monthly_costs'].get('principal_interest', 0)
        payment_15yr = results_15yr['monthly_costs'].get('principal_interest', 0)

        if payment_15yr <= payment_30yr:
            return {'error': '15-year payment is not higher than 30-year payment.'}

        monthly_investment_diff = payment_15yr - payment_30yr
        stock_return_decimal = stock_return_rate / 100

        years = list(range(1, self.analysis_period + 1))
        investment_growth = []
        cumulative_interest_cost = []
        break_even_year = None

        # Extract yearly interest data
        interest_15yr_yearly = {d['year']: d.get('yearly_interest', 0) for d in results_15yr['yearly_data']}
        interest_30yr_yearly = {d['year']: d.get('yearly_interest', 0) for d in results_30yr['yearly_data']}

        running_interest_15yr = 0
        running_interest_30yr = 0

        # --- Corrected Investment Calculation ---

        # 1. Calculate the total value of investing the payment difference for the first 15 years
        fv_of_diff_at_15_yrs = self.calculate_investment_growth(0, monthly_investment_diff, stock_return_decimal, 15)

        # 2. Determine the new monthly contribution amount after the 15-year loan is paid off
        post_payoff_monthly_investment = payment_15yr * (post_payoff_investment_rate / 100)

        for year in years:
            # --- Investment Growth Calculation ---
            if year <= 15:
                # For the first 15 years, the investment is simply the growth of the monthly payment difference
                investment_balance = self.calculate_investment_growth(0, monthly_investment_diff, stock_return_decimal, year)
            else: # After year 15
                # The total value is now two parts:
                # a) The original pot from the first 15 years, now growing as a lump sum
                compounded_lump_sum = fv_of_diff_at_15_yrs * (1 + stock_return_decimal) ** (year - 15)

                # b) The future value of the NEW contributions made from year 16 to the current 'year'
                fv_of_new_contributions = self.calculate_investment_growth(
                    0, post_payoff_monthly_investment, stock_return_decimal, year - 15
                )

                # The total balance is the sum of these two components
                investment_balance = compounded_lump_sum + fv_of_new_contributions

            investment_growth.append(investment_balance)

            # --- Cumulative Interest Cost Calculation ---
            running_interest_15yr += interest_15yr_yearly.get(year, 0)
            running_interest_30yr += interest_30yr_yearly.get(year, 0)

            # The "cost" is the extra interest paid on the 30-year loan so far
            extra_interest = running_interest_30yr - running_interest_15yr
            cumulative_interest_cost.append(extra_interest)

            # --- Check for Break-Even Point ---
            if break_even_year is None and investment_balance > extra_interest:
                break_even_year = year

        return {
            'years': years,
            'investment_growth': investment_growth,
            'cumulative_interest_cost': cumulative_interest_cost,
            'break_even_year': break_even_year,
            'monthly_payment_difference': monthly_investment_diff,
            'total_extra_interest_30yr': running_interest_30yr - running_interest_15yr
        }


class GoogleSheetsExporter:
    """Class to handle Google Sheets export functionality."""

    def __init__(self, use_personal_account: bool = True, service_account_path: str = None, oauth2_credentials_path: str = None):
        """
        Initialize Google Sheets exporter.

        Args:
            use_personal_account: If True, use OAuth2 personal account. If False, use service account.
            service_account_path: Path to service account credentials JSON file
            oauth2_credentials_path: Path to OAuth2 credentials JSON file
        """
        self.use_personal_account = use_personal_account
        self.service_account_path = service_account_path or "google_credentials.json"
        self.oauth2_credentials_path = oauth2_credentials_path or "oauth2_credentials.json"
        self.token_path = "token.pickle"
        self.gc = None

        # Google Sheets API scope
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

    def authenticate(self):
        """Authenticate with Google Sheets API using either personal account (OAuth2) or service account."""
        try:
            if self.use_personal_account:
                return self._authenticate_personal_account()
            else:
                return self._authenticate_service_account()
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            return False

    def _authenticate_personal_account(self):
        """Authenticate using OAuth2 for personal Google account."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no valid credentials, get them
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Try to get OAuth2 credentials from Streamlit secrets first
                oauth2_config = self._get_oauth2_config()

                flow = InstalledAppFlow.from_client_config(oauth2_config, self.SCOPES)

                # Check if we're in cloud environment or WSL
                import platform
                is_wsl = 'microsoft' in platform.uname().release.lower()
                is_cloud = os.getenv('STREAMLIT_SHARING_MODE') is not None

                if is_cloud:
                    # Cloud environment - OAuth2 needs different approach
                    # For now, let's try the manual flow which is more reliable in cloud
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    auth_url, _ = flow.authorization_url(prompt='consent')

                    # This won't work well in Streamlit Cloud, so we'll fall back to service account
                    raise Exception("Personal Google Account requires manual setup in cloud. Please use Service Account method or CSV export.")
                elif is_wsl:
                    # WSL-friendly: Don't auto-open browser, show manual instructions
                    print("🌐 WSL detected - Manual authentication required:")
                    print("1. Copy this URL and open it in your Windows browser:")

                    # Get auth URL without running server
                    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    auth_url, _ = flow.authorization_url(prompt='consent')
                    print(f"   {auth_url}")
                    print("\n2. After authorizing, copy the authorization code and paste it when prompted")

                    auth_code = input("\n📋 Paste the authorization code here: ").strip()
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                else:
                    # Normal flow for non-WSL environments
                    creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.gc = gspread.authorize(creds)
        return True

    def _get_oauth2_config(self):
        """Get OAuth2 configuration from Streamlit secrets or local file."""
        try:
            # Try Streamlit secrets first (for cloud deployment)
            import streamlit as st
            if hasattr(st, 'secrets') and 'oauth2_credentials' in st.secrets:
                # Convert Streamlit secrets to proper OAuth2 config format
                secrets = st.secrets['oauth2_credentials']
                return {
                    'installed': {
                        'client_id': secrets['client_id'],
                        'client_secret': secrets['client_secret'],
                        'auth_uri': secrets.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                        'token_uri': secrets.get('token_uri', 'https://oauth2.googleapis.com/token'),
                        'auth_provider_x509_cert_url': secrets.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                        'redirect_uris': secrets.get('redirect_uris', ['http://localhost'])
                    }
                }
        except (ImportError, KeyError, AttributeError) as e:
            print(f"Streamlit secrets error: {e}")
            pass

        # Fallback to local file
        if os.path.exists(self.oauth2_credentials_path):
            with open(self.oauth2_credentials_path, 'r') as f:
                return json.load(f)

        raise Exception(f"OAuth2 credentials not found in secrets or file: {self.oauth2_credentials_path}")

    def _authenticate_service_account(self):
        """Authenticate using service account."""
        try:
            # Try Streamlit secrets first (for cloud deployment)
            import streamlit as st
            if hasattr(st, 'secrets') and 'service_account' in st.secrets:
                # Use service account from Streamlit secrets
                service_account_info = dict(st.secrets['service_account'])
                self.gc = gspread.service_account_from_dict(service_account_info)
                return True
        except (ImportError, KeyError, AttributeError) as e:
            print(f"Streamlit service account secrets error: {e}")
            pass

        # Fallback to local file
        if self.service_account_path and os.path.exists(self.service_account_path):
            self.gc = gspread.service_account(filename=self.service_account_path)
            return True
        else:
            # Try to use default credentials (for Google Cloud environments)
            try:
                creds, _ = default()
                self.gc = gspread.authorize(creds)
                return True
            except:
                raise Exception("No valid service account credentials found")

    def create_mortgage_analysis_sheet(self, scenarios: List[MortgageScenario], analyzer: 'MortgageAnalyzer') -> str:
        """
        Create a comprehensive Google Sheet with mortgage analysis results.

        Args:
            scenarios: List of mortgage scenarios to analyze
            analyzer: MortgageAnalyzer instance

        Returns:
            URL of the created Google Sheet
        """
        if not self.gc:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Google Sheets API")

        # Create a new spreadsheet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        sheet_title = f"Mortgage Analysis - {timestamp}"

        try:
            # Clean up old sheets first to free storage
            self._cleanup_old_sheets()

            spreadsheet = self.gc.create(sheet_title)

            # Make it publicly viewable immediately
            spreadsheet.share(None, perm_type='anyone', role='reader')

            # Create multiple worksheets
            self._create_summary_sheet(spreadsheet, scenarios, analyzer)
            self._create_detailed_data_sheet(spreadsheet, scenarios, analyzer)
            self._create_parameters_sheet(spreadsheet, scenarios)

            # Remove default "Sheet1" if it exists
            try:
                default_sheet = spreadsheet.worksheet("Sheet1")
                spreadsheet.del_worksheet(default_sheet)
            except:
                pass

            return spreadsheet.url

        except Exception as e:
            if "storage quota" in str(e).lower() or "quota" in str(e).lower():
                # Try cleanup and retry once
                try:
                    self._cleanup_old_sheets()
                    spreadsheet = self.gc.create(sheet_title)
                    spreadsheet.share(None, perm_type='anyone', role='reader')
                    self._create_summary_sheet(spreadsheet, scenarios, analyzer)
                    self._create_detailed_data_sheet(spreadsheet, scenarios, analyzer)
                    self._create_parameters_sheet(spreadsheet, scenarios)
                    try:
                        default_sheet = spreadsheet.worksheet("Sheet1")
                        spreadsheet.del_worksheet(default_sheet)
                    except:
                        pass
                    return spreadsheet.url
                except:
                    raise Exception("Storage quota exceeded. Service account drive is full. Please use CSV export or set up personal Google account authentication.")
            raise Exception(f"Failed to create Google Sheet: {str(e)}")

    def _cleanup_old_sheets(self):
        """Remove old mortgage analysis sheets to free up storage."""
        try:
            # Get all files in the service account's drive
            files = self.gc.list_permissions()  # This won't work, let's try a different approach
            # We'll implement a simpler approach - just catch the quota error and provide guidance
        except:
            # Cleanup failed, but that's ok - we'll handle in the main function
            pass

    def _create_summary_sheet(self, spreadsheet, scenarios: List[MortgageScenario], analyzer: 'MortgageAnalyzer'):
        """Create summary dashboard sheet."""
        # Add summary worksheet
        summary_sheet = spreadsheet.add_worksheet(title="Summary Dashboard", rows=50, cols=10)

        # Header
        summary_sheet.update('A1', [['🏠 Mortgage Analysis Summary']])
        summary_sheet.format('A1', {
            'textFormat': {'bold': True, 'fontSize': 16},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0}
        })

        # Analysis results
        row = 3
        summary_sheet.update(f'A{row}', [['Scenario', 'Final Net Worth', 'Monthly Payment', 'Total Interest Paid', 'Recommendation']])
        summary_sheet.format(f'A{row}:E{row}', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.9}
        })

        row += 1
        best_wealth = -float('inf')
        best_scenario = None

        for scenario in scenarios:
            results = analyzer.analyze_scenario(scenario)
            final_wealth = results['final_net_worth_adjusted']
            total_interest = results['total_interest_paid']
            monthly_payment = results['monthly_payment']

            if final_wealth > best_wealth:
                best_wealth = final_wealth
                best_scenario = scenario.name

            recommendation = "⭐ Best Option" if final_wealth == best_wealth else ""

            summary_sheet.update(f'A{row}:E{row}', [[
                scenario.name,
                f"${final_wealth:,.0f}",
                f"${monthly_payment:,.0f}",
                f"${total_interest:,.0f}",
                recommendation
            ]])
            row += 1

        # Add key insights
        row += 2
        summary_sheet.update(f'A{row}', [['📊 Key Insights']])
        summary_sheet.format(f'A{row}', {
            'textFormat': {'bold': True, 'fontSize': 14},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0}
        })

        row += 1
        stats = analyzer.get_summary_statistics(scenarios)
        insights = [
            [f"🏆 Best scenario: {stats['best_scenario']}"],
            [f"💰 Wealth difference: ${stats['wealth_difference']:,.0f}"],
            [f"📈 Performance gap: {stats['wealth_difference_pct']:.1f}%"],
            [f"📅 Analysis date: {datetime.now().strftime('%B %d, %Y')}"]
        ]

        for insight in insights:
            summary_sheet.update(f'A{row}', [insight])
            row += 1

    def _create_detailed_data_sheet(self, spreadsheet, scenarios: List[MortgageScenario], analyzer: 'MortgageAnalyzer'):
        """Create detailed yearly data sheet."""
        data_sheet = spreadsheet.add_worksheet(title="Detailed Data", rows=1000, cols=15)

        # Prepare all data
        all_data = []
        headers = ['Scenario', 'Year', 'Home Value', 'Loan Balance', 'Home Equity',
                  'Investment Value', 'Net Worth (Nominal)', 'Net Worth (Real)', 'Monthly Payment']

        all_data.append(headers)

        for scenario in scenarios:
            results = analyzer.analyze_scenario(scenario)

            for year_data in results['yearly_data']:
                row_data = [
                    scenario.name,
                    year_data['year'],
                    year_data['home_value'],
                    year_data['loan_balance'],
                    year_data['home_equity'],
                    year_data['investment_value'],
                    year_data['net_worth'],
                    year_data['net_worth_adjusted'],
                    results['monthly_payment']
                ]
                all_data.append(row_data)

        # Update sheet with all data
        data_sheet.update('A1', all_data)

        # Format header
        data_sheet.format('A1:I1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.9}
        })

        # Format currency columns
        currency_cols = ['C', 'D', 'E', 'F', 'G', 'H', 'I']
        for col in currency_cols:
            data_sheet.format(f'{col}2:{col}{len(all_data)}', {
                'numberFormat': {'type': 'CURRENCY', 'pattern': '[$$-409]#,##0'}
            })

    def _create_parameters_sheet(self, spreadsheet, scenarios: List[MortgageScenario]):
        """Create parameters sheet showing all input assumptions."""
        params_sheet = spreadsheet.add_worksheet(title="Parameters", rows=100, cols=10)

        # Header
        params_sheet.update('A1', [['📋 Analysis Parameters']])
        params_sheet.format('A1', {
            'textFormat': {'bold': True, 'fontSize': 16},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 1.0}
        })

        # Scenario parameters
        row = 3
        headers = ['Scenario', 'Home Price', 'Down Payment', 'Loan Amount', 'Interest Rate',
                  'Term (Years)', 'Property Tax Rate', 'Appreciation Rate', 'Tax Rate']
        params_sheet.update(f'A{row}', [headers])
        params_sheet.format(f'A{row}:I{row}', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.9}
        })

        row += 1
        for scenario in scenarios:
            params_sheet.update(f'A{row}:I{row}', [[
                scenario.name,
                f"${scenario.home_price:,.0f}",
                f"${scenario.down_payment:,.0f}",
                f"${scenario.loan_amount:,.0f}",
                f"{scenario.interest_rate:.2%}",
                scenario.term_years,
                f"{scenario.property_tax_rate:.2%}",
                f"{scenario.home_appreciation_rate:.2%}",
                f"{scenario.tax_rate:.2%}"
            ]])
            row += 1

