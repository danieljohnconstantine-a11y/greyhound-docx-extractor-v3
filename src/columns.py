# Final 60-column schema (expanded: added Distance_m and Race_Grade)

SUMMARY_COLUMNS = [
    # Group A – Identification & current race context
    "Track",                # 1
    "Race_Date",            # 2
    "Race_No",              # 3
    "Distance_m",           # 4 NEW
    "Race_Grade",           # 5 NEW
    "Box",                  # 6
    "Dog_Name",             # 7
    "Tab_No",               # 8
    "FF_Form",              # 9
    "BP",                   # 10
    "A/S",                  # 11
    "WT (kg)",              # 12
    "Trainer",              # 13
    "Sire",                 # 14
    "Dam",                  # 15
    "Owner",                # 16

    # Group B – Career / aggregated stats
    "Career_W-P-S",         # 17
    "Prize_Money",          # 18
    "RTC",                  # 19
    "DLR",                  # 20
    "DLW",                  # 21
    "Car_PM/s (G1)",        # 22
    "12m_PM/s (G2)",        # 23
    "API (G3)",             # 24
    "RTC/km",               # 25
    "Trainer_Win_%",        # 26
    "Trainer_Place_%",      # 27
    "Raced_Dist_W-P-S",     # 28
    "Crs_W-P-S",            # 29
    "Dist_W-P-S",           # 30
    "FU_W-P-S",             # 31
    "2U_W-P-S",             # 32
    "DOD",                  # 33

    # Group B – Speed aggregation
    "Avg_Speed_km/h",       # 34
    "Min_Speed_km/h",       # 35
    "Max_Speed_km/h",       # 36
    "Hist_Count",           # 37

    # Group C – Most recent run snapshot
    "Hist_Date",            # 38
    "Hist_Track",           # 39
    "Hist_Distance",        # 40
    "Hist_Finish_Pos",      # 41
    "Hist_Margin_L",        # 42
    "Hist_Race_Time",       # 43
    "Hist_Sec_Time",        # 44
    "Hist_Sec_Time_Adj",    # 45
    "Hist_Speed_km/h",      # 46
    "Hist_SOT",             # 47
    "Hist_RST",             # 48
    "Hist_BP",              # 49
    "Hist_Odds",            # 50
    "Hist_API",             # 51
    "Hist_Prize_Won",       # 52
    "Hist_Winner",          # 53
    "Hist_2nd_Place",       # 54
    "Hist_3rd_Place",       # 55
    "Hist_Settled_Turn",    # 56
    "Hist_Ongoing_Winners", # 57
    "Hist_Track_Direction", # 58

    # Metadata
    "Data_Source_File",     # 59
    "Parse_Timestamp",      # 60
]

DEDUPE_KEYS = ("Track", "Race_Date", "Race_No", "Box", "Dog_Name")

# History row schema stays unchanged
HISTORY_COLUMNS = [
    "Track",
    "Race_Date",
    "Race_No",
    "Box",
    "Dog_Name",
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

# Legacy columns remain untouched for compatibility
LEGACY_COLUMNS = []
ALL_COLUMNS = SUMMARY_COLUMNS + LEGACY_COLUMNS
