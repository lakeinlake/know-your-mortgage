import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario
from src.utils.shared_components import apply_custom_css, check_pmi_requirement, calculate_recommended_emergency_fund
from src.utils.state_manager import initialize, AppState
from src.utils.ui_components import create_tax_sidebar, create_common_sidebar

st.set_page_config(
    page_title="Mortgage Analysis - Know Your Mortgage",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# 1. Initialize state
initialize()

st.markdown('<h1 class="main-header">🏠 Mortgage Scenario Analysis</h1>', unsafe_allow_html=True)

st.markdown("""
Compare different mortgage scenarios side-by-side. Analyze 15-year vs 30-year mortgages,
different down payment strategies, and cash purchase options to find the best approach for your situation.
""")

st.sidebar.header("📊 Mortgage Parameters")

# 2. Render UI and get computed values directly
selected_state, tax_rate, property_tax_rate = create_tax_sidebar()
params = create_common_sidebar()
home_price = params['home_price']
down_payment_100k = params['down_payment_1']
down_payment_200k = params['down_payment_2']

# PMI warnings
pmi_required_1, monthly_pmi_1, ltv_1 = check_pmi_requirement(home_price, down_payment_100k)
if pmi_required_1:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi_1:.0f}/month (LTV: {ltv_1:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv_1:.1%})")

pmi_required_2, monthly_pmi_2, ltv_2 = check_pmi_requirement(home_price, down_payment_200k)
if pmi_required_2:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi_2:.0f}/month (LTV: {ltv_2:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv_2:.1%})")

rate_30yr = params['rate_30yr']
rate_15yr = params['rate_15yr']
stock_return = params['stock_return']
inflation_rate = params['inflation_rate']
home_appreciation = params['home_appreciation']
emergency_fund = params['emergency_fund']

# Initialize analyzer
analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=emergency_fund)

# Create scenarios (using dataclass syntax)
scenarios = [
    MortgageScenario(
        name=f"30-Year, ${down_payment_100k/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_100k,
        loan_amount=home_price - down_payment_100k,
        interest_rate=rate_30yr,
        term_years=30,
        property_tax_rate=property_tax_rate,
        home_appreciation_rate=home_appreciation,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    ),
    MortgageScenario(
        name=f"30-Year, ${down_payment_200k/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_200k,
        loan_amount=home_price - down_payment_200k,
        interest_rate=rate_30yr,
        term_years=30,
        property_tax_rate=property_tax_rate,
        home_appreciation_rate=home_appreciation,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    ),
    MortgageScenario(
        name=f"15-Year, ${down_payment_100k/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_100k,
        loan_amount=home_price - down_payment_100k,
        interest_rate=rate_15yr,
        term_years=15,
        property_tax_rate=property_tax_rate,
        home_appreciation_rate=home_appreciation,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    ),
    MortgageScenario(
        name=f"15-Year, ${down_payment_200k/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_200k,
        loan_amount=home_price - down_payment_200k,
        interest_rate=rate_15yr,
        term_years=15,
        property_tax_rate=property_tax_rate,
        home_appreciation_rate=home_appreciation,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    ),
    MortgageScenario(
        name="Cash Purchase",
        home_price=home_price,
        down_payment=home_price,
        loan_amount=0,
        interest_rate=0,
        term_years=0,
        property_tax_rate=property_tax_rate,
        home_appreciation_rate=home_appreciation,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    )
]

# Analyze all scenarios automatically
results = {}
for scenario in scenarios:
    results[scenario.name] = analyzer.analyze_scenario(scenario)

# Display results
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h2 class="sub-header">📈 Net Worth Over Time</h2>', unsafe_allow_html=True)

    fig_networth = go.Figure()

    for scenario_name, data in results.items():
        if 'yearly_data' in data:
            years = [d['year'] for d in data['yearly_data']]
            net_worth_real = [d['net_worth_adjusted'] for d in data['yearly_data']]

            fig_networth.add_trace(go.Scatter(
                x=years,
                y=net_worth_real,
                mode='lines',
                name=f"{scenario_name} (Real)",
                line=dict(width=3)
            ))

    fig_networth.update_layout(
        title="Net Worth Progression (Inflation-Adjusted)",
        xaxis_title="Years",
        yaxis_title="Net Worth ($)",
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig_networth, use_container_width=True)

