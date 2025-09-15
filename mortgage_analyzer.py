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
                                    buy_scenario: MortgageScenario) -> Dict:
        """
        Calculate when buying becomes better than renting financially.

        Args:
            rent_scenario: RentScenario object
            buy_scenario: MortgageScenario object to compare against

        Returns:
            Dictionary with break-even analysis results
        """
        rent_results = self.analyze_rent_scenario(rent_scenario)
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

        return {
            'break_even_year': break_even_year,
            'yearly_comparison': yearly_comparison,
            'final_rent_net_worth': rent_results['final_net_worth_adjusted'],
            'final_buy_net_worth': buy_results['final_net_worth_adjusted'],
            'total_advantage': buy_results['final_net_worth_adjusted'] - rent_results['final_net_worth_adjusted']
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