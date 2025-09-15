# Know Your Mortgage - Claude Code Instructions

## Project Overview
**Version 2.0.0** - Comprehensive financial education platform built with Python and Streamlit.

**What it does:**
- Compares mortgage scenarios (15-year, 30-year, cash purchase)
- **NEW:** Rent vs Buy analysis with break-even calculations
- **NEW:** Complete first-time home buyer education platform
- **NEW:** State-specific tax integration (all 50 states)
- **NEW:** Financial health dashboard with professional guidance
- Investment opportunity cost modeling and advanced export capabilities

**Live Production:** https://know-your-mortgage-e7xnzpbgxc2oqqugtgjvye.streamlit.app/

## Key Files & Architecture
- `streamlit_app.py` - Main web dashboard (58K+ lines, comprehensive UI)
- `mortgage_analyzer.py` - Core calculation engine (40K+ lines, advanced modeling)
- `app.py` - Clean deployment entry point
- `requirements.txt` - Python dependencies
- `tests/` - Comprehensive test suite with 4 test scripts
- `CHANGELOG.md` - Complete version history and feature documentation
- `PROJECT_SUMMARY.md` - Development overview and achievements
- `README.md` - User-facing comprehensive documentation

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

# Test all features comprehensively
cd tests && python run_all_tests.py

# Test specific components
python test_rent_vs_buy.py
python test_first_time_buyer.py
python test_enhanced_features.py
python test_glossary_tax_features.py

# Test imports
python -c "from mortgage_analyzer import MortgageAnalyzer, RentScenario; print('Import successful')"
```

## Project Architecture v2.0.0

### Core Classes
- `MortgageAnalyzer` - Main calculation engine with 30+ advanced methods
- `MortgageScenario` - Data structure for mortgage scenarios
- **NEW:** `RentScenario` - Complete rental analysis modeling
- **NEW:** Educational functions for first-time buyer guidance
- **NEW:** State-specific tax and property intelligence

### Major Feature Categories

#### 1. Financial Analysis Engine
- Multiple mortgage scenario comparison (15-year, 30-year, cash)
- **NEW:** Comprehensive rent vs buy analysis with break-even calculations
- Investment opportunity cost modeling with tax benefits
- Inflation-adjusted calculations (Real vs Nominal values)
- **NEW:** State-specific tax integration (all 50 states + federal brackets)

#### 2. Educational Platform
- **NEW:** Comprehensive financial glossary (PMI, LTV, HOA, FHA, DTI, APR)
- **NEW:** First-time home buyer golden rules and guidance
- **NEW:** Real-time PMI calculations and warnings
- **NEW:** Emergency fund recommendations (6-12 months for homeowners)
- **NEW:** Debt-to-income analysis (28% housing, 43% total debt rules)

#### 3. Financial Health Assessment
- **NEW:** 4-metric professional dashboard (debt ratio, housing ratio, cash reserves, net worth)
- **NEW:** Real-time affordability feedback with color-coded warnings
- **NEW:** Smart home price recommendations (conservative vs aggressive budgets)
- **NEW:** Annual income + net worth separation (cash vs investments)

#### 4. Advanced Export & Reporting
- Enhanced CSV export with comprehensive rent/buy data
- **NEW:** Professional summary table exports
- **NEW:** Executive reports with AI-generated recommendations
- **NEW:** Multiple format options for different audiences

## Common Development Tasks

### Adding New Features
- **Mortgage scenarios:** Modify scenario creation in `streamlit_app.py`
- **Financial calculations:** Add methods to `MortgageAnalyzer` class in `mortgage_analyzer.py`
- **Educational content:** Update glossary and golden rules in `show_golden_rules()` function
- **State data:** Update state tax/property tax dictionaries in tax selection section
- **Visualizations:** Add/modify Plotly charts in dashboard sections

### Testing & Validation
- **Run full test suite:** `cd tests && python run_all_tests.py`
- **Syntax validation:** `python -m py_compile *.py`
- **Feature testing:** Use individual test scripts for specific components
- **UI testing:** Run locally with `streamlit run streamlit_app.py`

### Common Modifications
- **Add new glossary terms:** Update comprehensive glossary in `streamlit_app.py`
- **State-specific data:** Modify tax rate or property tax dictionaries
- **Educational content:** Enhance golden rules or add new tips
- **Export formats:** Add new report types in export section
- **Financial metrics:** Update dashboard calculations or thresholds

## Dependencies & Tech Stack
```txt
# Core Framework
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0

