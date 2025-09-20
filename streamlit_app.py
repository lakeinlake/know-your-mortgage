import streamlit as st
from src.utils.shared_components import apply_custom_css
from src.utils.state_manager import AppState

st.set_page_config(
    page_title="Know Your Mortgage - Home",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

# Initialize session state for consistency across app
AppState.initialize()

st.markdown('<h1 class="main-header">🏠 Know Your Mortgage</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #666; margin-bottom: 2rem;">Your Complete Financial Education Platform for Smart Home Buying</h3>', unsafe_allow_html=True)

st.markdown("""
Welcome to the **most comprehensive mortgage and home buying analysis platform** available. Whether you're a first-time buyer
or looking to optimize your next purchase, our tools provide professional-grade financial analysis to help you make informed decisions.
""")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🎯 What Makes This Platform Unique")

    st.markdown("""
    **🎓 Education First Approach:**
    - Complete glossary of mortgage terms (PMI, LTV, DTI, APR)
    - Golden rules for first-time home buyers
    - Real-time affordability warnings and guidance
    - Professional-level financial education

    **📊 Comprehensive Analysis:**
    - Multi-scenario mortgage comparison (15-year vs 30-year)
    - Rent vs Buy break-even analysis
    - Investment opportunity cost modeling
    - State-specific tax integration (all 50 states)

    **💰 Financial Health Assessment:**
    - 4-metric professional dashboard
    - Real-time debt-to-income calculations
    - Emergency fund recommendations
    - Personalized home price guidance

    **📈 Advanced Features:**
    - Inflation-adjusted (real vs nominal) analysis
    - PMI calculations and warnings
    - Professional export capabilities
    - Executive-level reporting
    """)

with col2:
    st.markdown("### 🚀 Quick Start Guide")

    st.info("""
    **New to Home Buying?**

    1. **📚 Start with Education**
       Learn essential terms and golden rules

    2. **📊 Check Financial Health**
       Assess your readiness to buy

    3. **🏠 Analyze Mortgages**
       Compare different loan scenarios

    4. **🏢 Rent vs Buy**
       Determine if buying makes sense

    5. **💾 Export Reports**
       Generate professional documentation
    """)

    st.success("""
    **Ready to Jump In?**

    Use the sidebar navigation to explore:
    - 📚 Education center
    - 🏠 Mortgage analysis
    - 🏢 Rent vs buy comparison
    - 🏘️ Market comparison (Carmel vs Fishers)
    - 📊 Financial health check
    - 💾 Professional reports
    """)

st.markdown("---")

st.markdown("### 📱 Platform Features")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎓 Education", "🏠 Mortgage Analysis", "🏢 Rent vs Buy", "🏘️ Market Analysis", "📊 Financial Health"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 📚 Complete Learning Center

        **Golden Rules for Home Buyers:**
        - Down payment strategies (3% to 20%+)
        - Emergency fund requirements for homeowners
        - Debt-to-income ratio guidelines
        - Smart home buying timeline

        **Comprehensive Glossary:**
        - PMI (Private Mortgage Insurance)
        - LTV (Loan-to-Value Ratio)
        - DTI (Debt-to-Income Ratio)
        - APR vs Interest Rate
        - FHA, Conventional, VA loans
        """)

    with col2:
        st.markdown("""
        #### 💡 Interactive Learning Tools

        **Quick Calculators:**
        - PMI requirement checker
        - Emergency fund calculator
        - Affordability estimator
        - Break-even analysis preview

        **Pro Tips & Warnings:**
        - Red flags to avoid
        - Signs of good deals
        - Document preparation checklist
        - Lender shopping strategies
        """)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🏠 Advanced Mortgage Comparison

        **Compare Multiple Scenarios:**
        - 30-year vs 15-year mortgages
        - Different down payment strategies
        - Cash purchase analysis
        - Investment opportunity costs

        **Real-Time Calculations:**
        - PMI requirements and costs
        - Monthly payment breakdowns
        - Total interest over loan term
        - Net worth projections
        """)

    with col2:
        st.markdown("""
        #### 📈 Professional Visualizations

        **Interactive Charts:**
        - Net worth progression over 30 years
        - Home equity building timeline
        - Investment growth comparisons
        - Monthly payment analysis

        **Detailed Breakdowns:**
        - Year-by-year financial data
        - Interest vs principal progression
        - Tax benefit calculations
        - Inflation-adjusted values
        """)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🏢 Comprehensive Rent vs Buy Analysis

        **Break-Even Analysis:**
        - Exact year when buying becomes better
        - Total cost comparison over time
        - Investment opportunity with down payment
        - Rent escalation modeling

        **Key Factors Considered:**
        - Annual rent increases
        - Home appreciation rates
        - Stock market investment returns
        - Tax benefits of homeownership
        """)

    with col2:
        st.markdown("""
        #### 💰 Financial Impact Modeling

        **Long-Term Projections:**
        - 30-year net worth comparison
        - Cash flow analysis
        - Investment portfolio growth
        - Total housing costs

        **Decision Support:**
        - Break-even timeline analysis
        - Risk vs benefit assessment
        - Lifestyle factor considerations
        - Professional recommendations
        """)

with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 🏘️ Real Estate Market Analysis

        **Carmel vs Fishers Comparison:**
        - Historical housing price trends (2019-2024)
        - Future market projections (2025-2030)
        - Single-family vs townhouse analysis
        - Investment performance metrics

        **Demographic Integration:**
        - Population growth impact on prices
        - Median income vs affordability ratios
        - School district rating correlations
        - Employment growth indicators
        """)

    with col2:
        st.markdown("""
        #### 📈 Investment Intelligence

        **Market Timing Analysis:**
        - Optimal buying windows
        - Market cycle positioning
        - Risk vs opportunity assessment
        - Long-term appreciation forecasts

        **Data-Driven Insights:**
        - Rental yield comparisons
        - Price-to-income affordability metrics
        - Economic driver analysis
        - Professional investment recommendations
        """)

