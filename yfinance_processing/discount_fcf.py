import pandas as pd

def discount_fcfs(df_forecasted: pd.DataFrame, wacc: float) -> pd.DataFrame:
    """
    Discounts forecasted FCFFs using the provided WACC.

    Args:
        df_forecasted (pd.DataFrame): DataFrame with 'date' and 'fcff' columns.
        wacc (float): Weighted Average Cost of Capital as a decimal (e.g. 0.12 for 12%).

    Returns:
        pd.DataFrame: Original dataframe with an added 'discounted_fcf' column.
    """
    df = df_forecasted.copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Calculate t = year difference from the first date
    df['t'] = (df['date'].dt.year - df['date'].dt.year.min()) + 1

    # Calculate discounted FCF
    df['discounted_fcf'] = df['fcff'] / ((1 + wacc) ** df['t'])

    return df

def calculate_npv_from_discounted(df: pd.DataFrame) -> float:
    """
    Calculates the Net Present Value (NPV) by summing the discounted free cash flows.

    Args:
        df (pd.DataFrame): DataFrame containing a 'discounted_fcf' column.

    Returns:
        float: The Net Present Value (NPV).
    """
    if 'discounted_fcf' not in df.columns:
        raise ValueError("DataFrame must contain a 'discounted_fcf' column.")

    npv = df['discounted_fcf'].sum()
    return npv

