import re
import pandas as pd

from src.columns import HISTORY_COLUMNS


def _to_float_or_none(v):
    if v is None:
        return None
    s = str(v).strip()
    if s == "":
        return None
    try:
        return float(s)
    except Exception:
        return None


def _parse_time_to_seconds(s: str | None) -> float | None:
    if s is None:
        return None
    text = str(s).strip()
    if not text:
        return None

    # typical race time "30.12"
    m = re.match(r"^(\d{2,3}\.\d{1,3})$", text)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None

    # allow plain float
    try:
        return float(text)
    except Exception:
        return None


def _compute_speed_kmh(dist_str: str | None, time_str: str | None) -> float | None:
    dist_m = None
    if dist_str is not None:
        m = re.search(r"(\d{2,4})", str(dist_str))
        if m:
            try:
                dist_m = float(m.group(1))
            except Exception:
                dist_m = None

    t_s = _parse_time_to_seconds(time_str)

    if dist_m is None or t_s is None or t_s == 0:
        return None

    return (dist_m * 3.6) / t_s


def map_history_header(h: str) -> str | None:
    h = h.upper()
    if "DATE" in h:
        return "Hist_Date"
    if "TRACK" in h or "VENUE" in h:
        return "Hist_Track"
    if "DIST" in h or "DIS" in h:
        return "Hist_Distance"
    if "POS" in h or "PLC" in h or "PLACE" in h:
        return "Hist_Finish_Pos"
    if "MARGIN" in h or "MARG" in h:
        return "Hist_Margin_L"
    if "TIME" in h and "SEC" not in h:
        return "Hist_Race_Time"
    if "SEC" in h and "ADJ" not in h:
        return "Hist_Sec_Time"
    if "ADJ" in h:
        return "Hist_Sec_Time_Adj"
    if "SOT" in h or "TRK" in h:
        return "Hist_SOT"
    if "RST" in h:
        return "Hist_RST"
    if "BOX" in h or "BP" in h:
        return "Hist_BP"
    if "ODDS" in h or "SP" in h:
        return "Hist_Odds"
    if "API" in h:
        return "Hist_API"
    if "PRIZE" in h or "STAKE" in h or "STK" in h:
        return "Hist_Prize_Won"
    if "WINNER" in h:
        return "Hist_Winner"
    if "2ND" in h:
        return "Hist_2nd_Place"
    if "3RD" in h:
        return "Hist_3rd_Place"
    if "SETTLE" in h or "SETTL" in h:
        return "Hist_Settled_Turn"
    if "ONGOING" in h:
        return "Hist_Ongoing_Winners"
    if "DIR" in h or "RAIL" in h:
        return "Hist_Track_Direction"
    return None


def parse_history_blocks(blocks, meeting_info, dog_rows):
    """
    Full NSW/GBOTA compliant history parser.
    Produces one HISTORY_COLUMNS dict per history run.
    No silent drops.
    """

    # Known dog names
    dog_names = sorted(
        {r.get("Dog_Name", "").strip() for r in dog_rows if r.get("Dog_Name")},
        key=len,
        reverse=True,
    )

    # Box lookup per dog
    dog_to_box = {
        (r.get("Dog_Name", "").strip()): (r.get("Box") or "").strip()
        for r in dog_rows
        if r.get("Dog_Name")
    }

    hist_rows = []
    current_dog = None

    for b in blocks:

        # Detect dog context in paragraphs
        if b["type"] == "paragraph":
            text = b["text"]
            for name in dog_names:
                if re.search(r"\b" + re.escape(name) + r"\b", text):
                    current_dog = name
                    break

        # Parse history table
        elif b["type"] == "table":

            rows = b["rows"]
            if len(rows) < 2:
                continue

            # Identify history table headers
            header = [c.upper() for c in rows[0]]
            header_str = " ".join(header)

            # Must include DATE + (DIST or TIME or MARGIN)
            if "DATE" not in header_str:
                continue
            if not any(x in header_str for x in ["DIST", "DIS", "TIME", "MARGIN"]):
                continue

            # Map header columns
            col_map = {}
            for idx, h in enumerate(header):
                key = map_history_header(h)
                if key:
                    col_map[idx] = key

            # Require essential fields
            has_date = any(v == "Hist_Date" for v in col_map.values())
            has_other = any(
                v in ["Hist_Distance", "Hist_Race_Time"] for v in col_map.values()
            )
            if not (has_date and has_other):
                continue

            # Process each row
            for r in rows[1:]:
                hist = {k: "" for k in HISTORY_COLUMNS}

                hist["Track"] = meeting_info.get("Track", "")
                hist["Race_Date"] = meeting_info.get("Race_Date", "")
                hist["Race_No"] = meeting_info.get("Race_No", "")
                hist["Dog_Name"] = current_dog or ""
                hist["Box"] = dog_to_box.get(current_dog or "", "")
                hist["Data_Source_File"] = meeting_info.get("Data_Source_File", "")

                # Column values
                for idx, val in enumerate(r):
                    if idx not in col_map:
                        continue
                    key = col_map[idx]
                    hist[key] = val.strip()

                # Compute Hist_Speed_km/h
                spd = _compute_speed_kmh(
                    hist.get("Hist_Distance"), hist.get("Hist_Race_Time")
                )
                hist["Hist_Speed_km/h"] = round(spd, 3) if spd is not None else ""

                hist_rows.append(hist)

    return hist_rows
