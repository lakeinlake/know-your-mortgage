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

# Removed: get_state_tax_data() - now handled by session_manager.py

# Removed: initialize_session_state() - now handled by session_manager.py

# Removed: add_tax_selection_sidebar() - now handled by session_manager.py

# Removed: add_common_sidebar_parameters() - now handled by session_manager.py

def configure_page(page_title, page_icon="🏠"):
    """Configure page settings"""
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )