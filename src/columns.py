# src/columns.py

# List of all columns expected in the race summary output
SUMMARY_COLUMNS = [
    # Meeting-level fields
    "Race_Date", "Race_Time", "Track", "Race_No", "Race_Name",
    "Distance_m", "Race_Grade",
    # Dog-level fields
    "Dog_Name", "Box", "ColourCode", "Sex", "Age",
    "Trainer", "Owner",
    "Career_Wins", "Career_Seconds", "Career_Thirds", "Career_Starters",
    "Win_Percent", "Place_Percent", "Career_PrizeMoney",
    "PrizeMoneyWon", "Odds",
    # (Add additional fields as needed up to 60 total, e.g. race margin, sectional times, etc.)
]

# List of columns for each historical run record
HISTORY_COLUMNS = [
    "Hist_Date", "Hist_Track", "Hist_Distance_m",
    "Hist_Race_Time_s", "Hist_Finish_Pos", "Hist_Prize_Won",
    "Hist_Odds",
    # If needed, also include fields like sectional times, track direction, etc.
]