with col2:
    st.markdown('<h2 class="sub-header">💰 Monthly Payments</h2>', unsafe_allow_html=True)

    payment_data = []
    for scenario_name, data in results.items():
        if 'monthly_payment' in data and data['monthly_payment'] > 0:
            payment_data.append({
                'Scenario': scenario_name,
                'Monthly Payment': data['monthly_payment']
            })

    if payment_data:
        df_payments = pd.DataFrame(payment_data)

        fig_payments = px.bar(
            df_payments,
            x='Scenario',
            y='Monthly Payment',
            title="Monthly Payment Comparison",
            color='Monthly Payment',
            color_continuous_scale='viridis'
        )

        fig_payments.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig_payments, use_container_width=True)

st.markdown('<h2 class="sub-header">📋 Detailed Analysis</h2>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Investment Growth", "Home Equity", "Interest Analysis", "Year-by-Year Data"])

with tab1:
    st.subheader("Investment Value Over Time")

    fig_investment = go.Figure()

    for scenario_name, data in results.items():
        if 'yearly_data' in data:
            years = [d['year'] for d in data['yearly_data']]
            investment_values = [d['investment_value'] for d in data['yearly_data']]

            fig_investment.add_trace(go.Scatter(
                x=years,
                y=investment_values,
                mode='lines',
                name=f"{scenario_name}",
                line=dict(width=2)
            ))

    fig_investment.update_layout(
        title="Investment Portfolio Growth Over Time (Real Values)",
        xaxis_title="Years",
        yaxis_title="Investment Value ($)",
        hovermode='x unified'
    )

    st.plotly_chart(fig_investment, use_container_width=True)

with tab2:
    st.subheader("Home Equity Progression")

    fig_equity = go.Figure()

    for scenario_name, data in results.items():
        if 'yearly_data' in data:
            years = [d['year'] for d in data['yearly_data']]
            home_equity = [d.get('home_equity', 0) for d in data['yearly_data']]

            fig_equity.add_trace(go.Scatter(
                x=years,
                y=home_equity,
                mode='lines',
                name=scenario_name,
                line=dict(width=2)
            ))

    fig_equity.update_layout(
        title="Home Equity Growth Over Time",
        xaxis_title="Years",
        yaxis_title="Home Equity ($)",
        hovermode='x unified'
    )

    st.plotly_chart(fig_equity, use_container_width=True)

with tab3:
    st.subheader("Total Interest Paid")

    interest_data = []
    for scenario_name, data in results.items():
        if 'total_interest' in data and data['total_interest'] > 0:
            interest_data.append({
                'Scenario': scenario_name,
                'Total Interest': data['total_interest']
            })

    if interest_data:
        df_interest = pd.DataFrame(interest_data)

        fig_interest = px.bar(
            df_interest,
            x='Scenario',
            y='Total Interest',
            title="Total Interest Paid Over Loan Term",
            color='Total Interest',
            color_continuous_scale='reds'
        )

        fig_interest.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_interest, use_container_width=True)

with tab4:
    st.subheader("Detailed Year-by-Year Breakdown")

    selected_scenario = st.selectbox(
        "Select scenario for detailed breakdown:",
        list(results.keys())
    )

    if selected_scenario and selected_scenario in results:
        data = results[selected_scenario]

        if 'yearly_data' in data:
            df_yearly = pd.DataFrame(data['yearly_data'])
            st.dataframe(df_yearly, use_container_width=True)
        else:
            st.info("Year-by-year data not available for this scenario")

st.markdown("### Why Compare Mortgage Scenarios?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🎯 Key Questions This Analysis Answers:**
    - Should I choose a 15-year or 30-year mortgage?
    - How much should I put down to optimize my finances?
    - Is it better to pay cash or finance and invest the difference?
    - What's the real cost difference between scenarios?
    """)

with col2:
    st.markdown("""
    **📊 What You'll See:**
    - Net worth projections over 30 years
    - Monthly payment comparisons
    - Investment growth opportunities
    - Total interest costs
    - Year-by-year financial breakdown
    """)

st.markdown("---")
st.markdown("💡 **Next Steps:** Visit other pages to analyze rent vs buy scenarios, check your financial readiness, or generate professional reports.")