import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.shared_components import apply_custom_css, show_golden_rules, show_glossary
from src.utils.state_manager import AppState

st.set_page_config(
    page_title="Education - Know Your Mortgage",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Initialize session state for consistency
AppState.initialize()

st.markdown('<h1 class="main-header">📚 First-Time Home Buyer Education</h1>', unsafe_allow_html=True)

st.markdown("""
Welcome to your comprehensive home buying education center! Whether you're a first-time buyer or
need a refresher, this page covers everything you need to know about mortgages and home buying.
""")

tab1, tab2 = st.tabs(["🎓 Golden Rules", "📖 Financial Glossary"])

with tab1:
    st.markdown("### Essential Guidelines for Home Buyers")
    show_golden_rules()

    st.markdown("### 🧮 Quick Calculators")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("PMI Calculator")
        home_price_pmi = st.number_input("Home Price", min_value=50000, max_value=2000000, value=400000, step=10000, key="pmi_home")
        down_payment_pmi = st.number_input("Down Payment", min_value=1000, max_value=int(home_price_pmi*0.5), value=40000, step=1000, key="pmi_down")

        ltv = (home_price_pmi - down_payment_pmi) / home_price_pmi
        down_percent = (down_payment_pmi / home_price_pmi) * 100

        if ltv > 0.8:
            pmi_annual = (home_price_pmi - down_payment_pmi) * 0.005
            pmi_monthly = pmi_annual / 12
            st.error(f"⚠️ PMI Required: ${pmi_monthly:.0f}/month")
            st.write(f"Down Payment: {down_percent:.1f}% (need 20% to avoid PMI)")
        else:
            st.success("✅ No PMI needed!")
            st.write(f"Down Payment: {down_percent:.1f}%")

    with col2:
        st.subheader("Emergency Fund Calculator")
        monthly_income = st.number_input("Monthly Gross Income", min_value=1000, max_value=50000, value=8000, step=500, key="emergency_income")
        monthly_expenses = st.number_input("Monthly Expenses", min_value=500, max_value=30000, value=4000, step=250, key="emergency_expenses")

        emergency_3_months = monthly_expenses * 3
        emergency_6_months = monthly_expenses * 6
        emergency_homeowner = monthly_expenses * 8  # Higher for homeowners

        st.write(f"**Minimum Emergency Fund:** ${emergency_3_months:,.0f} (3 months)")
        st.write(f"**Recommended:** ${emergency_6_months:,.0f} (6 months)")
        st.write(f"**Homeowner Target:** ${emergency_homeowner:,.0f} (8 months)")

with tab2:
    st.markdown("### Complete Financial Terms Reference")
    show_glossary()

    st.markdown("### 💡 Pro Tips")

    col1, col2 = st.columns(2)

    with col1:
        st.info("""
        **🏦 Shopping for Lenders:**
        - Get quotes from at least 3 lenders
        - Compare APR, not just interest rate
        - Check for origination fees and points
        - Consider local credit unions
        - Lock your rate when you find a good deal
        """)

        st.warning("""
        **🚨 Red Flags to Avoid:**
        - Lenders who pressure you to borrow more
        - Rates that seem too good to be true
        - No documentation ("NINJA") loans
        - Prepayment penalties
        - Balloon payments
        """)

    with col2:
        st.success("""
        **✅ Signs of a Good Deal:**
        - APR within 0.25% of national average
        - No origination fees or reasonable ones
        - Responsive, helpful loan officer
        - Clear explanation of all costs
        - Good online reviews and BBB rating
        """)

        st.info("""
        **📋 Documents You'll Need:**
        - 2 years of tax returns
        - 2 months of bank statements
        - Pay stubs (last 30 days)
        - Employment verification letter
        - List of assets and debts
        - Driver's license and Social Security card
        """)

st.markdown("---")
st.markdown("**💡 Ready to analyze your specific situation?** Visit the other pages to:")
st.markdown("- 🏠 **Mortgage Analysis:** Compare different loan scenarios")
st.markdown("- 🏢 **Rent vs Buy:** Determine if buying makes financial sense")
st.markdown("- 📊 **Financial Health:** Check your readiness to buy")
st.markdown("- 💾 **Export Reports:** Generate professional reports for planning")