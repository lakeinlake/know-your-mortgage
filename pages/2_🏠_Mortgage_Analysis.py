import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario
from src.utils.shared_components import apply_custom_css, check_pmi_requirement
from src.utils.state_manager import initialize


# --- Helper Functions ---
def display_pmi_status(scenario_num, dp_percent, home_price, down_payment):
    """Checks and displays PMI status in the sidebar."""
    pmi_required, monthly_pmi, _ = check_pmi_requirement(home_price, down_payment)
    if pmi_required:
        st.sidebar.warning(f"Scenario {scenario_num} ({dp_percent:.1f}% down): PMI required (~${monthly_pmi:.0f}/mo)")
    else:
        st.sidebar.success(f"Scenario {scenario_num} ({dp_percent:.1f}% down): No PMI needed")

def find_net_worth_break_even(data_15yr, data_30yr, investment_growth):
    """Finds the year when the net worth of the 30-yr scenario surpasses the 15-yr."""
    yearly_15 = {d['year']: d for d in data_15yr['yearly_data']}
    yearly_30 = {d['year']: d for d in data_30yr['yearly_data']}

    # Track when we get closest for debugging
    closest_year = None
    smallest_gap = float('inf')

    for year in range(1, 31):
        if year not in yearly_15 or year not in yearly_30 or year > len(investment_growth):
            continue

        # Correctly use the total net worth for the 15-year scenario, which includes
        # its home equity AND the growth of its own investment portfolio.
        total_net_worth_15yr = yearly_15[year]['net_worth']

        # For the 30-year scenario, the total net worth is its own calculated net worth
        # PLUS the additional value from investing the monthly payment difference.
        total_net_worth_30yr = yearly_30[year]['net_worth'] + investment_growth[year - 1]

        # Track closest approach
        gap = total_net_worth_15yr - total_net_worth_30yr
        if gap < smallest_gap:
            smallest_gap = gap
            closest_year = year

        if total_net_worth_30yr > total_net_worth_15yr:
            return year

    # For debugging: show why break-even never happened
    if closest_year:
        print(f"DEBUG: Closest approach in Year {closest_year}, gap was ${smallest_gap:,.0f}")
        print(f"  15yr: ${yearly_15[closest_year]['net_worth']:,.0f}")
        print(f"  30yr: ${yearly_30[closest_year]['net_worth'] + investment_growth[closest_year - 1]:,.0f}")

    return "Never"

def display_breakeven_metric(dp_key, opportunity_analysis, scenarios_by_dp):
    """Displays the net worth break-even metric for a given down payment."""
    if 'error' not in opportunity_analysis:
        data_15yr = scenarios_by_dp[dp_key]["15yr"]
        data_30yr = scenarios_by_dp[dp_key]["30yr"]

        break_even_year = find_net_worth_break_even(data_15yr, data_30yr, opportunity_analysis['investment_growth'])
        monthly_diff = opportunity_analysis['monthly_payment_difference']

        st.metric(
            label=f"🔄 {dp_key} Net Worth Break-Even",
            value=f"Year {break_even_year}" if break_even_year != 'Never' else "Never",
            delta=f"Invest monthly ${monthly_diff:,.0f} savings",
            help="The year when the 30-year loan's total net worth (equity + investments) surpasses the 15-year loan's net worth."
        )


# --- App Setup ---
st.set_page_config(
    page_title="Mortgage Analysis - Know Your Mortgage",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)
apply_custom_css()
initialize()

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
st.markdown('<h1 class="main-header">🏠 Mortgage Analysis (Indiana)</h1>', unsafe_allow_html=True)
st.markdown("Compare 15-year vs. 30-year mortgages with different down payments for an Indiana home purchase.")

# --- Sidebar for Core Inputs ---
st.sidebar.header("📊 Core Mortgage Parameters")

home_price = st.sidebar.number_input(
    "Home Price ($)",
    min_value=100000,
    max_value=2000000,
    value=350000,
    step=10000,
    format="%d"
)

dp_percent_1 = st.sidebar.slider(
    "Down Payment Scenario 1 (%)",
    min_value=0.0,
    max_value=100.0,
    value=10.0,
    step=0.5,
    format="%.1f%%"
)

