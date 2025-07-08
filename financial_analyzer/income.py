import logging
from financial_analyzer.logging_config import setup_logging
import json

logger = setup_logging()


class IncomeStatement:
    """Handles income statement calculations for public and private companies."""

    def __init__(self):
        """
        Initialize income statement attributes with None.
        """
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
        logger.info("IncomeStatement initialized")

    def calculate_gross_profit(self):
        """
        Calculate gross profit as revenue minus cost of goods sold (COGS).

        Raises:
            ValueError: If revenue or COGS is None.
        """
        if self.revenue is None:
            logger.error("Missing revenue data")
            raise ValueError("Revenue cannot be None")
        elif self.cogs is None:
            logger.error("Missing COGS data")
            raise ValueError("COGS cannot be None")
        else:
            self.gross_profit = self.revenue - self.cogs
            logger.info(f"Gross profit calculated: {self.gross_profit}")

    def calculate_ebitda(self):
        """
        Calculate EBITDA as gross profit minus operating expenses.

        Raises:
            ValueError: If gross_profit or operating_expenses is None.
        """
        if self.gross_profit is None:
            logger.error("Missing gross profit data")
            raise ValueError("Gross profit cannot be None")
        elif self.operating_expenses is None:
            logger.error("Missing operating expenses data")
            raise ValueError("Operating expenses cannot be None")
        else:
            self.ebitda = self.gross_profit - self.operating_expenses
            logger.info(f"EBITDA calculated: {self.ebitda}")

    def calculate_ebit(self):
        """
        Calculate EBIT as EBITDA minus depreciation and amortization.

        Raises:
            ValueError: If ebitda or D_and_A is None.
        """
        if self.ebitda is None:
            logger.error("Missing EBITDA data")
            raise ValueError("EBITDA cannot be None")
        elif self.D_and_A is None:
            logger.error("Missing depreciation and amortization data")
            raise ValueError("Depreciation and amortization cannot be None")
        else:
            self.ebit = self.ebitda - self.D_and_A
            logger.info(f"EBIT calculated: {self.ebit}")

    def calculate_ebt(self):
        """
        Calculate EBT as EBIT minus interest expenses.

        Raises:
            ValueError: If ebit or interest_expenses is None.
        """
        if self.ebit is None:
            logger.error("Missing EBIT data")
            raise ValueError("EBIT cannot be None")
        elif self.interest_expenses is None:
            logger.error("Missing interest expenses data")
            raise ValueError("Interest expenses cannot be None")
        else:
            self.ebt = self.ebit - self.interest_expenses
            logger.info(f"EBT calculated: {self.ebt}")

    def calculate_net_income(self):
        """
        Calculate net income as EBT minus taxes.

        Raises:
            ValueError: If ebt or taxes is None.
        """
        if self.ebt is None:
            logger.error("Missing EBT data")
            raise ValueError("EBT cannot be None")
        elif self.taxes is None:
            logger.error("Missing taxes data")
            raise ValueError("Taxes cannot be None")
        else:
            self.net_income = self.ebt - self.taxes
            logger.info(f"Net income calculated: {self.net_income}")


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
        logger.info("Income statement converted to dictionary")
        return income_statement_dict

    def to_json(self):
        """
        Return a JSON string representation of all income statement properties and their values.

        Returns:
            str: JSON-formatted string of income statement data.
        """
        try:
            income_statement_json = json.dumps(self.to_dict(), indent=4)
            logger.info("Income statement converted to JSON")
            return income_statement_json
        except Exception as e:
            logger.error(f"Error converting income statement to JSON: {e}")
            raise


