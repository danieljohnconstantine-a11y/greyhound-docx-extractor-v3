# Locked schema: 58 Dog_Summary columns in exact order
SUMMARY_COLUMNS = [
    # Meeting metadata
    "Track",                # 1
    "Race_Date",            # 2 (YYYY-MM-DD preferred)
    "Race_No",              # 3
    "Distance_m",           # 4
    "Race_Name",            # 5
    "Grade",                # 6
    "PrizeMoney",           # 7
    "Weather",              # 8
    "Track_Condition",      # 9
    "Meeting_Notes",        # 10

    # Dog entry core
    "Box",                  # 11
    "Dog_Name",             # 12
    "Tab_No",               # 13
    "Trainer",              # 14
    "Owner",                # 15
    "Sex",                  # 16
    "Color",                # 17
    "Whelped",              # 18
    "Age_Months",           # 19
    "Sire",                 # 20
    "Dam",                  # 21
    "Starting_Price",       # 22
    "Odds",                 # 23
    "Scratched",            # 24
    "Reserve",              # 25
    "Weight_kg",            # 26
    "Run_No",               # 27
    "FF_Form",              # 28

    # Career and track/distance stats
    "Career_Starts",        # 29
    "Career_Wins",          # 30
    "Career_Seconds",       # 31
    "Career_Thirds",        # 32
    "Career_Prizemoney",    # 33
    "Career_BestTime",      # 34
    "ThisTrack_Starts",     # 35
    "ThisTrack_Wins",       # 36
    "ThisTrack_BestTime",   # 37
    "ThisDistance_Starts",  # 38
    "ThisDistance_Wins",    # 39
    "ThisDistance_BestTime",# 40

    # Sectionals / ratings
    "FirstSplit_s",         # 41
    "SecondSplit_s",        # 42
    "RunHome_s",            # 43
    "EarlySpeedRating",     # 44
    "Comments",             # 45
    "Trainer_Recent_Form",  # 46

    # Last run snapshot
    "Last_Run_Date",        # 47
    "Last_Run_Track",       # 48
    "Last_Run_Distance_m",  # 49
    "Last_Run_Box",         # 50
    "Last_Run_Time_s",      # 51
    "Last_Run_Position",    # 52
    "Last_Run_Margin_Lens", # 53
    "Last_Run_Comments",    # 54

    # Aggregates from history
    "Hist_Count",           # 55
    "Avg_Speed_km_h",       # 56
    "Min_Speed_km_h",       # 57
    "Max_Speed_km_h",       # 58
]

# Dedupe keys for Dog_Summary
DEDUPE_KEYS = ("Track", "Race_Date", "Race_No", "Box", "Dog_Name")

# Race history sheet columns (not constrained to 58; flexible and separate)
HISTORY_COLUMNS = [
    "Track",
    "Race_Date",
    "Race_No",
    "Race_Name",
    "Grade",
    "Distance_m",
    "Dog_Name",
    "Box",
    "Tab_No",
    "Trainer",
    "Time_s",
    "Speed_km_h",
    "Position",
    "Margin_Lens",
    "Field_Size",
    "Starting_Price",
    "Odds",
    "Sectional1_s",
    "Sectional2_s",
    "RunHome_s",
    "Weight_kg",
    "Comments",
    "Source_File",
]
