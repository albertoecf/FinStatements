import pandas as pd
from settings import logger

def fcf_growth(df_: pd.DataFrame) -> float:
    """
    Calculates the average annual growth rate of FCF.

    Args:
        df_ (pd.DataFrame): DataFrame with columns 'date' and 'fcf'.

    Returns:
        float: Average growth rate as a decimal (e.g. 0.12 for 12%).
    """
    df_ = df_.copy()
    try:
        df_ = df_.sort_values("date")
    except KeyError:
        logger.error("No 'date' column found in DataFrame.")

    # Calculate year-over-year growth
    try:
        df_["fcff_growth"] = df_["fcff"].pct_change()
    except KeyError:
        logger.error("No 'fcff' column found in DataFrame.")

    # Calculate the average growth rate excluding NaN
    avg_growth = df_["fcff_growth"].mean()

    return avg_growth


def forecast_fcf_using_growth(df_: pd.DataFrame) -> pd.DataFrame:
    """
    Forecasts FCF for 5 years into the future using the historical average growth rate.

    Args:
        df_ (pd.DataFrame): DataFrame with columns 'date' and 'fcf'.

    Returns:
        pd.DataFrame: DataFrame with forecasted 'date' and 'fcf' including historical + forecast.
    """
    avg_growth = fcf_growth(df_)
    df_ = df_.copy()

    # Ensure dates are datetime
    df_['date'] = pd.to_datetime(df_['date'])

    last_date = df_['date'].max()
    last_fcf = df_.loc[df_['date'] == last_date, 'fcff'].values[0]

    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(years=1), periods=5, freq='YE')
    forecast_fcfs = []

    current_fcf = last_fcf
    for _ in range(5):
        current_fcf = current_fcf * (1 + avg_growth)
        forecast_fcfs.append(current_fcf)

    forecast_df = pd.DataFrame({
        'date': forecast_dates,
        'fcff': forecast_fcfs
    })

    # Combine historical and forecast data
    combined_df = pd.concat([df_[['date', 'fcff']], forecast_df], ignore_index=True)

    return combined_df


if __name__ == '__main__':
    from fetch_fcf import fetch_fcf

    df = fetch_fcf("MELI")
    df.rename(columns={'date': 'date', 'fcf': 'fcf'}, inplace=True)
    print(fcf_growth(df))
    print(forecast_fcf_using_growth(df))
