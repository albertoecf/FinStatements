import pandas as pd
from settings import logger


def fcf_growth(df_: pd.DataFrame) -> float:
    """
    Calculates the average annual growth rate of FCF.

    Args:
        df_ (pd.DataFrame): DataFrame with columns 'date' and 'fcff'.

    Returns:
        float: Average growth rate as a decimal (e.g. 0.12 for 12%).
    """
    df_ = df_.copy()
    try:
        df_ = df_.sort_values("date")
    except KeyError:
        logger.error("No 'date' column found in DataFrame.")

    # Calculate period-over-period growth
    try:
        df_["fcff_growth"] = df_["fcff"].pct_change()
    except KeyError:
        logger.error("No 'fcff' column found in DataFrame.")

    # Calculate the average growth rate excluding NaN
    avg_growth = df_["fcff_growth"].mean()

    return avg_growth


def forecast_fcf_using_growth(df_: pd.DataFrame, periods: int = 5, freq: str = 'YE') -> pd.DataFrame:
    """
    Forecasts FCF into the future using the historical average growth rate.

    Args:
        df_ (pd.DataFrame): DataFrame with columns 'date' and 'fcff'.
        periods (int): Number of periods to forecast.
        freq (str): Frequency string compatible with pandas date_range (e.g., 'Y', 'Q').

    Returns:
        pd.DataFrame: DataFrame with forecasted 'date' and 'fcff' including historical + forecast.
    """
    avg_growth = fcf_growth(df_)
    df_ = df_.copy()

    # Ensure dates are datetime
    df_['date'] = pd.to_datetime(df_['date'])

    last_date = df_['date'].max()
    last_fcf = df_.loc[df_['date'] == last_date, 'fcff'].values[0]

    # Shift start date by 1 period to avoid duplicating last_date
    forecast_dates = pd.date_range(start=last_date + pd.tseries.frequencies.to_offset(freq),
                                   periods=periods,
                                   freq=freq)

    forecast_fcfs = []
    current_fcf = last_fcf
    for _ in range(periods):
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

    df = fetch_fcf("GOOG")
    df.rename(columns={'date': 'date', 'fcf': 'fcff'}, inplace=True)

    print(f"Average Growth: {fcf_growth(df):.2%}")
    forecasted_df = forecast_fcf_using_growth(df, periods=5, freq='YE')
    print(forecasted_df)
