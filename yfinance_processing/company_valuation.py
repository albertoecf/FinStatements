import pandas as pd
from wacc import calculate_wacc
from fetch_fcf import fetch_fcf
from fcf_forecast import forecast_fcf_interface
from discount_fcf import discount_fcfs, calculate_npv_from_discounted
from terminal_value import calculate_present_terminal_value


def main(tickers: list[str], forecast_method: str = 'growth', perpetual_growth_rate: float = 0.02) -> pd.DataFrame:
    """
    Process multiple tickers to calculate valuation metrics.

    Args:
        tickers (list[str]): List of ticker strings.
        forecast_method (str): Forecasting method to use.
        perpetual_growth_rate (float): Perpetual growth rate for terminal value.

    Returns:
        pd.DataFrame: DataFrame with columns:
                      ['ticker', 'wacc', 'npv', 'present_terminal_value', 'total_value']
    """
    results = []

    for ticker in tickers:
        try:
            wacc = calculate_wacc(ticker)
            fcf_df = fetch_fcf(ticker)
            df_forecasted = forecast_fcf_interface(fcf_df, method=forecast_method, periods=5, freq="YE")
            df_discounted = discount_fcfs(df_forecasted, wacc)
            npv = calculate_npv_from_discounted(df_discounted)
            present_terminal_value = calculate_present_terminal_value(df_forecasted, wacc, perpetual_growth_rate)
            total_value = npv + present_terminal_value

            results.append({
                "ticker": ticker,
                "wacc": wacc,
                "npv": npv,
                "present_terminal_value": present_terminal_value,
                "total_value": total_value
            })

        except Exception as e:
            # Handle errors gracefully, log or print as needed
            print(f"Error processing {ticker}: {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    # Example usage
    from settings import sp500_tickers

    df_valuation = main(sp500_tickers, forecast_method='growth', perpetual_growth_rate=0.02)
    print(df_valuation)
