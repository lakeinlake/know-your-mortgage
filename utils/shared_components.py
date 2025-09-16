import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling for the application"""
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
    monthly_housing_cost = monthly_payment * 1.4
    return monthly_housing_cost * 6

def check_pmi_requirement(home_price, down_payment):
    """Check if PMI is required and calculate cost"""
    loan_to_value = (home_price - down_payment) / home_price

    if loan_to_value > 0.8:
        pmi_rate = 0.005
        annual_pmi = (home_price - down_payment) * pmi_rate
        monthly_pmi = annual_pmi / 12
        return True, monthly_pmi, loan_to_value

    return False, 0, loan_to_value

def show_glossary():
    """Display comprehensive financial glossary"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🏠 PMI (Private Mortgage Insurance)**
        - Required when down payment < 20%
        - Protects lender if you default
        - Typically 0.3% - 1.5% of loan amount annually
        - Can be removed once you have 20% equity

        **📊 LTV (Loan-to-Value Ratio)**
        - Loan amount ÷ home value
        - Lower LTV = better loan terms
        - 80% LTV = 20% down payment
        - Used to determine PMI requirement

        **🏘️ HOA (Homeowners Association)**
        - Monthly/annual fees for community amenities
        - Can range from $50-500+ per month
        - Covers maintenance, amenities, insurance
        - Factor into total monthly housing cost

        **🏛️ FHA Loan**
        - Federal Housing Administration loan
        - Lower down payment (3.5% minimum)
        - More flexible credit requirements
        - Requires mortgage insurance premium
        """)

    with col2:
        st.markdown("""
        **💳 DTI (Debt-to-Income Ratio)**
        - Total monthly debts ÷ gross monthly income
        - Front-end DTI: Housing costs only (≤28%)
        - Back-end DTI: All debts (≤43%)
        - Lower DTI = better loan approval odds

        **📈 APR (Annual Percentage Rate)**
        - True cost of borrowing including fees
        - Higher than interest rate due to fees
        - Use for comparing loan offers
        - Includes points, origination fees, etc.

        **🔢 Principal & Interest**
        - Principal: Amount borrowed
        - Interest: Cost of borrowing money
        - Early payments go mostly to interest
        - Later payments go mostly to principal

        **🏦 Escrow Account**
        - Lender holds money for taxes/insurance
        - Paid as part of monthly mortgage
        - Ensures bills are paid on time
        - Can increase your monthly payment
        """)

def get_state_tax_data():
    """Get comprehensive state tax and property tax data"""
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

    federal_brackets = {
        "10% ($0 - $11,000)": 10,
        "12% ($11,001 - $44,725)": 12,
        "22% ($44,726 - $95,375)": 22,
        "24% ($95,376 - $182,050)": 24,
        "32% ($182,051 - $231,250)": 32,
        "35% ($231,251 - $578,125)": 35,
        "37% ($578,126+)": 37
    }

    return state_tax_rates, property_tax_averages, federal_brackets

def add_tax_selection_sidebar():
    """Add comprehensive state and federal tax selection to sidebar"""
    st.sidebar.subheader("🏛️ Tax Information")

    state_tax_rates, property_tax_averages, federal_brackets = get_state_tax_data()

    # State selection
    selected_state = st.sidebar.selectbox(
        "Select Your State",
        options=list(state_tax_rates.keys()),
        index=list(state_tax_rates.keys()).index("California"),
        help="Used to estimate combined federal + state tax rate"
    )

    state_rate = state_tax_rates[selected_state]

    # Federal tax bracket selection
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

        **Varies by Location:**
        - State averages range from 0.28% to 2.49%
        - Local rates can vary significantly within states
        - Consider this when choosing where to buy
        - Higher taxes often mean better schools/services
        """)

    return selected_state, tax_rate, property_tax_rate

def configure_page(page_title, page_icon="🏠"):
    """Configure page settings"""
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )