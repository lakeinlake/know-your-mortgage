import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from mortgage_analyzer import MortgageAnalyzer, MortgageScenario, RentScenario, GoogleSheetsExporter
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

# Add first-time home buyer guidance
def show_golden_rules():
    """Display golden rules for first-time home buyers"""
    st.info("""
    ## 🎯 First-Time Home Buyer Golden Rules

    **💰 Down Payment Guidelines:**
    - Put down 20% to avoid PMI (Private Mortgage Insurance)
    - Minimum: 3-5% for conventional loans, 3.5% for FHA
    - More down payment = lower monthly payments but less money to invest

    **🚨 Emergency Fund Rules:**
    - Keep 3-6 months of expenses in emergency fund
    - For homeowners: 6-12 months recommended (maintenance costs)
    - Don't use emergency fund for down payment!

    **📊 Debt-to-Income Guidelines:**
    - Total monthly debts should be ≤ 43% of gross income
    - Housing costs should be ≤ 28% of gross income
    - Lower ratios = better loan terms

    **🏠 Additional Costs to Budget:**
    - Property taxes (1-3% of home value annually)
    - Homeowners insurance ($1,000-3,000/year)
    - Maintenance (1-3% of home value annually)
    - HOA fees (if applicable)
    - Utilities and moving costs

    **🎯 Smart Home Buying Strategy:**
    1. Get pre-approved for a mortgage first
    2. Shop around for best rates (get 3+ quotes)
    3. Consider total cost of ownership, not just monthly payment
    4. Don't buy at the top of your budget - leave room for surprises
    5. Think long-term: Will you stay 5+ years?
    6. Factor in your commute and lifestyle needs

    **📱 This Tool Helps You:**
    - Compare different down payment strategies
    - Understand PMI costs and when to avoid them
    - See real vs nominal values (inflation-adjusted)
    - Compare buying vs renting financially
    - Calculate appropriate emergency fund levels
    - Export professional reports for planning
    """)

def calculate_recommended_emergency_fund(monthly_payment, home_price):
    """Calculate recommended emergency fund for homeowners"""
    # Conservative approach: 6 months of total housing costs
    # Includes mortgage, property tax, insurance, maintenance
    monthly_housing_cost = monthly_payment * 1.4  # Add 40% for taxes, insurance, maintenance
    return monthly_housing_cost * 6

def check_pmi_requirement(home_price, down_payment):
    """Check if PMI is required and calculate cost"""
    loan_to_value = (home_price - down_payment) / home_price

    if loan_to_value > 0.8:  # More than 80% financed
        # PMI typically costs 0.3% to 1.5% of loan amount annually
        pmi_rate = 0.005  # 0.5% annual rate (middle estimate)
        annual_pmi = (home_price - down_payment) * pmi_rate
        monthly_pmi = annual_pmi / 12
        return True, monthly_pmi, loan_to_value

    return False, 0, loan_to_value

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

# First-time home buyer guidance section
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    **Welcome to the comprehensive mortgage analysis tool!** Compare different mortgage scenarios,
    analyze rent vs buy decisions, and make informed decisions about your home purchase.

    🎯 **Key Features:** Compare mortgages • Rent vs Buy analysis • Investment opportunity costs • Professional reports
    """)

with col2:
    if st.button("📚 First-Time Buyer Guide", type="secondary"):
        st.session_state.show_guide = not st.session_state.get('show_guide', False)

# Show educational content if requested
if st.session_state.get('show_guide', False):
    with st.expander("🎓 First-Time Home Buyer Education", expanded=True):
        show_golden_rules()

# Glossary section at the top
with st.expander("📚 Financial Terms Glossary (Essential for First-Time Buyers)", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 💰 Key Financial Terms

        **PMI (Private Mortgage Insurance):**
        - Required when down payment < 20%
        - Protects lender if you default
        - Typically 0.3% - 1.5% of loan amount annually
        - Can be removed once you reach 20% equity

        **LTV (Loan-to-Value Ratio):**
        - Loan amount ÷ Home value
        - 80% LTV = 20% down payment
        - Lower LTV = better rates, no PMI

        **DTI (Debt-to-Income Ratio):**
        - Total monthly debts ÷ Monthly income
        - Housing DTI: ≤ 28% recommended
        - Total DTI: ≤ 43% for most loans

        **APR (Annual Percentage Rate):**
        - True cost including fees and interest
        - Higher than interest rate
        - Better for comparing loan offers

        **Real vs Nominal Values:**
        - **Real**: Adjusted for inflation (true purchasing power)
        - **Nominal**: Raw dollar amounts
        - **Example**: $1M in 30 years ≈ $410K today (3% inflation)
        """)

    with col2:
        st.markdown("""
        ### 🏠 Loan & Property Terms

        **FHA Loan:**
        - Government-backed loan program
        - 3.5% minimum down payment
        - Lower credit score requirements
        - Requires mortgage insurance

        **Conventional Loan:**
        - Not government-backed
        - Typically 3-5% minimum down
        - Better rates for good credit
        - PMI removable at 20% equity

        **HOA (Homeowners Association):**
        - Monthly/annual fees for shared amenities
        - Can range from $50-500+ per month
        - Not included in mortgage payment
        - Factor into total housing costs

        **Escrow Account:**
        - Lender holds money for taxes/insurance
        - Part of monthly payment
        - Ensures bills are paid on time

        **Closing Costs:**
        - Fees to finalize the purchase
        - Typically 2-5% of home price
        - Includes appraisal, title, inspection
        - Separate from down payment
        """)

    # Quick reference guide
    st.markdown("""
    ### 🎯 Quick Reference: Good vs Concerning

    | Metric | 🟢 Good | 🟡 Caution | 🔴 Risky |
    |--------|----------|-------------|----------|
    | Down Payment | 20%+ | 10-19% | <10% |
    | Housing DTI | <25% | 25-28% | >28% |
    | Total DTI | <36% | 36-43% | >43% |
    | Credit Score | 740+ | 680-739 | <680 |
    | Emergency Fund | 6+ months | 3-6 months | <3 months |
    | LTV Ratio | <80% | 80-90% | >90% |
    """)

    st.info("💡 **Focus on 'Real' values throughout the analysis** - they show what your money will actually be worth in today's purchasing power.")

