"""
snapshot_joiner.py
------------------
Injects the "most recent run snapshot" (columns 36–56) into each summary row.

Group key:
    (Race_Date, Track, Race_No, Dog_Name, Box)

Rules:
    • Only real history rows are used.
    • "Most recent" = highest parsed Hist_Date (YYYY-MM-DD)
    • If Hist_Date missing or unparsable, treat as very old (rank last).
    • If no history for a dog → leave all snapshot fields blank.
    • No invention of values.
"""

import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime


SNAPSHOT_FIELDS = [
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
]


def _group_key(row: Dict) -> Tuple[str, str, str, str, str]:
    return (
        (row.get("Race_Date") or "").strip(),
        (row.get("Track") or "").strip(),
        str(row.get("Race_No") or "").strip(),
        (row.get("Dog_Name") or "").strip(),
        (row.get("Box") or "").strip(),
    )


def _parse_hist_date(d):
    """
    Parse a history date into a sortable datetime.
    If parsing fails, return a very old date (1900-01-01) so it will rank last.
    """
    if not d:
        return datetime(1900, 1, 1)
    try:
        return pd.to_datetime(d, dayfirst=True)
    except Exception:
        return datetime(1900, 1, 1)


def build_snapshot_map(history_rows: List[Dict]) -> Dict[Tuple[str,str,str,str,str], Dict]:
    """
    Build a lookup: group_key → most recent history row dict.
    """
    grouped = {}

    for hr in history_rows:
        key = _group_key(hr)
        hist_date_value = _parse_hist_date(hr.get("Hist_Date"))

        if key not in grouped:
            grouped[key] = (hist_date_value, hr)
        else:
            existing_date, _ = grouped[key]
            if hist_date_value > existing_date:
                grouped[key] = (hist_date_value, hr)

    # return only the row dicts, without the stored dates
    return {k: v[1] for k, v in grouped.items()}


def inject_snapshot(summary_rows: List[Dict], history_rows: List[Dict]) -> List[Dict]:
    """
    For each summary row, inject the most recent history run snapshot
    based on the group key.

    Missing snapshot fields remain empty strings.
    """
    snapshot_map = build_snapshot_map(history_rows)
    output = []

    for row in summary_rows:
        key = _group_key(row)
        snapshot = snapshot_map.get(key)

        if snapshot:
            for f in SNAPSHOT_FIELDS:
                row[f] = snapshot.get(f, "")
        else:
            for f in SNAPSHOT_FIELDS:
                row.setdefault(f, "")

        output.append(row)

    return output