dp_percent_2 = st.sidebar.slider(
    "Down Payment Scenario 2 (%)",
    min_value=0.0,
    max_value=100.0,
    value=20.0,
    step=0.5,
    format="%.1f%%"
)

rate_30yr = st.sidebar.number_input("30-Year Rate (%)", min_value=0.1, max_value=10.0, value=6.5, step=0.01, format="%.2f")
rate_15yr = st.sidebar.number_input("15-Year Rate (%)", min_value=0.1, max_value=10.0, value=5.8, step=0.01, format="%.2f")

# --- Advanced Assumptions Expander ---
with st.expander("Advanced Assumptions & Overrides"):
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
            index=2,  # Default to 22% bracket (common for home buyers)
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
        property_tax_rate = INDIANA_PROPERTY_TAX_RATE / 100  # Convert to decimal

# --- Calculations ---
down_payment_1 = home_price * (dp_percent_1 / 100)
down_payment_2 = home_price * (dp_percent_2 / 100)
combined_tax_rate = (federal_tax_rate + INDIANA_STATE_TAX_RATE) / 100  # Convert to decimal

# --- PMI Warnings ---
st.sidebar.header("PMI Status")
display_pmi_status(1, dp_percent_1, home_price, down_payment_1)
display_pmi_status(2, dp_percent_2, home_price, down_payment_2)

# --- Scenario Generation ---
analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=0)  # Simplified: no separate emergency fund

scenarios_to_run = [
    ("30-Year", dp_percent_1, down_payment_1, rate_30yr / 100, 30),
    ("30-Year", dp_percent_2, down_payment_2, rate_30yr / 100, 30),
    ("15-Year", dp_percent_1, down_payment_1, rate_15yr / 100, 15),
    ("15-Year", dp_percent_2, down_payment_2, rate_15yr / 100, 15),
]

scenarios = []
for term_name, dp_perc, dp_amount, rate, term_years in scenarios_to_run:
    scenarios.append(
        MortgageScenario(
            name=f"{term_name}, {dp_perc:.1f}% Down",
            home_price=home_price,
            down_payment=dp_amount,
            loan_amount=home_price - dp_amount,
            interest_rate=rate,
            term_years=term_years,
            property_tax_rate=property_tax_rate,
            home_appreciation_rate=home_appreciation / 100,
            tax_rate=combined_tax_rate,
            inflation_rate=inflation_rate / 100,
            stock_return_rate=stock_return / 100,
            emergency_fund=0
        )
    )

# --- Available Cash Input ---
st.sidebar.header("💰 Available Cash")

# --- Available Cash Calculation ---
max_down_payment = max([s.down_payment for s in scenarios])
default_cash = int(max_down_payment * 1.5)  # Smart default

available_cash = st.sidebar.number_input(
    "Total Available Cash ($)",
    min_value=0,
    max_value=5000000,
    value=default_cash,
    step=10000,
    format="%d",
    help="Total cash available for down payment, closing costs, and investments. This affects the 'invest the difference' analysis."
)

# --- Post-Payoff Investment Behavior ---
st.sidebar.header("📈 Post-Payoff Investment")
post_payoff_investment_rate = st.sidebar.slider(
    "Post-Payoff Investment Rate (%)",
    min_value=0,
    max_value=100,
    value=75,
    step=5,
    format="%d%%",
    help="After the 15-year mortgage is paid off, what percentage of the freed-up monthly payment will be invested? The rest is assumed to go toward lifestyle/other goals."
)

# --- Analysis ---
results = {}
valid_scenarios = []
for scenario in scenarios:
    required_cash = scenario.down_payment + (scenario.home_price * CLOSING_COST_RATE)
    # All scenarios should be valid now since we calculated available_cash based on the max
    results[scenario.name] = analyzer.analyze_scenario_corrected(scenario, available_cash)
    valid_scenarios.append(scenario)

# --- Results Display ---
if not results:
    st.error("No valid scenarios to analyze. Please check your inputs.")
