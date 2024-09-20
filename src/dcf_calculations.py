from datetime import datetime
from config import TICKER, COUNTRY

def get_risk_free_rate(data):
    # Use the ir_api to get the risk-free rate
    latest_data = data['ir_data']['data'][0]
    for item in data['ir_data']['data']:
        if item['security_desc'] == 'Treasury Bills':
            latest_data = item
            break
    return float(latest_data['avg_interest_rate_amt']) / 100

def calculate_market_risk_premium(data):
    # Assume Historical last 20 years S&P CAGR to be 11.1%
    historical_market_return = 0.111
    rf_rate = get_risk_free_rate(data)
    return historical_market_return - rf_rate

def get_beta(ticker, data):
    return data['company_data'][0]['beta']

def estimate_growth_rate(income_data):
    # Calculate the average revenue growth rate from historical data
    revenues = [year['revenue'] for year in income_data]
    growth_rates = [(revenues[i] - revenues[i+1]) / revenues[i+1] for i in range(len(revenues)-1)]
    return sum(growth_rates) / len(growth_rates)

def estimate_terminal_growth_rate(data):
    # Use the GDP growth rate forecast from the IMF data
    # Get the growth rate for the current year
    current_year = datetime.now().year
    current_year_growth = data['gdp_data']['values']['NGDP_RPCH'][COUNTRY].get(str(current_year), None)
    if current_year_growth is None:
        last_known_year = max(int(year) for year in data['gdp_data']['values']['NGDP_RPCH'][COUNTRY].keys())
        current_year_growth = data['gdp_data']['values']['NGDP_RPCH'][COUNTRY][str(last_known_year)]
    return current_year_growth / 100  # Convert percentage to decimal
    

def calculate_fcff(cashflow_data, income_data):
    ebit = income_data[0]['operatingIncome']
    tax_rate = income_data[0]['incomeTaxExpense'] / income_data[0]['incomeBeforeTax']
    depreciation = cashflow_data[0]['depreciationAndAmortization']
    capex = cashflow_data[0]['capitalExpenditure']
    change_in_working_capital = cashflow_data[0]['changeInWorkingCapital']
    
    fcff = ebit * (1 - tax_rate) + depreciation - capex - change_in_working_capital
    return fcff

def calculate_fcfe(cashflow_data, income_data, balanceSheet_data):
    net_income = income_data[0]['netIncome']
    depreciation = cashflow_data[0]['depreciationAndAmortization']
    capex = cashflow_data[0]['capitalExpenditure']
    change_in_working_capital = cashflow_data[0]['changeInWorkingCapital']
    net_borrowing = balanceSheet_data[0]['totalDebt'] - balanceSheet_data[1]['totalDebt']
    
    fcfe = net_income + depreciation - capex - change_in_working_capital + net_borrowing
    return fcfe

def calculate_wacc(balanceSheet_data, income_data, rf_rate, beta, market_risk_premium):
    total_debt = balanceSheet_data[0]['totalDebt']
    total_equity = balanceSheet_data[0]['totalStockholdersEquity']
    total_capital = total_debt + total_equity
    
    cost_of_debt = income_data[0]['interestExpense'] / total_debt
    tax_rate = income_data[0]['incomeTaxExpense'] / income_data[0]['incomeBeforeTax']
    after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)
    
    cost_of_equity = rf_rate + beta * market_risk_premium
    
    wacc = (total_debt / total_capital) * after_tax_cost_of_debt + (total_equity / total_capital) * cost_of_equity
    return wacc, cost_of_equity

def project_cash_flows(initial_fcff, growth_rate, years):
    projected_cash_flows = []
    for i in range(years):
        projected_cash_flows.append(initial_fcff * (1 + growth_rate) ** (i + 1))
    return projected_cash_flows

def calculate_terminal_value(final_year_fcff, terminal_growth_rate, wacc):
    return final_year_fcff * (1 + terminal_growth_rate) / (wacc - terminal_growth_rate)

def calculate_present_value(cash_flows, terminal_value, wacc):
    pv_cash_flows = sum([cf / (1 + wacc) ** (i + 1) for i, cf in enumerate(cash_flows)])
    pv_terminal_value = terminal_value / (1 + wacc) ** len(cash_flows)
    return pv_cash_flows + pv_terminal_value

def calculate_firm_and_equity_value(present_value, balanceSheet_data):
    firm_value = present_value
    net_debt = balanceSheet_data[0]['netDebt']
    equity_value = firm_value - net_debt
    return firm_value, equity_value

