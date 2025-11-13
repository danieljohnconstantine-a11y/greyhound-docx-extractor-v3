from typing import List, Dict
from collections import defaultdict


def _to_float_or_none(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None


def _speed_kmh(distance_m: float, time_s: float):
    # Speed = distance (km) / time (h) = (m * 3.6) / s
    if distance_m is None or time_s is None or time_s == 0:
        return None
    return (distance_m * 3.6) / time_s


def aggregate_speeds(summary_rows: List[Dict], history_rows: List[Dict]) -> List[Dict]:
    """
    Per dog aggregation from history rows:
    - Hist_Count (count of history rows, regardless of speed availability)
    - Avg_Speed_km_h, Min_Speed_km_h, Max_Speed_km_h computed only on rows with both distance and time
    No assumptions: if no valid speeds, leave blanks.
    Dog identity is matched by Dog_Name; Track/Race_Date/Race_No context is not enforced here as histories span multiple meetings.
    """
    # Collect by Dog_Name
    by_dog = defaultdict(list)
    for r in history_rows:
        dog = (r.get("Dog_Name") or "").strip()
        if dog == "":
            continue
        dist = _to_float_or_none(r.get("Distance_m"))
        time_s = _to_float_or_none(r.get("Time_s"))
        spd = _speed_kmh(dist, time_s)
        by_dog[dog].append({"dist": dist, "time": time_s, "speed": spd})

    # Compute aggregates
    agg = {}
    for dog, rows in by_dog.items():
        hist_count = len(rows)
        speeds = [x["speed"] for x in rows if x["speed"] is not None]
        avg = round(sum(speeds) / len(speeds), 3) if speeds else None
        mn = round(min(speeds), 3) if speeds else None
        mx = round(max(speeds), 3) if speeds else None
        agg[dog] = {
            "Hist_Count": hist_count,
            "Avg_Speed_km_h": avg,
            "Min_Speed_km_h": mn,
            "Max_Speed_km_h": mx,
        }

    # Merge back into summary rows without assumptions for missing dogs
    out = []
    for row in summary_rows:
        dog = (row.get("Dog_Name") or "").strip()
        a = agg.get(dog)
        if a:
            row["Hist_Count"] = str(a["Hist_Count"]) if a["Hist_Count"] is not None else ""
            row["Avg_Speed_km_h"] = a["Avg_Speed_km_h"] if a["Avg_Speed_km_h"] is not None else ""
            row["Min_Speed_km_h"] = a["Min_Speed_km_h"] if a["Min_Speed_km_h"] is not None else ""
            row["Max_Speed_km_h"] = a["Max_Speed_km_h"] if a["Max_Speed_km_h"] is not None else ""
        out.append(row)

    return out
