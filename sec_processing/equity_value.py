import yfinance as yf


def get_market_equity_value(ticker):
    """
    Fetches number of shares outstanding and current price
    to calculate market capitalization.

    :param ticker: Stock ticker symbol (str)
    :return: market equity value in USD (float)
    """
    try:
        stock = yf.Ticker(ticker)

        # Fetch shares outstanding
        shares_outstanding = stock.info.get("sharesOutstanding")
        if shares_outstanding is None:
            raise ValueError("Shares outstanding not found")

        # Fetch current price
        current_price = stock.info.get("currentPrice")
        if current_price is None:
            raise ValueError("Current price not found")

        # Calculate market cap / equity value
        market_equity_value = shares_outstanding * current_price

        return market_equity_value

    except Exception as e:
        print(f"Error fetching market equity value for {ticker}: {e}")
        return None


# Example usage
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
for ticker in tickers:
    equity_value = get_market_equity_value(ticker)
    print(f"{ticker} Market Equity Value: ${equity_value:,.2f}")
