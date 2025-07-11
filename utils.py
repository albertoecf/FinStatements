from models.discounted_cash_flow import CashFlowEntry
from typing import List
import pandas as pd
import settings


def forecast_fcf(projections: List[CashFlowEntry], forecast_years: int = 5) -> List[CashFlowEntry]:
    """
    Forecast future free cash flows based on historical growth rate.

    Args:
        projections (List[CashFlowEntry]): Historical FCF data.
        forecast_years (int): Number of future years to forecast.

    Returns:
        List[CashFlowEntry]: Historical + forecasted FCF projections.
    """
    # Convert to DataFrame
    df = pd.DataFrame([{"year": p.year, "fcf": p.free_cash_flow} for p in projections])
    df = df.sort_values("year").reset_index(drop=True)

    # Calculate year-over-year growth rate
    df["growth"] = df["fcf"].pct_change()

    # Calculate FCF in millions of USD
    df["fcf_million_usd"] = df["fcf"] / 1_000_000

    # Calculate average growth rate (excluding first NaN)
    avg_growth = df["growth"][1:].mean()

    # Prepare forecast starting from the last known year and FCF
    last_year = df["year"].iloc[-1]
    last_fcf = df["fcf"].iloc[-1]

    # Forecast future years and append to DataFrame
    forecast_rows = []
    for i in range(1, forecast_years + 1):
        next_year = last_year + i
        next_fcf = last_fcf * (1 + avg_growth)
        forecast_rows.append({
            "year": next_year,
            "fcf": next_fcf,
            "growth": avg_growth,
            "fcf_million_usd": next_fcf / 1_000_000
        })
        last_fcf = next_fcf  # update base for next iteration

    # Append forecast rows to df
    forecast_df = pd.DataFrame(forecast_rows)
    df_final = pd.concat([df, forecast_df], ignore_index=True)

    # todo: Should we include the company name?
    # Log the final DataFrame
    # settings.logger.info("Forecast FCF DataFrame:\n%s", df_final.to_string(index=False))

    # Convert forecast rows to CashFlowEntry objects
    forecast = [
        CashFlowEntry(year=row["year"], free_cash_flow=row["fcf"])
        for row in forecast_rows
    ]

    return forecast
