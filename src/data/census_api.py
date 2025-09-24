"""
Census API Integration for Carmel vs Fishers Demographic Data
Provides real Census data with fallback to sample data for reliability.
"""

import requests
import logging
import pandas as pd
import os
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Constants ---
def _load_census_api_key():
    """
    Load Census API key from multiple sources with fallback logic.

    Priority order:
    1. Streamlit secrets (when running in Streamlit)
    2. Direct TOML file reading (for testing/development)
    3. Environment variable CENSUS_API_KEY
    4. None (fallback to sample data)

    Returns:
        str or None: The API key if found, None otherwise
    """
    # Method 1: Try Streamlit secrets first (when available)
    if STREAMLIT_AVAILABLE:
        try:
            # Check if we're running in Streamlit context
            if hasattr(st, 'secrets') and st.secrets:
                api_key = st.secrets.get("census", {}).get("api_key", None)
                if api_key:
                    return api_key
        except Exception:
            # Streamlit secrets not available or accessible
            pass

    # Method 2: Try reading .streamlit/secrets.toml directly
    try:
        import toml
        secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = toml.load(f)
                api_key = secrets.get("census", {}).get("api_key", None)
                if api_key:
                    return api_key
    except ImportError:
        # toml package not available, try manual parsing
        try:
            secrets_path = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
            if os.path.exists(secrets_path):
                with open(secrets_path, 'r') as f:
                    content = f.read()
                    # Simple extraction for [census] api_key = "value"
                    if '[census]' in content:
                        for line in content.split('\n'):
                            if 'api_key' in line and '=' in line:
                                # Extract value between quotes
                                parts = line.split('=', 1)
                                if len(parts) == 2:
                                    value = parts[1].strip()
                                    # Remove quotes if present
                                    if (value.startswith('"') and value.endswith('"')) or \
                                       (value.startswith("'") and value.endswith("'")):
                                        return value[1:-1]
        except Exception:
            pass
    except Exception:
        pass

    # Method 3: Try environment variable
    api_key = os.environ.get('CENSUS_API_KEY')
    if api_key:
        return api_key

    # Method 4: No key found
    return None

CENSUS_API_KEY = _load_census_api_key()
BASE_URL = "https://api.census.gov/data"

# FIPS Codes for Indiana Cities
FIPS_CODES = {
    "Indiana": "18",
    "Carmel": "10342",   # Correct FIPS for Carmel city, Indiana
    "Fishers": "23278"   # Correct FIPS for Fishers city, Indiana
}

# Census Variables for ACS 5-Year Data Profiles
CENSUS_VARS = {
    "population": "DP05_0033E",      # Total Population
    "median_income": "DP03_0062E"   # Median Household Income
}

# --- Sample Data as Fallback ---
SAMPLE_DATA = {
    "Carmel": {
        2019: {"population": 97800, "median_income": 112000},
        2020: {"population": 98200, "median_income": 115000},
        2021: {"population": 98800, "median_income": 119000},
        2022: {"population": 99500, "median_income": 123000},
        2023: {"population": 100100, "median_income": 126000},
        2024: {"population": 100800, "median_income": 129000},
    },
    "Fishers": {
        2019: {"population": 95300, "median_income": 89000},
        2020: {"population": 96800, "median_income": 92000},
        2021: {"population": 98500, "median_income": 95000},
        2022: {"population": 100200, "median_income": 98000},
        2023: {"population": 102100, "median_income": 101000},
        2024: {"population": 104000, "median_income": 104000},
    }
}

# --- Data Fetching Logic ---

def _fetch_census_data_for_year(year, place_name):
    """
    Helper to fetch demographic data for a single place and year from Census API.

    Args:
        year (int): Year to fetch data for
        place_name (str): City name ("Carmel" or "Fishers")

    Returns:
        dict: Contains population and median_income data

    Raises:
        ValueError: If API key missing or no data returned
        requests.RequestException: If API call fails
    """
    if not CENSUS_API_KEY:
        raise ValueError("Census API key not found in Streamlit secrets.")

    place_fips = FIPS_CODES[place_name]
    state_fips = FIPS_CODES["Indiana"]
    variables = ",".join(CENSUS_VARS.values())

    url = f"{BASE_URL}/{year}/acs/acs5/profile?get={variables}&for=place:{place_fips}&in=state:{state_fips}&key={CENSUS_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        if len(data) < 2:
            raise ValueError(f"No data returned from Census API for {place_name} in {year}")

        # Parse response - first row is headers, second row is data
        headers = data[0]
        values = data[1]

        return {
            "population": int(values[headers.index(CENSUS_VARS["population"])]),
            "median_income": int(values[headers.index(CENSUS_VARS["median_income"])])
        }

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"API request failed: {e}")
    except (ValueError, KeyError, IndexError) as e:
        raise ValueError(f"Failed to parse Census API response: {e}")


