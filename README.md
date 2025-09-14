# 🏠 Comprehensive Mortgage Analysis Tool

A powerful, interactive web application for analyzing and comparing different mortgage scenarios to make informed home financing decisions. Built with Python and Streamlit, this tool helps you understand the long-term financial implications of various mortgage strategies.

## 🌟 Features

### Core Functionality
- **Multiple Scenario Comparison**: Compare 30-year, 15-year mortgages with different down payments, and cash purchases
- **Time Value of Money**: Inflation-adjusted calculations for real purchasing power analysis
- **Investment Analysis**: Model opportunity costs by comparing mortgage payments vs. stock market investments
- **Tax Benefits**: Account for mortgage interest deduction based on your tax bracket
- **Comprehensive Calculations**:
  - Monthly payment calculations
  - Full amortization schedules
  - Investment growth projections
  - Home appreciation modeling
  - Net worth tracking over 30 years

### Interactive Dashboard
- **Real-time Visualizations**:
  - Net worth projections (nominal and inflation-adjusted)
  - Monthly payment comparisons
  - Investment growth charts
  - Home equity progression
  - Interest cost analysis
- **Customizable Parameters**:
  - Home price slider ($100K - $2M)
  - Adjustable down payment options
  - Variable interest rates
  - Stock market return rates
  - Inflation rate adjustments
  - Tax rate configuration
  - Property tax settings
- **Export Capabilities**:
  - Full CSV export with year-by-year breakdown
  - Summary report generation
  - All data downloadable for further analysis

## 📋 Default Assumptions

The tool comes with research-based default values that can be customized:

| Parameter | Default Value | Description |
|-----------|--------------|-------------|
| Home Price | $500,000 | Property purchase price |
| 15-Year Rate | 5.6% | Interest rate for 15-year mortgage |
| 30-Year Rate | 6.1% | Interest rate for 30-year mortgage |
| Stock Return | 8% | Expected annual stock market return |
| Inflation | 3% | Annual inflation rate |
| Home Appreciation | 5% | Annual home value increase |
| Property Tax | 2% | Annual property tax rate |
| Tax Rate | 26% | Marginal tax rate for deductions |
| Emergency Fund | $50,000 | Kept separate, not invested |

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the project**:
```bash
mkdir mortgage_analyzer
cd mortgage_analyzer
```

2. **Create the project files**:
   - Save `mortgage_analyzer.py` (core logic)
   - Save `streamlit_app.py` (web interface)
   - Save `requirements.txt` (dependencies)

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## 📊 Usage

### Running the Application

1. **Start the Streamlit app**:
```bash
streamlit run streamlit_app.py
```

2. **Access the dashboard**:
   - The app will automatically open in your default browser
   - If not, navigate to `http://localhost:8501`

### Using the Dashboard

1. **Configure Parameters** (Left Sidebar):
   - Adjust home price using the slider
   - Set down payment amounts for comparison
   - Modify interest rates for different loan terms
   - Configure investment and economic assumptions

2. **Analyze Results** (Main Panel):
   - Review net worth projections over 30 years
   - Compare monthly payments across scenarios
   - Check the summary table with rankings
   - Explore detailed tabs for deeper insights

3. **Export Data**:
   - Click "Generate CSV Export" for full data
   - Use "Generate Summary Report" for a text summary

### Programmatic Usage

You can also use the `MortgageAnalyzer` class directly in Python:

```python
from mortgage_analyzer import MortgageAnalyzer, MortgageScenario

# Initialize analyzer
analyzer = MortgageAnalyzer(home_price=500000)

# Create a custom scenario
scenario = MortgageScenario(
    name="Custom 20-Year",
    home_price=500000,
    down_payment=100000,
    loan_amount=400000,
    interest_rate=0.055,
    term_years=20,
    stock_return_rate=0.08,
    inflation_rate=0.03
)

# Analyze the scenario
results = analyzer.analyze_scenario(scenario)

# View results
print(f"Monthly Payment: ${results['monthly_payment']:,.2f}")
print(f"Total Interest: ${results['total_interest']:,.2f}")
print(f"Final Net Worth (Real): ${results['final_net_worth_adjusted']:,.2f}")
```

## 📈 Scenarios Analyzed

The tool compares four primary scenarios:

