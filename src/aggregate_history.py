import pandas as pd
import numpy as np

def aggregate_speeds(history_df):
    """
    Input: history_df with columns:
        Track, Race_Date, Race_No, Box, Dog_Name,
        Hist_Distance, Hist_Race_Time, Hist_Speed_km/h, Data_Source_File

    Output:
        speed_agg: dict keyed by (Track, Race_Date, Race_No, Box, Dog_Name)
        with fields required in SUMMARY_COLUMNS:
            - Avg_Speed_km/h
            - Min_Speed_km/h
            - Max_Speed_km/h
            - Hist_Count
    """

    if history_df is None or len(history_df) == 0:
        return {}

    # Ensure numeric
    df = history_df.copy()
    df["Hist_Speed_km/h"] = pd.to_numeric(df["Hist_Speed_km/h"], errors="coerce")

    # Group key
    key_cols = ["Track", "Race_Date", "Race_No", "Box", "Dog_Name"]

    speed_agg = {}

    for key, group in df.groupby(key_cols):
        speeds = group["Hist_Speed_km/h"].dropna()

        if len(speeds) == 0:
            avg_speed = np.nan
            min_speed = np.nan
            max_speed = np.nan
        else:
            avg_speed = speeds.mean()
            min_speed = speeds.min()
            max_speed = speeds.max()

        # EXACT names for SUMMARY_COLUMNS
        speed_agg[key] = {
            "Avg_Speed_km/h": avg_speed,
            "Min_Speed_km/h": min_speed,
            "Max_Speed_km/h": max_speed,
            "Hist_Count": len(group),
        }

    return speed_agg
