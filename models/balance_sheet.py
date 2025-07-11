from pydantic import BaseModel, Field
from typing import Optional
from models.company import Company


class BalanceSheet(BaseModel):
    """
    Represents a company's balance sheet with key financial position data.
    """

    company: Company

    # Assets
    cash_and_equivalents: Optional[float] = Field(None, description="Cash and short-term investments")
    short_term_investments: Optional[float] = Field(None, description="Short-term investments")
    net_receivables: Optional[float] = Field(None, description="Net receivables")
    inventory: Optional[float] = Field(None, description="Inventory")
    total_current_assets: Optional[float] = Field(None, description="Total current assets")
    property_plant_equipment: Optional[float] = Field(None, description="Property, plant & equipment")
    total_assets: Optional[float] = Field(None, description="Total assets")

    # Liabilities
    accounts_payable: Optional[float] = Field(None, description="Accounts payable")
    short_term_debt: Optional[float] = Field(None, description="Short-term debt")
    total_current_liabilities: Optional[float] = Field(None, description="Total current liabilities")
    long_term_debt: Optional[float] = Field(None, description="Long-term debt")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities")

    # Equity
    common_stock: Optional[float] = Field(None, description="Common stock value")
    retained_earnings: Optional[float] = Field(None, description="Retained earnings")
    total_equity: Optional[float] = Field(None, description="Total stockholders' equity")

    # Other
    fiscal_date_ending: Optional[str] = Field(None, description="Date of the balance sheet")

    def to_dict(self):
        """
        Convert balance sheet data into a dictionary.
        """
        return self.dict()

    def to_json(self):
        """
        Return a JSON-compatible dict with company and balance sheet data.
        """
        return {
            "company": self.company.dict(),
            "balance_sheet": self.dict(exclude={"company"})
        }
