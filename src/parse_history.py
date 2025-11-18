# src/parse_history.py

import re
from datetime import datetime
from columns import HISTORY_COLUMNS

def parse_history_blocks(text):
    """
    Parse all historical run entries in the text.
    Returns a list of dicts with history columns.
    """
    history_records = []
    # Regex to match lines like "2nd of 8 28/10/2025 Track ... Distance 400m ... Race Time 0:22.65 ... Prize Won $903"
    hist_pattern = re.compile(
        r'^(?P<finish>\d+)(?:st|nd|rd|th)\s+of\s+\d+\s+'
        r'(?P<date>\d{1,2}/\d{1,2}/\d{4})\s+'
        r'(?P<track>\w+)\s+'
        r'.*?Distance\s+(?P<distance>\d+)\s*m.*?'
        r'Race Time\s+(?P<race_time>[0-9:]+\.?\d*)\s*Sec.*?'
        r'Prize Won\s*\$(?P<prize>\d+)'
    )
    for line in text.splitlines():
        m = hist_pattern.search(line)
        if not m:
            continue
        rec = {}
        # Position
        rec["Hist_Finish_Pos"] = int(m.group("finish"))
        # Date (convert to ISO)
        raw_date = m.group("date")
        rec["Hist_Date"] = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
        # Track
        rec["Hist_Track"] = m.group("track")
        # Distance
        dist = int(m.group("distance"))
        rec["Hist_Distance_m"] = dist
        # Race time (format e.g. "0:22.65" or "22.65")
        time_str = m.group("race_time")
        if ":" in time_str:
            # if format mm:ss.ss or similar
            parts = time_str.split(':')
            secs = float(parts[-1])
        else:
            secs = float(time_str)
        rec["Hist_Race_Time_s"] = secs
        # Prize won
        rec["Hist_Prize_Won"] = int(m.group("prize"))
        # Odds (if present)
        odds_match = re.search(r'Odds\s*([\d\.]+)', line)
        if odds_match:
            rec["Hist_Odds"] = float(odds_match.group(1))
        else:
            rec["Hist_Odds"] = None
        # Compute speed (m/s) if possible
        if dist and secs and secs != 0:
            rec["Hist_Speed_mps"] = round(dist / secs, 2)
        else:
            rec["Hist_Speed_mps"] = None
        # Ensure all history columns are present
        for key in HISTORY_COLUMNS:
            rec.setdefault(key, "")
        history_records.append(rec)
    return history_records
