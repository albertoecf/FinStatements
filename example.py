import asyncio
from models.company import Company
from models.income_statement import create_public_income_statement


async def main():
    # Create Company instance for Google
    company = Company(
        name="Alphabet Inc.",
        is_public=True,
        industry="518210",  # Example NAICS code for internet publishing
        symbol="GOOG",
        stock_market="NASDAQ"
    )

    # Fetch income statement and instantiate the class
    public_income_stmt = await create_public_income_statement(company)

    # Output JSON
    print(public_income_stmt.to_json())


if __name__ == "__main__":
    asyncio.run(main())