# Sidebar for inputs
st.sidebar.header("📊 Analysis Parameters")

# Quick tips toggle
with st.sidebar.expander("💡 Quick Tips for Home Buyers"):
    st.markdown("""
    **💰 Down Payment Tips:**
    - 20% = No PMI + Better rates
    - 10-19% = PMI required but manageable
    - 5-9% = Higher PMI + riskier
    - 3-5% = FHA loans available

    **🚨 Red Flags:**
    - Monthly payment > 28% of income
    - Total debt > 43% of income
    - Emergency fund < 3 months expenses
    - No money left for maintenance

    **✅ Green Lights:**
    - Stable job + income
    - Good credit score (740+)
    - Low debt-to-income ratio
    - 6+ months emergency fund

    **📊 Use the Financial Profile below** to get real-time
    affordability analysis and personalized recommendations!
    """)

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

# Real-time home price affordability feedback (need to calculate based on future income inputs)
# This will be updated after we have income data

down_payment_100k = st.sidebar.slider(
    "Down Payment - Option 1 ($)",
    min_value=20000,
    max_value=home_price,
    value=min(100000, home_price),
    step=10000,
    format="$%d",
    help="Down payment for first comparison scenario"
)

# PMI warning for Option 1
pmi_required_1, monthly_pmi_1, ltv_1 = check_pmi_requirement(home_price, down_payment_100k)
if pmi_required_1:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi_1:.0f}/month (LTV: {ltv_1:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv_1:.1%})")

down_payment_200k = st.sidebar.slider(
    "Down Payment - Option 2 ($)",
    min_value=20000,
    max_value=home_price,
    value=min(200000, home_price),
    step=10000,
    format="$%d",
    help="Down payment for second comparison scenario"
)

# PMI warning for Option 2
pmi_required_2, monthly_pmi_2, ltv_2 = check_pmi_requirement(home_price, down_payment_200k)
if pmi_required_2:
    st.sidebar.warning(f"⚠️ PMI Required: ~${monthly_pmi_2:.0f}/month (LTV: {ltv_2:.1%})")
else:
    st.sidebar.success(f"✅ No PMI needed (LTV: {ltv_2:.1%})")

# Rent vs Buy Analysis
st.sidebar.subheader("Rent vs Buy Analysis")
include_rent_analysis = st.sidebar.checkbox(
    "Include Rent Comparison",
    value=True,
    help="Compare buying vs renting the same property"
)

