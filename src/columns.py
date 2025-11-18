"""
Locked 60-column schema for Dog Summary and History Snapshot.
Updated to place the first five columns in this exact order:

1. Race_Date
2. Track
3. Race_No
4. Dog_Name
5. Box
"""

SUMMARY_COLUMNS = [
    # --- Updated start order (LOCKED) ---
    "Race_Date",           # 1
    "Track",               # 2
    "Race_No",             # 3
    "Dog_Name",            # 4
    "Box",                 # 5

    # --- Group A – Dog Identification / Current Race ---
    "Tab_No",              # 6
    "FF_Form",             # 7
    "BP",                  # 8
    "A/S",                 # 9
    "WT (kg)",             # 10
    "Trainer",             # 11
    "Sire",                # 12
    "Dam",                 # 13
    "Owner",               # 14

    # --- Group B – Career/Aggregates ---
    "Career_W-P-S",        # 15
    "Prize_Money",         # 16
    "RTC",                 # 17
    "DLR",                 # 18
    "DLW",                 # 19
    "Car_PM/s (G1)",       # 20
    "12m_PM/s (G2)",       # 21
    "API (G3)",            # 22
    "RTC/km",              # 23
    "Trainer_Win_%",       # 24
    "Trainer_Place_%",     # 25
    "Raced_Dist_W-P-S",    # 26
    "Crs_W-P-S",           # 27
    "Dist_W-P-S",          # 28
    "FU_W-P-S",            # 29
    "2U_W-P-S",            # 30
    "DOD",                 # 31

    # --- Group B – Speed Aggregation (computed) ---
    "Avg_Speed_km/h",      # 32
    "Min_Speed_km/h",      # 33
    "Max_Speed_km/h",      # 34
    "Hist_Count",          # 35

    # --- Group C – Most Recent Run Snapshot ---
    "Hist_Date",            # 36
    "Hist_Track",           # 37
    "Hist_Distance",        # 38
    "Hist_Finish_Pos",      # 39
    "Hist_Margin_L",        # 40
    "Hist_Race_Time",       # 41
    "Hist_Sec_Time",        # 42
    "Hist_Sec_Time_Adj",    # 43
    "Hist_Speed_km/h",      # 44
    "Hist_SOT",             # 45
    "Hist_RST",             # 46
    "Hist_BP",              # 47
    "Hist_Odds",            # 48
    "Hist_API",             # 49
    "Hist_Prize_Won",       # 50
    "Hist_Winner",          # 51
    "Hist_2nd_Place",       # 52
    "Hist_3rd_Place",       # 53
    "Hist_Settled_Turn",    # 54
    "Hist_Ongoing_Winners", # 55
    "Hist_Track_Direction", # 56

    # --- Metadata ---
    "Data_Source_File",     # 57
    "Parse_Timestamp",      # 58
]

# History rows get their own schema (matching parse_history.py)
HISTORY_COLUMNS = [
    "Track",
    "Race_Date",
    "Race_No",
    "Dog_Name",
    "Box",
    "Hist_Date",
    "Hist_Track",
    "Hist_Distance",
    "Hist_Finish_Pos",
    "Hist_Margin_L",
    "Hist_Race_Time",
    "Hist_Sec_Time",
    "Hist_Sec_Time_Adj",
    "Hist_Speed_km/h",
    "Hist_SOT",
    "Hist_RST",
    "Hist_BP",
    "Hist_Odds",
    "Hist_API",
    "Hist_Prize_Won",
    "Hist_Winner",
    "Hist_2nd_Place",
    "Hist_3rd_Place",
    "Hist_Settled_Turn",
    "Hist_Ongoing_Winners",
    "Hist_Track_Direction",
    "Data_Source_File",
]
