from wacc import calculate_wacc
from fetch_fcf import fetch_fcf
from fcf_forecast import forecast_fcf_interface
from discount_fcf import discount_fcfs, calculate_npv_from_discounted
from terminal_value import calculate_present_terminal_value


def main(ticker, forecast_method: str = 'growth'):
    wacc = calculate_wacc(ticker)
    fcf_df = fetch_fcf(ticker)
    df_forecasted = forecast_fcf_interface(fcf_df, method=forecast_method, periods=5, freq="YE")
    df_discounted = discount_fcfs(df_forecasted, wacc)
    npv = calculate_npv_from_discounted(df_discounted)
    present_terminal_value = calculate_present_terminal_value(df_forecasted, wacc, perpetual_growth_rate=0.2)

    total_value = npv + present_terminal_value
    return total_value


if __name__ == '__main__':
    ticker = "NVDA"
    company_value = main(ticker, forecast_method='growth')
    print(f'Company present value :  {company_value}')
