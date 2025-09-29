import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, RentScenario
from src.utils.shared_components import apply_custom_css, check_pmi_requirement

st.set_page_config(
    page_title="Rent vs Buy - Know Your Mortgage",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# --- Constants ---
# Economic Assumptions
DEFAULT_STOCK_RETURN = 7.5
DEFAULT_INFLATION_RATE = 2.5
DEFAULT_HOME_APPRECIATION = 3.0

# Indiana-Specific
INDIANA_STATE_TAX_RATE = 3.23
INDIANA_PROPERTY_TAX_RATE = 0.87

# Mortgage & Financial Parameters
CLOSING_COST_RATE = 0.03
PMI_RATE = 0.005  # 0.5% annual PMI rate
PMI_REMOVAL_LTV = 0.78 # Loan-to-value ratio to remove PMI
HOME_INSURANCE_RATE = 0.003 # 0.3% of home value annually
MAINTENANCE_RATE = 0.01 # 1% of home value annually
DEFAULT_FEDERAL_TAX_RATE = 24.0 # For UI default only

# --- Header ---
st.markdown('<h1 class="main-header">🏢 Rent vs Buy Analysis (Indiana)</h1>', unsafe_allow_html=True)

st.markdown("""
Decide whether renting or buying makes more financial sense for your situation in Indiana. This analysis compares
the total financial impact of renting vs purchasing the same property over time, including break-even points
and long-term wealth building potential.
""")

# --- Sidebar for Core Inputs ---
st.sidebar.header("🏢 Core Rent vs Buy Parameters")

home_price = st.sidebar.number_input(
    "Home Price ($)",
    min_value=100000,
    max_value=2000000,
    value=350000,
    step=10000,
    format="%d"
)

down_payment_percent = st.sidebar.slider(
    "Down Payment (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0,
    step=0.5,
    format="%.1f%%"
)

rate_30yr = st.sidebar.number_input("30-Year Mortgage Rate (%)", min_value=0.1, max_value=10.0, value=6.5, step=0.01, format="%.2f")

# --- Rent-Specific Parameters ---
st.sidebar.subheader("🏠 Rental Information")

monthly_rent = st.sidebar.number_input(
    "Monthly Rent ($)",
    min_value=500,
    max_value=10000,
    value=2500,
    step=50,
    format="%d"
)

rent_increase = st.sidebar.number_input(
    "Annual Rent Increase (%)",
    min_value=0.0,
    max_value=10.0,
    value=3.0,
    step=0.1,
    format="%.1f"
)

renters_insurance = st.sidebar.number_input(
    "Monthly Renters Insurance ($)",
    min_value=0,
    max_value=500,
    value=25,
    step=5,
    format="%d"
)

# --- Timeline Input ---
st.sidebar.subheader("📅 Your Plans")
planned_stay_years = st.sidebar.number_input(
    "How many years do you plan to stay?",
    min_value=1,
    max_value=30,
    value=7,
    step=1,
    help="This helps determine if renting or buying makes more sense for your timeline"
)

# --- Advanced Assumptions Expander (Collapsed by default for cleaner UI) ---
with st.expander("🔧 Advanced Assumptions & Your Inputs", expanded=False):
    st.markdown("#### 📋 Your Current Scenario")
    scenario_col1, scenario_col2 = st.columns(2)
    with scenario_col1:
        down_payment_display = home_price * (down_payment_percent / 100)
        st.markdown(f"""
        **🏠 Home Purchase:**
        - Price: ${home_price:,}
        - Down Payment: ${down_payment_display:,} ({down_payment_percent}%)
        - 30-Year Rate: {rate_30yr:.1f}%
        """)
    with scenario_col2:
        st.markdown(f"""
        **🏢 Rental:**
        - Monthly Rent: ${monthly_rent:,}
        - Annual Increase: {rent_increase:.1f}%
        - Renters Insurance: ${renters_insurance}/month
        - Planned Stay: {planned_stay_years} years
        """)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 💰 Financial")
        # Federal Tax Bracket with income ranges (Married Filing Jointly)
        tax_brackets = {
            "10% ($0 - $23,200)": 10.0,
            "12% ($23,201 - $94,300)": 12.0,
            "22% ($94,301 - $201,050)": 22.0,
            "24% ($201,051 - $383,900)": 24.0,
            "32% ($383,901 - $487,450)": 32.0,
            "35% ($487,451 - $731,200)": 35.0,
            "37% ($731,201+)": 37.0
        }

        selected_bracket = st.selectbox(
            "Federal Tax Bracket (2024 Married Filing Jointly)",
            options=list(tax_brackets.keys()),
            index=3,  # Default to 24% bracket (common for home buyers)
            help="Select based on your combined annual income"
        )
        federal_tax_rate = tax_brackets[selected_bracket]

    with col2:
        st.markdown("#### 📈 Economic")
        stock_return = st.number_input("Avg. Stock Market Return (%)", min_value=0.0, max_value=15.0, value=DEFAULT_STOCK_RETURN, step=0.5)
        inflation_rate = st.number_input("Avg. Inflation Rate (%)", min_value=0.0, max_value=10.0, value=DEFAULT_INFLATION_RATE, step=0.5)
        home_appreciation = st.number_input("Avg. Home Appreciation (%)", min_value=0.0, max_value=10.0, value=DEFAULT_HOME_APPRECIATION, step=0.5)

    with col3:
        st.markdown("#### 🇮🇳 Indiana Defaults")
        st.metric("State Income Tax", f"{INDIANA_STATE_TAX_RATE}%")
        st.metric("Avg. Property Tax", f"{INDIANA_PROPERTY_TAX_RATE}%")
        emergency_fund = st.number_input("Emergency Fund ($)", min_value=0, max_value=100000, value=25000, step=1000, format="%d")

# --- Calculations ---
down_payment = home_price * (down_payment_percent / 100)
combined_tax_rate = (federal_tax_rate + INDIANA_STATE_TAX_RATE) / 100  # Convert to decimal
property_tax_rate = INDIANA_PROPERTY_TAX_RATE / 100  # Convert to decimal

# Convert percentages to decimals for calculations
rate_30yr = rate_30yr / 100
stock_return = stock_return / 100
inflation_rate = inflation_rate / 100
home_appreciation = home_appreciation / 100
rent_increase = rent_increase / 100

# --- Helper Functions for New Features ---
def calculate_rent_to_purchase_power(monthly_rent, interest_rate, down_payment_percent=0.20):
    """Calculate what home price the current rent could afford for both 15-year and 30-year loans"""
    # Assume 75% of rent goes to P&I (25% for taxes/insurance)
    estimated_pi = monthly_rent * 0.75
    monthly_rate = interest_rate / 12

    results = {}

    # Calculate for both 15-year and 30-year loans
    for term_years, term_name in [(15, "15-year"), (30, "30-year")]:
        n_payments = term_years * 12

        if monthly_rate == 0:
            max_loan = estimated_pi * n_payments
        else:
            # Reverse mortgage formula: loan = payment * [(1-(1+r)^-n)/r]
            max_loan = estimated_pi * ((1 - (1 + monthly_rate)**-n_payments) / monthly_rate)

        # Add down payment to get total home price
        max_home_price = max_loan / (1 - down_payment_percent)

        results[term_name] = {
            'max_home_price': max_home_price,
            'max_loan': max_loan,
            'estimated_pi': estimated_pi,
            'term_years': term_years
        }

    return results

def get_verdict(break_even_year, planned_stay_years):
    """Generate clear verdict based on timeline vs break-even"""
    if isinstance(break_even_year, str) or break_even_year is None or break_even_year > 30:
        if planned_stay_years >= 10:
            return "🏢 **Rent** - Buying never pays off in this scenario", "warning"
        else:
            return "🏢 **Rent** - Short timeline favors renting", "info"

    difference = break_even_year - planned_stay_years

    if difference <= -2:  # Break-even is 2+ years before they leave
        return "🏠 **Buy** - Clear financial winner for your timeline", "success"
    elif difference <= 0:  # Break-even is at or just before they leave
        return "🏠 **Buy** - Buying pays off just in time", "success"
    elif difference <= 2:  # Break-even is 1-2 years after they leave
        return "🤔 **Close Call** - Consider non-financial factors", "warning"
    else:  # Break-even is much later
        return "🏢 **Rent** - Buying won't pay off in your timeline", "error"

# --- PMI Status ---
st.sidebar.header("PMI Status")
pmi_required, monthly_pmi, ltv = check_pmi_requirement(home_price, down_payment)
if pmi_required:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi:.0f}/month (LTV: {ltv:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv:.1%})")

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
    tax_rate=combined_tax_rate,
    inflation_rate=inflation_rate,
    stock_return_rate=stock_return,
    emergency_fund=emergency_fund
)

