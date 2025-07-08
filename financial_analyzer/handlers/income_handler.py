from financial_analyzer.income import IncomeStatement
import logging

logger = logging.getLogger(__name__)


def prompt_float_input(prompt_text, default_value):
    while True:
        try:
            user_input = input(f"{prompt_text} [default: {default_value}]: ") or str(default_value)
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a number.")


def handle_private_income_statement():
    """Handle income statement input and calculation for private companies."""
    income = IncomeStatement()
    income.revenue = prompt_float_input("Enter revenue", 100000)
    income.cogs = prompt_float_input("Enter COGS", 40000)
    income.operating_expenses = prompt_float_input("Enter operating expenses", 20000)
    income.D_and_A = prompt_float_input("Enter depreciation and amortization", 5000)
    income.interest_expenses = prompt_float_input("Enter interest expenses", 3000)
    income.taxes = prompt_float_input("Enter taxes", 8000)

    # Perform calculations
    income.calculate_gross_profit()
    income.calculate_ebitda()
    income.calculate_ebit()
    income.calculate_ebt()
    income.calculate_net_income()

    # Display results
    print("\n=== Income Statement Summary ===")
    for key, value in income.to_dict().items():
        print(f"{key}: {value}")
