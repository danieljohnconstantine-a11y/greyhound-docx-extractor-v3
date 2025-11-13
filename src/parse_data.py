import re
from datetime import datetime
from typing import Dict, List, Tuple

from . import columns as C


def _blanked_row():
    return {k: "" for k in C.SUMMARY_COLUMNS}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def _try_parse_date(s: str):
    # Try common AU formats: DD/MM/YYYY, DD-MM-YYYY, D/M/YY, etc.
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return ""


def parse_meeting_header(doc_data: Dict) -> Dict:
    """
    Parse high-level meeting info from headers and early paragraphs.
    Fields: Track, Race_Date, Race_No, Distance_m, Race_Name, Grade, PrizeMoney, Weather, Track_Condition
    Returns a dict with keys from SUMMARY_COLUMNS where applicable; rest blank.
    """
    header = _blanked_row()

    text_lines = []
    text_lines.extend(doc_data.get("headers", []))
    text_lines.extend(doc_data.get("paragraphs", [])[:50])  # first 50 paragraphs likely contain header data
    text_blob = "\n".join(text_lines)

    # Track: look for "Track: NAME"
    m = re.search(r"Track\s*:\s*([A-Za-z \-']+)", text_blob, re.IGNORECASE)
    if m:
        header["Track"] = m.group(1).strip()

    # Race No: "Race 5" or "Race: 5"
    m = re.search(r"\bRace\s*[:#]?\s*(\d{1,2})\b", text_blob, re.IGNORECASE)
    if m:
        header["Race_No"] = m.group(1).strip()

    # Race Name (optional)
    m = re.search(r"Race Name\s*:\s*(.+)", text_blob, re.IGNORECASE)
    if m:
        header["Race_Name"] = m.group(1).strip()

    # Distance, capture digits + 'm'
    m = re.search(r"\b(\d{3,5})\s*m\b", text_blob, re.IGNORECASE)
    if m:
        header["Distance_m"] = m.group(1).strip()

    # Date: try to find typical date pattern
    m = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", text_blob)
    if m:
        header["Race_Date"] = _try_parse_date(m.group(1))

    # Grade
    m = re.search(r"\bGrade\s*:\s*([A-Za-z0-9 \-/]+)", text_blob, re.IGNORECASE)
    if m:
        header["Grade"] = m.group(1).strip()

    # PrizeMoney
    m = re.search(r"Prize\s*Money\s*:\s*([\$A-Za-z0-9, ]+)", text_blob, re.IGNORECASE)
    if m:
        header["PrizeMoney"] = m.group(1).strip()

    # Weather
    m = re.search(r"Weather\s*:\s*([A-Za-z ]+)", text_blob, re.IGNORECASE)
    if m:
        header["Weather"] = m.group(1).strip()

    # Track Condition
    m = re.search(r"(Track\s*Condition|Going)\s*:\s*([A-Za-z \-]+)", text_blob, re.IGNORECASE)
    if m:
        header["Track_Condition"] = m.group(2).strip()

    # Meeting notes (any free text indicated)
    m = re.search(r"(Notes?|Remarks?)\s*:\s*(.+)", text_blob, re.IGNORECASE)
    if m:
        header["Meeting_Notes"] = m.group(2).strip()

    return header


