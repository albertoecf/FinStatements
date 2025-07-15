import yfinance as yf

def get_market_cap(ticker: str) -> float:
    """
    Fetches the current market capitalization of a company using yfinance.

    Args:
        ticker (str): Ticker symbol of the company.

    Returns:
        float: Market capitalization in dollars.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    market_cap = info.get("marketCap", None)
    return market_cap

if __name__ == "__main__":
    from settings import sp500_tickers
    for ticker in sp500_tickers:
        market_cap = get_market_cap(ticker)
        print(f'{ticker} s market_cap: {market_cap}')