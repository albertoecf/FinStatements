import asyncio
import settings
from models.company import Company, StockMarket
from data_fetchers.FMPFetcher import FMPFetcher
from models.income_statement import PublicIncomeStatement
from models.discounted_cash_flow import DiscountedCashFlow, CashFlowProjection


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


async def fetch_cash_flow_projections(symbol: str, years: int = 5):
    """
    Fetch historical or projected free cash flows for the company.
    """
    fetcher = FMPFetcher(api_key=settings.FMP_API)
    try:
        # Fetch historical cash flows as a proxy for projections.
        data = await fetcher.fetch_cash_flow_statement(symbol, limit=years)
        projections = []
        for entry in reversed(data):  # reverse to get chronological order
            year = int(entry["calendarYear"])
            fcf = entry.get("freeCashFlow") or 0.0
            projections.append(
                CashFlowProjection(year=year, free_cash_flow=fcf)
            )
        return projections
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
        # Enrich company info
        company = await enrich_company_profile(company)

        # Fetch income statement
        income_statement = await create_public_income_statement(company)

        # Fetch free cash flow projections (5 years)
        projections = await fetch_cash_flow_projections(company.symbol)

        # Build and calculate DCF
        dcf_model = DiscountedCashFlow(
            company_name=company.name,
            discount_rate=0.08,  # Example WACC 8%
            terminal_growth_rate=0.025,  # Example 2.5% terminal growth
            projections=projections
        )
        dcf_model.calculate_terminal_value()
        dcf_model.calculate_enterprise_value()

    except Exception as e:
        settings.logger.error(f"Failed to fetch data for {symbol}: {e}")
        return

    # Log outputs
    settings.logger.info(f"Company info: {company.json()}")
    settings.logger.info(f"Income Statement JSON for {symbol}:\n{income_statement.to_json()}")
    settings.logger.info(f"DCF Valuation for {symbol}: {dcf_model.enterprise_value:.2f}")


    try:
        fetcher = FMPFetcher(api_key=settings.FMP_API)
        profile_data = await fetcher.fetch_company_profile("GOOG")
        market_cap = profile_data.get("mktCap")
    except Exception as e:
        market_cap = 20
        settings.logger.error(f"Failed to fetch data for {symbol}: {e}")

    settings.logger.info(f"DCF Valuation for GOOG: ${dcf_model.enterprise_value:,.2f}")
    settings.logger.info(f"Current Market Cap for GOOG: ${market_cap:,.2f}")

    if dcf_model.enterprise_value > market_cap:
        print("Your DCF valuation is higher than market price. GOOG may be undervalued.")
    else:
        print("Your DCF valuation is lower than market price. GOOG may be overvalued or fairly valued.")


if __name__ == "__main__":
    asyncio.run(run_workflow())