if include_rent_analysis:
    monthly_rent = st.sidebar.slider(
        "Monthly Rent ($)",
        min_value=500,
        max_value=int(home_price * 0.01),
        value=int(home_price * 0.005),
        step=100,
        format="$%d",
        help="Monthly rent for equivalent property"
    )

    rent_increase = st.sidebar.slider(
        "Annual Rent Increase (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.5,
        format="%.1f%%",
        help="Expected annual rent increase"
    ) / 100

    renters_insurance = st.sidebar.slider(
        "Annual Renters Insurance ($)",
        min_value=0,
        max_value=1000,
        value=200,
        step=50,
        format="$%d",
        help="Annual cost of renters insurance"
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

# Emergency fund guidance - calculate after basic parameters are set
# Initialize analyzer here for emergency fund calculation
temp_analyzer = MortgageAnalyzer(home_price=home_price, emergency_fund=emergency_fund)
sample_payment = temp_analyzer.calculate_monthly_payment(
    home_price - down_payment_100k, rate_30yr, 30
)
recommended_emergency = calculate_recommended_emergency_fund(sample_payment, home_price)

if emergency_fund < recommended_emergency * 0.5:  # Less than 50% of recommended
    st.sidebar.error(f"🚨 Emergency fund too low! Recommended: ${recommended_emergency:,.0f}")
elif emergency_fund < recommended_emergency:
    st.sidebar.warning(f"⚠️ Consider ${recommended_emergency:,.0f} for homeowners")
else:
    st.sidebar.success("✅ Good emergency fund level")

# Financial Profile & Affordability Analysis
st.sidebar.subheader("💰 Your Financial Profile")

annual_income = st.sidebar.number_input(
    "Annual Gross Income ($)",
    min_value=20000,
    max_value=1000000,
    value=96000,
    step=5000,
    help="Your total annual income before taxes"
)

monthly_income = annual_income / 12

monthly_debts = st.sidebar.number_input(
    "Monthly Debt Payments ($)",
    min_value=0,
    max_value=20000,
    value=500,
    step=100,
    help="Car loans, credit cards, student loans, etc. (monthly payments)"
)

# Net Worth Breakdown
st.sidebar.write("**Net Worth Breakdown:**")
cash_savings = st.sidebar.number_input(
    "Cash Savings ($)",
    min_value=0,
    max_value=2000000,
    value=150000,
    step=10000,
    help="Liquid cash available (savings, checking, CDs)"
)

stock_investments = st.sidebar.number_input(
    "Stock/Investment Portfolio ($)",
    min_value=0,
    max_value=5000000,
    value=100000,
    step=10000,
    help="Stocks, bonds, 401k, IRA, etc."
)

total_net_worth = cash_savings + stock_investments

# Affordability Analysis
max_housing_payment = monthly_income * 0.28
max_total_debt = monthly_income * 0.43
available_for_housing = max_total_debt - monthly_debts

# Current home affordability check
current_payment = temp_analyzer.calculate_monthly_payment(
    home_price - down_payment_100k, rate_30yr, 30
)

# Add property tax and insurance estimates (use default 2% for property tax)
estimated_prop_tax = (home_price * 0.02) / 12  # Default 2% property tax
estimated_insurance = 200  # Rough estimate
total_housing_cost = current_payment + estimated_prop_tax + estimated_insurance

# Debt-to-income ratios
housing_ratio = (total_housing_cost / monthly_income) * 100
total_debt_ratio = ((total_housing_cost + monthly_debts) / monthly_income) * 100

st.sidebar.write("**📊 Affordability Analysis:**")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Max Housing", f"${max_housing_payment:,.0f}/mo")
with col2:
    st.metric("Available", f"${available_for_housing:,.0f}/mo")

# Comprehensive affordability feedback
if total_housing_cost > available_for_housing:
    st.sidebar.error(f"🚨 House too expensive! Payment: ${total_housing_cost:,.0f} > Limit: ${available_for_housing:,.0f}")
elif total_housing_cost > max_housing_payment:
    st.sidebar.warning(f"⚠️ Tight budget. Housing ratio: {housing_ratio:.1f}% (ideal <28%)")
elif housing_ratio > 25:
    st.sidebar.warning(f"⚠️ Consider lower price. Housing ratio: {housing_ratio:.1f}%")
else:
    st.sidebar.success(f"✅ Affordable! Housing ratio: {housing_ratio:.1f}%")

# Total debt ratio feedback
if total_debt_ratio > 43:
    st.sidebar.error(f"🚨 Total debt too high: {total_debt_ratio:.1f}% (max 43%)")
elif total_debt_ratio > 36:
    st.sidebar.warning(f"⚠️ High debt load: {total_debt_ratio:.1f}%")
else:
    st.sidebar.success(f"✅ Good debt ratio: {total_debt_ratio:.1f}%")

# Net worth insights
st.sidebar.write(f"**Total Net Worth:** ${total_net_worth:,.0f}")
if cash_savings < down_payment_100k + emergency_fund:
    shortage = (down_payment_100k + emergency_fund) - cash_savings
    st.sidebar.warning(f"⚠️ Need ${shortage:,.0f} more cash for down payment + emergency fund")

# Smart home price recommendations
st.sidebar.write("**🎯 Recommended Home Price Range:**")

# Calculate conservative and aggressive price ranges
conservative_max_payment = monthly_income * 0.25  # Conservative 25%
aggressive_max_payment = monthly_income * 0.30   # Aggressive 30%

# Estimate affordable home prices (roughly)
conservative_home_price = conservative_max_payment * 240  # ~240x monthly payment rule
aggressive_home_price = aggressive_max_payment * 240

# Adjust for down payment
conservative_with_down = conservative_home_price + down_payment_100k
aggressive_with_down = aggressive_home_price + down_payment_100k

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Conservative", f"${conservative_with_down:,.0f}", help="25% of income to housing")
with col2:
    st.metric("Aggressive", f"${aggressive_with_down:,.0f}", help="30% of income to housing")

# Current home price feedback
if home_price > aggressive_with_down:
    price_ratio = (home_price / aggressive_with_down - 1) * 100
    st.sidebar.error(f"🚨 Current home ${price_ratio:.0f}% over aggressive budget!")
elif home_price > conservative_with_down:
    st.sidebar.warning(f"⚠️ Above conservative range - requires careful budgeting")
else:
    st.sidebar.success(f"✅ Within conservative budget - good choice!")

# Tax Rate Section with State Selection
st.sidebar.subheader("🏛️ Tax Information")

# State selection for tax rates
state_tax_rates = {
    "Alabama": 5.0, "Alaska": 0.0, "Arizona": 4.5, "Arkansas": 5.9, "California": 13.3,
    "Colorado": 4.4, "Connecticut": 6.9, "Delaware": 6.6, "Florida": 0.0, "Georgia": 5.75,
    "Hawaii": 11.0, "Idaho": 6.0, "Illinois": 4.95, "Indiana": 3.23, "Iowa": 8.53,
    "Kansas": 5.7, "Kentucky": 5.0, "Louisiana": 4.25, "Maine": 7.15, "Maryland": 5.75,
    "Massachusetts": 5.0, "Michigan": 4.25, "Minnesota": 9.85, "Mississippi": 5.0,
    "Missouri": 5.3, "Montana": 6.75, "Nebraska": 6.84, "Nevada": 0.0, "New Hampshire": 0.0,
    "New Jersey": 10.75, "New Mexico": 5.9, "New York": 10.9, "North Carolina": 4.99,
    "North Dakota": 2.9, "Ohio": 3.99, "Oklahoma": 5.0, "Oregon": 9.9, "Pennsylvania": 3.07,
    "Rhode Island": 5.99, "South Carolina": 7.0, "South Dakota": 0.0, "Tennessee": 0.0,
    "Texas": 0.0, "Utah": 4.85, "Vermont": 8.75, "Virginia": 5.75, "Washington": 0.0,
    "West Virginia": 6.5, "Wisconsin": 7.65, "Wyoming": 0.0
}

selected_state = st.sidebar.selectbox(
    "Select Your State",
    options=list(state_tax_rates.keys()),
    index=list(state_tax_rates.keys()).index("California"),
    help="Used to estimate combined federal + state tax rate"
)

state_rate = state_tax_rates[selected_state]

# Federal tax bracket selection
federal_brackets = {
    "10% ($0 - $11,000)": 10,
    "12% ($11,001 - $44,725)": 12,
    "22% ($44,726 - $95,375)": 22,
    "24% ($95,376 - $182,050)": 24,
    "32% ($182,051 - $231,250)": 32,
    "35% ($231,251 - $578,125)": 35,
    "37% ($578,126+)": 37
}

federal_bracket = st.sidebar.selectbox(
    "Federal Tax Bracket (2024)",
    options=list(federal_brackets.keys()),
    index=2,  # Default to 22%
    help="Your marginal federal income tax rate"
)

federal_rate = federal_brackets[federal_bracket]

# Combined tax rate
combined_rate = federal_rate + state_rate
tax_rate = combined_rate / 100

st.sidebar.write(f"**Combined Tax Rate:** {combined_rate:.1f}%")
st.sidebar.write(f"- Federal: {federal_rate}%")
st.sidebar.write(f"- {selected_state} State: {state_rate}%")

# Tax rate explanation
with st.sidebar.expander("❓ What is this tax rate used for?"):
    st.markdown("""
    **Mortgage Interest Deduction:**
    - You can deduct mortgage interest from taxable income
    - This reduces your tax bill by: Interest × Your Tax Rate
    - Example: $10,000 interest × 26% rate = $2,600 tax savings

    **Important Notes:**
    - Only applies if you itemize deductions
    - Standard deduction is $14,600 (single) / $29,200 (married)
    - Most effective for higher-income earners
    - Consult a tax professional for personalized advice

    **This tool uses your combined rate to calculate:**
    - Annual tax savings from mortgage interest
    - Effective mortgage interest rate after tax benefits
    """)

# Property Tax Information
st.sidebar.subheader("🏠 Property Tax Rate")

# Common property tax rates by state (approximate averages)
property_tax_averages = {
    "Alabama": 0.41, "Alaska": 1.19, "Arizona": 0.62, "Arkansas": 0.61, "California": 0.75,
    "Colorado": 0.51, "Connecticut": 2.14, "Delaware": 0.57, "Florida": 0.83, "Georgia": 0.89,
    "Hawaii": 0.28, "Idaho": 0.69, "Illinois": 2.27, "Indiana": 0.85, "Iowa": 1.53,
    "Kansas": 1.41, "Kentucky": 0.86, "Louisiana": 0.55, "Maine": 1.28, "Maryland": 1.06,
    "Massachusetts": 1.17, "Michigan": 1.64, "Minnesota": 1.12, "Mississippi": 0.81,
    "Missouri": 0.97, "Montana": 0.84, "Nebraska": 1.73, "Nevada": 0.53, "New Hampshire": 2.18,
    "New Jersey": 2.49, "New Mexico": 0.80, "New York": 1.68, "North Carolina": 0.84,
    "North Dakota": 0.98, "Ohio": 1.53, "Oklahoma": 0.90, "Oregon": 0.87, "Pennsylvania": 1.58,
    "Rhode Island": 1.53, "South Carolina": 0.57, "South Dakota": 1.32, "Tennessee": 0.67,
    "Texas": 1.80, "Utah": 0.60, "Vermont": 1.90, "Virginia": 0.82, "Washington": 0.92,
    "West Virginia": 0.59, "Wisconsin": 1.85, "Wyoming": 0.62
}

# Auto-populate based on selected state
default_prop_tax = property_tax_averages.get(selected_state, 2.0)

property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (%)",
    min_value=0.0,
    max_value=5.0,
    value=default_prop_tax,
    step=0.1,
    format="%.1f%%",
    help=f"Annual property tax as percentage of home value. {selected_state} average: {default_prop_tax:.1f}%"
) / 100

