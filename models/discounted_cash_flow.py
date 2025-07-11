from pydantic import BaseModel, Field
from typing import Optional, List


class CashFlowEntry(BaseModel):
    """
    Represents an individual year's projected free cash flow.
    """
    year: int
    free_cash_flow: float


class DiscountedCashFlow(BaseModel):
    """
    Represents a Discounted Cash Flow (DCF) valuation model.
    """

    company_symbol: Optional[str] = Field(..., description="Symbol of the company")
    company_name: Optional[str] = None
    discount_rate: float = Field(..., description="Discount rate used for DCF (e.g. WACC)")
    terminal_growth_rate: float = Field(..., description="Terminal growth rate after projection period")
    projections: List[CashFlowEntry] = Field(..., description="Projected free cash flows per year")
    terminal_value: Optional[float] = Field(None, description="Calculated terminal value")
    enterprise_value: Optional[float] = Field(None, description="Final enterprise value from DCF calculation")

    def calculate_terminal_value(self):
        """
        Calculate terminal value using the Gordon Growth Model.
        """
        if not self.projections:
            raise ValueError("No cash flow projections provided.")

        last_fcf = self.projections[-1].free_cash_flow
        # The discount rate must always be greater than the terminal growth rate.
        if self.discount_rate < self.terminal_growth_rate:
            raise ValueError("Discount rate must be greater than terminal growth rate.")
        self.terminal_value = (last_fcf * (1 + self.terminal_growth_rate)) / (
                self.discount_rate - self.terminal_growth_rate)

    def calculate_enterprise_value(self):
        """
        Calculate total enterprise value as sum of discounted cash flows plus discounted terminal value.
        """
        discounted_sum = 0
        for i, proj in enumerate(self.projections, start=1):
            discounted = proj.free_cash_flow / ((1 + self.discount_rate) ** i)
            discounted_sum += discounted

        if self.terminal_value is None:
            self.calculate_terminal_value()

        discounted_terminal = self.terminal_value / ((1 + self.discount_rate) ** len(self.projections))
        self.enterprise_value = discounted_sum + discounted_terminal

    def to_dict(self):
        """
        Convert DCF model data into a dictionary.
        """
        return self.dict()

    def to_json(self):
        """
        Return a JSON-compatible dict for output or logging.
        """
        return self.dict()