def _map_entry_headers_to_schema(headers_row: List[str]) -> Dict[int, str]:
    """
    Given a table header row, map each column index to a SUMMARY_COLUMNS field.
    This is heuristics-based, tolerant of naming variance.
    """
    mapping = {}
    for idx, h in enumerate(headers_row):
        h_norm = _norm(h)

        if re.search(r"\bbox\b", h_norm):
            mapping[idx] = "Box"
        elif re.search(r"\b(dog|name)\b", h_norm):
            mapping[idx] = "Dog_Name"
        elif re.search(r"\b(tab|no\.?|#)\b", h_norm):
            mapping[idx] = "Tab_No"
        elif "trainer" in h_norm:
            mapping[idx] = "Trainer"
        elif "owner" in h_norm:
            mapping[idx] = "Owner"
        elif "sex" in h_norm:
            mapping[idx] = "Sex"
        elif "colour" in h_norm or "color" in h_norm:
            mapping[idx] = "Color"
        elif "whelp" in h_norm:
            mapping[idx] = "Whelped"
        elif "age" in h_norm:
            mapping[idx] = "Age_Months"
        elif "sire" in h_norm:
            mapping[idx] = "Sire"
        elif "dam" in h_norm:
            mapping[idx] = "Dam"
        elif re.search(r"^sp$|starting price|sp/odds|start price|starting", h_norm):
            mapping[idx] = "Starting_Price"
        elif "odds" in h_norm:
            mapping[idx] = "Odds"
        elif "scratch" in h_norm:
            mapping[idx] = "Scratched"
        elif "reserve" in h_norm or h_norm in {"res", "rsv"}:
            mapping[idx] = "Reserve"
        elif "weight" in h_norm:
            mapping[idx] = "Weight_kg"
        elif re.search(r"\b(run|rn)\b", h_norm):
            mapping[idx] = "Run_No"
        elif "ff" in h_norm or "form" in h_norm:
            mapping[idx] = "FF_Form"
        elif "first split" in h_norm or "1st split" in h_norm or "split1" in h_norm:
            mapping[idx] = "FirstSplit_s"
        elif "second split" in h_norm or "2nd split" in h_norm or "split2" in h_norm:
            mapping[idx] = "SecondSplit_s"
        elif "run home" in h_norm or "runhome" in h_norm:
            mapping[idx] = "RunHome_s"
        elif "early speed" in h_norm:
            mapping[idx] = "EarlySpeedRating"
        elif "comments" in h_norm or "comment" in h_norm:
            mapping[idx] = "Comments"
        elif "trainer recent" in h_norm or "trainer form" in h_norm:
            mapping[idx] = "Trainer_Recent_Form"
        elif "last run date" in h_norm:
            mapping[idx] = "Last_Run_Date"
        elif "last run track" in h_norm:
            mapping[idx] = "Last_Run_Track"
        elif "last run distance" in h_norm:
            mapping[idx] = "Last_Run_Distance_m"
        elif "last run box" in h_norm:
            mapping[idx] = "Last_Run_Box"
        elif "last run time" in h_norm:
            mapping[idx] = "Last_Run_Time_s"
        elif "last run position" in h_norm or "last pos" in h_norm:
            mapping[idx] = "Last_Run_Position"
        elif "last run margin" in h_norm:
            mapping[idx] = "Last_Run_Margin_Lens"
        elif "last run comments" in h_norm:
            mapping[idx] = "Last_Run_Comments"
        elif "career starts" in h_norm:
            mapping[idx] = "Career_Starts"
        elif "career wins" in h_norm:
            mapping[idx] = "Career_Wins"
        elif "career seconds" in h_norm:
            mapping[idx] = "Career_Seconds"
        elif "career thirds" in h_norm:
            mapping[idx] = "Career_Thirds"
        elif "career prizemoney" in h_norm or "career prize" in h_norm:
            mapping[idx] = "Career_Prizemoney"
        elif "career best" in h_norm:
            mapping[idx] = "Career_BestTime"
        elif "this track starts" in h_norm:
            mapping[idx] = "ThisTrack_Starts"
        elif "this track wins" in h_norm:
            mapping[idx] = "ThisTrack_Wins"
        elif "this track best" in h_norm:
            mapping[idx] = "ThisTrack_BestTime"
        elif "this distance starts" in h_norm:
            mapping[idx] = "ThisDistance_Starts"
        elif "this distance wins" in h_norm:
            mapping[idx] = "ThisDistance_Wins"
        elif "this distance best" in h_norm:
            mapping[idx] = "ThisDistance_BestTime"
        # else: unmapped, will be logged
    return mapping


def parse_dog_entries(doc_data: Dict, meeting_header: Dict) -> Tuple[List[Dict], Dict]:
    """
    Parse the main dog entry table(s).
    Will attempt to find a table with recognizable header cells such as 'Box', 'Dog', 'Trainer', etc.
    Returns: (rows, unmapped_header_info)
    """
    rows_out = []
    unmapped_info = {}

    tables = doc_data.get("tables", [])
    if not tables:
        return rows_out, unmapped_info

    for t_idx, table in enumerate(tables):
        if not table or len(table) < 2:
            continue
        header_row = [c.strip() for c in table[0]]
        mapping = _map_entry_headers_to_schema(header_row)

        # consider a valid entry table if we mapped at least Box and Dog_Name
        if "Box" not in mapping.values() or "Dog_Name" not in mapping.values():
            continue

        # log unmapped headers for audit
        unmapped = []
        for i, text in enumerate(header_row):
            if i not in mapping:
                unmapped.append(text)
        if unmapped:
            unmapped_info[f"table_{t_idx}_unmapped_headers"] = unmapped

        # read data rows
        for r in table[1:]:
            row = _blanked_row()
            # copy meeting-level metadata into each row
            for k in ["Track", "Race_Date", "Race_No", "Distance_m", "Race_Name", "Grade", "PrizeMoney", "Weather", "Track_Condition", "Meeting_Notes"]:
                row[k] = meeting_header.get(k, "")

            for i, cell_text in enumerate(r):
                if i in mapping:
                    col = mapping[i]
                    row[col] = cell_text.strip()

            # ensure Dog_Name presence; skip if no dog name
            if row["Dog_Name"]:
                rows_out.append(row)

    return rows_out, unmapped_info