st.sidebar.write(f"**{selected_state} average:** {default_prop_tax:.1f}%")

with st.sidebar.expander("💡 Property Tax Tips"):
    st.markdown("""
    **Property Tax Basics:**
    - Paid annually to local government
    - Based on assessed home value
    - Funds schools, roads, public services
    - Can be appealed if assessment seems high

    **What affects your rate:**
    - Local school district quality
    - Municipal services provided
    - Recent home sales in area
    - Property improvements/renovations

    **Planning tips:**
    - Factor into total monthly housing cost
    - May be included in mortgage payment (escrow)
    - Can increase with home value appreciation
    - Different rates within same city/county
    """)

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

# Add rent scenario if enabled
if include_rent_analysis:
    rent_scenario = RentScenario(
        name=f"Rent (${monthly_rent:,.0f}/month)",
        home_price=home_price,
        monthly_rent=monthly_rent,
        annual_rent_increase=rent_increase,
        renters_insurance=renters_insurance,
        down_payment_invested=down_payment_100k,  # Use first down payment option
        closing_costs=home_price * 0.03,  # 3% closing costs
        inflation_rate=inflation_rate,
        stock_return_rate=stock_return,
        emergency_fund=emergency_fund
    )

# Analyze all scenarios
results = {}
for scenario in scenarios:
    results[scenario.name] = analyzer.analyze_scenario(scenario)

