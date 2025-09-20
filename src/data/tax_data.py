"""
Static tax and financial data for Know Your Mortgage application.
Contains state tax rates, property tax averages, and federal tax brackets.
"""

from functools import lru_cache


@lru_cache(maxsize=1)
def get_static_data():
    """Cached static data - loaded once per session"""
    state_tax_rates = {
        "Alabama": 5.0, "Alaska": 0.0, "Arizona": 4.5, "Arkansas": 5.9, "California": 13.3,
        "Colorado": 4.4, "Connecticut": 6.9, "Delaware": 6.6, "Florida": 0.0, "Georgia": 5.75,
        "Hawaii": 11.0, "Idaho": 6.0, "Illinois": 4.95, "Indiana": 3.23, "Iowa": 8.53,
        "Kansas": 5.7, "Kentucky": 5.0, "Louisiana": 6.0, "Maine": 7.15, "Maryland": 5.75,
        "Massachusetts": 5.0, "Michigan": 4.25, "Minnesota": 9.85, "Mississippi": 5.0,
        "Missouri": 5.4, "Montana": 6.9, "Nebraska": 6.84, "Nevada": 0.0, "New Hampshire": 5.0,
        "New Jersey": 10.75, "New Mexico": 5.9, "New York": 10.9, "North Carolina": 4.99,
        "North Dakota": 2.9, "Ohio": 3.99, "Oklahoma": 5.0, "Oregon": 9.9, "Pennsylvania": 3.07,
        "Rhode Island": 5.99, "South Carolina": 7.0, "South Dakota": 0.0, "Tennessee": 0.0,
        "Texas": 0.0, "Utah": 4.85, "Vermont": 8.75, "Virginia": 5.75, "Washington": 0.0,
        "West Virginia": 6.5, "Wisconsin": 7.65, "Wyoming": 0.0, "Washington DC": 9.75
    }

    property_tax_averages = {
        "Alabama": 0.41, "Alaska": 1.19, "Arizona": 0.66, "Arkansas": 0.63, "California": 0.75,
        "Colorado": 0.51, "Connecticut": 2.14, "Delaware": 0.57, "Florida": 0.83, "Georgia": 0.89,
        "Hawaii": 0.28, "Idaho": 0.69, "Illinois": 2.27, "Indiana": 0.87, "Iowa": 1.53,
        "Kansas": 1.41, "Kentucky": 0.86, "Louisiana": 0.55, "Maine": 1.28, "Maryland": 1.04,
        "Massachusetts": 1.04, "Michigan": 1.34, "Minnesota": 1.12, "Mississippi": 0.81,
        "Missouri": 0.97, "Montana": 0.83, "Nebraska": 1.73, "Nevada": 0.53, "New Hampshire": 2.18,
        "New Jersey": 2.49, "New Mexico": 0.80, "New York": 1.40, "North Carolina": 0.84,
        "North Dakota": 0.98, "Ohio": 1.53, "Oklahoma": 0.90, "Oregon": 0.87, "Pennsylvania": 1.43,
        "Rhode Island": 1.53, "South Carolina": 0.57, "South Dakota": 1.17, "Tennessee": 0.66,
        "Texas": 1.80, "Utah": 0.60, "Vermont": 1.86, "Virginia": 0.82, "Washington": 0.87,
        "West Virginia": 0.59, "Wisconsin": 1.85, "Wyoming": 0.62, "Washington DC": 0.56
    }

    federal_brackets = {
        "10% ($0 - $11,000)": 10, "12% ($11,001 - $44,725)": 12, "22% ($44,726 - $95,375)": 22,
        "24% ($95,376 - $182,050)": 24, "32% ($182,051 - $231,250)": 32,
        "35% ($231,251 - $578,125)": 35, "37% ($578,126+)": 37
    }

    return state_tax_rates, property_tax_averages, federal_brackets