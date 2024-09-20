# autoDcf
autoDcf is a Python-based tool for performing automated Discounted Cash Flow (DCF) analysis on publicly traded companies. It uses both Free Cash Flow to Firm (FCFF) and Free Cash Flow to Equity (FCFE) methods to calculate intrinsic value per share.

## Features
- Fetches financial data from various APIs
- Calculates risk-free rate, market risk premium, and beta
- Estimates growth rate and terminal growth rate
- Performs DCF analysis using both FCFF and FCFE methods
- Provides detailed output of valuation process and results

## Installation
1. Clone this repository
2. Install required dependencies (list dependencies here)
3. Set up your API key in the `config.py` file:
   - Create an account and get your API key from [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs/dashboard)

## Usage
1. Set the desired ticker symbol and country in config.py
2. Run the main script:
   ```bash
   python main.py
   ```
3. View the results in the console output

## Configuration
Edit the config.py file to set:
- `API_KEY`: Your Financial Modeling Prep API key
- `TICKER`: The stock ticker symbol you want to analyze
- `COUNTRY`: The country code for GDP data (e.g., "USA")
- `REFRESH`: Set to True to fetch new data from APIs, False to use cached data

## File Structure
```
autoDcf/
├── data/
│   ├── financial_data.json
│   ├── ir_data.json
│   ├── balanceSheet_data.json
│   ├── company_data.json
│   ├── income_data.json
│   ├── avg_interest_rates.json
│   ├── cashflow_data.json
│   ├── gdp_data.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── data_fetcher.py
│   ├── dcf_calculations.py
│   ├── excel_export.py
├── .gitignore
├── .gitattributes
├── LICENSE
├── README.md
├── requirements.txt
```

## API Data Sources
- Financial Modeling Prep API: Company financials and profile
- U.S. Treasury Fiscal Data API: Interest rates
- IMF Data Mapper API: GDP growth projections

## Limitations
- Relies on the accuracy of third-party API data
- Uses simplified growth and terminal value assumptions
- Does not account for qualitative factors or market sentiment
- Currently only supports USA based API's 