### 1. 30-Year Mortgage with $100K Down
- Longest term, lowest monthly payment
- Maximum leverage for investment opportunities
- Higher total interest paid

### 2. 15-Year Mortgage with $100K Down
- Shorter term, higher monthly payment
- Faster equity building
- Significant interest savings

### 3. 15-Year Mortgage with $200K Down
- Lower loan amount, moderate monthly payment
- Reduced interest costs
- Less capital for investments

### 4. Cash Purchase
- No mortgage payments or interest
- Immediate full equity
- Opportunity cost of capital

## 🔧 Technical Architecture

### Project Structure
```
mortgage_analyzer/
│
├── mortgage_analyzer.py    # Core calculation engine
├── streamlit_app.py        # Web dashboard interface
├── requirements.txt        # Python dependencies
└── README.md              # Documentation
```

### Key Components

#### MortgageAnalyzer Class
- Handles all financial calculations
- Generates amortization schedules
- Calculates investment growth
- Adjusts for inflation
- Compares multiple scenarios

#### MortgageScenario Dataclass
- Encapsulates scenario parameters
- Ensures data consistency
- Enables easy scenario creation

#### Streamlit Dashboard
- Interactive parameter controls
- Real-time chart updates
- Professional visualizations
- CSV export functionality

## 📊 Calculation Methodology

### Monthly Payment Formula
```
P = L[c(1 + c)^n]/[(1 + c)^n - 1]
```
Where:
- P = Monthly payment
- L = Loan amount
- c = Monthly interest rate
- n = Number of payments

### Investment Growth
- Compound interest with monthly contributions
- Tax-advantaged account assumptions
- Reinvestment of tax savings from mortgage deduction

### Inflation Adjustment
- Converts nominal values to real purchasing power
- Uses compound inflation over analysis period
- Critical for long-term comparisons

## 🎯 Key Insights Provided

1. **Optimal Financing Strategy**: Identifies which mortgage approach maximizes long-term wealth
2. **Opportunity Cost Analysis**: Shows impact of investing vs. paying down mortgage
3. **Tax Benefit Quantification**: Calculates actual savings from mortgage interest deduction
4. **Break-even Analysis**: Determines when different strategies intersect
5. **Risk Assessment**: Compares guaranteed savings vs. market return assumptions

## ⚠️ Limitations & Disclaimers

### Not Included
- Private Mortgage Insurance (PMI) calculations
- Homeowners insurance costs
- HOA fees
- Maintenance and repair costs
- Closing costs and fees
- Market volatility modeling
- Variable rate mortgages

### Assumptions
- Stable income throughout period
- Constant tax laws
- No prepayments or refinancing
- Linear home appreciation
- Constant investment returns

### Important Note
This tool provides estimates based on simplified models. Always consult with qualified financial advisors, tax professionals, and mortgage specialists for personalized advice.

## 🔄 Extending the Tool

### Adding New Scenarios
```python
# In streamlit_app.py, add to scenarios list:
MortgageScenario(
    name="Custom Scenario",
    home_price=home_price,
    down_payment=custom_amount,
    loan_amount=home_price - custom_amount,
    interest_rate=custom_rate,
    term_years=custom_term,
    # ... other parameters
)
```

### Customizing Visualizations
- Modify Plotly chart configurations in `streamlit_app.py`
- Add new chart types in the detailed analysis tabs
- Customize color schemes and styling

### Adding New Calculations
- Extend `MortgageAnalyzer` class with new methods
- Add results to the `analyze_scenario` output
- Display in dashboard through new metrics or charts

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add PMI calculations
- Include closing cost analysis
- Model market volatility
- Add rent vs. buy comparison
- Include refinancing analysis
- Support for ARMs (Adjustable Rate Mortgages)

## 📄 License

This project is provided as-is for educational and analytical purposes. Use at your own risk for financial decision-making.

## 🙏 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web app framework
- [Plotly](https://plotly.com/) - Interactive visualizations
- [Pandas](https://pandas.pydata.org/) - Data analysis
- [NumPy](https://numpy.org/) - Numerical computations

## 📞 Support

For questions, issues, or suggestions, please open an issue on the project repository or contact the development team.

---

**Version**: 1.0.0
**Last Updated**: 2024
**Status**: Production Ready