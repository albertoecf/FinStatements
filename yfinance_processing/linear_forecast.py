import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def linear_forecast_fcff(fcff_df: pd.DataFrame, periods: int, freq: str = "Q"):
    """
    Performs a simple linear projection of FCFF.

    Args:
        fcff_df (pd.DataFrame): DataFrame with columns 'date' and 'fcff'.
        periods (int): Number of future periods to forecast.
        freq (str): Frequency of the forecast (e.g. 'Q' for quarterly, 'A' for annual).

    Returns:
        pd.DataFrame: DataFrame with columns 'date' and 'fcff_forecast' including historical data + forecast.
    """
    # Make a copy to avoid mutating original df
    fcff_df = fcff_df.copy()

    # Ensure 'date' is datetime
    fcff_df['date'] = pd.to_datetime(fcff_df['date'])

    # Drop rows where 'fcff' is NaN
    fcff_df = fcff_df.dropna(subset=['fcff'])

    # Convert dates to ordinal
    fcff_df['date_ordinal'] = fcff_df['date'].map(pd.Timestamp.toordinal)

    # Define X and y for regression
    X = fcff_df['date_ordinal'].values.reshape(-1, 1)
    y = fcff_df['fcff'].values

    # Fit linear model
    model = LinearRegression()
    model.fit(X, y)

    # Future dates for prediction
    last_date = fcff_df['date'].max()
    future_dates = pd.date_range(start=last_date, periods=periods + 1, freq=freq)[1:]
    future_ordinals = future_dates.map(pd.Timestamp.toordinal).values.reshape(-1, 1)

    # Predictions
    fcff_forecast = model.predict(future_ordinals)

    # Forecast DataFrame
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'fcff': fcff_forecast
    })

    # Add historical fcff values as forecast for plotting continuity
    fcff_df['fcff'] = fcff_df['fcff']

    # Combine historical + forecast
    result_df = pd.concat([fcff_df[['date', 'fcff']], forecast_df], ignore_index=True)

    return result_df


if __name__ == '__main__':
    # Example usage:
    # fcff_df = pd.DataFrame({'date': [...], 'fcff': [...]})
    from fetch_fcf import fetch_fcf

    df = fetch_fcf(ticker='AAPL')
    result = linear_forecast_fcff(df, periods=8, freq='Q')
    plt.plot(result['date'], result['fcff_forecast'], label='FCFF Forecast')
    plt.show()
