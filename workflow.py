import asyncio
import settings
from models.company import Company, StockMarket
from models.income_statement import create_public_income_statement


async def run_workflow():
    symbol = input("Enter company symbol (default GOOG): ").strip().upper() or "GOOG"

    # For demo, we create a public company with NYSE as default market.
    # You can enhance input to ask for stock_market if you want.
    company = Company(
        name=symbol,
        is_public=True,
        symbol=symbol,
        stock_market=StockMarket.NYSE
    )

    try:
        income_statement = await create_public_income_statement(company)
    except Exception as e:
        settings.logger.error(f"Failed to fetch income statement for {symbol}: {e}")
        return

    # Log JSON output
    json_output = income_statement.to_json()
    settings.logger.info(f"Income Statement JSON for {symbol}:\n{json_output}")


if __name__ == "__main__":
    asyncio.run(run_workflow())
