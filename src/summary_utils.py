# src/summary_utils.py

import re

COLOUR_MAP = {
    'bl': 'Blue', 'rd': 'Red', 'bk': 'Black', 'w': 'White',
    'w/bl': 'White/Blue', 'bb': 'Blue/Black',
    'fawn': 'Fawn', 'fwn': 'Fawn', 'brn': 'Brown', 'bdl': 'Brindle',
    # Add other mappings as needed
}
SEX_MAP = {'D': 'Dog', 'B': 'Bitch'}

def normalize_summary_fields(record):
    """
    Clean and normalize fields in a single race summary record.
    Returns a new dict with standardized formats.
    """
    norm = {}
    for key, val in record.items():
        if isinstance(val, str):
            val = val.strip()
        # Meeting-level fields
        if key == "Race_Date" and val:
            # Already in YYYY-MM-DD format (if parse applied)
            norm[key] = val
        elif key == "Race_Time" and val:
            # Ensure HH:MM format (24-hour)
            try:
                # Some inputs might be "H:MM" or "HH:MM"
                t = datetime.strptime(val, "%H:%M")
                norm[key] = t.strftime("%H:%M")
            except Exception:
                norm[key] = val
        elif key == "Distance_m" and val != "":
            norm[key] = int(re.sub(r'\D', '', str(val)))
        # Dog-level fields
        elif key in ("Dog_Name", "Trainer", "Owner") and val:
            norm[key] = val.title()
        elif key == "ColourCode" and val:
            # Normalize color code
            color = val.lower()
            norm[key] = COLOUR_MAP.get(color, color.capitalize())
        elif key == "Sex" and val:
            sex = val.upper()
            norm[key] = SEX_MAP.get(sex, sex)
        elif key == "Age" and val != "":
            norm[key] = int(val)
        elif key == "Box" and val != "":
            norm[key] = int(val)
        elif key in ("Career_Wins", "Career_Seconds", "Career_Thirds", "Career_Starters",
                     "Win_Percent", "Place_Percent", "PrizeMoneyWon", "Career_PrizeMoney") and val != "":
            # Remove non-digit (just in case) then convert
            num = re.sub(r'[^\d.]', '', str(val))
            if num:
                norm[key] = int(float(num))
            else:
                norm[key] = 0
        elif key == "Odds" and val != "":
            # Odds can be float; remove trailing 'F' (favorite) or similar
            odds_str = str(val).replace('F', '')
            try:
                norm[key] = float(odds_str)
            except:
                norm[key] = val
        else:
            # Default: keep as-is or empty string for missing
            norm[key] = val if val not in (None, [], {}) else ""
    return norm
