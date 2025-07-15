

# this function will accept a df and return the forecast based on the forecasting approach

import pandas as pd
from prophet_forecast import forecast_fcff
from company_growth import forecast_fcf_using_growth
from linear_forecast import linear_forecast_fcff

def forecast_fcf_interface(df: pd.DataFrame, method: str = "growth", periods: int = 5, freq: str = "Y") -> pd.DataFrame:
    """
    Forecasts Free Cash Flow using the specified method.

    :param df: DataFrame with columns ['date', 'fcf']
    :param method: Forecasting method. Options: "growth", "linear", "prophet"
    :param periods: Number of future periods to forecast
    :param freq: Frequency of future periods. Default is yearly ('Y')
    :return: DataFrame with columns ['date', 'fcf'] including forecasted values
    """

    if method == "growth":
        forecast_df = forecast_fcf_using_growth(df, periods, freq)
    elif method == "linear":
        forecast_df = linear_forecast_fcff(df, periods, freq)
    elif method == "prophet":
        forecast_df = forecast_fcff(df, periods, freq)
    else:
        raise ValueError(f"Invalid method '{method}'. Choose from 'growth', 'linear', 'prophet'.")

    return forecast_df

