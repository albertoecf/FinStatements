from sec_processing.equity_value import get_market_equity_value
from sec_processing.tc_comparison import main as get_tc
from sec_processing.debt_value import main as get_debt

ticker = "GOOG"

equity = get_market_equity_value(ticker)
tc = get_tc([ticker])
debt = get_debt([ticker])

print(f'equity: {equity}, tc: {tc}, debt: {debt}')