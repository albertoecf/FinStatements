import pandas as pd


def calculate_present_terminal_value(df: pd.DataFrame, wacc: float, perpetual_growth_rate: float) -> float:
    """
    Calculates the terminal value (TV) using the Gordon Growth Model.
    This function is meant to be used only with forecasted df as it counts the periods present in the df.

    Args:
        df (pd.DataFrame): DataFrame containing a 'fcff' column with forecasted free cash flows.
        wacc (float): Weighted Average Cost of Capital as a decimal (e.g. 0.12).
        perpetual_growth_rate (float): Perpetual growth rate as a decimal (e.g. 0.02).

    Returns:
        float: The terminal value discounted back to present value.
    """
    if 'fcff' not in df.columns:
        raise ValueError("DataFrame must contain a 'fcff' column.")

    # Last forecasted FCF
    last_fcf = df['fcff'].iloc[-1]

    # Calculate terminal value at year n+1
    tv = last_fcf * (1 + perpetual_growth_rate) / (wacc - perpetual_growth_rate)

    # Discount terminal value back to present value
    periods = len(df)
    discounted_tv = tv / ((1 + wacc) ** periods)

    return discounted_tv


if __name__ == "__main__":
    from fetch_fcf import fetch_fcf
    from fcf_forecast import forecast_fcf_interface
    from wacc import calculate_wacc
    from settings import sp500_tickers

    # Example perpetual growth assumption (e.g. 2%)
    g = 0.02

    results = []

    for ticker in sp500_tickers:
        try:
            df = fetch_fcf(ticker)
            df_forecasted = forecast_fcf_interface(df, method="growth", periods=5, freq="YE")
            wacc = calculate_wacc(ticker)
            terminal_value = calculate_present_terminal_value(df_forecasted, wacc, g)

            results.append({
                "ticker": ticker,
                "terminal_value": terminal_value
            })

            print(f"{ticker} - Terminal Value (discounted to present): {terminal_value:,.2f}")
        except:
            print(f"{ticker} - Terminal Value not found")
    # Convert results to DataFrame
    terminal_value_df = pd.DataFrame(results)
    print("\n=== Terminal Value DataFrame ===")
    print(terminal_value_df)
