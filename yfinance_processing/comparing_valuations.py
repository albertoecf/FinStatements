import pandas as pd
from company_valuation import company_valuation
from market_cap import get_market_cap
from settings import sp500_tickers


def compare_valuations(
        tickers: list[str],
        forecast_method: str = 'growth',
        perpetual_growth_rate: float = 0.02
) -> pd.DataFrame:
    """
    Compare intrinsic valuation vs market cap for a list of tickers.

    Args:
        tickers (list[str]): List of ticker strings.
        forecast_method (str): Forecasting method to use.
        perpetual_growth_rate (float): Perpetual growth rate for terminal value.

    Returns:
        pd.DataFrame: DataFrame with columns:
            ['ticker', 'company_value', 'company_market_cap', 'valuation_status', 'percent_diff']
    """
    results = []

    for ticker in tickers:
        try:
            company_value = company_valuation(ticker, forecast_method, perpetual_growth_rate)
            company_market_cap = get_market_cap(ticker)

            if company_market_cap > company_value:
                valuation_status = "Overrated"
                percent_diff = ((company_market_cap - company_value) / company_value) * 100
            else:
                valuation_status = "Underrated"
                percent_diff = ((company_value - company_market_cap) / company_value) * 100

            results.append({
                "ticker": ticker,
                "company_value": company_value,
                "company_market_cap": company_market_cap,
                "valuation_status": valuation_status,
                "percent_diff": percent_diff
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df_comparison = compare_valuations(sp500_tickers, forecast_method='growth', perpetual_growth_rate=0.02)
    print(df_comparison)
