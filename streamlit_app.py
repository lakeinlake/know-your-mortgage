import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, GoogleSheetsExporter
import io
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Mortgage Analysis Tool",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight {
        background-color: #ffd700;
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">🏠 Comprehensive Mortgage Analysis Tool</h1>', unsafe_allow_html=True)

# Glossary section at the top
with st.expander("📚 Key Terms & Concepts (Click to expand)", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 💰 Financial Terms

        **Real vs Nominal Values:**
        - **Real**: Money adjusted for inflation (purchasing power)
        - **Nominal**: Raw dollar amounts (face value)
        - **Why it matters**: \\$1M in 30 years ≠ \\$1M today
        - **Real vs Nominal Example**: \\$1,000,000 in 30 years with 3% inflation = \\$410,000 in today's buying power

        **Net Worth Components:**
        - **Home Equity**: Home value minus remaining loan balance
        - **Investment Value**: Money invested in stock market
        - **Total Net Worth**: Home equity + investments + emergency fund

        **Tax Benefits:**
        - **Mortgage Interest Deduction**: Reduces taxable income
        - **Tax Savings**: Amount saved on taxes each year
        """)

    with col2:
        st.markdown("""
        ### 📊 Analysis Concepts

        **Opportunity Cost:**
        - Money used for down payments can't be invested
        - Higher down payment = less money for stock market
        - Trade-off between guaranteed savings vs potential gains

        **Scenarios Compared:**
        - **30-Year Mortgage**: Lower payments, more interest
        - **15-Year Mortgage**: Higher payments, less interest
        - **Cash Purchase**: No payments, no leverage

        **Key Assumption:**
        - Excess money is invested in stock market
        - Emergency fund kept separate (not invested)
        """)

    st.info("💡 **Focus on 'Real' values throughout the analysis** - they show what your money will actually be worth in today's purchasing power.")

# Sidebar for inputs
st.sidebar.header("📊 Analysis Parameters")

# Basic parameters
st.sidebar.subheader("Property & Financing")
home_price = st.sidebar.slider(
    "Home Price ($)",
    min_value=100000,
    max_value=2000000,
    value=500000,
    step=10000,
    format="$%d",
    help="Total purchase price of the home"
)

down_payment_100k = st.sidebar.slider(
    "Down Payment - Option 1 ($)",
    min_value=20000,
    max_value=home_price,
    value=min(100000, home_price),
    step=10000,
    format="$%d",
    help="Down payment for first comparison scenario"
)

down_payment_200k = st.sidebar.slider(
    "Down Payment - Option 2 ($)",
    min_value=20000,
    max_value=home_price,
    value=min(200000, home_price),
    step=10000,
    format="$%d",
    help="Down payment for second comparison scenario"
)

# Interest rates
st.sidebar.subheader("Interest Rates")
rate_30yr = st.sidebar.slider(
    "30-Year Rate (%)",
    min_value=3.0,
    max_value=10.0,
    value=6.1,
    step=0.1,
    format="%.1f%%",
    help="Annual interest rate for 30-year mortgage"
) / 100

rate_15yr = st.sidebar.slider(
    "15-Year Rate (%)",
    min_value=3.0,
    max_value=10.0,
    value=5.6,
    step=0.1,
    format="%.1f%%",
    help="Annual interest rate for 15-year mortgage"
) / 100

# Investment and economic parameters
st.sidebar.subheader("Investment & Economy")
stock_return = st.sidebar.slider(
    "Stock Market Return (%)",
    min_value=0.0,
    max_value=15.0,
    value=8.0,
    step=0.5,
    format="%.1f%%",
    help="Expected annual stock market return"
) / 100

inflation_rate = st.sidebar.slider(
    "Inflation Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=3.0,
    step=0.5,
    format="%.1f%%",
    help="Expected annual inflation rate"
) / 100

home_appreciation = st.sidebar.slider(
    "Home Appreciation (%)",
    min_value=0.0,
    max_value=10.0,
    value=5.0,
    step=0.5,
    format="%.1f%%",
    help="Expected annual home value appreciation"
) / 100

# Advanced parameters
st.sidebar.subheader("Other Parameters")
emergency_fund = st.sidebar.number_input(
    "Emergency Fund ($)",
    min_value=0,
    max_value=200000,
    value=50000,
    step=5000,
    help="Amount to keep as emergency fund (not invested)"
)

tax_rate = st.sidebar.slider(
    "Tax Rate (%)",
    min_value=0.0,
    max_value=40.0,
    value=26.0,
    step=1.0,
    format="%.0f%%",
    help="Marginal tax rate for mortgage interest deduction"
) / 100

property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (%)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.1,
    format="%.1f%%",
    help="Annual property tax as percentage of home value"
) / 100

# Initialize analyzer
analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=emergency_fund)

# Create scenarios with custom parameters
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

# Analyze all scenarios
results = {}
for scenario in scenarios:
    results[scenario.name] = analyzer.analyze_scenario(scenario)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="sub-header">📈 Net Worth Over Time</h2>', unsafe_allow_html=True)

    # Create net worth chart
    fig_networth = go.Figure()

    for scenario_name, result in results.items():
        years = [d['year'] for d in result['yearly_data']]
        net_worth = [d['net_worth'] for d in result['yearly_data']]
        net_worth_real = [d['net_worth_adjusted'] for d in result['yearly_data']]

        # Nominal values
        fig_networth.add_trace(go.Scatter(
            x=years,
            y=net_worth,
            mode='lines',
            name=f"{scenario_name} (Nominal)",
            line=dict(width=2),
            visible='legendonly'
        ))

        # Real values (adjusted for inflation)
        fig_networth.add_trace(go.Scatter(
            x=years,
            y=net_worth_real,
            mode='lines',
            name=f"{scenario_name} (Real)",
            line=dict(width=3, dash='solid')
        ))

    fig_networth.update_layout(
        title="Net Worth Projection (30 Years) - Focus on 'Real' Values",
        xaxis_title="Year",
        yaxis_title="Net Worth ($)",
        height=500,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig_networth, width="stretch")

    st.info("💡 **Real vs Nominal Explained:** The solid lines show 'Real' values (inflation-adjusted purchasing power) - these are the most important for decision-making. The dotted lines show 'Nominal' values (raw dollar amounts). Click legend items to show/hide different scenarios.")

with col2:
    st.markdown('<h2 class="sub-header">💰 Monthly Payments</h2>', unsafe_allow_html=True)

    # Monthly payment comparison chart
    payment_data = []
    for scenario_name, result in results.items():
        # Create more descriptive labels that include both term and down payment
        if "Cash Purchase" in scenario_name:
            label = "Cash\n(No Payment)"
        else:
            term = "30yr" if "30-Year" in scenario_name else "15yr"
            down_amount = scenario_name.split('$')[1].split('K')[0] + "K"
            label = f"{term}\n${down_amount} Down"

        payment_data.append({
            'Scenario': label,
            'Monthly Payment': result['monthly_payment'],
            'Full Name': scenario_name
        })

    df_payments = pd.DataFrame(payment_data)

    fig_payments = px.bar(
        df_payments,
        x='Scenario',
        y='Monthly Payment',
        color='Monthly Payment',
        color_continuous_scale='RdYlGn_r',  # Red (high) to Green (low)
        title="Monthly Payment Comparison",
        hover_data={'Full Name': True, 'Monthly Payment': ':$,.0f'}
    )

    fig_payments.update_layout(
        height=400,
        showlegend=False,
        yaxis_title="Monthly Payment ($)",
        xaxis_title="Loan Type & Down Payment"
    )

    # Add value labels on bars
    fig_payments.update_traces(
        texttemplate='$%{y:,.0f}',
        textposition='outside'
    )

    st.plotly_chart(fig_payments, width="stretch")

    st.info("💡 **Chart Explanation:** Higher bars = higher monthly payments. The 15-year mortgages have higher monthly payments but save significantly on total interest. Cash purchase has $0 monthly payment but uses all available capital upfront.")

# Summary table
st.markdown('<h2 class="sub-header">📊 Scenario Comparison Summary</h2>', unsafe_allow_html=True)

comparison_df = analyzer.compare_scenarios(scenarios)
st.dataframe(
    comparison_df,
    width="stretch",
    hide_index=True,
    column_config={
        "Rank": st.column_config.NumberColumn(
            "Rank",
            help="Ranking based on final net worth (inflation-adjusted)",
            format="%d"
        ),
        "Final Net Worth (Real)": st.column_config.TextColumn(
            "Final Net Worth (Real)",
            help="Net worth in today's purchasing power - this is what matters most for comparisons"
        )
    }
)

# Key metrics in columns
st.markdown('<h2 class="sub-header">🎯 Key Insights</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

# Get summary statistics
stats = analyzer.get_summary_statistics(scenarios)

with col1:
    st.metric(
        label="Best Scenario",
        value=stats['best_scenario'].split(',')[0],
        help="Scenario with highest inflation-adjusted net worth after 30 years"
    )

with col2:
    st.metric(
        label="Wealth Difference",
        value=f"${stats['wealth_difference']:,.0f}",
        delta=f"{stats['wealth_difference_pct']:.1f}%",
        help="Difference between best and worst scenarios"
    )

with col3:
    best_result = results[stats['best_scenario']]
    st.metric(
        label="Best Final Wealth",
        value=f"${stats['max_final_wealth']:,.0f}",
        help="Highest inflation-adjusted net worth"
    )

with col4:
    # Calculate average monthly payment
    avg_payment = sum(r['monthly_payment'] for r in results.values()) / len(results)
    st.metric(
        label="Avg Monthly Payment",
        value=f"${avg_payment:,.0f}",
        help="Average monthly payment across all scenarios"
    )

# Detailed analysis tabs
st.markdown('<h2 class="sub-header">📋 Detailed Analysis</h2>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Investment Growth", "Home Equity", "Interest Analysis", "Year-by-Year Data"])

with tab1:
    st.subheader("Investment Value Over Time")

    fig_investment = go.Figure()

    for scenario_name, result in results.items():
        years = [d['year'] for d in result['yearly_data']]
        investment = [d['investment_value'] for d in result['yearly_data']]

        fig_investment.add_trace(go.Scatter(
            x=years,
            y=investment,
            mode='lines',
            name=scenario_name,
            line=dict(width=2)
        ))

    fig_investment.update_layout(
        xaxis_title="Year",
        yaxis_title="Investment Value ($)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_investment, width="stretch")

    st.info("💡 This shows how your invested money grows over time. Scenarios with lower down payments and monthly payments allow more money to be invested in the stock market.")

with tab2:
    st.subheader("Home Equity Progression")

    fig_equity = go.Figure()

    for scenario_name, result in results.items():
        if result['loan_amount'] > 0:  # Skip cash purchase
            years = [d['year'] for d in result['yearly_data']]
            equity = [d['home_equity'] for d in result['yearly_data']]

            fig_equity.add_trace(go.Scatter(
                x=years,
                y=equity,
                mode='lines',
                name=scenario_name,
                line=dict(width=2)
            ))

    fig_equity.update_layout(
        xaxis_title="Year",
        yaxis_title="Home Equity ($)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_equity, width="stretch")

    st.info("💡 Home equity grows through both principal payments and home appreciation. Larger down payments and shorter loan terms build equity faster.")

with tab3:
    st.subheader("Total Interest Paid")

    interest_data = []
    for scenario_name, result in results.items():
        if result['total_interest'] > 0:
            interest_data.append({
                'Scenario': scenario_name,
                'Total Interest': result['total_interest'],
                'Tax Savings': result['total_interest'] * tax_rate
            })

    if interest_data:
        df_interest = pd.DataFrame(interest_data)

        fig_interest = go.Figure()

        fig_interest.add_trace(go.Bar(
            name='Total Interest',
            x=df_interest['Scenario'],
            y=df_interest['Total Interest'],
            marker_color='indianred'
        ))

        fig_interest.add_trace(go.Bar(
            name='Tax Savings',
            x=df_interest['Scenario'],
            y=df_interest['Tax Savings'],
            marker_color='lightgreen'
        ))

        fig_interest.update_layout(
            barmode='group',
            xaxis_title="Scenario",
            yaxis_title="Amount ($)",
            height=400
        )

        st.plotly_chart(fig_interest, width="stretch")

        st.info(f"💡 Tax savings assume a {tax_rate*100:.0f}% marginal tax rate on mortgage interest deduction.")

with tab4:
    st.subheader("Detailed Year-by-Year Breakdown")

    # Selector for scenario
    selected_scenario = st.selectbox(
        "Select Scenario:",
        options=list(results.keys())
    )

    # Create detailed dataframe for selected scenario
    selected_result = results[selected_scenario]
    yearly_df = pd.DataFrame(selected_result['yearly_data'])

    # Format columns for display
    display_columns = ['year', 'home_value', 'loan_balance', 'home_equity',
                      'investment_value', 'net_worth', 'net_worth_adjusted']

    yearly_display = yearly_df[display_columns].copy()

    # Format currency columns
    currency_cols = ['home_value', 'loan_balance', 'home_equity',
                    'investment_value', 'net_worth', 'net_worth_adjusted']

    for col in currency_cols:
        yearly_display[col] = yearly_display[col].apply(lambda x: f"${x:,.0f}")

    yearly_display.columns = ['Year', 'Home Value', 'Loan Balance', 'Home Equity',
                             'Investment Value', 'Net Worth (Nominal)', 'Net Worth (Real)']

    st.dataframe(
        yearly_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Net Worth (Real)": st.column_config.TextColumn(
                "Net Worth (Real) 💰",
                help="Inflation-adjusted value - what this money can actually buy in today's terms"
            ),
            "Net Worth (Nominal)": st.column_config.TextColumn(
                "Net Worth (Nominal)",
                help="Raw dollar amount without inflation adjustment"
            )
        }
    )

    st.info("💡 **Focus on the 'Real' column** - this shows what your wealth will actually be worth in today's purchasing power. The nominal values will look much higher due to inflation.")

# Export functionality
st.markdown('<h2 class="sub-header">💾 Export Results</h2>', unsafe_allow_html=True)

# Google Sheets export temporarily disabled for debugging
# Uncomment this section when authentication issues are resolved
"""
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🚧 **Google Sheets Export**: Temporarily disabled for maintenance. Use CSV export below for now.")
    # Google Sheets export code commented out for now
    # Will be re-enabled once authentication issues are resolved

with col2:
"""

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Generate CSV Export", type="primary"):
        # Create CSV data
        csv_df = analyzer.export_results(scenarios, 'temp.csv')

        # Convert to CSV string
        csv_buffer = io.StringIO()
        csv_df.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()

        st.download_button(
            label="📊 Download Full Analysis CSV",
            data=csv_string,
            file_name='mortgage_analysis.csv',
            mime='text/csv'
        )

        st.success("✅ CSV file ready for download!")

        # Add helpful instructions for Google Sheets import
        st.info("""
        **💡 To import to Google Sheets:**
        1. Go to [Google Sheets](https://sheets.google.com)
        2. Create a new sheet
        3. File → Import → Upload your downloaded CSV
        4. Share the sheet with friends and family!
        """)

with col2:
    if st.button("📄 Generate Summary Report", type="secondary"):
        # Create summary report
        report = f"""# Mortgage Analysis Report

## Parameters
- Home Price: ${home_price:,.0f}
- 30-Year Rate: {rate_30yr*100:.1f}%
- 15-Year Rate: {rate_15yr*100:.1f}%
- Stock Return: {stock_return*100:.1f}%
- Inflation: {inflation_rate*100:.1f}%

## Best Scenario
**{stats['best_scenario']}**
- Final Net Worth (Real): ${stats['max_final_wealth']:,.0f}

## Comparison Summary
{comparison_df.to_string()}

## Key Insight
The best scenario outperforms the worst by ${stats['wealth_difference']:,.0f} ({stats['wealth_difference_pct']:.1f}%),
demonstrating the importance of optimizing your mortgage strategy based on your financial goals and market expectations.
"""

        st.download_button(
            label="📝 Download Summary Report",
            data=report,
            file_name='mortgage_analysis_report.txt',
            mime='text/plain'
        )

        st.success("✅ Report ready for download!")

# Footer with instructions
st.markdown("---")
st.markdown("""
### 📖 How to Use This Tool

1. **Adjust Parameters**: Use the sidebar to modify home price, down payments, interest rates, and investment assumptions
2. **Review Charts**: Examine the net worth projections and monthly payment comparisons
3. **Analyze Results**: Check the summary table to see which scenario performs best
4. **Export Data**: Download the full analysis as CSV or a summary report

### 🎯 Key Considerations

- **💡 Focus on Real Values**: See the glossary above for detailed explanations of Real vs Nominal values
- **Investment Risk**: Stock market returns are not guaranteed; consider your risk tolerance
- **Tax Benefits**: Mortgage interest deduction can significantly reduce effective interest costs
- **Opportunity Cost**: Money used for larger down payments cannot be invested elsewhere

### ⚠️ Disclaimer

This tool provides estimates based on simplified assumptions.

Always consult with qualified financial advisors for personalized advice.
""")

# Add a note about assumptions
with st.expander("📋 View All Assumptions"):
    st.markdown("""
    ### Financial Assumptions
    - **Emergency Fund**: Kept separate and not invested
    - **Investment Vehicle**: Assumes tax-advantaged accounts (401k, IRA)
    - **Property Costs**: Only property tax included (no HOA, insurance, maintenance)
    - **Tax Deduction**: Assumes itemized deductions for mortgage interest
    - **Market Returns**: Constant annual returns (no volatility modeling)

    ### Calculation Methods
    - **Compound Interest**: Monthly compounding for investments
    - **Amortization**: Standard mortgage amortization formula
    - **Inflation Adjustment**: Annual compounding using CPI model
    - **Home Appreciation**: Annual compounding

    ### Limitations
    - Does not account for PMI (Private Mortgage Insurance)
    - Assumes stable income throughout the period
    - No consideration of life events (job loss, health issues)
    - Market volatility not modeled
    - Tax laws assumed constant
    """)

# Performance metrics at the bottom
st.markdown("---")
st.caption("🚀 Mortgage Analysis Tool v1.0 | Built with Streamlit & Python")