else:
    # --- 4 KEY DECISION METRICS ---
    st.markdown("---")
    st.success(f"✅ **Analysis Complete** - Assuming ${available_cash:,.0f} available cash (calculated automatically)")

    st.markdown('<h2 class="sub-header">🎯 4 Key Decision Metrics</h2>', unsafe_allow_html=True)

    # Metric 1: Total Monthly Housing Cost
    st.markdown("### 💰 **Metric 1: Total Monthly Housing Cost** (Your Cash Flow Impact)")
    cost_col1, cost_col2 = st.columns(2)

    payment_scenarios = [(name, data['monthly_costs']['total_monthly']) for name, data in results.items()]
    if payment_scenarios:
        payment_scenarios.sort(key=lambda x: x[1])  # Sort by monthly cost

        with cost_col1:
            lowest_name, lowest_cost = payment_scenarios[0]
            st.metric(
                label=f"💚 Lowest Monthly Cost ({lowest_name})",
                value=f"${lowest_cost:,.0f}/month"
            )

        with cost_col2:
            highest_name, highest_cost = payment_scenarios[-1]
            monthly_difference = highest_cost - lowest_cost
            st.metric(
                label=f"📊 Highest Monthly Cost ({highest_name})",
                value=f"${highest_cost:,.0f}/month",
                delta=monthly_difference,
                delta_color="inverse"
            )

    # Show all monthly costs in a clean table
    st.markdown("**Complete Monthly Cost Comparison:**")
    cost_summary = []
    for name, data in results.items():
        costs = data['monthly_costs']
        cost_summary.append({
            'Scenario': name,
            'Total Monthly': costs.get('total_monthly', 0),
            'P&I': costs.get('principal_interest', 0),
            'Tax + Insurance': costs.get('property_tax', 0) + costs.get('insurance', 0),
            'PMI': costs.get('pmi', 0),
            'Maintenance': costs.get('maintenance', 0)
        })

    df_costs = pd.DataFrame(cost_summary)
    df_costs = df_costs.sort_values('Total Monthly')  # Sort by total cost
    st.dataframe(df_costs.style.format({
        'Total Monthly': '${:,.0f}',
        'P&I': '${:,.0f}',
        'Tax + Insurance': '${:,.0f}',
        'PMI': '${:,.0f}',
        'Maintenance': '${:,.0f}'
    }), width='stretch')

    # Metric 2: Freedom Point (Debt-Free Date)
    st.markdown("### 🏆 **Metric 2: Freedom Point** (When You'll Be Debt-Free)")
    freedom_col1, freedom_col2 = st.columns(2)

    # Calculate debt-free dates
    import datetime
    current_year = datetime.datetime.now().year
    freedom_dates = []

    for name, data in results.items():
        if "15-Year" in name:
            debt_free_year = current_year + 15
            freedom_dates.append((name, debt_free_year, "15 years"))
        elif "30-Year" in name:
            debt_free_year = current_year + 30
            freedom_dates.append((name, debt_free_year, "30 years"))

    if freedom_dates:
        freedom_dates.sort(key=lambda x: x[1])  # Sort by year

        with freedom_col1:
            earliest_name, earliest_year, earliest_term = freedom_dates[0]
            st.metric(
                label=f"🎉 Debt-Free First ({earliest_name})",
                value=f"{earliest_year} ({earliest_term})"
            )

        with freedom_col2:
            latest_name, latest_year, latest_term = freedom_dates[-1]
            year_difference = latest_year - earliest_year
            st.metric(
                label=f"📅 Debt-Free Later ({latest_name})",
                value=f"{latest_year} ({latest_term})",
                delta=f"+{year_difference} years",
                delta_color="inverse"
            )

    st.info("💡 **Freedom Point Impact:** Being debt-free 15 years earlier eliminates your largest monthly expense, unlocking massive cash flow for retirement, travel, or other goals.")

    # Metric 3: The Low Down Payment Trade-Off
    st.markdown("### 💳 **Metric 3: The Low Down Payment Trade-Off** (Upfront Cash vs. PMI Cost)")
    cash_col, pmi_col = st.columns(2)

    # Find scenarios for 10% and 20% down
    scenarios_10_down = {name: data for name, data in results.items() if "10.0% Down" in name}
    scenarios_20_down = {name: data for name, data in results.items() if "20.0% Down" in name}

    # --- Upfront Cash Calculation ---
    with cash_col:
        st.markdown("#### 💰 Upfront Cash Needed")
        st.markdown(f"*Assumes {CLOSING_COST_RATE*100:.0f}% closing costs*")
        closing_costs = home_price * CLOSING_COST_RATE

        upfront_10 = (home_price * 0.10) + closing_costs
        upfront_20 = (home_price * 0.20) + closing_costs
        cash_difference = upfront_20 - upfront_10

        # Breakdown for 10% down
        down_10 = home_price * 0.10
        st.metric(
            label="Cash for 10% Down",
            value=f"${upfront_10:,.0f}",
            delta=f"${down_10:,.0f} down + ${closing_costs:,.0f} closing"
        )

        # Breakdown for 20% down
        down_20 = home_price * 0.20
        st.metric(
            label="Cash for 20% Down",
            value=f"${upfront_20:,.0f}",
            delta=f"${down_20:,.0f} down + ${closing_costs:,.0f} closing"
        )

    # --- PMI Cost Calculation ---
    with pmi_col:
        st.markdown("#### 💸 The Cost of PMI")
        pmi_scenario_data = next(iter(scenarios_10_down.values()), None)

        if pmi_scenario_data and pmi_scenario_data['monthly_costs'].get('pmi', 0) > 0:
            monthly_pmi = pmi_scenario_data['monthly_costs']['pmi']

            # Accurately find when PMI is removed
            target_balance = home_price * PMI_REMOVAL_LTV
            pmi_removal_year = None
            for year_data in pmi_scenario_data['yearly_data']:
                if year_data['loan_balance'] <= target_balance:
                    pmi_removal_year = year_data['year']
                    break

            if pmi_removal_year:
                total_pmi_cost = monthly_pmi * 12 * pmi_removal_year
                st.metric(
                    label="PMI on 10% Down Scenario",
                    value=f"${monthly_pmi:,.0f} / month",
                    delta=f"~${total_pmi_cost:,.0f} total over {pmi_removal_year} years",
                    delta_color="inverse"
                )
            else: # Fallback if PMI is never removed (unlikely)
                st.metric(
                    label="PMI on 10% Down Scenario",
                    value=f"${monthly_pmi:,.0f} / month",
                    help="PMI is paid until loan balance reaches 78% of home value."
                )
        else:
            st.metric(
                label="PMI Cost",
                value="$0",
                help="No PMI required for 20% down payment scenarios."
            )

    st.info("💡 **The Trade-Off:** A 20% down payment requires more cash upfront but saves you thousands in PMI costs, which is money that doesn't build your equity.")

    # --- Charts ---
    col1, col2 = st.columns(2)

    # Metric 4: Net Worth Break-Even Point
    st.markdown("### 📈 **Metric 4: Net Worth Break-Even** (When 'Invest the Difference' Pays Off)")

    st.info("""
    💡 **How Net Worth Break-Even Works:**

    **15-Year Strategy:** Higher payments build equity fast + home appreciation
    **30-Year Strategy:** Lower payments + invest the monthly difference in stocks

    **Example:** If 15-year costs \$3,200/month and 30-year costs \$2,800/month:
    - You save $400/month with the 30-year loan
    - Invest that $400/month in the stock market
    - Break-even = when your (home equity + investments) surpasses the 15-year's total wealth

    **Why it might show "Never":** The 15-year builds equity so fast (via principal paydown + home appreciation) that even with stock market returns, the 30-year + investments can't catch up in 30 years. This is common when home appreciation is 3%+ or stock returns are only modest.

    **When break-even happens:** Usually requires high stock returns (8-10%) or low home appreciation (0-2%).

    **Post-Payoff Assumption:** After 15 years, the model assumes you invest """ + f"{post_payoff_investment_rate}%" + """ of your freed-up mortgage payment. The rest goes to lifestyle improvements or other goals.
    """)

    # --- Opportunity Cost Analysis Setup ---
    opportunity_analyses = {}
    scenarios_by_dp = {}
    dp_keys_map = {
        f"{dp_percent_1:.1f}% Down": f"{dp_percent_1:.1f}% Down",
        f"{dp_percent_2:.1f}% Down": f"{dp_percent_2:.1f}% Down"
    }
    for name, data in results.items():
        for key_str, dp_key in dp_keys_map.items():
            if key_str in name:
                if dp_key not in scenarios_by_dp:
                    scenarios_by_dp[dp_key] = {}
                if "30-Year" in name:
                    scenarios_by_dp[dp_key]["30yr"] = data
                elif "15-Year" in name:
                    scenarios_by_dp[dp_key]["15yr"] = data
                break

    for dp_key, scenarios in scenarios_by_dp.items():
        if "30yr" in scenarios and "15yr" in scenarios:
            opportunity_analyses[dp_key] = analyzer.analyze_opportunity_cost(
                scenarios["30yr"], scenarios["15yr"], stock_return, post_payoff_investment_rate
            )

    # --- Net Worth Break-Even Calculation & Display ---
    if opportunity_analyses:
        breakeven_col1, breakeven_col2 = st.columns(2)

        # --- Display metrics for each down payment scenario ---
        dp_keys = list(opportunity_analyses.keys())

        with breakeven_col1:
            if len(dp_keys) > 0:
                dp_key = dp_keys[0]
                display_breakeven_metric(dp_key, opportunity_analyses[dp_key], scenarios_by_dp)

        with breakeven_col2:
            if len(dp_keys) > 1:
                dp_key = dp_keys[1]
                display_breakeven_metric(dp_key, opportunity_analyses[dp_key], scenarios_by_dp)

        st.info("💡 **Net Worth Break-Even:** This shows when the 30-year mortgage + investing the monthly savings *actually* makes you wealthier than the 15-year mortgage's rapid equity growth. This is a more accurate comparison for long-term wealth building.")

        # --- Break-Even Visualization Chart ---
        st.markdown("#### 📊 **Net Worth Break-Even Visualization**")

        # Create chart for each down payment scenario
        for dp_key, analysis in opportunity_analyses.items():
            if 'error' not in analysis and dp_key in scenarios_by_dp:
                data_15yr = scenarios_by_dp[dp_key]["15yr"]
                data_30yr = scenarios_by_dp[dp_key]["30yr"]

                # Prepare data for charting
                years = []
                net_worth_15yr = []
                net_worth_30yr_total = []

                yearly_15 = {d['year']: d for d in data_15yr['yearly_data']}
                yearly_30 = {d['year']: d for d in data_30yr['yearly_data']}

                for year in range(1, min(31, len(analysis['investment_growth']) + 1)):
                    if year in yearly_15 and year in yearly_30:
                        years.append(year)

                        # Path 1: 15-year total net worth
                        net_worth_15yr.append(yearly_15[year]['net_worth'])

                        # Path 2: 30-year total net worth (base + invested difference)
                        nw_30_base = yearly_30[year]['net_worth']
                        nw_30_total = nw_30_base + analysis['investment_growth'][year - 1]
                        net_worth_30yr_total.append(nw_30_total)

                # Create the chart
                fig_breakeven = go.Figure()

                # Line for "Wealth with 15-Year Mortgage"
                fig_breakeven.add_trace(go.Scatter(
                    x=years,
                    y=net_worth_15yr,
                    mode='lines',
                    name=f'Wealth with 15-Year Mortgage ({dp_key})',
                    line=dict(color='blue', width=3),
                    hovertemplate='Year: %{x}<br>Net Worth: $%{y:,.0f}<extra></extra>'
                ))

                # Line for "Wealth with 30-Year Mortgage & Investments"
                fig_breakeven.add_trace(go.Scatter(
                    x=years,
                    y=net_worth_30yr_total,
                    mode='lines',
                    name=f'Wealth with 30-Year Mortgage & Investments ({dp_key})',
                    line=dict(color='green', width=3),
                    hovertemplate='Year: %{x}<br>Total Net Worth: $%{y:,.0f}<extra></extra>'
                ))

                # Add annotation for Year 15 mortgage payoff
                if 15 in years:
                    idx_15 = years.index(15)
                    y_15_value = max(net_worth_15yr[idx_15], net_worth_30yr_total[idx_15])

                    # Add vertical line at Year 15
                    fig_breakeven.add_vline(
                        x=15,
                        line_dash="dot",
                        line_color="gray",
                        annotation_text=f"15-Year Mortgage<br>Paid Off<br>({post_payoff_investment_rate}% invested)",
                        annotation_position="top"
                    )

                # Find and mark break-even point
                break_even_year = find_net_worth_break_even(data_15yr, data_30yr, analysis['investment_growth'])
                if break_even_year != "Never" and break_even_year in years:
                    idx = years.index(break_even_year)
                    break_even_value = net_worth_30yr_total[idx]

                    fig_breakeven.add_trace(go.Scatter(
                        x=[break_even_year],
                        y=[break_even_value],
                        mode='markers',
                        name=f'Break-Even Point (Year {break_even_year})',
                        marker=dict(size=12, color='orange', symbol='star'),
                        hovertemplate=f'Break-Even!<br>Year: {break_even_year}<br>Net Worth: ${break_even_value:,.0f}<extra></extra>'
                    ))

                fig_breakeven.update_layout(
                    title=f"Net Worth Comparison: 15-Year vs. 30-Year (+ Investments) - {dp_key}",
                    xaxis_title="Year of Loan",
                    yaxis_title="Total Net Worth ($)",
                    hovermode='x unified',
                    height=500,
                    legend=dict(
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01
                    )
                )

                st.plotly_chart(fig_breakeven, width='stretch')

                # Add interpretation
                monthly_diff = analysis['monthly_payment_difference']
                if break_even_year != "Never":
                    st.success(f"✅ **{dp_key}**: Break-even occurs in Year {break_even_year}. After this point, the 30-year + ${monthly_diff:,.0f}/month investment strategy builds more wealth than the 15-year mortgage.")
                else:
                    st.warning(f"⚠️ **{dp_key}**: No break-even within 30 years. The 15-year mortgage's rapid equity building outpaces the 30-year + ${monthly_diff:,.0f}/month investment strategy throughout the analysis period.")

                st.markdown("---")

    # --- Decision Framework ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h2 class="sub-header">🤔 Decision Framework</h2>', unsafe_allow_html=True)

        st.markdown("""
        **📋 How to Use These 4 Metrics to Decide:**

        **1. Start with Affordability (Metric 1)**
        - Can you comfortably afford the higher 15-year payment?
        - If not, choose the 30-year mortgage for cash flow flexibility

        **2. Consider Your Personality (Metric 2)**
        - Do you value the certainty of being debt-free sooner?
        - Choose 15-year for "forced savings" and peace of mind

        **3. Evaluate PMI Impact (Metric 3)**
        - Can you stretch to 20% down to eliminate PMI?
        - This is often a smart financial move if you can do it safely

        **4. Investment Discipline (Metric 4)**
        - Are you disciplined enough to invest the monthly difference?
        - If yes, and you'll stay past the break-even point, consider 30-year
        """)

    with col2:
        st.markdown('<h2 class="sub-header">💰 Total Interest Comparison</h2>', unsafe_allow_html=True)

        # Show total interest paid for each scenario
        interest_summary = []
        for name, data in results.items():
            if data['total_interest'] > 0:
                interest_summary.append({
                    'Scenario': name,
                    'Total Interest': data['total_interest']
                })

        if interest_summary:
            df_interest = pd.DataFrame(interest_summary)
            df_interest = df_interest.sort_values('Total Interest')  # Sort by total interest

            # Create a simple bar chart
            fig_interest = px.bar(
                df_interest,
                x='Scenario',
                y='Total Interest',
                title="Total Interest Paid Over Loan Term",
                color='Total Interest',
                color_continuous_scale='reds'
            )
            fig_interest.update_layout(height=400)
            st.plotly_chart(fig_interest, width='stretch')

            # Show the numbers
            lowest_interest = df_interest.iloc[0]
            highest_interest = df_interest.iloc[-1]
            interest_savings = highest_interest['Total Interest'] - lowest_interest['Total Interest']

            st.metric(
                label="💰 Interest Savings (15-year vs 30-year)",
                value=f"${interest_savings:,.0f}",
                delta=f"{lowest_interest['Scenario']} saves the most"
            )

    # --- Detailed Tabs ---
    st.markdown('<h2 class="sub-header">📋 Detailed Analysis</h2>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Interest & Amortization", "Investment vs Extra Interest", "Home Equity Building", "Year-by-Year Data"])

    with tab1:
        st.markdown("The **Total Interest Paid** bar chart is shown in the summary section above.")
        st.info("Select a scenario from the dropdown in the **Year-by-Year Data** tab to see its detailed amortization schedule.")

    with tab2:
        st.markdown("**Investment Growth vs Extra Interest Cost (30-year vs 15-year)**")
        if opportunity_analyses:
            # Create chart for each down payment scenario
            for dp_key, analysis in opportunity_analyses.items():
                if 'error' not in analysis:
                    fig_opportunity = go.Figure()

                    # Investment growth line
                    fig_opportunity.add_trace(go.Scatter(
                        x=analysis['years'],
                        y=analysis['investment_growth'],
                        mode='lines',
                        name=f'{dp_key}: Investment Growth',
                        line=dict(color='green'),
                        hovertemplate='Year: %{x}<br>Investment Value: $%{y:,.0f}<extra></extra>'
                    ))

                    # Extra interest cost line
                    fig_opportunity.add_trace(go.Scatter(
                        x=analysis['years'],
                        y=analysis['cumulative_interest_cost'],
                        mode='lines',
                        name=f'{dp_key}: Extra Interest Cost',
                        line=dict(color='red'),
                        hovertemplate='Year: %{x}<br>Extra Interest: $%{y:,.0f}<extra></extra>'
                    ))

                    # Mark break-even point
                    if analysis.get('break_even_year'):
                        break_even_year = analysis['break_even_year']
                        break_even_value = analysis['investment_growth'][break_even_year - 1]
                        fig_opportunity.add_trace(go.Scatter(
                            x=[break_even_year],
                            y=[break_even_value],
                            mode='markers',
                            name=f'Break-Even (Year {break_even_year})',
                            marker=dict(size=10, color='orange'),
                            hovertemplate=f'Break-Even Point<br>Year: {break_even_year}<br>Value: ${break_even_value:,.0f}<extra></extra>'
                        ))

                    fig_opportunity.update_layout(
                        title=f"Investment Growth vs Extra Interest Cost - {dp_key}",
                        xaxis_title="Year",
                        yaxis_title="Amount ($)",
                        hovermode='x unified',
                        height=400
                    )

                    st.plotly_chart(fig_opportunity, width='stretch')

                    # Show key metrics
                    col1, col2, col3 = st.columns(3)
                    monthly_diff = analysis['monthly_payment_difference']
                    break_even = analysis.get('break_even_year', 'Never')
                    total_extra_interest = analysis['total_extra_interest_30yr']

                    col1.metric("Monthly Difference", f"${monthly_diff:,.0f}")
                    col2.metric("Break-Even Point", f"Year {break_even}" if break_even != 'Never' else "Never")
                    col3.metric("Total Extra Interest (30-yr)", f"${total_extra_interest:,.0f}")

                    st.markdown("---")
        else:
            st.info("Analysis requires both 15-year and 30-year scenarios with matching down payments.")

    with tab3:
        st.markdown("**Home Equity Building Comparison**")
        fig_equity = go.Figure()
        for name, data in results.items():
            fig_equity.add_trace(go.Scatter(
                x=[d['year'] for d in data['yearly_data']],
                y=[d['home_equity'] for d in data['yearly_data']],
                mode='lines',
                name=name,
                hovertemplate=f'{name}<br>Year: %{{x}}<br>Home Equity: $%{{y:,.0f}}<extra></extra>'
            ))
        fig_equity.update_layout(
            title="Home Equity Growth Over Time",
            xaxis_title="Year",
            yaxis_title="Home Equity ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_equity, width='stretch')

    with tab4:
        selected_scenario = st.selectbox("Select scenario for detailed breakdown:", list(results.keys()))
        if selected_scenario:
            df_yearly = pd.DataFrame(results[selected_scenario]['yearly_data'])

            # Expand monthly_costs dictionary into separate columns for better readability
            if 'monthly_costs' in df_yearly.columns:
                # Extract monthly costs into separate columns
                monthly_costs_expanded = pd.json_normalize(df_yearly['monthly_costs'])
                monthly_costs_expanded.columns = [f'monthly_{col}' for col in monthly_costs_expanded.columns]

                # Combine with main dataframe
                df_yearly = pd.concat([df_yearly.drop('monthly_costs', axis=1), monthly_costs_expanded], axis=1)

            # Format numeric columns
            numeric_cols = df_yearly.select_dtypes(include=['number']).columns
            format_dict = {}
            for col in numeric_cols:
                if col == 'year':
                    format_dict[col] = '{:.0f}'
                elif 'monthly_' in col:
                    format_dict[col] = '${:,.0f}'
                else:
                    format_dict[col] = '${:,.0f}'

            st.dataframe(df_yearly.style.format(format_dict), width='stretch')

    # --- Assumptions and Calculations Section ---
    st.markdown("---")
    st.markdown('<h2 class="sub-header">📋 Analysis Assumptions & Calculations</h2>', unsafe_allow_html=True)

    with st.expander("📊 View All Assumptions and Calculation Methods"):

        st.markdown("### 🏠 **Core Assumptions**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **🇮🇳 Indiana-Specific:**
            - **State Income Tax**: {INDIANA_STATE_TAX_RATE}% (hard-coded)
            - **Property Tax Rate**: {INDIANA_PROPERTY_TAX_RATE}% annually (hard-coded)
            - **Combined Tax Rate**: {federal_tax_rate + INDIANA_STATE_TAX_RATE}% (Federal + State)

            **💰 Financial Assumptions:**
            - **Closing Costs**: 3% of home price
            - **PMI Rate**: 0.5% annually on loan amount (when LTV > 80%)
            - **PMI Removal**: When LTV drops below 78%
            - **Homeowners Insurance**: 0.3% of home value annually
            - **Maintenance**: 1% of home value annually
            """)

        with col2:
            st.markdown(f"""
            **📈 Economic Assumptions:**
            - **Stock Market Return**: {stock_return}% annually
            - **Inflation Rate**: {inflation_rate}% annually
            - **Home Appreciation**: {home_appreciation}% annually

            **💵 Cash Calculation:**
            - **Available Cash**: ${available_cash:,.0f} (auto-calculated)
            - **Method**: 1.5× your highest down payment scenario
            - **Purpose**: Realistic assumption for investment calculations
            """)

        st.markdown("### 🧮 **Calculation Methods**")

        st.markdown("""
        **Monthly Payment Components:**
        1. **Principal & Interest**: Standard amortization formula
        2. **Property Tax**: (Home Value × Property Tax Rate) ÷ 12
        3. **PMI**: (Loan Amount × 0.5%) ÷ 12 (if LTV > 80%)
        4. **Insurance**: (Home Value × 0.3%) ÷ 12
        5. **Maintenance**: (Home Value × 1.0%) ÷ 12

        **Net Worth Calculation:**
        - **Home Equity**: Current Home Value - Remaining Loan Balance
        - **Investments**: Remaining cash invested in stock market
        - **Total Net Worth**: Home Equity + Investment Value + Emergency Fund
        - **Inflation-Adjusted**: Present value using inflation rate

        **Investment Logic:**
        - **Initial Investment**: Available Cash - Down Payment - Closing Costs
        - **Monthly Investment**: Additional savings from lower payments (if any)
        - **Post-Payoff**: Full mortgage payment invested after loan is paid off
        - **Returns**: Compounded annually at stock market return rate

        **Tax Benefits:**
        - **Mortgage Interest Deduction**: Calculated but simplified
        - **Note**: Assumes itemized deductions exceed standard deduction
        """)

        st.markdown("### ⚠️ **Important Notes**")

        st.markdown("""
        **What's Included:**
        ✅ All homeownership costs (PITI + insurance + maintenance)
        ✅ PMI calculations and automatic removal
        ✅ Closing costs and selling costs
        ✅ Inflation-adjusted analysis
        ✅ Investment opportunity costs
        ✅ Indiana-specific tax rates

        **Limitations:**
        ⚠️ Tax deductions are simplified
        ⚠️ Assumes consistent market returns
        ⚠️ Does not include HOA fees
        ⚠️ Property tax increases with home value
        ⚠️ Emergency fund kept separate (not invested)

        **Recommendation:**
        💡 Use this analysis for comparison purposes. Consult a financial advisor for personalized advice.
        """)

    st.markdown("---")
    st.markdown("💡 **Next Steps:** This analysis helps you compare scenarios. Consider your personal financial goals, risk tolerance, and local market conditions when making your decision.")