# Analyze rent scenario separately if enabled
rent_results = None
break_even_analysis = None
if include_rent_analysis:
    rent_results = analyzer.analyze_rent_scenario(rent_scenario)
    # Compare rent vs best mortgage scenario (first one: 30-year)
    break_even_analysis = analyzer.calculate_break_even_analysis(rent_scenario, scenarios[0])

# Financial Health Summary
st.markdown('<h2 class="sub-header">💰 Your Financial Health Overview</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    debt_status = "🟢 Good" if total_debt_ratio <= 36 else "🟡 High" if total_debt_ratio <= 43 else "🔴 Too High"
    st.metric(
        "Debt-to-Income",
        f"{total_debt_ratio:.1f}%",
        delta=f"{debt_status}",
        help="Total monthly debts including proposed housing"
    )

with col2:
    housing_status = "🟢 Good" if housing_ratio <= 25 else "🟡 Tight" if housing_ratio <= 28 else "🔴 High"
    st.metric(
        "Housing Ratio",
        f"{housing_ratio:.1f}%",
        delta=f"{housing_status}",
        help="Housing costs as % of income"
    )

with col3:
    cash_ratio = cash_savings / annual_income
    cash_status = "🟢 Strong" if cash_ratio >= 0.5 else "🟡 Moderate" if cash_ratio >= 0.25 else "🔴 Low"
    st.metric(
        "Cash Reserves",
        f"{cash_ratio:.1f}x income",
        delta=f"{cash_status}",
        help="Cash savings as multiple of annual income"
    )

with col4:
    net_worth_ratio = total_net_worth / annual_income
    nw_status = "🟢 Excellent" if net_worth_ratio >= 3 else "🟡 Building" if net_worth_ratio >= 1 else "🔴 Low"
    st.metric(
        "Net Worth",
        f"{net_worth_ratio:.1f}x income",
        delta=f"{nw_status}",
        help="Total net worth as multiple of annual income"
    )

# Key insights based on financial profile
if total_debt_ratio > 43 or housing_ratio > 28:
    st.error("🚨 **Financial Risk Warning:** Your debt ratios exceed recommended limits. Consider a lower-priced home or paying down existing debt first.")
elif cash_savings < down_payment_100k + emergency_fund:
    st.warning("⚠️ **Cash Flow Concern:** You may not have enough liquid cash for both down payment and emergency fund. Consider a smaller down payment or building more savings.")
elif home_price > aggressive_with_down:
    st.warning(f"⚠️ **Budget Stretch:** This home price (${home_price:,.0f}) exceeds your recommended range (${aggressive_with_down:,.0f}). Consider homes in the ${conservative_with_down:,.0f} - ${aggressive_with_down:,.0f} range.")
else:
    st.success("✅ **Financial Health Looks Good:** Your debt ratios, cash reserves, and home price selection appear to be within reasonable ranges for your income level.")

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

    # Add rent scenario to chart if enabled
    if include_rent_analysis and rent_results:
        years = [d['year'] for d in rent_results['yearly_data']]
        net_worth = [d['net_worth'] for d in rent_results['yearly_data']]
        net_worth_real = [d['net_worth_adjusted'] for d in rent_results['yearly_data']]

        # Nominal values
        fig_networth.add_trace(go.Scatter(
            x=years,
            y=net_worth,
            mode='lines',
            name=f"{rent_scenario.name} (Nominal)",
            line=dict(width=2, color='red'),
            visible='legendonly'
        ))

        # Real values (adjusted for inflation)
        fig_networth.add_trace(go.Scatter(
            x=years,
            y=net_worth_real,
            mode='lines',
            name=f"{rent_scenario.name} (Real)",
            line=dict(width=3, dash='solid', color='red')
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

    # Add rent scenario to monthly payment comparison
    if include_rent_analysis and rent_results:
        payment_data.append({
            'Scenario': f"Rent\n(${monthly_rent:,.0f}/mo)",
            'Monthly Payment': monthly_rent + (renters_insurance / 12),
            'Full Name': rent_scenario.name
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

# Rent vs Buy Break-Even Analysis
if include_rent_analysis and break_even_analysis:
    st.markdown('<h2 class="sub-header">🏠 vs 🏢 Rent vs Buy Analysis</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Break-Even Point",
            value=f"{break_even_analysis['break_even_year']} years" if break_even_analysis['break_even_year'] else "Never",
            help="When buying becomes financially better than renting"
        )

    with col2:
        final_advantage = break_even_analysis['total_advantage']
        st.metric(
            label="30-Year Advantage (Buying)",
            value=f"${final_advantage:,.0f}",
            delta=f"vs Renting",
            help="Total financial advantage of buying over renting after 30 years"
        )

    with col3:
        rent_net_worth = break_even_analysis['final_rent_net_worth']
        st.metric(
            label="Final Net Worth (Renting)",
            value=f"${rent_net_worth:,.0f}",
            help="Net worth after 30 years of renting and investing"
        )

    # Break-even chart
    st.subheader("Buy vs Rent Comparison Over Time")

    fig_breakeven = go.Figure()

    years = [data['year'] for data in break_even_analysis['yearly_comparison']]
    buy_values = [data['buy_net_worth'] for data in break_even_analysis['yearly_comparison']]
    rent_values = [data['rent_net_worth'] for data in break_even_analysis['yearly_comparison']]

    fig_breakeven.add_trace(go.Scatter(
        x=years,
        y=buy_values,
        mode='lines',
        name="Buying (30-year mortgage)",
        line=dict(width=3, color='blue')
    ))

    fig_breakeven.add_trace(go.Scatter(
        x=years,
        y=rent_values,
        mode='lines',
        name="Renting + Investing",
        line=dict(width=3, color='red')
    ))

    # Add break-even point marker
    if break_even_analysis['break_even_year']:
        break_even_year = break_even_analysis['break_even_year']
        break_even_value = break_even_analysis['yearly_comparison'][break_even_year-1]['buy_net_worth']

        fig_breakeven.add_trace(go.Scatter(
            x=[break_even_year],
            y=[break_even_value],
            mode='markers',
            name=f"Break-Even (Year {break_even_year})",
            marker=dict(size=12, color='green', symbol='star')
        ))

    fig_breakeven.update_layout(
        title="Rent vs Buy: Net Worth Comparison Over Time",
        xaxis_title="Year",
        yaxis_title="Net Worth (Real, Inflation-Adjusted)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_breakeven, use_container_width=True)

    # Summary insights
    if break_even_analysis['break_even_year']:
        st.success(f"📈 **Buying becomes better than renting after {break_even_analysis['break_even_year']} years**")
    else:
        st.warning(f"⚠️ **Renting appears financially better in this scenario over 30 years**")

    if final_advantage > 0:
        advantage_pct = (final_advantage / rent_net_worth) * 100
        st.info(f"💰 **After 30 years, buying provides ${final_advantage:,.0f} more wealth ({advantage_pct:.1f}% advantage)**")
    else:
        disadvantage_pct = abs(final_advantage / rent_net_worth) * 100
        st.info(f"💸 **After 30 years, renting provides ${abs(final_advantage):,.0f} more wealth ({disadvantage_pct:.1f}% advantage)**")

# Detailed analysis tabs
st.markdown('<h2 class="sub-header">📋 Detailed Analysis</h2>', unsafe_allow_html=True)

# Update tabs to include rent analysis
if include_rent_analysis:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Investment Growth", "Home Equity", "Interest Analysis", "Year-by-Year Data", "Rent Details"])
else:
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

# Add rent details tab if enabled
if include_rent_analysis:
    with tab5:
        st.subheader("Rent Analysis Details")

        if rent_results:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="Starting Monthly Rent",
                    value=f"${monthly_rent:,.0f}",
                    help="Initial monthly rent amount"
                )

            with col2:
                final_year_rent = rent_results['yearly_data'][-1]['monthly_rent']
                st.metric(
                    label="Year 30 Monthly Rent",
                    value=f"${final_year_rent:,.0f}",
                    delta=f"+{((final_year_rent/monthly_rent - 1) * 100):.1f}%",
                    help="Monthly rent in year 30 after annual increases"
                )

            with col3:
                total_rent_30yr = rent_results['total_rent_paid']
                st.metric(
                    label="Total Rent Paid (30 Years)",
                    value=f"${total_rent_30yr:,.0f}",
                    help="Cumulative rent payments over 30 years"
                )

            # Rent escalation chart
            st.subheader("Rent Escalation Over Time")

            fig_rent = go.Figure()

            years = [d['year'] for d in rent_results['yearly_data']]
            monthly_rents = [d['monthly_rent'] for d in rent_results['yearly_data']]
            annual_rents = [d['annual_rent_paid'] for d in rent_results['yearly_data']]

            fig_rent.add_trace(go.Scatter(
                x=years,
                y=monthly_rents,
                mode='lines',
                name="Monthly Rent",
                line=dict(width=3, color='orange'),
                yaxis='y'
            ))

            fig_rent.add_trace(go.Scatter(
                x=years,
                y=annual_rents,
                mode='lines',
                name="Annual Rent",
                line=dict(width=3, color='red'),
                yaxis='y2'
            ))

            fig_rent.update_layout(
                title="Rent Increases Over Time",
                xaxis_title="Year",
                yaxis=dict(title="Monthly Rent ($)", side='left'),
                yaxis2=dict(title="Annual Rent ($)", side='right', overlaying='y'),
                height=400,
                hovermode='x unified'
            )

            st.plotly_chart(fig_rent, use_container_width=True)

            # Detailed rent data table
            st.subheader("Year-by-Year Rent Analysis")

            rent_df = pd.DataFrame(rent_results['yearly_data'])
            rent_df_display = rent_df[['year', 'monthly_rent', 'annual_rent_paid', 'cumulative_rent_paid', 'investment_value', 'net_worth_adjusted']].copy()
            rent_df_display.columns = ['Year', 'Monthly Rent', 'Annual Rent', 'Cumulative Rent', 'Investment Value', 'Net Worth (Real)']

            # Format as currency
            for col in ['Monthly Rent', 'Annual Rent', 'Cumulative Rent', 'Investment Value', 'Net Worth (Real)']:
                rent_df_display[col] = rent_df_display[col].apply(lambda x: f"${x:,.0f}")

            st.dataframe(
                rent_df_display,
                use_container_width=True,
                hide_index=True,
                height=400
            )

# Export functionality
st.markdown('<h2 class="sub-header">💾 Export Results</h2>', unsafe_allow_html=True)

# Google Sheets export temporarily disabled for debugging
# Uncomment this section when authentication issues are resolved

# col1, col2, col3 = st.columns(3)
#
# with col1:
#     st.info("🚧 **Google Sheets Export**: Temporarily disabled for maintenance. Use CSV export below for now.")
#     # Google Sheets export code commented out for now
#     # Will be re-enabled once authentication issues are resolved
#
# with col2:

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Enhanced CSV Export", type="primary"):
        # Create comprehensive CSV with multiple sheets worth of data
        all_data = []

        # Mortgage scenarios data
        for scenario in scenarios:
            result = analyzer.analyze_scenario(scenario)
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
                    'Monthly Payment': result['monthly_payment'],
                    'Property Tax': year_data.get('property_tax', 0),
                    'Interest Paid': year_data.get('yearly_interest', 0)
                })

        # Add rent data if available
        if include_rent_analysis and rent_results:
            for year_data in rent_results['yearly_data']:
                all_data.append({
                    'Type': 'Rent',
                    'Scenario': rent_scenario.name,
                    'Year': year_data['year'],
                    'Home Value': year_data['home_value_if_bought'],
                    'Loan Balance': 0,
                    'Home Equity': 0,
                    'Investment Value': year_data['investment_value'],
                    'Net Worth (Nominal)': year_data['net_worth'],
                    'Net Worth (Real)': year_data['net_worth_adjusted'],
                    'Monthly Payment': year_data['monthly_rent'],
                    'Property Tax': 0,
                    'Interest Paid': 0,
                    'Annual Rent': year_data['annual_rent_paid'],
                    'Cumulative Rent': year_data['cumulative_rent_paid']
                })

        csv_df = pd.DataFrame(all_data)

        # Convert to CSV string
        csv_buffer = io.StringIO()
        csv_df.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()

        st.download_button(
            label="📊 Download Enhanced CSV",
            data=csv_string,
            file_name='comprehensive_mortgage_analysis.csv',
            mime='text/csv'
        )

        st.success("✅ Enhanced CSV ready! Includes rent vs buy data if enabled.")

with col2:
    if st.button("📋 Summary Table Export", type="secondary"):
        # Create summary comparison table
        summary_data = []

        # Add mortgage scenarios
        for scenario in scenarios:
            result = analyzer.analyze_scenario(scenario)
            summary_data.append({
                'Scenario': scenario.name,
                'Type': 'Mortgage',
                'Down Payment': f"${scenario.down_payment:,.0f}",
                'Monthly Payment': f"${result['monthly_payment']:,.0f}",
                'Total Interest': f"${result['total_interest']:,.0f}",
                'Final Net Worth (Real)': f"${result['final_net_worth_adjusted']:,.0f}",
                'Final Net Worth (Nominal)': f"${result['final_net_worth']:,.0f}"
            })

        # Add rent scenario
        if include_rent_analysis and rent_results:
            summary_data.append({
                'Scenario': rent_scenario.name,
                'Type': 'Rent',
                'Down Payment': f"${rent_scenario.down_payment_invested:,.0f} (Invested)",
                'Monthly Payment': f"${monthly_rent + (renters_insurance/12):,.0f}",
                'Total Interest': f"${rent_results['total_rent_paid']:,.0f} (Total Rent)",
                'Final Net Worth (Real)': f"${rent_results['final_net_worth_adjusted']:,.0f}",
                'Final Net Worth (Nominal)': f"${rent_results['final_net_worth']:,.0f}"
            })

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

        st.success("✅ Summary table ready for download!")

with col3:
    if st.button("📄 Executive Report", type="secondary"):
        # Create comprehensive executive report
        report = f"""# Comprehensive Mortgage & Housing Analysis Report
Generated: {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}

## Executive Summary

### Property Details
- Home Price: ${home_price:,.0f}
- Analysis Period: 30 years
- Emergency Fund: ${emergency_fund:,.0f}

### Market Assumptions
- 30-Year Mortgage Rate: {rate_30yr*100:.1f}%
- 15-Year Mortgage Rate: {rate_15yr*100:.1f}%
- Expected Stock Market Return: {stock_return*100:.1f}%
- Expected Inflation Rate: {inflation_rate*100:.1f}%
- Expected Home Appreciation: {home_appreciation*100:.1f}%
- Property Tax Rate: {property_tax_rate*100:.1f}%
- Tax Bracket: {tax_rate*100:.0f}%

## Analysis Results

### Best Financial Strategy
**{stats['best_scenario']}**
- Final Net Worth (Real): ${stats['max_final_wealth']:,.0f}
- Performance advantage: ${stats['wealth_difference']:,.0f} ({stats['wealth_difference_pct']:.1f}%) over worst scenario

### All Scenarios Compared
{comparison_df.to_string(index=False)}
"""

        # Add rent vs buy analysis if enabled
        if include_rent_analysis and break_even_analysis:
            rent_section = f"""
## Rent vs Buy Analysis

### Rental Scenario
- Monthly Rent: ${monthly_rent:,.0f}
- Annual Rent Increase: {rent_increase*100:.1f}%
- Renters Insurance: ${renters_insurance:,.0f}/year
- Down Payment Invested: ${rent_scenario.down_payment_invested:,.0f}

### Break-Even Analysis
- Break-Even Point: {break_even_analysis['break_even_year']} years ({break_even_analysis['break_even_year'] if break_even_analysis['break_even_year'] else 'Never'})
- 30-Year Advantage (Buying): ${break_even_analysis['total_advantage']:,.0f}
- Final Net Worth (Renting): ${break_even_analysis['final_rent_net_worth']:,.0f}
- Final Net Worth (Buying): ${break_even_analysis['final_buy_net_worth']:,.0f}

### Recommendation
"""
            if break_even_analysis['break_even_year'] and break_even_analysis['break_even_year'] <= 10:
                rent_section += "🏠 **BUYING RECOMMENDED** - Short break-even period makes buying financially advantageous.\n"
            elif break_even_analysis['break_even_year'] and break_even_analysis['break_even_year'] <= 20:
                rent_section += "⚖️ **MODERATE ADVANTAGE TO BUYING** - Consider personal factors like mobility and maintenance preferences.\n"
            elif break_even_analysis['break_even_year']:
                rent_section += "🏢 **CONSIDER RENTING** - Long break-even period suggests renting may be better for shorter stays.\n"
            else:
                rent_section += "🏢 **RENTING RECOMMENDED** - Financial analysis favors renting and investing in this scenario.\n"

            report += rent_section

        report += f"""
## Key Financial Insights

1. **Total Wealth Impact**: The choice between scenarios can impact your net worth by ${stats['wealth_difference']:,.0f} over 30 years.

2. **Monthly Cash Flow**: Consider both the monthly payment burden and opportunity cost of down payments.

3. **Investment Opportunity**: Money not tied up in real estate can be invested in the stock market at {stock_return*100:.1f}% expected return.

4. **Inflation Protection**: Real values account for {inflation_rate*100:.1f}% annual inflation, showing true purchasing power.

5. **Tax Benefits**: Mortgage interest deduction provides tax savings based on your {tax_rate*100:.0f}% marginal rate.

## Important Disclaimers

This analysis is based on simplified assumptions and should not be considered financial advice. Consider factors not included in this model:

- Private Mortgage Insurance (PMI)
- Homeowners insurance
- HOA fees
- Maintenance and repair costs
- Closing costs and transaction fees
- Market volatility
- Personal lifestyle preferences
- Job mobility requirements

Consult with qualified financial advisors, tax professionals, and mortgage specialists for personalized advice.

---
Generated by Mortgage Analysis Tool
Live Version: https://know-your-mortgage-e7xnzpbgxc2oqqugtgjvye.streamlit.app/
"""

        st.download_button(
            label="📝 Download Executive Report",
            data=report,
            file_name='executive_mortgage_report.txt',
            mime='text/plain'
        )

        st.success("✅ Comprehensive executive report ready for download!")

# Footer with instructions
st.markdown("---")
st.markdown("""
### 📖 How to Use This Tool

1. **Adjust Parameters**: Use the sidebar to modify home price, down payments, interest rates, and investment assumptions
2. **Enable Rent Analysis**: Check "Include Rent Comparison" to compare buying vs renting
3. **Review Charts**: Examine the net worth projections and monthly payment comparisons
4. **Analyze Break-Even**: See when buying becomes better than renting financially
5. **Explore Detailed Tabs**: Check Investment Growth, Home Equity, Interest Analysis, and Rent Details
6. **Export Data**: Choose from Enhanced CSV, Summary Table, or Executive Report

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