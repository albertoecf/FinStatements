import yfinance as yf


def get_risk_free_rate():
    # Por simplicidad usamos el bono 10 años de USA, ticker ^TNX, en porcentaje
    tnx = yf.Ticker("^TNX")
    rf = tnx.history(period="1d")["Close"].iloc[-1] / 100
    return rf


def get_market_return():
    # Estimamos retorno promedio anual del mercado S&P500
    sp500 = yf.Ticker("^GSPC")
    hist = sp500.history(period="10y", interval="1mo")
    hist["returns"] = hist["Close"].pct_change()
    return hist["returns"].mean() * 12  # anualizado


def get_cost_of_equity(ticker):
    stock = yf.Ticker(ticker)
    beta = stock.info.get('beta', None)
    if beta is None:
        raise ValueError("No se encontró beta para este ticker.")
    rf = get_risk_free_rate()
    rm = get_market_return()
    cost_equity = rf + beta * (rm - rf)
    return cost_equity


def get_cost_of_debt(ticker):
    stock = yf.Ticker(ticker)
    fin = stock.financials
    income_stmt = fin.copy()
    # Intentamos obtener el gasto de intereses
    try:
        interest_expense = abs(income_stmt.loc['Interest Expense'].iloc[0])
    except KeyError:
        interest_expense = None

    balance = stock.balance_sheet
    try:
        short_term_debt = balance.loc['Short Long Term Debt'].iloc[0]
    except KeyError:
        short_term_debt = 0
    try:
        long_term_debt = balance.loc['Long Term Debt'].iloc[0]
    except KeyError:
        long_term_debt = 0

    total_debt = short_term_debt + long_term_debt
    if total_debt == 0 or interest_expense is None:
        raise ValueError("No se pudo obtener gasto de intereses o deuda total.")

    cost_debt = interest_expense / total_debt
    return cost_debt


def get_tax_rate(ticker):
    stock = yf.Ticker(ticker)
    income_stmt = stock.financials
    try:
        income_tax_expense = abs(income_stmt.loc['Income Tax Expense'].iloc[0])
        pretax_income = income_stmt.loc['Income Before Tax'].iloc[0]
        tax_rate = income_tax_expense / pretax_income
    except KeyError:
        tax_rate = 0.21  # valor por defecto (ej. tasa corporativa USA)
    return tax_rate


def get_market_value_equity(ticker):
    stock = yf.Ticker(ticker)
    shares_outstanding = stock.info.get('sharesOutstanding', None)
    current_price = stock.info.get('currentPrice', None)
    if shares_outstanding is None or current_price is None:
        raise ValueError("No se pudo obtener datos de mercado de acciones")
    return shares_outstanding * current_price


def get_market_value_debt(ticker):
    # Aquí aproximamos la deuda total del balance (puede no ser valor de mercado exacto)
    stock = yf.Ticker(ticker)
    balance = stock.balance_sheet
    try:
        short_term_debt = balance.loc['Short Long Term Debt'].iloc[0]
    except KeyError:
        short_term_debt = 0
    try:
        long_term_debt = balance.loc['Long Term Debt'].iloc[0]
    except KeyError:
        long_term_debt = 0
    return short_term_debt + long_term_debt


def calculate_wacc(ticker):
    E = get_market_value_equity(ticker)
    D = get_market_value_debt(ticker)
    V = E + D
    Re = get_cost_of_equity(ticker)
    Rd = get_cost_of_debt(ticker)
    Tc = get_tax_rate(ticker)

    wacc = (E / V) * Re + (D / V) * Rd * (1 - Tc)
    return wacc


if __name__ == "__main__":
    tickers = ["MSFT", "JNJ", "HD", "GOOGL", "TSLA", "HD", "JNJ"]
    for ticker in tickers:
        print(ticker)
        wacc = calculate_wacc(ticker)
        print(f"WACC para {ticker}: {wacc:.2%}")
