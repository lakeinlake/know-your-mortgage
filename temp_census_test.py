import streamlit as st
import requests
import os

st.title("🔍 Census API Key Debug Test")

# 1. Test if st.secrets can read the census API key
st.header("1. Testing Streamlit Secrets")
census_api_key = st.secrets.get("census", {}).get("api_key")

if census_api_key:
    st.success("✅ Success: Census API key found in st.secrets.")
    # For security, let's not print the full key.
    st.write(f"- Key starts with: `{census_api_key[:5]}...`")
    st.write(f"- Key ends with: `...{census_api_key[-5:]}`")
    st.write(f"- Key length: {len(census_api_key)} characters")
else:
    st.error("❌ Failure: Census API key NOT found in st.secrets.")
    st.write("- `st.secrets.get(\"census\", {}).get(\"api_key\")` returned None.")

    # Debug: Show what's actually in st.secrets
    st.write("**Debug: st.secrets content:**")
    try:
        st.write(f"- Available sections: {list(st.secrets.keys())}")
        if "census" in st.secrets:
            st.write(f"- Census section keys: {list(st.secrets['census'].keys())}")
        else:
            st.write("- 'census' section not found in secrets")
    except Exception as e:
        st.write(f"- Error reading secrets: {e}")

# 2. Make a direct Census API call to validate the key
if census_api_key:
    st.header("2. Testing Census API Call")

    # Test with a simple API call (using correct FIPS code for Carmel)
    test_url = f"https://api.census.gov/data/2022/acs/acs5/profile?get=DP05_0033E&for=place:10342&in=state:18&key={census_api_key}"
    st.write("Making test API call to Census Bureau...")
    st.code(f"URL: https://api.census.gov/data/2022/acs/acs5/profile?get=DP05_0033E&for=place:10342&in=state:18&key=YOUR_KEY", language="text")

    try:
        with st.spinner("Testing API call..."):
            response = requests.get(test_url, timeout=10)

        status_code = response.status_code
        st.write(f"**Response Status Code:** {status_code}")

        if status_code == 200:
            st.success("✅ Success: API call successful (HTTP 200). The API key is valid!")
            try:
                # Try to parse the JSON response
                data = response.json()
                st.write("✅ Successfully parsed JSON response.")

                # Display the data
                st.write("**API Response:**")
                st.json(data)

                if isinstance(data, list) and len(data) > 1:
                    st.write(f"**Sample Data:** {data[1]}")
                    if len(data[1]) > 0:
                        population = data[1][0]
                        st.metric("Carmel Population (2022)", f"{int(population):,}")

            except requests.exceptions.JSONDecodeError:
                st.warning("⚠️ Warning: API call returned 200, but response is not valid JSON.")
                st.text(f"Response Text (first 200 chars): {response.text[:200]}")

        elif status_code == 401 or status_code == 403:
            st.error("❌ Failure: API call failed with status 401/403 (Unauthorized/Forbidden).")
            st.write("This strongly suggests the API key is invalid or has been entered incorrectly.")
            st.text(f"Response Text: {response.text}")

        elif status_code == 400:
            st.error("❌ Failure: Bad Request (400)")
            st.write("The API request format might be incorrect, or the year/geography might not be available.")
            st.text(f"Response Text: {response.text}")

        else:
            st.error(f"❌ Failure: API call failed with status code {status_code}.")
            st.write("This could be an issue with the API service itself or the request format.")
            st.text(f"Response Text: {response.text}")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failure: An exception occurred while making the API request.")
        st.text(f"Error: {e}")
else:
    st.header("2. Skipping API Call Test")
    st.warning("Cannot perform API call test because the API key was not found.")

st.header("3. Debugging Summary")

if census_api_key:
    st.success("🎯 **Next Steps:** If the API call succeeded, the issue might be in our main application's Census API integration logic.")
else:
    st.error("🎯 **Next Steps:** Fix the secrets.toml configuration first. Check file location and format.")

st.markdown("---")
st.markdown("**File Locations to Check:**")
st.code("""
1. .streamlit/secrets.toml should be in project root
2. Format should be:
   [census]
   api_key = "your_key_here"

3. Restart Streamlit after adding secrets
""", language="toml")

# Also print to terminal for debugging
print("\n=== TERMINAL DEBUG OUTPUT ===")
print(f"API Key Found: {bool(census_api_key)}")
if census_api_key:
    print(f"Key Length: {len(census_api_key)}")
    print(f"Key Preview: {census_api_key[:5]}...{census_api_key[-5:]}")
print("=============================\n")