def calculate_dcf(data, rf_rate, beta, market_risk_premium, growth_rate, terminal_growth_rate, years, debug=False):
    cashflow_data = data['cashflow_data']
    balanceSheet_data = data['balanceSheet_data']
    income_data = data['income_data']
    
    # FCFF calculation
    fcff = calculate_fcff(cashflow_data, income_data)
    wacc, cost_of_equity = calculate_wacc(balanceSheet_data, income_data, rf_rate, beta, market_risk_premium)
    fcff_projected_cash_flows = project_cash_flows(fcff, growth_rate, years)
    fcff_terminal_value = calculate_terminal_value(fcff_projected_cash_flows[-1], terminal_growth_rate, wacc)
    fcff_present_value = calculate_present_value(fcff_projected_cash_flows, fcff_terminal_value, wacc)
    fcff_firm_value, fcff_equity_value = calculate_firm_and_equity_value(fcff_present_value, balanceSheet_data)
    
    # FCFE calculation
    fcfe = calculate_fcfe(cashflow_data, income_data, balanceSheet_data)
    fcfe_projected_cash_flows = project_cash_flows(fcfe, growth_rate, years)
    fcfe_terminal_value = calculate_terminal_value(fcfe_projected_cash_flows[-1], terminal_growth_rate, cost_of_equity)
    fcfe_present_value = calculate_present_value(fcfe_projected_cash_flows, fcfe_terminal_value, cost_of_equity)
    fcfe_equity_value = fcfe_present_value
    
    shares_outstanding = income_data[0]['weightedAverageShsOutDil']
    fcff_intrinsic_value_per_share = fcff_equity_value / shares_outstanding
    fcfe_intrinsic_value_per_share = fcfe_equity_value / shares_outstanding
    
    fcff_data = [
        ("Initial Cash Flow", fcff, fcfe),
        ("Discount Rate", wacc, cost_of_equity),
        ("Terminal Value", fcff_terminal_value, fcfe_terminal_value),
        ("Present Value", fcff_present_value, fcfe_present_value),
        ("Equity Value", fcff_equity_value, fcfe_equity_value),
        ("Intrinsic Value/Share", fcff_intrinsic_value_per_share, fcfe_intrinsic_value_per_share)
    ]

    common_variables = [
        ("Risk-free Rate", rf_rate),
        ("Market Risk Premium", market_risk_premium),
        ("Beta", beta),
        ("Estimated Growth Rate", growth_rate),
        ("Terminal Growth Rate", terminal_growth_rate),
        ("Shares Outstanding", shares_outstanding),
        ("Cost of Equity", cost_of_equity)
    ]

    projected_cash_flows = [(i+1, fcff_projected_cash_flows[i], fcfe_projected_cash_flows[i]) for i in range(years)]

    if debug:
        print("\nDCF Valuation Comparison: FCFF vs FCFE")
        print("=" * 76)
        print(f"{'Variable':<25} | {'FCFF':<22} | {'FCFE':<22}")
        print("=" * 76)
        for var, fcff_val, fcfe_val in fcff_data:
            print(f"{var:<25} | ${fcff_val:,.2f} | ${fcfe_val:,.2f}")
        
        print("\nCommon Variables")
        print("=" * 46)
        print(f"{'Variable':<25} | {'Value':<18}")
        print("=" * 46)
        for var, val in common_variables:
            print(f"{var:<25} | {val:.2%}" if isinstance(val, float) else f"{var:<25} | {val:,}")
        
        print("\nProjected Cash Flows")
        print("=" * 76)
        print(f"{'Year':<10} | {'FCFF':<22} | {'FCFE':<22}")
        print("=" * 76)
        for year, fcff, fcfe in projected_cash_flows:
            print(f"{year:<10} | ${fcff:,.2f} | ${fcfe:,.2f}")
    
    return fcff_intrinsic_value_per_share, fcfe_intrinsic_value_per_share, fcff_data, common_variables, projected_cash_flows

# Calculate the required values using the data
# rf_rate = get_risk_free_rate(data)
# market_risk_premium = calculate_market_risk_premium(data)
# beta = get_beta(TICKER)
# growth_rate = estimate_growth_rate(data['income_data'])
# terminal_growth_rate = estimate_terminal_growth_rate()
# years = 5

# # Calculate and print the result
# fcff_intrinsic_value, fcfe_intrinsic_value = calculate_dcf(data['cashflow_data'], data['balanceSheet_data'], data['income_data'], 
#                                 rf_rate, beta, market_risk_premium, growth_rate, terminal_growth_rate, years, debug=True)
# print(f"\nThe intrinsic value per share for {TICKER} using FCFF is: ${fcff_intrinsic_value:.2f}")
# print(f"The intrinsic value per share for {TICKER} using FCFE is: ${fcfe_intrinsic_value:.2f}")