# Know Your Mortgage - Claude Code Instructions

## Project Overview
Comprehensive mortgage analysis tool built with Python and Streamlit. Compares different mortgage scenarios including 30-year, 15-year mortgages, cash purchases, and investment opportunity costs.

## Key Files
- `mortgage_analyzer.py` - Core calculation engine with MortgageAnalyzer class
- `streamlit_app.py` - Web dashboard interface
- `requirements.txt` - Python dependencies
- `README.md` - Comprehensive documentation

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (if exists)
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the Streamlit dashboard
streamlit run streamlit_app.py

# Access at: http://localhost:8501
```

### Development Workflow
```bash
# Check code quality (if tools available)
python -m py_compile mortgage_analyzer.py streamlit_app.py

# Test imports
python -c "from mortgage_analyzer import MortgageAnalyzer; print('Import successful')"
```

## Project Architecture

### Core Classes
- `MortgageAnalyzer` - Main calculation engine
- `MortgageScenario` - Data structure for mortgage scenarios

### Key Features
- Multiple mortgage scenario comparison
- Investment opportunity cost analysis
- Inflation-adjusted calculations
- Tax benefit modeling
- Interactive Streamlit dashboard
- CSV export functionality

## Common Tasks
- Modify scenarios in `streamlit_app.py`
- Add calculations in `mortgage_analyzer.py`
- Update visualizations using Plotly charts
- Export data analysis to CSV

## Dependencies
- streamlit
- pandas
- numpy
- plotly
- dataclasses (built-in)

## Notes
- Home price range: $100K - $2M
- Supports 15-year and 30-year mortgages
- Includes cash purchase analysis
- Models stock market investment alternatives