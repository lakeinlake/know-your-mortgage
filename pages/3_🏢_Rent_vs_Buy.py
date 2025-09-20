import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, RentScenario
from src.utils.shared_components import apply_custom_css, check_pmi_requirement, calculate_recommended_emergency_fund
from src.utils.state_manager import initialize, AppState
from src.utils.ui_components import create_tax_sidebar, create_common_sidebar, create_rent_sidebar

st.set_page_config(
    page_title="Rent vs Buy - Know Your Mortgage",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# 1. Initialize state
initialize()

st.markdown('<h1 class="main-header">🏢 Rent vs Buy Analysis</h1>', unsafe_allow_html=True)

st.markdown("""
Decide whether renting or buying makes more financial sense for your situation. This analysis compares
the total financial impact of renting vs purchasing the same property over time, including break-even points
and long-term wealth building potential.
""")

st.sidebar.header("🏢 Rent vs Buy Parameters")

# 2. Render UI and get computed values directly
selected_state, tax_rate, property_tax_rate = create_tax_sidebar()
params = create_common_sidebar()
rent_params = create_rent_sidebar()

home_price = params['home_price']
down_payment = params['down_payment_1']
rate_30yr = params['rate_30yr']
stock_return = params['stock_return']
inflation_rate = params['inflation_rate']
home_appreciation = params['home_appreciation']
emergency_fund = params['emergency_fund']

monthly_rent = rent_params['monthly_rent']
rent_increase = rent_params['rent_increase']
renters_insurance = rent_params['renters_insurance']

# PMI warnings for down payment
pmi_required_1, monthly_pmi_1, ltv_1 = check_pmi_requirement(home_price, down_payment)
if pmi_required_1:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi_1:.0f}/month (LTV: {ltv_1:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv_1:.1%})")

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

# Analyze scenarios using corrected method
corrected_results = analyzer.run_corrected_rent_vs_buy_analysis(buy_scenario, rent_scenario)

# Extract individual results for backward compatibility with existing chart code
rent_results = corrected_results.get('rent_results', {})
buy_results = corrected_results.get('buy_results', {})
break_even_analysis = corrected_results.get('break_even_analysis', {})

# Debug information
with st.expander("🐞 Debug Information", expanded=False):
    st.write("### Analysis Parameters")
    col_debug1, col_debug2 = st.columns(2)
    with col_debug1:
        st.write("**Buy Scenario:**")
        st.write(f"- Home Price: ${home_price:,}")
        st.write(f"- Down Payment: ${down_payment:,}")
        st.write(f"- Monthly Payment: ${buy_results.get('monthly_payment', 0):,.0f}")
        st.write(f"- Interest Rate: {rate_30yr:.1%}")
        st.write(f"- Property Tax: {property_tax_rate:.2%}")
    with col_debug2:
        st.write("**Rent Scenario:**")
        st.write(f"- Monthly Rent: ${monthly_rent:,}")
        st.write(f"- Rent Increase: {rent_increase:.1%}")
        st.write(f"- Down Payment Invested: ${down_payment:,}")
        st.write(f"- Stock Return: {stock_return:.1%}")

    st.write("### Break-even Analysis Results")
    st.json(break_even_analysis)

    if 'yearly_comparison' in break_even_analysis and break_even_analysis['yearly_comparison']:
        st.write("### First 5 Years Comparison")
        yearly_data = break_even_analysis['yearly_comparison'][:5]
        df_debug = pd.DataFrame(yearly_data)
        st.dataframe(df_debug)

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
st.subheader("Buy vs Rent Financial Advantage Over Time")

years = list(range(1, 31))
fig_comparison = go.Figure()

# Calculate net worth difference (Buy - Rent) to show break-even clearly
if 'yearly_data' in buy_results and 'yearly_data' in rent_results:
    buy_net_worth = [d['net_worth_adjusted'] for d in buy_results['yearly_data']]
    rent_net_worth = [d['net_worth_adjusted'] for d in rent_results['yearly_data']]

    # Calculate the difference: positive means buying is better, negative means renting is better
    net_worth_difference = [buy - rent for buy, rent in zip(buy_net_worth, rent_net_worth)]

    # Create the differential plot
    fig_comparison.add_trace(go.Scatter(
        x=years, y=net_worth_difference, mode='lines+markers',
        name='Buy Advantage Over Rent',
        line=dict(color='purple', width=3),
        marker=dict(size=4),
        fill='tonexty' if any(diff < 0 for diff in net_worth_difference) else None,
        fillcolor='rgba(255,0,0,0.1)' if any(diff < 0 for diff in net_worth_difference) else 'rgba(0,255,0,0.1)',
        hovertemplate='<b>Year %{x}</b><br>' +
                      'Net Worth Advantage: $%{y:,.0f}<br>' +
                      '<i>%{customdata}</i><extra></extra>',
        customdata=['Buying is better' if diff > 0 else 'Renting is better' if diff < 0 else 'Break-even point'
                   for diff in net_worth_difference]
    ))

    # Add zero line for reference
    fig_comparison.add_hline(y=0, line_dash="solid", line_color="gray", line_width=1,
                           annotation_text="Break-even line", annotation_position="bottom right")

# Add break-even year marker if it exists
if isinstance(break_even_year, (int, float)) and 1 <= break_even_year <= 30:
    fig_comparison.add_vline(x=break_even_year, line_dash="dash", line_color="red", line_width=2,
                           annotation_text=f"Break-even: Year {break_even_year:.0f}")

fig_comparison.update_layout(
    title="Financial Advantage: Buy vs Rent Over Time",
    xaxis_title="Years",
    yaxis_title="Net Worth Advantage of Buying ($)",
    hovermode='x unified',
    height=500,
    annotations=[
        dict(x=0.02, y=0.98, xref="paper", yref="paper",
             text="📈 Above zero: Buying is better<br>📉 Below zero: Renting is better",
             showarrow=False, font=dict(size=10), bgcolor="rgba(255,255,255,0.8)")
    ]
)

st.plotly_chart(fig_comparison, width='stretch')

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
    st.dataframe(df_comparison, width='stretch', hide_index=True)

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
    st.plotly_chart(fig_rent, width='stretch')

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
    st.plotly_chart(fig_cashflow, width='stretch')

st.markdown("---")
st.markdown("💡 **Next Steps:** Check your financial readiness on the Financial Health page or generate professional reports for detailed planning.")