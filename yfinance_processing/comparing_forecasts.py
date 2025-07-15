import pandas as pd
from settings import sp500_tickers
from fetch_fcf import fetch_fcf
from fcf_forecast import forecast_fcf_interface


def compare_forecast_methods(tickers: list[str], periods: int = 5, freq: str = "YE") -> pd.DataFrame:
    """
    For each ticker, forecast FCFF using linear, growth, and prophet methods,
    and return a combined DataFrame for comparison.

    :param tickers: List of ticker symbols.
    :param periods: Number of forecast periods.
    :param freq: Frequency string (e.g. 'Y' for yearly).
    :return: pd.DataFrame with ['ticker', 'date', 'fcff_linear', 'fcff_growth', 'fcff_prophet']
    """
    results = []

    for ticker in tickers:
        try:
            df = fetch_fcf(ticker)

            # Forecast using each method
            df_linear = forecast_fcf_interface(df, method="linear", periods=periods, freq=freq)
            df_growth = forecast_fcf_interface(df, method="growth", periods=periods, freq=freq)
            df_prophet = forecast_fcf_interface(df, method="prophet", periods=periods, freq=freq)

            # Rename fcff columns to reflect approach
            df_linear = df_linear.rename(columns={'fcff': 'fcff_linear'})
            df_growth = df_growth.rename(columns={'fcff': 'fcff_growth'})
            df_prophet = df_prophet.rename(columns={'fcff': 'fcff_prophet'})

            # Merge all forecasts on date
            df_merged = df_linear.merge(df_growth, on='date', how='outer')
            df_merged = df_merged.merge(df_prophet, on='date', how='outer')

            # Add ticker column
            df_merged['ticker'] = ticker

            # Reorder columns
            df_merged = df_merged[['ticker', 'date', 'fcff_linear', 'fcff_growth', 'fcff_prophet']]

            results.append(df_merged)

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    # Combine all tickers into a single DataFrame
    combined_df = pd.concat(results, ignore_index=True)

    return combined_df


if __name__ == "__main__":
    df_forecasts = compare_forecast_methods(sp500_tickers, periods=5, freq='YE')
    print(df_forecasts.head(1000))