# Google Sheets Integration (optional)
gspread>=5.12.0
google-auth>=2.23.0

# Built-in Python
dataclasses
io
warnings
datetime
```

## Current Capabilities & Scope

### Financial Analysis
- **Price range:** $100K - $2M homes
- **Mortgage types:** 15-year, 30-year, cash purchase
- **NEW:** Complete rent vs buy analysis with break-even timeline
- **Investment modeling:** Stock market alternatives with tax benefits
- **Geographic coverage:** All 50 states + DC for tax accuracy

### Educational Platform
- **Target audience:** First-time home buyers
- **Coverage:** Complete mortgage terminology and process education
- **Risk prevention:** Real-time warnings for poor financial decisions
- **Professional guidance:** Financial advisor-level recommendations

### User Interface
- **Dashboard:** Professional 4-metric financial health overview
- **Interaction:** Color-coded guidance (🟢🟡🔴) for instant feedback
- **Education:** Progressive disclosure with expandable help sections
- **Export:** Multiple professional report formats

## Development Status
- **Version:** 2.0.0 (Major Educational Platform Release)
- **Status:** Production ready with comprehensive feature set
- **Testing:** 100% feature coverage with automated test suite
- **Deployment:** Live on Streamlit Cloud with automatic updates
- **Quality:** Professional-grade code with extensive documentation

## Future Enhancement Opportunities
- Property-specific costs (HOA, maintenance, insurance)
- Local market data integration
- Refinancing analysis tools
- Advanced investment property modeling
- Client management for professionals
- API development for third-party integrations

---

## 🚨 Important Development Reminders

### Key Success Factors for v2.0.0
1. **Educational First:** This is now an education platform, not just a calculator
2. **State Awareness:** All 50 states supported - use state-specific defaults
3. **Risk Prevention:** Real-time warnings prevent poor financial decisions
4. **Professional Quality:** Financial advisor-level guidance and analysis
5. **Progressive Disclosure:** Educational content when users need it

### Critical Components (Don't Break!)
- **Financial Health Dashboard:** 4-metric assessment system
- **State Tax Integration:** 50-state coverage with federal bracket selection
- **PMI Warnings:** Real-time calculations for <20% down payments
- **Rent vs Buy:** Complete break-even analysis system
- **Comprehensive Glossary:** PMI, LTV, HOA, FHA, DTI, APR definitions

### Testing Protocol
- **ALWAYS run test suite** before major changes: `cd tests && python run_all_tests.py`
- **Validate syntax** for both main files: `python -m py_compile mortgage_analyzer.py streamlit_app.py`
- **Test educational features** to ensure content accuracy
- **Verify state-specific data** when modifying tax or property information

### Code Quality Standards
- **Educational accuracy:** All financial terms and calculations must be correct
- **User safety:** Prevent dangerous financial decisions through warnings
- **Professional presentation:** Clean UI with color-coded guidance
- **Comprehensive coverage:** No essential mortgage concept should be missing

### Deployment Notes
- **Production URL:** https://know-your-mortgage-e7xnzpbgxc2oqqugtgjvye.streamlit.app/
- **Auto-deployment:** GitHub pushes trigger automatic Streamlit Cloud updates
- **Version tracking:** Update CHANGELOG.md for significant changes
- **Test coverage:** Maintain 100% feature validation through test suite

---

**Last Updated:** December 15, 2024
**Current Version:** 2.0.0 - Educational Platform
**Status:** Production Ready with Full Feature Set