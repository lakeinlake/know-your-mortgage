import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, RentScenario
from utils.shared_components import apply_custom_css, check_pmi_requirement, calculate_recommended_emergency_fund, add_tax_selection_sidebar

st.set_page_config(
    page_title="Rent vs Buy - Know Your Mortgage",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

st.markdown('<h1 class="main-header">🏢 Rent vs Buy Analysis</h1>', unsafe_allow_html=True)

st.markdown("""
Decide whether renting or buying makes more financial sense for your situation. This analysis compares
the total financial impact of renting vs purchasing the same property over time, including break-even points
and long-term wealth building potential.
""")

st.sidebar.header("🏢 Rent vs Buy Parameters")

# State and tax selection
selected_state, tax_rate, property_tax_rate = add_tax_selection_sidebar()

# Sidebar inputs
home_price = st.sidebar.slider("Home Price ($)", 100000, 2000000, 500000, 10000, format="$%d")
down_payment = st.sidebar.slider("Down Payment ($)", 20000, home_price, min(100000, home_price), 10000, format="$%d")
monthly_rent = st.sidebar.slider("Monthly Rent ($)", 500, int(home_price * 0.01), int(home_price * 0.005), 100, format="$%d")
rent_increase = st.sidebar.slider("Annual Rent Increase (%)", 0.0, 10.0, 3.0, 0.5, format="%.1f%%") / 100
renters_insurance = st.sidebar.slider("Annual Renters Insurance ($)", 0, 1000, 200, 50, format="$%d")
rate_30yr = st.sidebar.slider("30-Year Mortgage Rate (%)", 3.0, 10.0, 6.1, 0.1, format="%.1f%%") / 100
stock_return = st.sidebar.slider("Stock Market Return (%)", 0.0, 15.0, 8.0, 0.5, format="%.1f%%") / 100
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0.0, 10.0, 3.0, 0.5, format="%.1f%%") / 100
home_appreciation = st.sidebar.slider("Home Appreciation (%)", 0.0, 10.0, 5.0, 0.5, format="%.1f%%") / 100
emergency_fund = st.sidebar.number_input("Emergency Fund ($)", 0, 200000, 50000, 5000)

# Initialize analyzer
analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=emergency_fund)

# Create buy scenario
buy_scenario = MortgageScenario(
    name="Buy: 30-Year Mortgage",
    home_price=home_price,
    down_payment=down_payment,
    loan_amount=home_price - down_payment,
    interest_rate=rate_30yr,
    term_years=30,
    property_tax_rate=property_tax_rate,
    home_appreciation_rate=home_appreciation,
    tax_rate=tax_rate,
    inflation_rate=inflation_rate,
    stock_return_rate=stock_return,
    emergency_fund=emergency_fund
)

# Create rent scenario (note: uses annual_rent_increase, not rent_increase)
rent_scenario = RentScenario(
    name=f"Rent (${monthly_rent:,.0f}/month)",
    home_price=home_price,
    monthly_rent=monthly_rent,
    annual_rent_increase=rent_increase,  # Note: annual_rent_increase
    renters_insurance=renters_insurance,
    down_payment_invested=down_payment,
    closing_costs=home_price * 0.03,
    inflation_rate=inflation_rate,
    stock_return_rate=stock_return,
    emergency_fund=emergency_fund
)

# Analyze scenarios - NOTE: different method call order than expected
rent_results = analyzer.analyze_rent_scenario(rent_scenario)
buy_results = analyzer.analyze_scenario(buy_scenario)
break_even_analysis = analyzer.calculate_break_even_analysis(rent_scenario, buy_scenario)

