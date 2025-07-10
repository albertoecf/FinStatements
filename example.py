import yfinance as yf

# Define your symbol, e.g., Apple Inc.
symbol = "AAPL"

# Create a Ticker object
ticker = yf.Ticker(symbol)

# ===== Income Statement =====
income_statement = ticker.financials
print(f"=== Income Statement for {symbol} ===")
print(income_statement)

# ===== Balance Sheet =====
balance_sheet = ticker.balance_sheet
print(f"\n=== Balance Sheet for {symbol} ===")
print(balance_sheet)

# ===== Cash Flow Statement =====
cash_flow = ticker.cashflow
print(f"\n=== Cash Flow Statement for {symbol} ===")
print(cash_flow)

# ===== Calculate Free Cash Flow =====
# FCF = Operating Cash Flow - Capital Expenditures
