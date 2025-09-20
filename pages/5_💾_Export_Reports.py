import streamlit as st
import pandas as pd
import io
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, RentScenario
from src.utils.shared_components import apply_custom_css
from src.utils.state_manager import initialize, AppState
from src.utils.ui_components import create_tax_sidebar, create_common_sidebar

st.set_page_config(
    page_title="Export Reports - Know Your Mortgage",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# 1. Initialize state
initialize()

st.markdown('<h1 class="main-header">💾 Export Reports & Data</h1>', unsafe_allow_html=True)

st.markdown("""
Generate professional reports and export detailed data from your mortgage and rent vs buy analysis.
Choose from CSV exports for spreadsheet analysis, summary tables for quick comparison, or executive reports for comprehensive planning.
""")

st.info("⚠️ **Note:** You need to run analysis on other pages first to generate data for export. Visit the Mortgage Analysis or Rent vs Buy pages to create scenarios.")

st.sidebar.header("📊 Export Configuration")

# 2. Render UI and get computed values directly
selected_state, tax_rate, property_tax_rate = create_tax_sidebar()
params = create_common_sidebar()
home_price = params['home_price']
down_payment_1 = params['down_payment_1']
down_payment_2 = params['down_payment_2']
rate_30yr = params['rate_30yr']
rate_15yr = params['rate_15yr']
stock_return = params['stock_return']
inflation_rate = params['inflation_rate']
home_appreciation = params['home_appreciation']
emergency_fund = params['emergency_fund']

include_rent_analysis = st.sidebar.checkbox("Include Rent vs Buy Analysis", value=True, key="include_rent_analysis")

if include_rent_analysis:
    st.sidebar.subheader("🏢 Rental Parameters")
    monthly_rent = st.sidebar.slider(
        "Monthly Rent ($)",
        min_value=500,
        max_value=int(home_price * 0.01),
        value=st.session_state.monthly_rent,
        step=100,
        format="$%d",
        key="monthly_rent"
    )

    rent_increase = st.sidebar.slider(
        "Annual Rent Increase (%)",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state.rent_increase * 100,
        step=0.5,
        format="%.1f%%",
        key="rent_increase_pct"
    ) / 100

    renters_insurance = st.sidebar.slider(
        "Annual Renters Insurance ($)",
        min_value=0,
        max_value=1000,
        value=st.session_state.renters_insurance,
        step=50,
        format="$%d",
        key="renters_insurance"
    )


# Generate analysis data automatically
analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=emergency_fund)

