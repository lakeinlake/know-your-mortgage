# Test Scripts

This directory contains test scripts to validate different features of the mortgage analysis tool.

## Test Scripts

### `test_rent_vs_buy.py`
Tests the rent vs buy analysis features:
- RentScenario class implementation
- Break-even analysis calculations
- Rent escalation modeling
- Investment opportunity analysis

### `test_first_time_buyer.py`
Tests first-time home buyer educational features:
- Golden rules implementation
- PMI calculations and warnings
- Emergency fund guidance
- Affordability calculators
- Educational content delivery

### `test_enhanced_features.py`
Tests enhanced financial profile features:
- Annual income vs monthly income inputs
- Net worth separation (cash vs stocks)
- Debt-to-income analysis
- Real-time affordability feedback
- Financial health dashboard

### `test_glossary_tax_features.py`
Tests comprehensive glossary and tax features:
- Financial term definitions (PMI, LTV, HOA, FHA)
- State-specific tax rate selection
- Property tax defaults by state
- Tax deduction explanations

## Running Tests

To run all tests:

```bash
cd tests
python3 test_rent_vs_buy.py
python3 test_first_time_buyer.py
python3 test_enhanced_features.py
python3 test_glossary_tax_features.py
```

Or run the comprehensive test suite:

```bash
python3 run_all_tests.py
```

## Test Coverage

These tests validate:
- ✅ Core mortgage analysis functionality
- ✅ Rent vs buy comparison features
- ✅ First-time buyer educational content
- ✅ Financial health analysis
- ✅ State-specific tax calculations
- ✅ Comprehensive financial glossary
- ✅ Real-time affordability feedback
- ✅ Professional reporting capabilities

All tests check for both implementation completeness and educational value delivery.