# Create rent scenario
rent_scenario = RentScenario(
    name=f"Rent (${monthly_rent:,.0f}/month)",
    home_price=home_price,
    monthly_rent=monthly_rent,
    annual_rent_increase=rent_increase,
    renters_insurance=renters_insurance,
    down_payment_invested=down_payment,
    closing_costs=home_price * CLOSING_COST_RATE,
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

# --- NEW: UNIQUE RENT VS BUY FEATURES ---
st.markdown("---")

# 1. THE VERDICT - Clear Recommendation
break_even_year = break_even_analysis.get('break_even_year', 'Never')
verdict_text, verdict_type = get_verdict(break_even_year, planned_stay_years)

st.markdown('<h1 class="main-header">🎯 The Verdict</h1>', unsafe_allow_html=True)

if verdict_type == "success":
    st.success(verdict_text)
elif verdict_type == "warning":
    st.warning(verdict_text)
elif verdict_type == "error":
    st.error(verdict_text)
else:
    st.info(verdict_text)

# 2. KEY METRICS DASHBOARD - The "Big Four" Unique to Rent vs Buy
st.markdown('<h2 class="sub-header">📊 Key Decision Metrics</h2>', unsafe_allow_html=True)

# Calculate Rent-to-Purchase Power for both loan terms
buying_power_results = calculate_rent_to_purchase_power(monthly_rent, rate_30yr, down_payment_percent/100)

# Calculate 5-year wealth impact
five_year_buy_worth = 0
five_year_rent_worth = 0
if len(buy_results.get('yearly_data', [])) >= 5:
    five_year_buy_worth = buy_results['yearly_data'][4]['net_worth_adjusted']  # Year 5 (index 4)
if len(rent_results.get('yearly_data', [])) >= 5:
    five_year_rent_worth = rent_results['yearly_data'][4]['net_worth_adjusted']  # Year 5 (index 4)

five_year_advantage = five_year_buy_worth - five_year_rent_worth

# Display the 4 unique metrics in a 2x2 grid
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    if isinstance(break_even_year, (int, float)):
        st.metric(
            "🔄 Break-Even Point",
            f"Year {break_even_year:.0f}",
            help="When buying starts to beat renting financially"
        )
    else:
        st.metric(
            "🔄 Break-Even Point",
            "Never",
            help="Renting is always better in this scenario"
        )

with col2:
    # Use 30-year as the main display (more optimistic, common for first-time buyers)
    main_buying_power = buying_power_results["30-year"]
    st.metric(
        "🏠 Your Rent's Buying Power (30-yr)",
        f"${main_buying_power['max_home_price']:,.0f}",
        f"~${main_buying_power['estimated_pi']:,.0f}/mo P&I",
        help=f"What home your ${monthly_rent:,}/mo rent could afford with {down_payment_percent}% down, 30-year loan"
    )

with col3:
    if five_year_advantage >= 0:
        st.metric(
            "📈 5-Year Wealth Impact",
            f"${five_year_advantage:,.0f}",
            "Buy advantage",
            delta_color="normal",
            help="Buying vs renting net worth difference after 5 years"
        )
    else:
        st.metric(
            "📈 5-Year Wealth Impact",
            f"${abs(five_year_advantage):,.0f}",
            "Rent advantage",
            delta_color="inverse",
            help="Renting vs buying net worth difference after 5 years"
        )

with col4:
    buy_monthly = buy_results.get('monthly_payment', 0)
    monthly_diff = buy_monthly - monthly_rent
    if monthly_diff >= 0:
        st.metric(
            "💰 Monthly Cash Flow",
            f"+${monthly_diff:,.0f}",
            "More for buying",
            delta_color="inverse",
            help="How much more per month buying costs vs renting"
        )
    else:
        st.metric(
            "💰 Monthly Cash Flow",
            f"${abs(monthly_diff):,.0f}",
            "Savings from buying",
            delta_color="normal",
            help="How much less per month buying costs vs renting"
        )

# 3. RENT-TO-PURCHASE POWER EXPLANATION
st.markdown("### 🏠 What Your Rent Could Buy You")
# Display both 15-year and 30-year buying power
col_15, col_30 = st.columns(2)

with col_15:
    bp_15 = buying_power_results["15-year"]
    st.info(f"""
    **15-Year Loan:**
    🏠 **\${bp_15['max_home_price']:,.0f}** home
    💰 \${bp_15['estimated_pi']:,.0f}/mo P&I
    🎯 Paid off in 15 years
    """)

with col_30:
    bp_30 = buying_power_results["30-year"]
    st.success(f"""
    **30-Year Loan:**
    🏠 **\${bp_30['max_home_price']:,.0f}** home
    💰 \${bp_30['estimated_pi']:,.0f}/mo P&I
    🎯 Lower monthly payments
    """)

st.markdown(f"""
💡 **Key Insight:** Your ${monthly_rent:,}/month rent could cover the mortgage on:
- **${bp_15['max_home_price']:,.0f}** home with a 15-year loan (paid off faster, less total interest)
- **${bp_30['max_home_price']:,.0f}** home with a 30-year loan (lower monthly payments, more buying power)

**The difference:** \${bp_30['max_home_price'] - bp_15['max_home_price']:,.0f} more buying power with the 30-year loan!
""")

# Add detailed breakdown in an expandable section
with st.expander("🧮 See the Math: How We Calculate Your Buying Power", expanded=False):
    bp_30 = buying_power_results["30-year"]  # Use 30-year for detailed explanation
    st.markdown(f"""
    ### 📐 **Step-by-Step Calculation (30-Year Example)**

    **Given:**
    - Monthly Rent: ${monthly_rent:,}
    - Down Payment: {down_payment_percent}%
    - Interest Rate: {rate_30yr*100:.1f}% annually
    - Loan Term: 30 years

    **Step 1: Estimate Principal & Interest (P&I)**
    ```
    Estimated P&I = Monthly Rent × 0.75
    Estimated P&I = ${monthly_rent:,} × 0.75 = ${bp_30['estimated_pi']:,.0f}
    ```
    *We assume 75% of your rent equivalent goes to P&I, 25% to property taxes and insurance*

    **Step 2: Calculate Maximum Loan Amount**
    Using the standard mortgage payment formula (reversed):
    ```
    Loan = P&I × [(1 - (1 + monthly_rate)^(-n_payments)) / monthly_rate]

    Where:
    - Monthly Rate = {rate_30yr*100:.1f}% ÷ 12 = {rate_30yr/12:.4f}
    - Number of Payments = 30 years × 12 = 360 payments

    Loan = ${bp_30['estimated_pi']:,.0f} × [(1 - (1 + {rate_30yr/12:.4f})^(-360)) / {rate_30yr/12:.4f}]
    Loan = ${bp_30['max_loan']:,.0f}
    ```

    **Step 3: Add Down Payment**
    ```
    Home Price = Loan Amount ÷ (1 - Down Payment %)
    Home Price = ${bp_30['max_loan']:,.0f} ÷ (1 - {down_payment_percent/100:.2f})
    Home Price = ${bp_30['max_home_price']:,.0f}
    ```

    ### 📊 **Comparison: 15-Year vs 30-Year**

    | Loan Term | Max Loan | Total Home Price | Monthly P&I |
    |-----------|----------|------------------|-------------|
    | 15-Year   | ${buying_power_results['15-year']['max_loan']:,.0f} | ${buying_power_results['15-year']['max_home_price']:,.0f} | ${buying_power_results['15-year']['estimated_pi']:,.0f} |
    | 30-Year   | ${buying_power_results['30-year']['max_loan']:,.0f} | ${buying_power_results['30-year']['max_home_price']:,.0f} | ${buying_power_results['30-year']['estimated_pi']:,.0f} |

    **Key Difference:** The same \${monthly_rent:,}/month rent gives you ${bp_30['max_home_price'] - buying_power_results['15-year']['max_home_price']:,.0f} more buying power with a 30-year loan!
    """)

st.success(f"""
**Key Insight:** Your ${monthly_rent:,}/month rent is equivalent to the total housing payment on:
- ${bp_15['max_home_price']:,.0f} home (15-year loan)
- ${bp_30['max_home_price']:,.0f} home (30-year loan)

Instead of paying rent with no equity building, you could be building ${bp_30['estimated_pi']:,.0f}/month in principal paydown plus home appreciation!
""")

# Important caveats and limitations
st.warning("""
⚠️ **Important Limitations & Caveats:**

🔹 **This is an estimate only** - Actual buying power varies based on your specific financial situation

🔹 **Hidden ownership costs not included** - Maintenance (1-3% of home value annually), HOA fees, and repairs aren't part of mortgage payments

🔹 **Assumes optimal conditions** - 20% down payment, Indiana average taxes/insurance, no HOA fees
""")

st.info("""
💡 **How to Use This Information:**
- Use this as a **starting point** for understanding your potential buying power in Indiana
- Consider the total cost of ownership, including maintenance and potential HOA fees
- Factor in your specific down payment amount and target neighborhoods
- Remember: building equity beats paying rent with no ownership benefits
""")

# Debug information (commented out for production)
# with st.expander("🐞 Debug Information", expanded=False):
#     st.write("### Analysis Parameters")
#     col_debug1, col_debug2 = st.columns(2)
#     with col_debug1:
#         st.write("**Buy Scenario:**")
#         st.write(f"- Home Price: ${home_price:,}")
#         st.write(f"- Down Payment: ${down_payment:,}")
#         st.write(f"- Monthly Payment: ${buy_results.get('monthly_payment', 0):,.0f}")
#         st.write(f"- Interest Rate: {rate_30yr:.1%}")
#         st.write(f"- Property Tax: {property_tax_rate:.2%}")
#     with col_debug2:
#         st.write("**Rent Scenario:**")
#         st.write(f"- Monthly Rent: ${monthly_rent:,}")
#         st.write(f"- Rent Increase: {rent_increase:.1%}")
#         st.write(f"- Down Payment Invested: ${down_payment:,}")
#         st.write(f"- Stock Return: {stock_return:.1%}")
#
#     st.write("### Break-even Analysis Results")
#     st.json(break_even_analysis)
#
#     if 'yearly_comparison' in break_even_analysis and break_even_analysis['yearly_comparison']:
#         st.write("### First 5 Years Comparison")
#         yearly_data = break_even_analysis['yearly_comparison'][:5]
#         df_debug = pd.DataFrame(yearly_data)
#         st.dataframe(df_debug)


# Display results
st.markdown('<h2 class="sub-header">📈 Financial Advantage Over Time</h2>', unsafe_allow_html=True)

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
# Determine smart default chart range based on break-even
if isinstance(break_even_year, (int, float)) and break_even_year <= 30:
    default_timeline = min(30, max(10, int(break_even_year) + 5))
else:
    default_timeline = 15  # Default if no break-even

# Add timeline control slider
chart_timeline = st.slider(
    "Chart Timeline (Years)",
    min_value=5,
    max_value=30,
    value=default_timeline,
    step=1,
    help="Adjust the timeline to focus on your planning horizon. Chart defaults to break-even + 5 years."
)

st.subheader(f"Buy vs Rent Financial Advantage Over Time ({chart_timeline} Years)")

years = list(range(1, chart_timeline + 1))
fig_comparison = go.Figure()

# Calculate net worth difference (Buy - Rent) to show break-even clearly
if 'yearly_data' in buy_results and 'yearly_data' in rent_results:
    # Use only the years within the chart timeline
    buy_net_worth = [d['net_worth_adjusted'] for d in buy_results['yearly_data'][:chart_timeline]]
    rent_net_worth = [d['net_worth_adjusted'] for d in rent_results['yearly_data'][:chart_timeline]]

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

# Add break-even year marker if it exists and is within the chart timeline
if isinstance(break_even_year, (int, float)) and 1 <= break_even_year <= chart_timeline:
    fig_comparison.add_vline(x=break_even_year, line_dash="dash", line_color="red", line_width=2,
                           annotation_text=f"Break-even: Year {break_even_year:.0f}",
                           annotation_position="top left")

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

# --- Break-Even Explanation Section ---
with st.expander("📖 How the Break-Even Point is Calculated", expanded=False):
    st.markdown(f"""
    The **break-even point** (Year {break_even_year if isinstance(break_even_year, (int, float)) else 'Never'}) is when the total net worth from **buying** a home surpasses the total net worth from **renting** and investing the difference.

    **How it works:**
    - **Net Worth from Buying** = Current Home Value - Remaining Mortgage Balance
    - **Net Worth from Renting** = Invested Down Payment + Invested Monthly Savings

    #### 🔑 Key Factors Influencing Break-Even:
    - **Upfront Costs**: Higher down payments and closing costs increase time to break even
    - **Home Appreciation vs Rent Increases**: Fast appreciation speeds up break-even
    - **Investment Returns**: Higher stock returns can delay buyer break-even
    - **Monthly Payment Difference**: Larger rent vs mortgage gap affects timeline
    """)

    # Display year-by-year breakdown for the first 10 years
    if 'yearly_comparison' in break_even_analysis and break_even_analysis['yearly_comparison']:
        st.markdown("#### 📊 Year-by-Year Financial Snapshot (First 10 Years)")
        yearly_data = break_even_analysis['yearly_comparison'][:10]
        df_breakdown = pd.DataFrame(yearly_data)

        # Select and rename columns for clarity
        if len(df_breakdown.columns) >= 4:
            df_breakdown = df_breakdown.iloc[:, :4]  # Take first 4 columns
            df_breakdown.columns = ['Year', 'Buyer Net Worth', 'Renter Net Worth', 'Buyer Advantage']

            st.dataframe(df_breakdown.style.format({
                'Buyer Net Worth': '${:,.0f}',
                'Renter Net Worth': '${:,.0f}',
                'Buyer Advantage': '${:,.0f}'
            }), hide_index=True, use_container_width=True)

# --- Parabola Mathematical Explanation ---
with st.expander("🧮 The Mathematics Behind the Curve (Parabola Explanation)", expanded=False):
    st.markdown(f"""
    The rent vs buy advantage curve follows a **parabolic (quadratic) equation** due to competing exponential growth rates.

    ### 📊 **General Equation:**
    ```
    Net Worth Advantage = at² + bt + c
    ```
    Where:
    - **t** = time (years)
    - **a** = curvature coefficient (negative = opens downward)
    - **b** = linear growth rate
    - **c** = initial disadvantage (upfront costs)

    ### 🧮 **Your Scenario Breakdown:**
    - **Stock Return**: {stock_return*100:.1f}% annually
    - **Home Appreciation**: {home_appreciation*100:.1f}% annually
    - **Rate Difference**: {(stock_return - home_appreciation)*100:.1f}% advantage to stocks

    ### 📐 **Why the Parabolic Shape:**

    **Early Years (Upfront Cost Impact):**
    - Large negative starting point due to down payment and closing costs
    - Linear recovery through principal paydown and equity building

    **Middle Years (Equity Building):**
    - Home appreciation and mortgage paydown give buying advantage
    - Peak advantage typically occurs around years 7-10

    **Later Years (Compound Returns):**
    - Higher stock returns ({stock_return*100:.1f}%) compound faster than home appreciation ({home_appreciation*100:.1f}%)
    - Exponential advantage to rental + investment strategy

    ### 🎯 **Stock Return Impact on Curve Shape:**

    | Stock Return | Parabola Shape | Long-term Winner |
    |--------------|----------------|------------------|
    | **10%+** | Narrow (steep decline) | Renting |
    | **7-9%** | Medium curve | Depends on timeline |
    | **5-6%** | Wide (gentle curve) | Buying for longer periods |
    | **≤3%** | Nearly linear | Buying almost always |

    ### 💡 **Key Mathematical Insight:**
    The **curvature coefficient 'a'** is roughly proportional to **(Stock Return - Home Appreciation)²**

    - Larger difference = steeper parabola = earlier second break-even
    - Smaller difference = gentler curve = buying advantage lasts longer
    """)

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