import asyncio
import settings
from models.company import Company, StockMarket
from data_fetchers.FMPFetcher import FMPFetcher
from models.income_statement import PublicIncomeStatement


async def create_public_income_statement(company: Company):
    fetcher = FMPFetcher(api_key=settings.FMP_API)
    try:
        income_data = await fetcher.fetch_income_statement(company.symbol)
        return PublicIncomeStatement(company, income_data)
    finally:
        await fetcher.close()


async def enrich_company_profile(company: Company) -> Company:
    if not company.symbol:
        raise ValueError("Company symbol required for profile enrichment")

    fetcher = FMPFetcher(api_key=settings.FMP_API)
    try:
        profile_data = await fetcher.fetch_company_profile(company.symbol)
        company.industry = profile_data.get("industry")
        company.sector = profile_data.get("sector")
        beta_value = profile_data.get("beta")
        company.beta = float(beta_value) if beta_value is not None else None
        company.name = profile_data.get("companyName", company.name)
        return company
    finally:
        await fetcher.close()


async def run_workflow():
    symbol = input("Enter company symbol (default GOOG): ").strip().upper() or "GOOG"

    company = Company(
        name=symbol,
        is_public=True,
        symbol=symbol,
        stock_market=StockMarket.NYSE
    )

    try:
        # First enrich company info with industry, sector, beta from FMP profile
        company = await enrich_company_profile(company)

        # Then fetch the income statement
        income_statement = await create_public_income_statement(company)
    except Exception as e:
        settings.logger.error(f"Failed to fetch data for {symbol}: {e}")
        return

    settings.logger.info(f"Company info: {company.json()}")
    settings.logger.info(f"Income Statement JSON for {symbol}:\n{income_statement.to_json()}")


if __name__ == "__main__":
    asyncio.run(run_workflow())