@st.cache_data(ttl=60 * 60 * 24)  # Cache for 24 hours
def get_demographic_data(years=None):
    """
    Fetches demographic data for Carmel and Fishers from Census API.
    Falls back to sample data if API fails for any reason.

    Args:
        years (list): Years to fetch data for. Defaults to 2019-2022 (latest available)

    Returns:
        tuple: (data_dict, data_source_string)
            - data_dict: Nested dict with structure {city: {year: {population, median_income}}}
            - data_source_string: "Census API" or "Sample Data"
    """
    if years is None:
        years = [2019, 2020, 2021, 2022]  # Latest available Census data

    data = {}
    data_source = "Census API"

    # If API key is missing, immediately fall back to sample data
    if not CENSUS_API_KEY:
        logging.warning("Census API key not found. Using sample data.")
        return SAMPLE_DATA, "Sample Data"

    # Try to fetch real Census data
    try:
        for city in ["Carmel", "Fishers"]:
            data[city] = {}
            for year in years:
                try:
                    city_year_data = _fetch_census_data_for_year(year, city)
                    data[city][year] = city_year_data
                    logging.info(f"Successfully fetched {city} {year} data from Census API")
                except Exception as e:
                    logging.warning(f"Failed to fetch Census data for {city} {year}: {e}")
                    # On any failure, fall back completely to sample data for consistency
                    logging.info("Falling back to sample data for reliability")
                    return SAMPLE_DATA, "Sample Data"

        logging.info(f"Successfully fetched all demographic data using Census API")
        return data, data_source

    except Exception as e:
        logging.error(f"Unexpected error in Census API integration: {e}")
        logging.info("Using sample data as fallback")
        return SAMPLE_DATA, "Sample Data"


def format_demographic_data_for_charts(demographic_data, data_source):
    """
    Formats demographic data into pandas DataFrames for chart visualization.

    Args:
        demographic_data (dict): Raw demographic data from get_demographic_data()
        data_source (str): Data source identifier

    Returns:
        tuple: (demographics_df, projections_df, data_source)
    """
    # Convert to DataFrame format matching existing structure
    rows = []
    for year in sorted(demographic_data["Carmel"].keys()):
        if year <= 2024:  # Historical data
            rows.append({
                'year': year,
                'carmel_population': demographic_data["Carmel"][year]["population"] / 1000,  # Convert to thousands
                'fishers_population': demographic_data["Fishers"][year]["population"] / 1000,
                'carmel_income': demographic_data["Carmel"][year]["median_income"],
                'fishers_income': demographic_data["Fishers"][year]["median_income"]
            })

    demographics_df = pd.DataFrame(rows)

    # Create simple projections for 2025-2030 based on recent trends
    if len(demographics_df) >= 2:
        latest_year = demographics_df['year'].max()
        carmel_pop_growth = (demographics_df['carmel_population'].iloc[-1] / demographics_df['carmel_population'].iloc[-2]) - 1
        fishers_pop_growth = (demographics_df['fishers_population'].iloc[-1] / demographics_df['fishers_population'].iloc[-2]) - 1
        carmel_income_growth = (demographics_df['carmel_income'].iloc[-1] / demographics_df['carmel_income'].iloc[-2]) - 1
        fishers_income_growth = (demographics_df['fishers_income'].iloc[-1] / demographics_df['fishers_income'].iloc[-2]) - 1

        proj_rows = []
        for year in range(latest_year + 1, 2031):
            years_ahead = year - latest_year
            proj_rows.append({
                'year': year,
                'carmel_population': demographics_df['carmel_population'].iloc[-1] * ((1 + carmel_pop_growth) ** years_ahead),
                'fishers_population': demographics_df['fishers_population'].iloc[-1] * ((1 + fishers_pop_growth) ** years_ahead),
                'carmel_income': demographics_df['carmel_income'].iloc[-1] * ((1 + carmel_income_growth) ** years_ahead),
                'fishers_income': demographics_df['fishers_income'].iloc[-1] * ((1 + fishers_income_growth) ** years_ahead)
            })

        projections_df = pd.DataFrame(proj_rows)
    else:
        projections_df = pd.DataFrame()

    return demographics_df, projections_df, data_source


def get_census_api_status():
    """
    Check if Census API is available and configured properly.

    Returns:
        dict: Status information about API availability
    """
    status = {
        "api_key_configured": bool(CENSUS_API_KEY),
        "api_accessible": False,
        "latest_data_year": None,
        "error_message": None
    }

    if not CENSUS_API_KEY:
        status["error_message"] = "Census API key not configured"
        return status

    # Test API connectivity with a simple call
    try:
        test_url = f"{BASE_URL}/2022/acs/acs5/profile?get=DP05_0033E&for=place:{FIPS_CODES['Carmel']}&in=state:{FIPS_CODES['Indiana']}&key={CENSUS_API_KEY}"
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            status["api_accessible"] = True
            status["latest_data_year"] = 2022  # Most recent full dataset
        else:
            status["error_message"] = f"API returned status code: {response.status_code}"
    except Exception as e:
        status["error_message"] = f"API connectivity test failed: {e}"

    return status


if __name__ == '__main__':
    # Test the module functionality
    print("Testing Census API integration...")

    # Check API status
    status = get_census_api_status()
    print(f"API Status: {status}")

    # Test data fetching
    try:
        demographics, source = get_demographic_data()
        print(f"\nData source: {source}")
        print(f"Sample data structure:")
        for city in demographics:
            print(f"{city}: {len(demographics[city])} years of data")
            latest_year = max(demographics[city].keys())
            latest_data = demographics[city][latest_year]
            print(f"  {latest_year}: Pop={latest_data['population']:,}, Income=${latest_data['median_income']:,}")
    except Exception as e:
        print(f"Error testing data fetch: {e}")