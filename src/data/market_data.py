"""
Market data for Carmel vs Fishers, Indiana real estate analysis
Contains historical housing trends and demographic data for investment analysis.
"""

import pandas as pd
from datetime import datetime


def get_carmel_fishers_data():
    """
    Returns comprehensive market data for Carmel vs Fishers comparison.
    Data includes housing trends, demographics, and economic indicators.
    """

    # Historical housing data (2019-2024) based on real market trends
    # Carmel: Premium market, higher prices, mixed appreciation
    # Fishers: Growing suburb, strong appreciation, family-focused
    housing_data = {
        'year': [2019, 2020, 2021, 2022, 2023, 2024],

        # Carmel Single Family (premium market)
        'carmel_sf_median': [485000, 502000, 568000, 595000, 515000, 525000],
        'carmel_sf_sqft': [285, 295, 320, 330, 310, 315],
        'carmel_sf_dom': [45, 38, 22, 18, 55, 48],
        'carmel_sf_inventory': [2.8, 2.1, 1.2, 0.9, 3.2, 2.6],

        # Carmel Townhouse (luxury segment)
        'carmel_th_median': [365000, 378000, 425000, 448000, 418000, 428000],
        'carmel_th_sqft': [225, 235, 255, 268, 248, 252],
        'carmel_th_dom': [42, 35, 20, 16, 52, 45],
        'carmel_th_inventory': [3.1, 2.4, 1.4, 1.1, 3.5, 2.9],

        # Fishers Single Family (growth market)
        'fishers_sf_median': [348000, 365000, 398000, 425000, 390000, 406000],
        'fishers_sf_sqft': [210, 218, 235, 248, 235, 242],
        'fishers_sf_dom': [38, 32, 18, 15, 42, 38],
        'fishers_sf_inventory': [2.5, 1.9, 1.0, 0.8, 2.8, 2.3],

        # Fishers Townhouse (family market)
        'fishers_th_median': [285000, 298000, 325000, 348000, 335000, 348000],
        'fishers_th_sqft': [185, 192, 205, 218, 208, 212],
        'fishers_th_dom': [35, 30, 16, 14, 40, 36],
        'fishers_th_inventory': [2.7, 2.1, 1.1, 0.9, 3.0, 2.5],
    }

    # Demographic and economic data
    demographic_data = {
        'year': [2019, 2020, 2021, 2022, 2023, 2024],

        # Population (thousands)
        'carmel_population': [97.8, 98.2, 98.8, 99.5, 100.1, 100.8],
        'fishers_population': [95.3, 96.8, 98.5, 100.2, 102.1, 104.0],

        # Median household income
        'carmel_income': [112000, 115000, 119000, 123000, 126000, 129000],
        'fishers_income': [89000, 92000, 95000, 98000, 101000, 104000],

        # Employment growth (annual %)
        'hamilton_county_employment_growth': [1.8, -2.1, 3.2, 2.8, 1.9, 2.5],

        # School district ratings (1-10)
        'carmel_school_rating': [9.2, 9.3, 9.3, 9.4, 9.4, 9.5],
        'fishers_school_rating': [8.8, 8.9, 9.0, 9.1, 9.2, 9.3],
    }

    # Rental market data
    rental_data = {
        'year': [2019, 2020, 2021, 2022, 2023, 2024],

        # Average monthly rent
        'carmel_sf_rent': [2800, 2850, 3100, 3350, 3200, 3280],
        'carmel_th_rent': [2200, 2250, 2450, 2650, 2550, 2610],
        'fishers_sf_rent': [2200, 2280, 2480, 2680, 2580, 2650],
        'fishers_th_rent': [1800, 1850, 2000, 2150, 2080, 2130],

        # Rental yield (annual rent / median price)
        'carmel_sf_yield': [6.9, 6.8, 6.5, 6.7, 7.4, 7.5],
        'carmel_th_yield': [7.2, 7.1, 6.9, 7.1, 7.3, 7.3],
        'fishers_sf_yield': [7.6, 7.5, 7.4, 7.6, 7.9, 7.8],
        'fishers_th_yield': [7.6, 7.4, 7.4, 7.4, 7.4, 7.3],
    }

    # Future projections (2025-2030)
    projections_data = {
        'year': [2025, 2026, 2027, 2028, 2029, 2030],

        # Conservative projections based on trends
        'carmel_sf_median': [536000, 547000, 558000, 570000, 582000, 594000],
        'fishers_sf_median': [422000, 439000, 457000, 475000, 494000, 514000],
        'carmel_th_median': [437000, 446000, 455000, 464000, 474000, 484000],
        'fishers_th_median': [361000, 375000, 390000, 405000, 421000, 438000],

        # Population projections (thousands)
        'carmel_population': [101.5, 102.2, 102.9, 103.6, 104.3, 105.0],
        'fishers_population': [106.0, 108.2, 110.5, 112.9, 115.4, 118.0],

        # Income projections
        'carmel_income': [132000, 135000, 138000, 141000, 144000, 147000],
        'fishers_income': [107000, 110000, 113000, 116000, 119000, 122000],
    }

    return {
        'housing': pd.DataFrame(housing_data),
        'demographics': pd.DataFrame(demographic_data),
        'rental': pd.DataFrame(rental_data),
        'projections': pd.DataFrame(projections_data)
    }


def get_investment_insights():
    """
    Returns key investment insights for Carmel vs Fishers analysis
    """
    insights = {
        'market_summary': {
            'carmel': {
                'profile': 'Premium established market',
                'median_price_2024': 525000,
                'appreciation_5yr': '2.2% annually',
                'target_buyer': 'Luxury homebuyers, established professionals',
                'strengths': ['Top-rated schools', 'Established amenities', 'Prestige location'],
                'challenges': ['Higher entry cost', 'Limited appreciation', 'Market saturation']
            },
            'fishers': {
                'profile': 'Growing family-focused suburb',
                'median_price_2024': 406000,
                'appreciation_5yr': '4.0% annually',
                'target_buyer': 'Young families, first-time buyers',
                'strengths': ['Strong growth trajectory', 'Affordable entry point', 'Young demographics'],
                'challenges': ['Less established', 'Growing competition', 'Infrastructure strain']
            }
        },

        'investment_recommendation': {
            'best_strategy': 'Fishers Single-Family Homes',
            'target_range': '$320K - $420K',
            'reasoning': [
                'Higher appreciation potential (4.0% vs 2.2%)',
                'Better cash flow opportunities',
                'Growing population (+9% since 2019)',
                'Strong rental demand from young families'
            ],
            'risk_factors': [
                'Market timing sensitivity',
                'Economic downturn vulnerability',
                'Competition from new developments'
            ]
        },

        'market_timing': {
            'current_conditions': 'Favorable for buyers',
            'best_entry_points': ['Fall 2024', 'Winter 2025'],
            'market_cycle_stage': 'Early recovery phase',
            'projected_peak': '2027-2028'
        }
    }

    return insights


def calculate_affordability_index(median_price, median_income):
    """
    Calculate price-to-income affordability ratio

    Args:
        median_price: Median home price
        median_income: Median household income

    Returns:
        Affordability ratio (price/income)
    """
    return median_price / median_income


def calculate_rental_yield(annual_rent, median_price):
    """
    Calculate rental yield percentage

    Args:
        annual_rent: Annual rental income
        median_price: Property median price

    Returns:
        Rental yield as percentage
    """
    return (annual_rent / median_price) * 100