# Create scenarios with all required parameters
scenarios = [
    MortgageScenario(
        name=f"30-Year, ${down_payment_1/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_1,
        loan_amount=home_price - down_payment_1,
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
        name=f"30-Year, ${down_payment_2/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_2,
        loan_amount=home_price - down_payment_2,
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
        name=f"15-Year, ${down_payment_1/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_1,
        loan_amount=home_price - down_payment_1,
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
        name=f"15-Year, ${down_payment_2/1000:.0f}K Down",
        home_price=home_price,
        down_payment=down_payment_2,
        loan_amount=home_price - down_payment_2,
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

if include_rent_analysis:
    rent_scenario = RentScenario(
        name=f"Rent (${monthly_rent:,.0f}/month)",
        home_price=home_price,
        monthly_rent=monthly_rent,
        annual_rent_increase=rent_increase,  # Fixed parameter name
        renters_insurance=renters_insurance,
        down_payment_invested=down_payment_1,
        closing_costs=home_price * 0.03,
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    )
    rent_results = analyzer.analyze_rent_scenario(rent_scenario)
    # Use correct method signature for break-even analysis
    break_even_analysis = analyzer.calculate_break_even_analysis(rent_scenario, scenarios[0])
else:
    rent_scenario = None
    rent_results = None
    break_even_analysis = None

# Store data for export
data = {
    'scenarios': scenarios,
    'results': results,
    'rent_scenario': rent_scenario,
    'rent_results': rent_results,
    'break_even_analysis': break_even_analysis,
    'analyzer': analyzer,
    'params': {
        'home_price': home_price,
        'rate_30yr': rate_30yr,
        'rate_15yr': rate_15yr,
        'stock_return': stock_return,
        'inflation_rate': inflation_rate,
        'home_appreciation': home_appreciation,
        'emergency_fund': emergency_fund,
        'selected_state': selected_state,
        'tax_rate': tax_rate,
        'property_tax_rate': property_tax_rate,
        'monthly_rent': monthly_rent if include_rent_analysis else None,
        'rent_increase': rent_increase if include_rent_analysis else None,
        'renters_insurance': renters_insurance if include_rent_analysis else None,
    }
}

# Export functionality
scenarios = data['scenarios']
results = data['results']
rent_scenario = data['rent_scenario']
rent_results = data['rent_results']
break_even_analysis = data['break_even_analysis']
params = data['params']

st.markdown('<h2 class="sub-header">💾 Export Options</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Enhanced CSV Export")
    st.markdown("**Comprehensive dataset with:**")
    st.markdown("- Year-by-year data for all scenarios")
    st.markdown("- Investment values and net worth")
    st.markdown("- Home equity progression")
    st.markdown("- Rent analysis (if enabled)")
    st.markdown("- Perfect for detailed spreadsheet analysis")

    if st.button("📊 Generate Enhanced CSV", type="primary"):
        all_data = []

        for scenario in scenarios:
            result = results[scenario.name]
            if 'yearly_data' in result:
                for year_data in result['yearly_data']:
                    all_data.append({
                        'Type': 'Mortgage',
                        'Scenario': scenario.name,
                        'Year': year_data['year'],
                        'Home Value': year_data['home_value'],
                        'Loan Balance': year_data['loan_balance'],
                        'Home Equity': year_data['home_equity'],
                        'Investment Value': year_data['investment_value'],
                        'Net Worth (Nominal)': year_data['net_worth'],
                        'Net Worth (Real)': year_data['net_worth_adjusted'],
                        'Monthly Payment': result.get('monthly_payment', 0),
                        'Property Tax': year_data.get('property_tax', 0),
                        'Interest Paid': year_data.get('yearly_interest', 0)
                    })

        if include_rent_analysis and rent_results and 'yearly_data' in rent_results:
            for year_data in rent_results['yearly_data']:
                all_data.append({
                    'Type': 'Rent',
                    'Scenario': 'Rent Scenario',
                    'Year': year_data['year'],
                    'Home Value': year_data.get('home_value_if_bought', 0),
                    'Loan Balance': 0,
                    'Home Equity': 0,
                    'Investment Value': year_data['investment_value'],
                    'Net Worth (Nominal)': year_data['net_worth'],
                    'Net Worth (Real)': year_data['net_worth_adjusted'],
                    'Monthly Payment': year_data['monthly_rent'],
                    'Property Tax': 0,
                    'Interest Paid': 0,
                    'Annual Rent': year_data.get('annual_rent_paid', 0),
                    'Cumulative Rent': year_data.get('cumulative_rent_paid', 0)
                })

        if all_data:
            csv_df = pd.DataFrame(all_data)
            csv_buffer = io.StringIO()
            csv_df.to_csv(csv_buffer, index=False)
            csv_string = csv_buffer.getvalue()

            st.download_button(
                label="📊 Download Enhanced CSV",
                data=csv_string,
                file_name='comprehensive_mortgage_analysis.csv',
                mime='text/csv'
            )
            st.success("✅ Enhanced CSV ready!")
        else:
            st.error("No data available for export")

with col2:
    st.markdown("### 📋 Summary Table Export")
    st.markdown("**Quick comparison table with:**")
    st.markdown("- Key metrics for each scenario")
    st.markdown("- Final net worth comparisons")
    st.markdown("- Monthly payment breakdown")
    st.markdown("- Total interest/rent costs")
    st.markdown("- Ideal for executive presentations")

    if st.button("📋 Generate Summary Table", type="secondary"):
        summary_data = []

        for scenario in scenarios:
            result = results[scenario.name]
            summary_data.append({
                'Scenario': scenario.name,
                'Type': 'Mortgage',
                'Down Payment': f"${scenario.down_payment:,.0f}",
                'Monthly Payment': f"${result.get('monthly_payment', 0):,.0f}",
                'Total Interest': f"${result.get('total_interest', 0):,.0f}",
                'Final Net Worth (Real)': f"${result.get('final_net_worth_adjusted', 0):,.0f}",
                'Final Net Worth (Nominal)': f"${result.get('final_net_worth', 0):,.0f}"
            })

        if include_rent_analysis and rent_results:
            summary_data.append({
                'Scenario': 'Rent Scenario',
                'Type': 'Rent',
                'Down Payment': f"${params['monthly_rent'] * 12 if params['monthly_rent'] else 0:,.0f} (Invested)",
                'Monthly Payment': f"${params['monthly_rent'] + (params['renters_insurance']/12 if params['renters_insurance'] else 0):,.0f}",
                'Total Interest': f"${rent_results.get('total_rent_paid', 0):,.0f} (Total Rent)",
                'Final Net Worth (Real)': f"${rent_results.get('final_net_worth_adjusted', 0):,.0f}",
                'Final Net Worth (Nominal)': f"${rent_results.get('final_net_worth', 0):,.0f}"
            })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            csv_buffer = io.StringIO()
            summary_df.to_csv(csv_buffer, index=False)
            csv_string = csv_buffer.getvalue()

            st.download_button(
                label="📋 Download Summary CSV",
                data=csv_string,
                file_name='mortgage_summary.csv',
                mime='text/csv'
            )
            st.success("✅ Summary table ready!")
        else:
            st.error("No data available for export")

with col3:
    st.markdown("### 📄 Executive Report")
    st.markdown("**Comprehensive professional report:**")
    st.markdown("- Executive summary with recommendations")
    st.markdown("- Detailed analysis methodology")
    st.markdown("- Market assumptions and disclaimers")
    st.markdown("- Break-even analysis (if rent enabled)")
    st.markdown("- Perfect for financial advisors/planning")

    if st.button("📄 Generate Executive Report", type="secondary"):
        best_scenario = max(results.keys(), key=lambda x: results[x].get('final_net_worth_adjusted', 0))
        best_wealth = results[best_scenario].get('final_net_worth_adjusted', 0)
        worst_wealth = min(results[x].get('final_net_worth_adjusted', 0) for x in results.keys())
        wealth_difference = best_wealth - worst_wealth

        report = f"""# Comprehensive Mortgage & Housing Analysis Report
Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}

## Executive Summary

### Property Details
- Home Price: ${params['home_price']:,.0f}
- Location: {params['selected_state']}
- Analysis Period: 30 years
- Emergency Fund: ${params['emergency_fund']:,.0f}

### Market Assumptions
- 30-Year Mortgage Rate: {params['rate_30yr']*100:.1f}%
- 15-Year Mortgage Rate: {params['rate_15yr']*100:.1f}%
- Expected Stock Market Return: {params['stock_return']*100:.1f}%
- Expected Inflation Rate: {params['inflation_rate']*100:.1f}%
- Expected Home Appreciation: {params['home_appreciation']*100:.1f}%

### Tax Information
- State: {params['selected_state']}
- Combined Tax Rate: {params['tax_rate']*100:.1f}%
- Property Tax Rate: {params['property_tax_rate']*100:.1f}%

## Analysis Results

### Best Financial Strategy
**{best_scenario}**
- Final Net Worth (Real): ${best_wealth:,.0f}
- Performance advantage: ${wealth_difference:,.0f} over worst scenario

### All Scenarios Summary
"""

        for scenario_name, result in results.items():
            report += f"""
**{scenario_name}:**
- Monthly Payment: ${result.get('monthly_payment', 0):,.0f}
- Total Interest: ${result.get('total_interest', 0):,.0f}
- Final Net Worth: ${result.get('final_net_worth_adjusted', 0):,.0f}
"""

        if include_rent_analysis and break_even_analysis:
            report += f"""
## Rent vs Buy Analysis

### Rental Scenario
- Monthly Rent: ${params['monthly_rent']:,.0f}
- Annual Rent Increase: {params['rent_increase']*100:.1f}%
- Renters Insurance: ${params['renters_insurance']:,.0f}/year

### Break-Even Analysis
- Break-Even Point: {break_even_analysis.get('break_even_year', 'Never')} years
- 30-Year Advantage: ${break_even_analysis.get('advantage_at_30_years', 0):,.0f}
- Final Net Worth (Renting): ${break_even_analysis.get('final_rent_net_worth', 0):,.0f}
- Final Net Worth (Buying): ${break_even_analysis.get('final_buy_net_worth', 0):,.0f}

### Recommendation
"""
            break_even_year = break_even_analysis.get('break_even_year')
            if break_even_year and break_even_year <= 10:
                report += "🏠 **BUYING RECOMMENDED** - Short break-even period makes buying financially advantageous.\n"
            elif break_even_year and break_even_year <= 20:
                report += "⚖️ **MODERATE ADVANTAGE TO BUYING** - Consider personal factors like mobility and maintenance preferences.\n"
            elif break_even_year:
                report += "🏢 **CONSIDER RENTING** - Long break-even period suggests renting may be better for shorter stays.\n"
            else:
                report += "🏢 **RENTING RECOMMENDED** - Financial analysis favors renting and investing in this scenario.\n"

        report += f"""
## Key Financial Insights

1. **Total Wealth Impact**: The choice between scenarios can impact your net worth by ${wealth_difference:,.0f} over 30 years.

2. **Monthly Cash Flow**: Consider both the monthly payment burden and opportunity cost of down payments.

3. **Investment Opportunity**: Money not tied up in real estate can be invested in the stock market at {params['stock_return']*100:.1f}% expected return.

4. **Inflation Protection**: Real values account for {params['inflation_rate']*100:.1f}% annual inflation, showing true purchasing power.

## Important Disclaimers

This analysis is based on simplified assumptions and should not be considered financial advice. Consider factors not included in this model:

- Private Mortgage Insurance (PMI)
- Homeowners insurance costs
- HOA fees
- Maintenance and repair costs
- Closing costs and transaction fees
- Market volatility
- Personal lifestyle preferences
- Job mobility requirements

Consult with qualified financial advisors, tax professionals, and mortgage specialists for personalized advice.

---
Generated by Know Your Mortgage Analysis Tool
Live Version: https://know-your-mortgage-e7xnzpbgxc2oqqugtgjvye.streamlit.app/
"""

        st.download_button(
            label="📝 Download Executive Report",
            data=report,
            file_name='executive_mortgage_report.txt',
            mime='text/plain'
        )
        st.success("✅ Executive report ready!")

st.markdown("---")

st.markdown("### 📊 Data Preview")

if st.checkbox("Show Summary Data Preview"):
    summary_data = []
    for scenario in scenarios:
        result = results[scenario.name]
        summary_data.append({
            'Scenario': scenario.name,
            'Monthly Payment': f"${result.get('monthly_payment', 0):,.0f}",
            'Total Interest': f"${result.get('total_interest', 0):,.0f}",
            'Final Net Worth (Real)': f"${result.get('final_net_worth_adjusted', 0):,.0f}"
        })

    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch', hide_index=True)

st.markdown("---")
st.markdown("### 📖 Export Tips")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **💡 CSV Export Best Practices:**
    - Enhanced CSV: Best for detailed analysis in Excel
    - Summary CSV: Best for quick comparisons
    - Both include inflation-adjusted (real) values
    - Year-by-year data shows progression over time
    """)

with col2:
    st.warning("""
    **⚠️ Important Notes:**
    - Generate analysis data first using sidebar parameters
    - Reports reflect current market assumptions
    - Consider updating parameters for different scenarios
    - Executive reports include important disclaimers
    """)

st.markdown("💡 **Next Steps:** Use exported data with financial advisors, compare scenarios in spreadsheets, or share professional reports for decision making.")