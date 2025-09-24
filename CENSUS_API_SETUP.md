# Census API Setup Instructions

## Overview
The market comparison page can use real U.S. Census Bureau demographic data for enhanced accuracy. This is optional - the application works perfectly with sample data if no API key is configured.

## Getting a Census API Key (Free)

1. **Visit the Census API Key Signup Page**
   - Go to: https://api.census.gov/data/key_signup.html
   - Fill out the form with your information
   - API keys are free and issued instantly

2. **Verify Your Email**
   - Check your email for the API key
   - Save the key securely

## Configuration Options

### For Local Development

Create a `.streamlit/secrets.toml` file in your project root:

```toml
[census]
api_key = "YOUR_API_KEY_HERE"
```

### For Streamlit Cloud Deployment

1. Go to your Streamlit Cloud dashboard
2. Navigate to your app settings
3. Under "Secrets", add:

```toml
[census]
api_key = "YOUR_API_KEY_HERE"
```

### For Other Deployments

Set the environment variable or configure your secrets management system to provide the Census API key through Streamlit's secrets interface.

## Data Coverage

**With Census API Key:**
- Real population and income data for Carmel and Fishers
- Historical data typically available 2019-2022 (with ~2 year lag)
- Data sourced from American Community Survey (ACS) 5-Year Estimates

**Without API Key (Default):**
- Realistic sample data based on market research
- Complete 2019-2024 historical trends
- Projections through 2030

## Benefits of Real Census Data

✅ **Credibility**: Official U.S. Census Bureau data
✅ **Accuracy**: Real demographic trends
✅ **Transparency**: Users know they're seeing official data
✅ **Validation**: Confirms investment analysis assumptions

## Fallback Behavior

The application is designed to be robust:
- If API key is missing → Uses sample data
- If API call fails → Falls back to sample data
- If data is incomplete → Uses sample data
- Always displays data source to users

## Testing Your Setup

1. **Add your API key** to Streamlit secrets
2. **Restart the application**
3. **Navigate to Market Comparison page**
4. **Look for data source indicator:**
   - 🟢 "Census API (Real-time U.S. Census Bureau data)" = Success!
   - 🔵 "Sample Data (Realistic sample data...)" = Using fallback

## Troubleshooting

**Common Issues:**
- **Wrong file location**: `.streamlit/secrets.toml` must be in project root
- **TOML syntax errors**: Check brackets and quotes are correct
- **API key format**: Use the exact key from the Census Bureau email
- **Caching**: Restart Streamlit after adding the key

**Still not working?**
- Check the browser console for error messages
- Verify your API key works at: https://api.census.gov/data/2022/acs/acs5/profile?get=DP05_0033E&for=place:10588&in=state:18&key=YOUR_KEY_HERE
- The application will show detailed logs about data source selection

## API Limits and Usage

- **Rate Limits**: Census API has reasonable limits for development use
- **Caching**: Data is cached for 24 hours to minimize API calls
- **Cost**: Census API is completely free
- **Reliability**: Government API with high uptime

---

**Note**: The Census API integration enhances the application but is not required. The sample data provides an excellent user experience and demonstrates all functionality.