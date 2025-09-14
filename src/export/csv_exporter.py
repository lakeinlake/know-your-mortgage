"""
CSV Export Functionality

This module handles exporting mortgage analysis results to CSV format
for easy sharing and import into spreadsheet applications.
"""

import pandas as pd
from typing import List
from ..core.scenario import MortgageScenario
from ..core.mortgage_analyzer import MortgageAnalyzer


class CSVExporter:
    """Handles CSV export of mortgage analysis results."""

    def __init__(self):
        """Initialize CSV exporter."""
        pass

    def export_results(self, scenarios: List[MortgageScenario], analyzer: MortgageAnalyzer,
                      filename: str = 'mortgage_analysis.csv') -> pd.DataFrame:
        """
        Export detailed analysis results to CSV file.

        Args:
            scenarios: List of scenarios to analyze and export
            analyzer: MortgageAnalyzer instance
            filename: Output CSV filename

        Returns:
            DataFrame containing the exported data
        """
        all_data = []

        for scenario in scenarios:
            results = analyzer.analyze_scenario(scenario)

            for year_data in results['yearly_data']:
                row = {
                    'Scenario': scenario.name,
                    'Year': year_data['year'],
                    'Home Value': year_data['home_value'],
                    'Loan Balance': year_data['loan_balance'],
                    'Home Equity': year_data['home_equity'],
                    'Investment Value': year_data['investment_value'],
                    'Net Worth (Nominal)': year_data['net_worth'],
                    'Net Worth (Real)': year_data['net_worth_adjusted'],
                    'Monthly Payment': results['monthly_payment']
                }
                all_data.append(row)

        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        return df