import pandas as pd
from prophet import Prophet

def forecast_fcff(df: pd.DataFrame, periods: int = 5, freq: str = "Y") -> pd.DataFrame:
    """
    Forecast future Free Cash Flow to Firm (FCFF) using Facebook Prophet.

    :param df: pandas DataFrame with columns ['date', 'fcff']
    :param periods: number of future periods to forecast
    :param freq: frequency for future periods (e.g., 'Y' for yearly, 'Q' for quarterly)
    :return: forecast DataFrame with columns ['date', 'fcff']
    """
    # Prepare data for Prophet
    df_prophet = df.rename(columns={"date": "ds", "fcff": "y"})
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
    df_prophet['y'] = df_prophet['y'].astype(float)

    # Initialize and fit Prophet model
    m = Prophet()
    m.fit(df_prophet)

    # Make future dataframe
    future = m.make_future_dataframe(periods=periods, freq=freq)

    # Forecast
    forecast = m.predict(future)

    # Return with original naming convention
    forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'fcff'})

    return forecast_df

if __name__ == "__main__":
    from fetch_fcf import fetch_fcf

    fcff_df = fetch_fcf("MSFT", period="annual")
    forecast_df = forecast_fcff(fcff_df, periods=5, freq='Y')
    print(forecast_df)
