Company Financials Extractor

A lightweight Python tool that downloads Income Statement, Balance Sheet, and Cash Flow Statement data for any ticker using Yahoo Finance (yfinance). The program cleans the data and exports it into three structured CSV files—ready for valuation models, analysis, or automation.

Features

User-input ticker (e.g., AAPL, CBA.AX, TSLA, BHP.AX)

Automatically fetches:

Income Statement

Balance Sheet

Cash Flow Statement

Cleans the data while keeping the original orientation:

Rows = line items

Columns = reporting periods

Exports three CSV files:

clean_income_statement.csv

clean_balance_sheet.csv

clean_cash_flow.csv

Missing data handled safely (NaNs preserved)

Requirements

Python 3.8+

pandas

yfinance

Install:

pip install pandas yfinance

How to Use

Run the script in Jupyter Notebook or Python.

Enter the ticker symbol when asked.

The script downloads and cleans all available financial statements.

CSV files appear in your working directory.

Example input:

Enter a ticker (e.g. CBA.AX, WBC.AX, AAPL): AAPL

Output Format

Each CSV contains:

line_item — name of the financial metric

statement — income, balance_sheet, or cash_flow

Columns for each reporting year

NaN values included where Yahoo provides no data

Example rows:

line_item, statement, 2024-06-30, 2023-06-30, 2022-06-30
Revenue, income, 383285000000, 394328000000, 365817000000
Gross Profit, income, 169088000000, 170782000000, 169147000000

Notes & Limitations

Yahoo generally provides only 4 years of annual data.

Small caps may have sparse disclosures.

NaNs remain to reflect actual data availability.