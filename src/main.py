from config import TICKER, REFRESH
from dcf_calculations import (
    calculate_dcf, get_risk_free_rate, calculate_market_risk_premium, 
    get_beta, estimate_growth_rate, estimate_terminal_growth_rate,
    monte_carlo_simulation, analyze_monte_carlo_results
)
from data_fetcher import fetch_data
from tabulate import tabulate

# Fetch or load data
data = fetch_data(REFRESH)

# Calculate required values
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

# Perform Monte Carlo simulation
monte_carlo_results = monte_carlo_simulation(
    data, rf_rate, beta, market_risk_premium, growth_rate, terminal_growth_rate, years, num_simulations=10000
)

# Analyze Monte Carlo results
mc_analysis = analyze_monte_carlo_results(monte_carlo_results)

# Print results
print(f"\nValuation Summary for {TICKER}:")
valuation_summary = [
    ["Method", "Intrinsic Value per Share"],
    ["FCFF", f"${fcff_intrinsic_value:.2f}"],
    ["FCFE", f"${fcfe_intrinsic_value:.2f}"]
]
print(tabulate(valuation_summary, headers="firstrow", tablefmt="grid"))

print("\nCommon Variables:")
common_vars_table = [[var, f"{val:.2%}" if isinstance(val, float) else f"{val:,}"] for var, val in common_variables]
print(tabulate(common_vars_table, headers=["Variable", "Value"], tablefmt="grid"))

print("\nProjected Cash Flows (with Mean Reversion):")
cash_flows_table = [[year, f"${fcff:,.2f}", f"${fcfe:,.2f}"] for year, fcff, fcfe in projected_cash_flows]
print(tabulate(cash_flows_table, headers=["Year", "FCFF", "FCFE"], tablefmt="grid"))

print("\nDCF Valuation Comparison: FCFF vs FCFE")
dcf_comparison = [
    ["Variable", "FCFF", "FCFE"],
    ["Initial Cash Flow", f"${fcff_data[0][1]:,.2f}", f"${fcff_data[0][2]:,.2f}"],
    ["Discount Rate", f"{fcff_data[1][1]:.2%}", f"{fcff_data[1][2]:.2%}"],
    ["Terminal Value", f"${fcff_data[2][1]:,.2f}", f"${fcff_data[2][2]:,.2f}"],
    ["Present Value", f"${fcff_data[3][1]:,.2f}", f"${fcff_data[3][2]:,.2f}"],
    ["Equity Value", f"${fcff_data[4][1]:,.2f}", f"${fcff_data[4][2]:,.2f}"],
    ["Intrinsic Value/Share", f"${fcff_data[5][1]:.2f}", f"${fcff_data[5][2]:.2f}"]
]
print(tabulate(dcf_comparison, headers="firstrow", tablefmt="grid"))

print("\nMonte Carlo Simulation Results:")
mc_table = []
for method in mc_analysis:
    mc_table.append([
        method.upper(),
        f"${mc_analysis[method]['mean']:.2f}",
        f"${mc_analysis[method]['median']:.2f}",
        f"${mc_analysis[method]['std_dev']:.2f}",
        f"${mc_analysis[method]['95_ci'][0]:.2f} - ${mc_analysis[method]['95_ci'][1]:.2f}"
    ])
print(tabulate(mc_table, headers=["Method", "Mean", "Median", "Std Dev", "95% CI"], tablefmt="grid"))