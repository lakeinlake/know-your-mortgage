import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.shared_components import apply_custom_css
from src.utils.state_manager import initialize
from src.data.market_data import get_carmel_fishers_data, get_investment_insights
from src.data.census_api import get_demographic_data, format_demographic_data_for_charts, get_census_api_status

st.set_page_config(
    page_title="Market Comparison - Know Your Mortgage",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

apply_custom_css()
initialize()

st.markdown('<h1 class="main-header">🏘️ Carmel vs Fishers Market Analysis</h1>', unsafe_allow_html=True)
st.markdown("""
**An investment-focused analysis of the Carmel and Fishers real estate markets.** This page compares key housing trends
to help you make a data-driven decision. The data presented is based on historical trends and simplified projections.
""")

# Load data
data = get_carmel_fishers_data()
insights = get_investment_insights()

# Get real Census demographic data with fallback to sample data
census_demographic_data, data_source = get_demographic_data()
census_demographics_df, census_projections_df, _ = format_demographic_data_for_charts(census_demographic_data, data_source)

# Update data structure to use real Census data for demographics
if not census_demographics_df.empty:
    data['demographics'] = census_demographics_df
if not census_projections_df.empty:
    data['projections'] = pd.concat([data['projections'], census_projections_df], ignore_index=True).drop_duplicates(subset=['year'])

st.markdown('<h2 class="sub-header">📊 Market Analysis</h2>', unsafe_allow_html=True)

# Data source indicator
if data_source == "Census API":
    st.success(f"📊 **Data Source:** {data_source} (Real-time U.S. Census Bureau data)")
else:
    st.info(f"📊 **Data Source:** {data_source} (Realistic sample data based on market research)")

# Create tabs for different analysis views
tab1, tab2 = st.tabs(["📈 Housing Trends", "👥 Demographics"])

with tab1:
    st.markdown("### 📈 Median Housing Price Trends")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()

        # Combine historical and projection data for a complete view
        housing_df = data['housing']
        proj_df = data['projections']
        full_df = pd.concat([housing_df, proj_df], ignore_index=True)

        # Define the four trend lines to be displayed
        lines_to_show = [
            ("Carmel Single Family", "carmel_sf_median", "#2E86C1"),
            ("Carmel Townhouse", "carmel_th_median", "#85C1E9"),
            ("Fishers Single Family", "fishers_sf_median", "#28B463"),
            ("Fishers Townhouse", "fishers_th_median", "#82E0AA")
        ]

        # Add all trend lines to the figure
        for name, column, color in lines_to_show:
            if column in full_df.columns:
                fig.add_trace(go.Scatter(
                    x=full_df['year'],
                    y=full_df[column],
                    mode='lines+markers',
                    name=name,
                    line=dict(color=color, width=3),
                    marker=dict(size=6)
                ))

        # Add a vertical line to distinguish historical data from projections
        fig.add_vline(x=2024.5, line_dash="dash", line_color="gray",
                     annotation_text="Projections", annotation_position="top")

        fig.update_layout(
            title="Median Price: Carmel vs. Fishers (Single Family & Townhouse)",
            xaxis_title="Year",
            yaxis_title="Median Price ($)",
            hovermode='x unified',
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📊 Key Market Stats (2024)")

        # Display current market snapshot metrics
        current_data = data['housing'][data['housing']['year'] == 2024].iloc[0]

        st.metric("Carmel SF Median", f"${current_data['carmel_sf_median']:,.0f}",
                 delta=f"{((current_data['carmel_sf_median'] / 485000) ** (1/5) - 1) * 100:.1f}% Ann. (5yr)")

        st.metric("Fishers SF Median", f"${current_data['fishers_sf_median']:,.0f}",
                 delta=f"{((current_data['fishers_sf_median'] / 348000) ** (1/5) - 1) * 100:.1f}% Ann. (5yr)")

        st.metric("Carmel TH Median", f"${current_data['carmel_th_median']:,.0f}",
                 delta=f"{((current_data['carmel_th_median'] / 365000) ** (1/5) - 1) * 100:.1f}% Ann. (5yr)")

        st.metric("Fishers TH Median", f"${current_data['fishers_th_median']:,.0f}",
                 delta=f"{((current_data['fishers_th_median'] / 285000) ** (1/5) - 1) * 100:.1f}% Ann. (5yr)")

        st.info("💡 **Note:** The other metrics (Days on Market, Inventory, etc.) are currently under review and will be added back once data quality is ensured.")

with tab2:
    st.markdown("### 👥 Demographic Trends")

    # Combine historical and projection data for demographics
    demo_df = data['demographics']
    proj_df = data['projections']

    # Create columns for population and income charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Population Growth")

        fig_pop = go.Figure()

        # Add population trend lines
        fig_pop.add_trace(go.Scatter(
            x=demo_df['year'],
            y=demo_df['carmel_population'],
            mode='lines+markers',
            name='Carmel',
            line=dict(color='#2E86C1', width=3),
            marker=dict(size=6)
        ))

        fig_pop.add_trace(go.Scatter(
            x=demo_df['year'],
            y=demo_df['fishers_population'],
            mode='lines+markers',
            name='Fishers',
            line=dict(color='#28B463', width=3),
            marker=dict(size=6)
        ))

        # Add projections
        fig_pop.add_trace(go.Scatter(
            x=proj_df['year'],
            y=proj_df['carmel_population'],
            mode='lines+markers',
            name='Carmel (Proj)',
            line=dict(color='#2E86C1', width=2, dash='dash'),
            marker=dict(size=4)
        ))

        fig_pop.add_trace(go.Scatter(
            x=proj_df['year'],
            y=proj_df['fishers_population'],
            mode='lines+markers',
            name='Fishers (Proj)',
            line=dict(color='#28B463', width=2, dash='dash'),
            marker=dict(size=4)
        ))

        fig_pop.add_vline(x=2024.5, line_dash="dash", line_color="gray",
                         annotation_text="Projections", annotation_position="top")

        fig_pop.update_layout(
            title="Population Trends (Thousands)",
            xaxis_title="Year",
            yaxis_title="Population (000s)",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_pop, use_container_width=True)

    with col2:
        st.subheader("Median Household Income")

        fig_income = go.Figure()

        # Add income trend lines
        fig_income.add_trace(go.Scatter(
            x=demo_df['year'],
            y=demo_df['carmel_income'],
            mode='lines+markers',
            name='Carmel',
            line=dict(color='#2E86C1', width=3),
            marker=dict(size=6)
        ))

        fig_income.add_trace(go.Scatter(
            x=demo_df['year'],
            y=demo_df['fishers_income'],
            mode='lines+markers',
            name='Fishers',
            line=dict(color='#28B463', width=3),
            marker=dict(size=6)
        ))

        # Add projections
        fig_income.add_trace(go.Scatter(
            x=proj_df['year'],
            y=proj_df['carmel_income'],
            mode='lines+markers',
            name='Carmel (Proj)',
            line=dict(color='#2E86C1', width=2, dash='dash'),
            marker=dict(size=4)
        ))

        fig_income.add_trace(go.Scatter(
            x=proj_df['year'],
            y=proj_df['fishers_income'],
            mode='lines+markers',
            name='Fishers (Proj)',
            line=dict(color='#28B463', width=2, dash='dash'),
            marker=dict(size=4)
        ))

        fig_income.add_vline(x=2024.5, line_dash="dash", line_color="gray",
                            annotation_text="Projections", annotation_position="top")

        fig_income.update_layout(
            title="Income Growth Trends",
            xaxis_title="Year",
            yaxis_title="Median Income ($)",
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig_income, use_container_width=True)

    # Demographics insights
    st.markdown("### 📊 Demographic Insights")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("#### 📈 Population Growth (2019-2024)")
        carmel_pop_growth = ((100.8 / 97.8) ** (1/5) - 1) * 100
        fishers_pop_growth = ((104.0 / 95.3) ** (1/5) - 1) * 100

        st.metric("Carmel", f"+{carmel_pop_growth:.1f}% annually", "97.8k → 100.8k")
        st.metric("Fishers", f"+{fishers_pop_growth:.1f}% annually", "95.3k → 104.0k")

        if fishers_pop_growth > carmel_pop_growth:
            st.success("🟢 Fishers shows stronger population growth")
        else:
            st.info("🔵 Similar population growth patterns")

    with col4:
        st.markdown("#### 💰 Income Growth (2019-2024)")
        carmel_income_growth = ((129000 / 112000) ** (1/5) - 1) * 100
        fishers_income_growth = ((104000 / 89000) ** (1/5) - 1) * 100

        st.metric("Carmel", f"+{carmel_income_growth:.1f}% annually", "$112k → $129k")
        st.metric("Fishers", f"+{fishers_income_growth:.1f}% annually", "$89k → $104k")

        if fishers_income_growth > carmel_income_growth:
            st.success("🟢 Fishers shows stronger income growth")
        else:
            st.info("🔵 Carmel shows stronger income growth")

    with col5:
        st.markdown("#### 🏠 Affordability (2024)")
        carmel_affordability = 525000 / 129000
        fishers_affordability = 406000 / 104000

        st.metric("Carmel Ratio", f"{carmel_affordability:.1f}x", "Price/Income")
        st.metric("Fishers Ratio", f"{fishers_affordability:.1f}x", "Price/Income")

        if fishers_affordability < carmel_affordability:
            st.success("🟢 Fishers more affordable")
        else:
            st.warning("🟡 Carmel more affordable")

        st.caption("💡 Ratios under 4.0x are generally considered affordable")

    # Correlation summary
    st.markdown("---")
    st.markdown("#### 🔗 Demographic-Housing Correlation")

    st.markdown("""
    **Key Insights:**
    - **Fishers** shows stronger population growth (+1.8% vs +0.6% annually), indicating people are moving in
    - **Fishers** income growth (+3.2% vs +2.9% annually) is supporting housing demand
    - **Fishers** maintains better affordability (3.9x vs 4.1x income ratio)
    - Population growth is a leading indicator of housing demand and price appreciation

    **Investment Implication:** Fishers' demographic trends support the housing price growth recommendation.
    """)


st.markdown("---")
st.markdown('<h2 class="sub-header">📋 Market Summary</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏠 **Carmel Profile**")
    carmel_profile = insights['market_summary']['carmel']
    st.write(f"**Profile:** {carmel_profile['profile']}")
    st.write(f"**2024 Median:** ${carmel_profile['median_price_2024']:,}")
    st.write(f"**5-Year Growth:** {carmel_profile['appreciation_5yr']}")

    with st.expander("View Strengths & Challenges"):
        st.write("**Strengths:**")
        for strength in carmel_profile['strengths']:
            st.write(f"✅ {strength}")

        st.write("**Challenges:**")
        for challenge in carmel_profile['challenges']:
            st.write(f"⚠️ {challenge}")

with col2:
    st.markdown("### 🏡 **Fishers Profile**")
    fishers_profile = insights['market_summary']['fishers']
    st.write(f"**Profile:** {fishers_profile['profile']}")
    st.write(f"**2024 Median:** ${fishers_profile['median_price_2024']:,}")
    st.write(f"**5-Year Growth:** {fishers_profile['appreciation_5yr']}")

    with st.expander("View Strengths & Challenges"):
        st.write("**Strengths:**")
        for strength in fishers_profile['strengths']:
            st.write(f"✅ {strength}")

        st.write("**Challenges:**")
        for challenge in fishers_profile['challenges']:
            st.write(f"⚠️ {challenge}")

with col3:
    st.markdown("### 💡 **Investment Recommendation**")
    recommendation = insights['investment_recommendation']
    st.success(f"**Best Strategy:** {recommendation['best_strategy']}")
    st.info(f"**Target Range:** {recommendation['target_range']}")
    st.write("**Key Drivers:** Strong population growth, affordable entry point, family-focused market")

st.markdown("---")
st.markdown("💡 **Next Steps:** Use this analysis with our mortgage and rent vs buy tools to evaluate specific properties and financing strategies.")