from config import TICKER, REFRESH
from dcf_calculations import calculate_dcf, get_risk_free_rate, calculate_market_risk_premium, get_beta, estimate_growth_rate, estimate_terminal_growth_rate
from data_fetcher import fetch_data
# from excel_export import export_to_excel

# Fetch or load data
data = fetch_data(REFRESH)
# Your existing code for fetching data, setting up variables, etc.

# Calculate and print the result
def calculate_required_values(data):
    rf_rate = get_risk_free_rate(data)
    market_risk_premium = calculate_market_risk_premium(data)
    beta = get_beta(TICKER, data)
    growth_rate = estimate_growth_rate(data['income_data'])
    terminal_growth_rate = estimate_terminal_growth_rate(data)
    years = 5
    return rf_rate, market_risk_premium, beta, growth_rate, terminal_growth_rate, years

# Calculate required values
rf_rate, market_risk_premium, beta, growth_rate, terminal_growth_rate, years = calculate_required_values(data)

# Perform DCF calculations
fcff_intrinsic_value, fcfe_intrinsic_value, fcff_data, common_variables, projected_cash_flows = calculate_dcf(
    data, rf_rate, beta, market_risk_premium, growth_rate, terminal_growth_rate, years, debug=True
)

# Print results
print(f"\nThe intrinsic value per share for {TICKER} using FCFF is: ${fcff_intrinsic_value:.2f}")
print(f"The intrinsic value per share for {TICKER} using FCFE is: ${fcfe_intrinsic_value:.2f}")

# Export to Excel - TBD