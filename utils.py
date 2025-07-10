from models.discounted_cash_flow import CashFlowProjection
from typing import List
import pandas as pd
import settings


def forecast_fcf(projections: List[CashFlowProjection], forecast_years: int = 5) -> List[CashFlowProjection]:
    """
    Forecast future free cash flows based on historical growth rate.

    Args:
        projections (List[CashFlowProjection]): Historical FCF data.
        forecast_years (int): Number of future years to forecast.

    Returns:
        List[CashFlowProjection]: Historical + forecasted FCF projections.
    """
    # Convert to DataFrame
    df = pd.DataFrame([{"year": p.year, "fcf": p.free_cash_flow} for p in projections])
    df = df.sort_values("year").reset_index(drop=True)

    # Calculate year-over-year growth rate
    df["growth"] = df["fcf"].pct_change()

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
        forecast_rows.append({"year": next_year, "fcf": next_fcf, "growth": avg_growth})
        last_fcf = next_fcf  # update base for next iteration

    # Append forecast rows to df
    forecast_df = pd.DataFrame(forecast_rows)
    df_final = pd.concat([df, forecast_df], ignore_index=True)

    # Log the final DataFrame
    settings.logger.info("Forecast FCF DataFrame:\n%s", df_final.to_string(index=False))

    # Convert forecast rows to CashFlowProjection objects
    forecast = [
        CashFlowProjection(year=row["year"], free_cash_flow=row["fcf"])
        for row in forecast_rows
    ]

    return forecast