with tab5:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        #### 📊 Professional Financial Assessment

        **4-Metric Dashboard:**
        - Debt-to-Income Ratio (≤36% ideal)
        - Housing Ratio (≤28% recommended)
        - Cash Reserves (6+ months ideal)
        - Net Worth Multiple (3x+ excellent)

        **Real-Time Guidance:**
        - Color-coded warnings (🟢🟡🔴)
        - Personalized recommendations
        - Action item prioritization
        - Budget optimization tips
        """)

    with col2:
        st.markdown("""
        #### 🎯 Personalized Recommendations

        **Smart Home Price Ranges:**
        - Conservative budget calculations
        - Aggressive maximum prices
        - Risk assessment warnings
        - Emergency fund adequacy

        **Action Plans:**
        - Debt reduction strategies
        - Savings acceleration plans
        - Timeline for home readiness
        - PMI avoidance strategies
        """)

st.markdown("---")

st.markdown("### 🌟 Why Choose This Platform?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 🎓 **Education-Focused**

    Unlike simple calculators, we prioritize **financial education**.
    Every feature includes explanations, warnings, and professional
    guidance to help you understand the "why" behind the numbers.

    - Comprehensive glossary
    - Real-time educational tips
    - Professional-grade analysis
    - Risk prevention warnings
    """)

with col2:
    st.markdown("""
    #### 📊 **Comprehensive Analysis**

    Our platform goes beyond basic calculations to provide
    **investment-grade financial modeling** with inflation
    adjustments and opportunity cost analysis.

    - Multi-scenario comparisons
    - 30-year projections
    - Inflation-adjusted values
    - Investment alternatives
    """)

with col3:
    st.markdown("""
    #### 💼 **Professional Quality**

    Generate **financial advisor-quality reports** and
    analysis suitable for serious financial planning
    and decision making.

    - Executive reports
    - Professional visualizations
    - Detailed data exports
    - Advisor-ready documentation
    """)

st.markdown("---")

st.markdown("### 🚀 Recent Updates (v2.0.0)")

col1, col2 = st.columns(2)

with col1:
    st.success("""
    **🆕 Major Platform Enhancements:**

    - **Multi-page architecture** for better organization
    - **State-specific tax integration** (all 50 states)
    - **Enhanced financial health dashboard**
    - **Professional export capabilities**
    - **Comprehensive educational content**
    - **Real-time affordability warnings**
    """)

with col2:
    st.info("""
    **📈 Advanced Analysis Features:**

    - **Break-even analysis** for rent vs buy decisions
    - **PMI calculations** with real-time warnings
    - **Emergency fund recommendations**
    - **Investment opportunity modeling**
    - **Inflation-adjusted projections**
    - **Executive-level reporting**
    """)

st.markdown("---")

st.markdown("### 📞 Support & Resources")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    #### 📚 **Learning Resources**
    - [First-Time Buyer Guide](📚_Education)
    - [Financial Glossary](📚_Education)
    - Golden Rules & Best Practices
    - Pro Tips & Warnings
    """)

with col2:
    st.markdown("""
    #### 🔧 **Analysis Tools**
    - [Mortgage Comparison](🏠_Mortgage_Analysis)
    - [Rent vs Buy Analysis](🏢_Rent_vs_Buy)
    - [Market Comparison](🏘️_Market_Comparison)
    - [Financial Health Check](📊_Financial_Health)
    - [Professional Reports](💾_Export_Reports)
    """)

with col3:
    st.markdown("""
    #### 💡 **Getting Started**
    - Use sidebar navigation to explore
    - Start with Education if new to buying
    - Check Financial Health first
    - Export reports for planning
    """)

st.markdown("---")

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
🏠 <strong>Know Your Mortgage v2.0.0</strong> | Educational Platform | Built with ❤️ for Smart Home Buyers<br>
<em>Empowering informed decisions through comprehensive financial education and analysis</em>
</div>
""", unsafe_allow_html=True)