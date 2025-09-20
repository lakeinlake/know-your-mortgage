"""
UI Components for Know Your Mortgage Application
Handles all sidebar UI rendering and user interactions.
"""
import streamlit as st
from src.data.tax_data import get_static_data
from src.utils.state_manager import SafeSessionState, AppState


class UIComponents:
    """Bulletproof UI components - zero race conditions"""

    @staticmethod
    def create_tax_sidebar():
        """Create tax selection sidebar"""
        state_tax_rates, property_tax_averages, federal_brackets = get_static_data()

        st.sidebar.subheader("🏛️ Tax Information")

        # State selection
        selected_state = st.sidebar.selectbox(
            "Select Your State",
            options=list(state_tax_rates.keys()),
            index=list(state_tax_rates.keys()).index(SafeSessionState.get('selected_state')),
            key="selected_state"
        )

        # Federal bracket selection
        federal_bracket = st.sidebar.selectbox(
            "Federal Tax Bracket (2024)",
            options=list(federal_brackets.keys()),
            index=list(federal_brackets.keys()).index(SafeSessionState.get('federal_bracket')),
            key="federal_bracket"
        )

        # Property tax with auto-update when state changes
        default_prop_tax = property_tax_averages.get(selected_state, 2.0)

        # Auto-update property tax when state changes
        if SafeSessionState.get('last_selected_state') != selected_state:
            SafeSessionState.set('property_tax_rate', default_prop_tax)
            SafeSessionState.set('last_selected_state', selected_state)

        st.sidebar.slider(
            "Property Tax Rate (%)",
            min_value=0.0,
            max_value=5.0,
            value=SafeSessionState.get('property_tax_rate'),
            step=0.1,
            format="%.1f%%",
            key="property_tax_rate",
            help=f"Annual property tax as percentage of home value. {selected_state} average: {default_prop_tax:.1f}%"
        )

        # Display combined rate
        state_rate = state_tax_rates[selected_state]
        federal_rate = federal_brackets[federal_bracket]
        combined_rate = federal_rate + state_rate

        st.sidebar.write(f"**Combined Tax Rate:** {combined_rate:.1f}%")
        st.sidebar.write(f"- Federal: {federal_rate}%")
        st.sidebar.write(f"- {selected_state} State: {state_rate}%")

        return AppState.get_tax_info()

    @staticmethod
    def create_common_sidebar():
        """Create common parameter sidebar"""
        st.sidebar.subheader("🏠 Property Parameters")

        # Home price
        st.sidebar.slider(
            "Home Price ($)",
            min_value=100000,
            max_value=2000000,
            value=SafeSessionState.get('home_price'),
            step=10000,
            format="$%d",
            key="home_price"
        )

        # Down payments
        current_home_price = SafeSessionState.get('home_price')
        st.sidebar.slider(
            "Down Payment Option 1 ($)",
            min_value=20000,
            max_value=current_home_price,
            value=min(SafeSessionState.get('down_payment_1'), current_home_price),
            step=10000,
            format="$%d",
            key="down_payment_1"
        )

        st.sidebar.slider(
            "Down Payment Option 2 ($)",
            min_value=20000,
            max_value=current_home_price,
            value=min(SafeSessionState.get('down_payment_2'), current_home_price),
            step=10000,
            format="$%d",
            key="down_payment_2"
        )

        st.sidebar.subheader("📈 Market Rates")

        # Interest rates
        st.sidebar.slider("30-Year Rate (%)", 3.0, 10.0, SafeSessionState.get('rate_30yr'), 0.1, key="rate_30yr")
        st.sidebar.slider("15-Year Rate (%)", 3.0, 10.0, SafeSessionState.get('rate_15yr'), 0.1, key="rate_15yr")

        st.sidebar.subheader("💼 Economic Assumptions")

        # Economic parameters
        st.sidebar.slider("Stock Market Return (%)", 0.0, 15.0, SafeSessionState.get('stock_return'), 0.5, key="stock_return")
        st.sidebar.slider("Inflation Rate (%)", 0.0, 10.0, SafeSessionState.get('inflation_rate'), 0.5, key="inflation_rate")
        st.sidebar.slider("Home Appreciation (%)", 0.0, 10.0, SafeSessionState.get('home_appreciation'), 0.5, key="home_appreciation")
        st.sidebar.number_input("Emergency Fund ($)", 0, 200000, SafeSessionState.get('emergency_fund'), 5000, key="emergency_fund")

        return AppState.get_common_params()

    @staticmethod
    def create_rent_sidebar():
        """Create rent-specific sidebar parameters"""
        st.sidebar.subheader("🏢 Rent Parameters")

        st.sidebar.slider("Monthly Rent ($)", 500, 10000, SafeSessionState.get('monthly_rent'), 50, key="monthly_rent")
        st.sidebar.slider("Annual Rent Increase (%)", 0.0, 10.0, SafeSessionState.get('rent_increase'), 0.5, key="rent_increase")
        st.sidebar.number_input("Annual Renters Insurance ($)", 0, 1000, SafeSessionState.get('renters_insurance'), 50, key="renters_insurance")

        return AppState.get_rent_params()

    @staticmethod
    def create_financial_health_sidebar():
        """Create financial health sidebar parameters"""
        st.sidebar.subheader("💰 Financial Information")

        st.sidebar.number_input("Annual Income ($)", 0, 1000000, SafeSessionState.get('annual_income'), 1000, key="annual_income")
        st.sidebar.number_input("Monthly Other Debts ($)", 0, 10000, SafeSessionState.get('monthly_debts'), 50, key="monthly_debts")
        st.sidebar.number_input("Cash Savings ($)", 0, 5000000, SafeSessionState.get('cash_savings'), 1000, key="cash_savings")
        st.sidebar.number_input("Stock Investments ($)", 0, 5000000, SafeSessionState.get('stock_investments'), 1000, key="stock_investments")

        st.sidebar.subheader("🎯 Target Purchase")
        st.sidebar.number_input("Target Home Price ($)", 100000, 2000000, SafeSessionState.get('target_home_price'), 10000, key="target_home_price")
        st.sidebar.number_input("Target Down Payment ($)", 0, SafeSessionState.get('target_home_price'), SafeSessionState.get('target_down_payment'), 1000, key="target_down_payment")
        st.sidebar.slider("Mortgage Rate (%)", 3.0, 10.0, SafeSessionState.get('mortgage_rate'), 0.1, key="mortgage_rate")

        return AppState.get_financial_health_params()


# Direct access to UI components
def create_tax_sidebar():
    """Create tax selection sidebar"""
    return UIComponents.create_tax_sidebar()

def create_common_sidebar():
    """Create common parameter sidebar"""
    return UIComponents.create_common_sidebar()

def create_rent_sidebar():
    """Create rent-specific sidebar parameters"""
    return UIComponents.create_rent_sidebar()

def create_financial_health_sidebar():
    """Create financial health sidebar parameters"""
    return UIComponents.create_financial_health_sidebar()