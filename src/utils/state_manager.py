"""
State Management for Know Your Mortgage Application
Handles session state initialization, access, and retrieval.
"""
import streamlit as st
from src.data.tax_data import get_static_data


class SafeSessionState:
    """Guaranteed safe session state access - no race conditions possible"""

    # Define all defaults in one place
    DEFAULTS = {
        # Tax and location
        'selected_state': "California",
        'federal_bracket': "22% ($44,726 - $95,375)",
        'property_tax_rate': 0.75,
        'last_selected_state': "California",

        # Property parameters
        'home_price': 500000,
        'down_payment_1': 100000,
        'down_payment_2': 200000,

        # Mortgage rates
        'rate_30yr': 6.1,
        'rate_15yr': 5.6,

        # Economic assumptions
        'stock_return': 8.0,
        'inflation_rate': 3.0,
        'home_appreciation': 5.0,
        'emergency_fund': 50000,

        # Rent vs Buy parameters
        'monthly_rent': 2650,  # 80% of total housing cost (~$3,278)
        'rent_increase': 3.5,  # Slightly higher rent increases
        'renters_insurance': 200,

        # Financial Health parameters
        'annual_income': 96000,
        'monthly_debts': 500,
        'cash_savings': 150000,
        'stock_investments': 100000,
        'target_home_price': 500000,
        'target_down_payment': 100000,
        'mortgage_rate': 6.1,

        # Market Comparison parameters
        'selected_city': "Both Cities",
        'property_type': "Both Types",
        'selected_metric': "Median Price",
        'analysis_type': "Price Trends",
        'time_range': "Historical (2019-2024)",
        'show_correlations': False
    }

    @classmethod
    def get(cls, key):
        """GUARANTEED safe access - always returns a value"""
        return st.session_state.get(key, cls.DEFAULTS.get(key, 0))

    @classmethod
    def set(cls, key, value):
        """Safe setter"""
        st.session_state[key] = value

    @classmethod
    def ensure_initialized(cls):
        """Ensure all keys exist - called once per page"""
        for key, default_value in cls.DEFAULTS.items():
            if key not in st.session_state:
                st.session_state[key] = default_value


class AppState:
    """Clean state management using guaranteed safe access"""

    @staticmethod
    def initialize():
        """Initialize session state - guaranteed safe"""
        SafeSessionState.ensure_initialized()

    @staticmethod
    def get_tax_info():
        """Get current tax information"""
        state_tax_rates, _, federal_brackets = get_static_data()

        selected_state = SafeSessionState.get('selected_state')
        federal_bracket = SafeSessionState.get('federal_bracket')

        state_rate = state_tax_rates.get(selected_state, 13.3)
        federal_rate = federal_brackets.get(federal_bracket, 22)

        combined_rate = federal_rate + state_rate
        tax_rate = combined_rate / 100
        property_tax_rate = SafeSessionState.get('property_tax_rate') / 100

        return selected_state, tax_rate, property_tax_rate

    @staticmethod
    def get_common_params():
        """Get all common parameters"""
        return {
            'home_price': SafeSessionState.get('home_price'),
            'down_payment_1': SafeSessionState.get('down_payment_1'),
            'down_payment_2': SafeSessionState.get('down_payment_2'),
            'rate_30yr': SafeSessionState.get('rate_30yr') / 100,
            'rate_15yr': SafeSessionState.get('rate_15yr') / 100,
            'stock_return': SafeSessionState.get('stock_return') / 100,
            'inflation_rate': SafeSessionState.get('inflation_rate') / 100,
            'home_appreciation': SafeSessionState.get('home_appreciation') / 100,
            'emergency_fund': SafeSessionState.get('emergency_fund')
        }

    @staticmethod
    def get_rent_params():
        """Get rent-specific parameters"""
        return {
            'monthly_rent': SafeSessionState.get('monthly_rent'),
            'rent_increase': SafeSessionState.get('rent_increase') / 100,
            'renters_insurance': SafeSessionState.get('renters_insurance')
        }

    @staticmethod
    def get_financial_health_params():
        """Get financial health parameters"""
        return {
            'annual_income': SafeSessionState.get('annual_income'),
            'monthly_debts': SafeSessionState.get('monthly_debts'),
            'cash_savings': SafeSessionState.get('cash_savings'),
            'stock_investments': SafeSessionState.get('stock_investments'),
            'target_home_price': SafeSessionState.get('target_home_price'),
            'target_down_payment': SafeSessionState.get('target_down_payment'),
            'mortgage_rate': SafeSessionState.get('mortgage_rate') / 100
        }

    @staticmethod
    def get_market_comparison_params():
        """Get market comparison parameters"""
        return {
            'selected_city': SafeSessionState.get('selected_city'),
            'property_type': SafeSessionState.get('property_type'),
            'selected_metric': SafeSessionState.get('selected_metric'),
            'analysis_type': SafeSessionState.get('analysis_type'),
            'time_range': SafeSessionState.get('time_range'),
            'show_correlations': SafeSessionState.get('show_correlations')
        }


# Simple initialization function for easy access
def initialize():
    """Initialize the application state"""
    AppState.initialize()

# Direct access to state information
def get_tax_info():
    """Get current tax information"""
    return AppState.get_tax_info()