def parse_history(doc_data: Dict, meeting_header: Dict) -> List[Dict]:
    """
    Parse dog history tables if present.
    Heuristics: any table with recognizable history headers like Date/Track/Dist/Box/Pos/Time/Margin.
    Each row maps to HISTORY_COLUMNS; missing data -> blank.
    """
    out = []
    tables = doc_data.get("tables", [])
    file_name = doc_data.get("file_path", "").split("/")[-1]

    def map_hist_headers(hs: List[str]):
        m = {}
        for idx, h in enumerate(hs):
            hn = _norm(h)
            if "date" in hn:
                m[idx] = "Race_Date"
            elif "track" in hn or "venue" in hn:
                m[idx] = "Track"
            elif "dist" in hn or "distance" in hn:
                m[idx] = "Distance_m"
            elif re.search(r"\bbox\b|draw|box no", hn):
                m[idx] = "Box"
            elif re.search(r"\bpos\b|position|place", hn):
                m[idx] = "Position"
            elif "time" in hn and "split" not in hn:
                m[idx] = "Time_s"
            elif "margin" in hn or "lens" in hn:
                m[idx] = "Margin_Lens"
            elif "field" in hn or "runners" in hn:
                m[idx] = "Field_Size"
            elif re.search(r"^sp$|starting price|sp/odds|start price|starting|odds", hn):
                m[idx] = "Starting_Price"
            elif "grade" in hn:
                m[idx] = "Grade"
            elif "race name" in hn or "event" in hn or "name" in hn:
                m[idx] = "Race_Name"
            elif "split1" in hn or "first split" in hn or "1st split" in hn:
                m[idx] = "Sectional1_s"
            elif "split2" in hn or "second split" in hn or "2nd split" in hn:
                m[idx] = "Sectional2_s"
            elif "run home" in hn or "runhome" in hn:
                m[idx] = "RunHome_s"
            elif "weight" in hn:
                m[idx] = "Weight_kg"
            elif "comment" in hn:
                m[idx] = "Comments"
            elif "dog" in hn or "name" in hn:
                m[idx] = "Dog_Name"
            elif "tab" in hn or hn in {"#", "no", "no."}:
                m[idx] = "Tab_No"
            elif "trainer" in hn:
                m[idx] = "Trainer"
        return m

    for table in tables:
        if not table or len(table) < 2:
            continue
        header = [c.strip() for c in table[0]]
        mapping = map_hist_headers(header)

        # A minimal set to qualify as "history-like"
        needed = {"Race_Date", "Track", "Distance_m"}
        if not needed.issubset(set(mapping.values())):
            continue

        for r in table[1:]:
            row = {k: "" for k in C.HISTORY_COLUMNS}
            # fill meeting-level defaults where appropriate
            row["Track"] = ""
            row["Race_Date"] = ""
            row["Race_No"] = ""
            row["Race_Name"] = ""
            row["Grade"] = ""
            row["Distance_m"] = ""
            row["Dog_Name"] = ""
            row["Box"] = ""
            row["Tab_No"] = ""
            row["Trainer"] = ""
            row["Time_s"] = ""
            row["Speed_km_h"] = ""
            row["Position"] = ""
            row["Margin_Lens"] = ""
            row["Field_Size"] = ""
            row["Starting_Price"] = ""
            row["Odds"] = ""
            row["Sectional1_s"] = ""
            row["Sectional2_s"] = ""
            row["RunHome_s"] = ""
            row["Weight_kg"] = ""
            row["Comments"] = ""
            row["Source_File"] = file_name

            for i, cell_text in enumerate(r):
                if i in mapping:
                    col = mapping[i]
                    val = cell_text.strip()
                    # try normalizing date strings
                    if col == "Race_Date":
                        val = _try_parse_meeting_date(val)
                    row[col] = val

            # Per mandate: never assume missing dog names; leave blank if not present.
            out.append(row)

    return out


def _try_parse_meeting_date(s: str) -> str:
    s = s.strip()
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d"]:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return ""
