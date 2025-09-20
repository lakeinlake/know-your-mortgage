import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mortgage_analyzer import MortgageAnalyzer, MortgageScenario
from src.utils.shared_components import apply_custom_css, check_pmi_requirement, calculate_recommended_emergency_fund
from src.utils.state_manager import initialize, AppState
from src.utils.ui_components import create_tax_sidebar, create_financial_health_sidebar

st.set_page_config(
    page_title="Financial Health - Know Your Mortgage",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()

st.markdown('<h1 class="main-header">📊 Financial Health Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
Evaluate your financial readiness for homeownership. This comprehensive assessment analyzes your debt ratios,
cash reserves, income stability, and provides personalized recommendations for your home buying journey.
""")

st.sidebar.header("💰 Your Financial Profile")

# 1. Initialize state
initialize()

# 2. Render UI and get computed values directly
selected_state, tax_rate, property_tax_rate = create_tax_sidebar()
health_params = create_financial_health_sidebar()

with st.sidebar.expander("💡 Financial Health Guidelines"):
    st.markdown("""
    **🎯 Ideal Financial Profile:**
    - Debt-to-Income: ≤ 36% (max 43%)
    - Housing Ratio: ≤ 25% (max 28%)
    - Cash Reserves: ≥ 6 months expenses
    - Emergency Fund: 6-12 months for homeowners
    - Credit Score: 740+ for best rates

    **🚨 Red Flags:**
    - DTI > 43% or Housing > 28%
    - Emergency fund < 3 months
    - Unstable income or employment
    - Recent credit issues

    **✅ Green Lights:**
    - Stable employment (2+ years)
    - Low debt ratios
    - Strong emergency fund
    - Good credit history
    """)

# Extract values from health_params
annual_income = health_params['annual_income']
monthly_income = annual_income / 12
monthly_debts = health_params['monthly_debts']
cash_savings = health_params['cash_savings']
stock_investments = health_params['stock_investments']
target_home_price = health_params['target_home_price']
target_down_payment = health_params['target_down_payment']
mortgage_rate = health_params['mortgage_rate']
emergency_fund = health_params.get('emergency_fund', 50000)  # Fallback if not in health_params

total_net_worth = cash_savings + stock_investments

# Initialize analyzer and run analysis automatically
analyzer = MortgageAnalyzer(home_price=target_home_price, emergency_fund=emergency_fund)

current_payment = analyzer.calculate_monthly_payment(
    target_home_price - target_down_payment, mortgage_rate, 30
)

estimated_prop_tax = (target_home_price * property_tax_rate) / 12
estimated_insurance = 200
total_housing_cost = current_payment + estimated_prop_tax + estimated_insurance

housing_ratio = (total_housing_cost / monthly_income) * 100
total_debt_ratio = ((total_housing_cost + monthly_debts) / monthly_income) * 100

max_housing_payment = monthly_income * 0.28
max_total_debt = monthly_income * 0.43
available_for_housing = max_total_debt - monthly_debts

recommended_emergency = calculate_recommended_emergency_fund(current_payment, target_home_price)

conservative_max_payment = monthly_income * 0.25
aggressive_max_payment = monthly_income * 0.28

pmi_required, monthly_pmi, ltv = check_pmi_requirement(target_home_price, target_down_payment)

# Analysis results display
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

conservative_max_price = (conservative_max_payment * 12 * 30) + target_down_payment
aggressive_max_price = (aggressive_max_payment * 12 * 30) + target_down_payment

if total_debt_ratio > 43 or housing_ratio > 28:
    st.error("🚨 **Financial Risk Warning:** Your debt ratios exceed recommended limits. Consider a lower-priced home or paying down existing debt first.")
elif cash_savings < target_down_payment + emergency_fund:
    shortage = (target_down_payment + emergency_fund) - cash_savings
    st.warning(f"⚠️ **Cash Flow Concern:** You need ${shortage:,.0f} more cash for down payment + emergency fund. Consider a smaller down payment or building more savings.")
elif target_home_price > aggressive_max_price:
    st.warning(f"⚠️ **Budget Stretch:** This home price (${target_home_price:,.0f}) exceeds your recommended range. Consider homes under ${aggressive_max_price:,.0f}.")
else:
    st.success("✅ **Financial Health Looks Good:** Your debt ratios, cash reserves, and home price selection appear to be within reasonable ranges for your income level.")

tab1, tab2, tab3, tab4 = st.tabs(["💡 Affordability Analysis", "💰 Cash Flow", "🎯 Recommendations", "📊 Detailed Breakdown"])

with tab1:
    st.subheader("Affordability Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Monthly Payment Breakdown")

        payment_data = {
            'Component': ['Principal & Interest', 'Property Tax (est.)', 'Insurance (est.)', 'PMI' if pmi_required else None],
            'Amount': [current_payment, estimated_prop_tax, estimated_insurance, monthly_pmi if pmi_required else None]
        }

        payment_data = {k: [v for v in values if v is not None] for k, values in payment_data.items()}
        df_payments = pd.DataFrame(payment_data)

        fig_payment = px.bar(
            df_payments,
            x='Component',
            y='Amount',
            title='Monthly Payment Breakdown',
            color='Amount',
            color_continuous_scale='blues'
        )
        fig_payment.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_payment, width='stretch')

    with col2:
        st.markdown("#### 🎯 Affordability Limits")

        st.metric("Maximum Housing Payment", f"${max_housing_payment:,.0f}/month", help="28% of gross income")
        st.metric("Available for Housing", f"${available_for_housing:,.0f}/month", help="After existing debts")
        st.metric("Current Payment", f"${total_housing_cost:,.0f}/month", help="Total estimated housing cost")

        remaining_budget = available_for_housing - total_housing_cost
        if remaining_budget >= 0:
            st.success(f"✅ ${remaining_budget:,.0f}/month under budget")
        else:
            st.error(f"🚨 ${abs(remaining_budget):,.0f}/month over budget")

with tab2:
    st.subheader("Cash Flow Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💵 Cash Requirements")

        cash_needs = {
            'Down Payment': target_down_payment,
            'Emergency Fund': recommended_emergency,
            'Closing Costs (est.)': target_home_price * 0.03,
            'Moving & Setup': 5000
        }

        total_cash_needed = sum(cash_needs.values())

        for item, amount in cash_needs.items():
            st.write(f"**{item}:** ${amount:,.0f}")

        st.write(f"**Total Cash Needed:** ${total_cash_needed:,.0f}")
        st.write(f"**Available Cash:** ${cash_savings:,.0f}")

        if cash_savings >= total_cash_needed:
            surplus = cash_savings - total_cash_needed
            st.success(f"✅ ${surplus:,.0f} surplus after purchase")
        else:
            shortage = total_cash_needed - cash_savings
            st.error(f"🚨 ${shortage:,.0f} shortage")

    with col2:
        st.markdown("#### 📈 Net Worth Impact")

        current_nw_breakdown = {
            'Cash Savings': cash_savings,
            'Investments': stock_investments
        }

        after_purchase_nw = {
            'Home Equity': target_down_payment,
            'Remaining Cash': max(0, cash_savings - target_down_payment - recommended_emergency),
            'Investments': stock_investments,
            'Emergency Fund': recommended_emergency
        }

        fig_nw = go.Figure()

        fig_nw.add_trace(go.Bar(
            name='Before Purchase',
            x=list(current_nw_breakdown.keys()),
            y=list(current_nw_breakdown.values()),
            marker_color='lightblue'
        ))

        fig_nw.add_trace(go.Bar(
            name='After Purchase',
            x=list(after_purchase_nw.keys()),
            y=list(after_purchase_nw.values()),
            marker_color='darkblue'
        ))

        fig_nw.update_layout(
            title='Net Worth Before vs After Purchase',
            barmode='group',
            height=400
        )

        st.plotly_chart(fig_nw, width='stretch')

with tab3:
    st.subheader("Personalized Recommendations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Optimal Home Price Range")

        conservative_price = conservative_max_payment * 12 * 25 + target_down_payment
        aggressive_price = aggressive_max_payment * 12 * 30 + target_down_payment

        st.write(f"**Conservative Range:** ${conservative_price:,.0f}")
        st.write(f"**Aggressive Range:** ${aggressive_price:,.0f}")
        st.write(f"**Current Target:** ${target_home_price:,.0f}")

        if target_home_price <= conservative_price:
            st.success("✅ Well within conservative budget")
        elif target_home_price <= aggressive_price:
            st.warning("⚠️ Stretching budget - ensure job security")
        else:
            st.error("🚨 Exceeds recommended budget")

    with col2:
        st.markdown("#### 💡 Action Items")

        if total_debt_ratio > 43:
            st.error("🚨 **Priority 1:** Reduce existing debt before buying")

        if cash_savings < target_down_payment + recommended_emergency:
            shortage = (target_down_payment + recommended_emergency) - cash_savings
            st.warning(f"⚠️ **Build Cash:** Save an additional ${shortage:,.0f}")

        if housing_ratio > 28:
            max_affordable = (monthly_income * 0.28 - estimated_prop_tax - estimated_insurance) * 12 * 30 + target_down_payment
            st.warning(f"💰 **Lower Price:** Consider homes under ${max_affordable:,.0f}")

        if emergency_fund < recommended_emergency:
            needed = recommended_emergency - emergency_fund
            st.info(f"💰 **Emergency Fund:** Build to ${recommended_emergency:,.0f} (need ${needed:,.0f} more)")

        if monthly_pmi > 0:
            additional_down = target_home_price * 0.2 - target_down_payment
            st.info(f"💡 **Avoid PMI:** Add ${additional_down:,.0f} to down payment")

with tab4:
    st.subheader("Detailed Financial Breakdown")

    financial_summary = {
        'Income & Debt': {
            'Annual Gross Income': f"${annual_income:,.0f}",
            'Monthly Gross Income': f"${monthly_income:,.0f}",
            'Monthly Debt Payments': f"${monthly_debts:,.0f}",
            'Debt-to-Income Ratio': f"{(monthly_debts/monthly_income)*100:.1f}%"
        },
        'Net Worth': {
            'Cash Savings': f"${cash_savings:,.0f}",
            'Investment Portfolio': f"${stock_investments:,.0f}",
            'Total Net Worth': f"${total_net_worth:,.0f}",
            'Net Worth to Income': f"{net_worth_ratio:.1f}x"
        },
        'Housing Costs': {
            'Target Home Price': f"${target_home_price:,.0f}",
            'Down Payment': f"${target_down_payment:,.0f} ({(target_down_payment/target_home_price)*100:.1f}%)",
            'Monthly Payment (P&I)': f"${current_payment:,.0f}",
            'Total Monthly Housing': f"${total_housing_cost:,.0f}",
            'Housing Ratio': f"{housing_ratio:.1f}%"
        },
        'Risk Assessment': {
            'Total DTI Ratio': f"{total_debt_ratio:.1f}% ({'✅ Good' if total_debt_ratio <= 36 else '⚠️ High' if total_debt_ratio <= 43 else '🚨 Too High'})",
            'Cash Reserves Ratio': f"{cash_ratio:.1f}x income ({'✅ Strong' if cash_ratio >= 0.5 else '⚠️ Moderate' if cash_ratio >= 0.25 else '🚨 Low'})",
            'Emergency Fund Status': f"${emergency_fund:,.0f} ({'✅ Adequate' if emergency_fund >= recommended_emergency else '⚠️ Low'})",
            'PMI Requirement': f"{'Yes' if pmi_required else 'No'} ({f'${monthly_pmi:.0f}/month' if pmi_required else 'N/A'})"
        }
    }

    for category, metrics in financial_summary.items():
        st.markdown(f"#### {category}")
        for metric, value in metrics.items():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**{metric}:**")
            with col2:
                st.write(value)
        st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 What This Analysis Provides")
    st.markdown("""
    **🎯 Comprehensive Assessment:**
    - Debt-to-income ratio analysis
    - Housing affordability calculations
    - Cash flow and liquidity review
    - Net worth impact projections

    **💡 Personalized Insights:**
    - Optimal home price range
    - Emergency fund recommendations
    - PMI avoidance strategies
    - Timeline for financial readiness
    """)

with col2:
    st.markdown("### 🎯 Key Benchmarks")
    st.markdown("""
    **📊 Ideal Financial Ratios:**
    - **Debt-to-Income:** ≤ 36% (max 43%)
    - **Housing Ratio:** ≤ 25% (max 28%)
    - **Cash Reserves:** ≥ 6 months expenses
    - **Emergency Fund:** 6-12 months for homeowners

    **🚨 Warning Signs:**
    - DTI > 43% or Housing > 28%
    - Emergency fund < 3 months
    - Cash shortage for down payment
    - Unstable income or employment
    """)

st.markdown("---")
st.markdown("💡 **Ready to Buy?** If your financial health looks good, explore mortgage scenarios and rent vs buy analysis to optimize your strategy.")