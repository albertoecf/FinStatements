import yfinance as yf
from typing import Union
import settings
from datetime import datetime
import os
import pickle


def get_risk_free_rate() -> float:
    """
    Retrieves the current 10-year US Treasury yield as risk-free rate,
    using a daily local cache to avoid unnecessary API calls.

    Returns:
        float: Risk-free rate as decimal (e.g. 0.045 for 4.5%)
    """
    cache_file = "rf_cache.pkl"
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            cache = pickle.load(f)
            if cache.get("date") == today:
                settings.logger.info(f"[Risk-Free Rate] Using cached value for {today}: {cache['rf']:.4%}")
                return cache["rf"]

    settings.logger.info(f"[Risk-Free Rate] Fetching new value from Yahoo Finance for {today}")
    ten_year = yf.Ticker("^TNX")
    rf = ten_year.history(period="1d")["Close"].iloc[-1] / 100

    with open(cache_file, "wb") as f:
        pickle.dump({"date": today, "rf": rf}, f)

    settings.logger.info(f"[Risk-Free Rate] Fetched and cached new value: {rf:.4%}")
    return rf


def get_beta(ticker: str) -> Union[float, None]:
    """
    Fetches the beta value for a given ticker.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        float: Beta value if available, else None.
    """
    stock = yf.Ticker(ticker)
    beta = stock.info.get("beta", None)
    return beta


def get_market_return(years: int = 10) -> float:
    """
    Estimates the market return using historical S&P500 returns.

    Args:
        years (int): Number of years to look back.

    Returns:
        float: Estimated annualized market return as decimal.
    """
    sp500 = yf.Ticker("^GSPC")
    hist = sp500.history(period=f"{years}y", interval="1mo")
    hist["returns"] = hist["Close"].pct_change()
    Rm = hist["returns"].mean() * 12  # Annualize monthly returns
    return Rm


def get_cost_of_equity(ticker: str) -> float:
    """
    Calculates the cost of equity using CAPM formula:
        cost_of_equity = Rf + Beta * (Rm - Rf)

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        float: Cost of equity as a decimal (e.g., 0.08 for 8%)
    """
    rf = get_risk_free_rate()
    beta = get_beta(ticker)
    Rm = get_market_return()

    if beta is None:
        raise ValueError(f"Beta not available for ticker: {ticker}")

    cost_of_equity = rf + beta * (Rm - rf)
    return cost_of_equity


if __name__ == "__main__":
    ticker_input = "MSFT"
    ticker_list = ["MSFT", "AAPL", "MELI"]
    for ticker in ticker_list:
        try:
            coe = get_cost_of_equity(ticker_input)
            print(f"Cost of Equity for {ticker_input}: {coe:.2%}")
        except ValueError as e:
            print(e)
