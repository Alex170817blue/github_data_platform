import pandas as pd


def add_period_columns(df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
   
    dt = pd.to_datetime(df[timestamp_col], utc=True)
    df = df.copy()
    df["week_start"] = dt.dt.to_period("W-MON").dt.start_time.dt.date
    df["month_start"] = dt.dt.to_period("M").dt.start_time.dt.date
    return df