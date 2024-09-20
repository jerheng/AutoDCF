import requests
import json
from config import API_KEY, TICKER, COUNTRY, REFRESH

def fetch_data(refresh=REFRESH):
    if refresh:
        # Fetch data from APIs
        cashflow_api = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{TICKER}?period=annual&apikey={API_KEY}"
        balanceSheet_api = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{TICKER}?period=annual&apikey={API_KEY}"
        income_api = f"https://financialmodelingprep.com/api/v3/income-statement/{TICKER}?period=annual&apikey={API_KEY}"
        company_api = f"https://financialmodelingprep.com/api/v3/profile/{TICKER}?apikey={API_KEY}"
        ir_api = f"https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"
        gdp_api = f"https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/{COUNTRY}"

        data = {
            'cashflow_data': requests.get(cashflow_api).json(),
            'balanceSheet_data': requests.get(balanceSheet_api).json(),
            'income_data': requests.get(income_api).json(),
            'company_data': requests.get(company_api).json(),
            'ir_data': requests.get(ir_api).json(),
            'gdp_data': requests.get(gdp_api).json()
        }

        # Save data to JSON file
        with open('data/financial_data.json', 'w') as f:
            json.dump(data, f)
    else:
        # Load data from JSON file
        with open('data/financial_data.json', 'r') as f:
            data = json.load(f)

    return data