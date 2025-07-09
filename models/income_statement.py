import json
import settings
from models.company import Company
from data_fetchers.income_statement_fetcher import FMPFetcher


class IncomeStatement:
    """Handles income statement calculations for public and private companies."""

    def __init__(self, company: Company):
        """
        Initialize income statement attributes with None.
        """

        self.company = company
        self.revenue: float = None
        self.cogs: float = None
        self.gross_profit: float = None
        self.operating_expenses: float = None
        self.ebitda: float = None
        self.D_and_A: float = None
        self.ebit: float = None
        self.interest_expenses: float = None
        self.ebt: float = None
        self.taxes: float = None
        self.net_income: float = None
        settings.logger.info("IncomeStatement initialized")

    def calculate_gross_profit(self):
        """
        Calculate gross profit as revenue minus cost of goods sold (COGS).

        Raises:
            ValueError: If revenue or COGS is None.
        """
        if self.revenue is None:
            settings.logger.error("Missing revenue data")
            raise ValueError("Revenue cannot be None")
        elif self.cogs is None:
            settings.logger.error("Missing COGS data")
            raise ValueError("COGS cannot be None")
        else:
            self.gross_profit = self.revenue - self.cogs

    def calculate_ebitda(self):
        """
        Calculate EBITDA as gross profit minus operating expenses.

        Raises:
            ValueError: If gross_profit or operating_expenses is None.
        """
        if self.gross_profit is None:
            settings.logger.error("Missing gross profit data")
            raise ValueError("Gross profit cannot be None")
        elif self.operating_expenses is None:
            settings.logger.error("Missing operating expenses data")
            raise ValueError("Operating expenses cannot be None")
        else:
            self.ebitda = self.gross_profit - self.operating_expenses

    def calculate_ebit(self):
        """
        Calculate EBIT as EBITDA minus depreciation and amortization.

        Raises:
            ValueError: If ebitda or D_and_A is None.
        """
        if self.ebitda is None:
            settings.logger.error("Missing EBITDA data")
            raise ValueError("EBITDA cannot be None")
        elif self.D_and_A is None:
            settings.logger.error("Missing depreciation and amortization data")
            raise ValueError("Depreciation and amortization cannot be None")
        else:
            self.ebit = self.ebitda - self.D_and_A

    def calculate_ebt(self):
        """
        Calculate EBT as EBIT minus interest expenses.

        Raises:
            ValueError: If ebit or interest_expenses is None.
        """
        if self.ebit is None:
            settings.logger.error("Missing EBIT data")
            raise ValueError("EBIT cannot be None")
        elif self.interest_expenses is None:
            settings.logger.error("Missing interest expenses data")
            raise ValueError("Interest expenses cannot be None")
        else:
            self.ebt = self.ebit - self.interest_expenses

    def calculate_net_income(self):
        """
        Calculate net income as EBT minus taxes.

        Raises:
            ValueError: If ebt or taxes is None.
        """
        if self.ebt is None:
            settings.logger.error("Missing EBT data")
            raise ValueError("EBT cannot be None")
        elif self.taxes is None:
            settings.logger.error("Missing taxes data")
            raise ValueError("Taxes cannot be None")
        else:
            self.net_income = self.ebt - self.taxes

    def to_dict(self):
        """
        Return a dictionary representation of all income statement properties and their values.

        Returns:
            dict: Key-value pairs of attribute names and their values.
        """
        # Build dictionary dynamically for maintainability
        income_statement_dict = {
            'revenue': self.revenue,
            'cogs': self.cogs,
            'gross_profit': self.gross_profit,
            'operating_expenses': self.operating_expenses,
            'ebitda': self.ebitda,
            'D_and_A': self.D_and_A,
            'ebit': self.ebit,
            'interest_expenses': self.interest_expenses,
            'ebt': self.ebt,
            'taxes': self.taxes,
            'net_income': self.net_income
        }

        return income_statement_dict

    def to_json(self):
        """
        Return a JSON-compatible dict with company and income statement data.
        """
        return {
            "company": {
                "name": self.company.name,
                "symbol": self.company.symbol,
                "stock_market": self.company.stock_market,
                "industry": self.company.industry,
                "is_public": self.company.is_public
            },
            "income_statement": {
                "revenue": self.revenue,
                "cogs": self.cogs,
                "gross_profit": self.gross_profit,
                "operating_expenses": self.operating_expenses,
                "ebitda": self.ebitda,
                "D_and_A": self.D_and_A,
                "ebit": self.ebit,
                "interest_expenses": self.interest_expenses,
                "ebt": self.ebt,
                "taxes": self.taxes,
                "net_income": self.net_income
            }
        }


class PrivateIncomeStatement(IncomeStatement):
    """
    Handles income statements for private companies.
    """

    def __init__(self, company: Company):
        super().__init__(company)


class PublicIncomeStatement(IncomeStatement):
    """
    Handles income statements for public companies by fetching data from FMP.
    """

    def __init__(self, company: Company, income_data: dict):
        super().__init__(company)
        # Populate attributes from income_data dictionary
        self.revenue = income_data.get("revenue")
        self.cogs = income_data.get("costOfRevenue")
        self.gross_profit = income_data.get("grossProfit")
        self.operating_expenses = income_data.get("operatingExpenses")
        self.ebitda = income_data.get("ebitda")
        self.D_and_A = income_data.get("depreciationAndAmortization")
        self.ebit = income_data.get("ebit")
        self.interest_expenses = income_data.get("interestExpense")
        self.ebt = income_data.get("ebt")
        self.taxes = income_data.get("incomeTaxExpense")
        self.net_income = income_data.get("netIncome")


async def create_public_income_statement(company: Company):
    fetcher = FMPFetcher(api_key=settings.FMP_API)
    try:
        income_data = await fetcher.fetch_income_statement(company.symbol)
        return PublicIncomeStatement(company, income_data)
    finally:
        await fetcher.close()


if __name__ == "__main__":
    income = IncomeStatement()

    income.revenue = float(input("Enter revenue: ") or 100000)
    income.cogs = float(input("Enter COGS: ") or 40000)
    income.operating_expenses = float(input("Enter operating expenses: ") or 20000)
    income.D_and_A = float(input("Enter depreciation and amortization: ") or 5000)
    income.interest_expenses = float(input("Enter interest expenses: ") or 3000)
    income.taxes = float(input("Enter taxes: ") or 8000)

    income.calculate_gross_profit()
    income.calculate_ebitda()
    income.calculate_ebit()
    income.calculate_ebt()
    income.calculate_net_income()

    print("\n=== Income Statement Summary ===")
    print(income.to_json())
