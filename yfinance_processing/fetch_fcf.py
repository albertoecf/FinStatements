import yfinance as yf
import pandas as pd


def fetch_fcf(ticker: str, period: str = "annual") -> pd.DataFrame:
    """
    Fetch Free Cash Flow (FCFF) data for a given ticker.

    Parameters:
    - ticker: str, stock ticker symbol
    - period: str, either "annual" or "quarterly"

    Returns:
    - pd.DataFrame with columns ['date', 'fcff']
      where 'date' is the report date and 'fcff' is Free Cash Flow to Firm (Operating CF - CapEx)
    """
    stock = yf.Ticker(ticker)

    if period == "annual":
        cashflow = stock.cashflow
    elif period == "quarterly":
        cashflow = stock.quarterly_cashflow
    else:
        raise ValueError("Period must be 'annual' or 'quarterly'")

    # Defensive: check if necessary rows exist
    required_rows = ['Operating Cash Flow', 'Capital Expenditure']
    for row in required_rows:
        if row not in cashflow.index:
            raise KeyError(f"'{row}' not found in cashflow data for {ticker}")

    # Calculate FCFF
    operating_cf = cashflow.loc['Operating Cash Flow']
    capex = cashflow.loc['Capital Expenditure']

    fcff = operating_cf - capex

    df = pd.DataFrame({
        'date': fcff.index,
        'fcff': fcff.values
    })

    # Option 1: keep datetime64[ns] dtype (recommended)
    df['date'] = pd.to_datetime(df['date'])

    # Option 2: convert to python date object
    # df['date'] = df['date'].apply(lambda x: x.date())

    df = df.sort_values('date').reset_index(drop=True)

    return df


if __name__ == "__main__":
    import settings

    ticker = "MELI"
    period = "quarterly"
    settings.logger.info(f'Fetching {period} Free Cash Flow Data for {ticker}')
    df_annual_fcf = fetch_fcf(ticker, period=period)
    settings.logger.info(df_annual_fcf.head())

    ticker_2 = "GOOG"
    period_2 = "annual"
    settings.logger.info(f'Fetching {period_2} Free Cash Flow Data for {ticker_2}')
    df_quarterly_fcf = fetch_fcf(ticker_2, period="annual")
    settings.logger.info(df_quarterly_fcf.head())