# Display results
st.markdown('<h2 class="sub-header">🏠 vs 🏢 Rent vs Buy Analysis</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    break_even_year = break_even_analysis.get('break_even_year', 'Never')
    if isinstance(break_even_year, (int, float)) and break_even_year > 0:
        st.metric("Break-Even Point", f"Year {break_even_year:.0f}", help="When buying becomes better than renting")
    else:
        st.metric("Break-Even Point", "Never", help="Renting is always better financially")

with col2:
    advantage_30yr = break_even_analysis.get('advantage_at_30_years', 0)
    winner = "Buy" if advantage_30yr > 0 else "Rent"
    st.metric("30-Year Winner", winner, f"${abs(advantage_30yr):,.0f} advantage", help="Better choice after 30 years")

with col3:
    final_net_worth_diff = break_even_analysis.get('final_net_worth_difference', 0)
    st.metric("Final Net Worth Difference", f"${final_net_worth_diff:,.0f}",
              delta_color="normal" if final_net_worth_diff >= 0 else "inverse",
              help="Buy minus Rent net worth at year 30")

# Chart
st.subheader("Buy vs Rent Comparison Over Time")

years = list(range(1, 31))
fig_comparison = go.Figure()

# Extract net worth data correctly
if 'yearly_data' in buy_results:
    buy_net_worth = [d['net_worth_adjusted'] for d in buy_results['yearly_data']]
    fig_comparison.add_trace(go.Scatter(
        x=years, y=buy_net_worth, mode='lines',
        name='Buy (Real Net Worth)', line=dict(color='green', width=3)
    ))

if 'yearly_data' in rent_results:
    rent_net_worth = [d['net_worth_adjusted'] for d in rent_results['yearly_data']]
    fig_comparison.add_trace(go.Scatter(
        x=years, y=rent_net_worth, mode='lines',
        name='Rent (Real Net Worth)', line=dict(color='blue', width=3)
    ))

if isinstance(break_even_year, (int, float)) and 1 <= break_even_year <= 30:
    fig_comparison.add_vline(x=break_even_year, line_dash="dash", line_color="red",
                           annotation_text=f"Break-even: Year {break_even_year:.0f}")

fig_comparison.update_layout(
    title="Rent vs Buy: Net Worth Comparison Over Time",
    xaxis_title="Years", yaxis_title="Real Net Worth ($)",
    hovermode='x unified', height=500
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Insights
insights = break_even_analysis.get('insights', [])
if insights:
    st.markdown("### 💡 Key Insights")
    for insight in insights:
        st.info(insight)

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Detailed Comparison", "🏢 Rent Analysis", "💰 Financial Breakdown"])

with tab1:
    st.subheader("Side-by-Side Comparison")

    # Extract data safely
    buy_monthly_payment = buy_results.get('monthly_payment', 0)
    buy_final_net_worth = buy_results.get('final_net_worth_adjusted', 0) if 'final_net_worth_adjusted' in buy_results else 0
    rent_final_net_worth = rent_results.get('final_net_worth_adjusted', 0) if 'final_net_worth_adjusted' in rent_results else 0
    total_rent_paid = rent_results.get('total_rent_paid', 0)
    total_interest = buy_results.get('total_interest', 0)

    comparison_data = {
        'Metric': ['Monthly Payment (Year 1)', 'Total Cost (30 Years)', 'Final Net Worth', 'Total Interest/Rent Paid'],
        'Buy Scenario': [
            f"${buy_monthly_payment:,.0f}",
            f"${buy_monthly_payment * 12 * 30:,.0f}",  # Approximate
            f"${buy_final_net_worth:,.0f}",
            f"${total_interest:,.0f}"
        ],
        'Rent Scenario': [
            f"${monthly_rent:,.0f}",
            f"${total_rent_paid:,.0f}",
            f"${rent_final_net_worth:,.0f}",
            f"${total_rent_paid:,.0f}"
        ]
    }
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Rent Analysis Details")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Starting Monthly Rent", f"${monthly_rent:,.0f}", help="Monthly rent in year 1")

    with col2:
        year_30_rent = monthly_rent * ((1 + rent_increase) ** 29)
        st.metric("Year 30 Monthly Rent", f"${year_30_rent:,.0f}",
                 f"+{((year_30_rent/monthly_rent - 1)*100):.0f}%", help="Monthly rent in year 30")

    with col3:
        total_rent_paid = rent_results.get('total_rent_paid', 0)
        st.metric("Total Rent Paid (30 Years)", f"${total_rent_paid:,.0f}", help="Total amount paid in rent over 30 years")

    st.subheader("Rent Escalation Over Time")
    rent_data = []
    current_rent = monthly_rent
    for year in range(1, 31):
        rent_data.append({'Year': year, 'Monthly Rent': current_rent, 'Annual Rent': current_rent * 12})
        current_rent *= (1 + rent_increase)

    df_rent = pd.DataFrame(rent_data)
    fig_rent = px.line(df_rent, x='Year', y='Monthly Rent', title='Monthly Rent Escalation Over Time')
    fig_rent.update_layout(height=400)
    st.plotly_chart(fig_rent, use_container_width=True)

with tab3:
    st.subheader("Cash Flow Analysis")

    years = list(range(1, 31))
    fig_cashflow = go.Figure()

    buy_monthly = [buy_monthly_payment] * 30
    rent_monthly = []
    current_rent = monthly_rent
    for year in range(30):
        rent_monthly.append(current_rent)
        current_rent *= (1 + rent_increase)

    fig_cashflow.add_trace(go.Scatter(x=years, y=buy_monthly, mode='lines', name='Buy: Monthly Payment', line=dict(color='green')))
    fig_cashflow.add_trace(go.Scatter(x=years, y=rent_monthly, mode='lines', name='Rent: Monthly Payment', line=dict(color='blue')))

    fig_cashflow.update_layout(title="Monthly Payment Comparison Over Time", xaxis_title="Years", yaxis_title="Monthly Payment ($)", hovermode='x unified')
    st.plotly_chart(fig_cashflow, use_container_width=True)

st.markdown("---")
st.markdown("💡 **Next Steps:** Check your financial readiness on the Financial Health page or generate professional reports for detailed planning.")