import re
from datetime import datetime

import pandas as pd
from docx import Document

from src.summary_utils import normalize_summary_fields
from src.parse_history import parse_history_blocks


def read_docx_tables(path: str):
    """
    Read a DOCX file and return a linear list of blocks:
    - {"type": "paragraph", "text": str}
    - {"type": "table", "rows": [[cell, ...], ...]}
    Order is preserved exactly as in the document.
    """
    doc = Document(path)
    blocks = []

    # paragraphs
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            blocks.append({"type": "paragraph", "text": t})

    # tables
    for tbl in doc.tables:
        rows = []
        for r in tbl.rows:
            cells = [c.text.strip() for c in r.cells]
            # skip fully empty rows
            if any(x for x in cells):
                rows.append(cells)
        if rows:
            blocks.append({"type": "table", "rows": rows})

    return blocks


def parse_meeting_header(blocks, source_file: str):
    """
    Extract meeting-level metadata from the paragraph blocks.
    Outputs keys that feed straight into the 60-column schema:
    Track, Race_Date, Race_No, Distance_m, Race_Name, Race_Grade, Data_Source_File.
    """
    info = {
        "Track": "",
        "Race_Date": "",
        "Race_No": "",
        "Distance_m": "",
        "Race_Name": "",
        "Race_Grade": "",
        "Data_Source_File": source_file,
    }

    for b in blocks:
        if b["type"] != "paragraph":
            continue

        t = b["text"]

        # Race number, e.g. "Race 1" / "Race: 1"
        m = re.search(r"Race\s*No\.?\s*(\d+)", t, re.I)
        if not m:
            m = re.search(r"\bRace\s*[:#]?\s*(\d{1,2})\b", t, re.I)
        if m:
            info["Race_No"] = m.group(1).strip()

        # Date, e.g. "15 Oct 25"
        m = re.search(r"(\d{1,2}\s*[A-Za-z]{3}\s*\d{2,4})", t)
        if m and not info["Race_Date"]:
            info["Race_Date"] = m.group(1).strip()

        # Track name (broad list; can be extended)
        m = re.search(
            r"(ALBANY|ANGLE PARK|BALLARAT|BENDIGO|CANBERRA|CANNINGTON|CAPALABA|DUBBO|DAWSON|GRAFTON|GOSFORD|HEALESVILLE|HORSHAM|IPSWICH|LAUNCESTON|MANDURAH|MURRAY BRIDGE|NORTHAM|RICHMOND|SALE|SANDOWN|TAREE|THE MEADOWS|TOWNSVILLE|TRARALGON|WAGGA|WARRAGUL|WARRNAMBOOL|WENTWORTH PARK|YOUNG)",
            t,
            re.I,
        )
        if m and not info["Track"]:
            info["Track"] = m.group(1).upper()

        # Distance, e.g. "520m"
        m = re.search(r"(\d{3,4})\s*m", t, re.I)
        if m and not info["Distance_m"]:
            info["Distance_m"] = m.group(1)

        # Race grade, e.g. "Grade 5", "Grade Maiden", "Grade 5/6"
        m = re.search(r"Grade\s*([A-Za-z0-9/ -]+)", t, re.I)
        if m and not info["Race_Grade"]:
            info["Race_Grade"] = m.group(1).strip()

        # Race name fallback: first reasonably long line if Race_Name still blank
        if not info["Race_Name"]:
            if " " in t and len(t.split()) >= 3:
                info["Race_Name"] = t

    # Normalise date -> YYYY-MM-DD if possible
    if info["Race_Date"]:
        try:
            info["Race_Date"] = pd.to_datetime(
                info["Race_Date"], dayfirst=True
            ).strftime("%Y-%m-%d")
        except Exception:
            # leave as-is if parsing fails
            pass

    return info


def map_header(h: str) -> str:
    """
    Map dog-entry table header text to internal keys.
    These internal keys are then normalized into SUMMARY_COLUMNS
    via normalize_summary_fields.
    """
    h = h.upper()

    # dog identity
    if "DOG" in h:
        return "Dog_Name"
    if "BOX" in h:
        return "Box"
    if "TAB" in h:
        return "Tab_No"
    if "TRAINER" in h:
        return "Trainer"
    if "WT" in h or "WEIGHT" in h:
        return "Weight_kg"
    if "FORM" in h:
        return "FF_Form"
    if h == "BP" or "BOX NO" in h:
        return "BP"

    # pedigree
    if "SIRE" in h:
        return "Sire"
    if "DAM" in h:
        return "Dam"
    if "OWNER" in h:
        return "Owner"

    # age/sex
    if "AGE" in h:
        return "Age"
    if "SEX" in h or "GENDER" in h:
        return "Sex"

    # career stats
    if "PRIZE" in h:
        return "PrizeMoney"
    if "WINS" in h:
        return "Wins"
    if "PLACES" in h:
        return "Places"
    if "STARTS" in h:
        return "Starts"
    if "DLR" in h:
        return "DLR"
    if "DLW" in h:
        return "DLW"
    if "RTC" in h:
        return "RTC"

    # fallback: title-case the header
    return h.title()


def parse_dog_table_rows(table_rows, meeting_info):
    """
    Given a single dog-entry table (header row + data rows) and the meeting_info dict,
    return a list of per-dog dicts (one per row).
    """
    rows = []
    headers = None

    for r in table_rows:
        if not headers:
            headers = [h.strip().upper() for h in r]
            continue

        row_dict = dict(meeting_info)

        for idx, val in enumerate(r):
            h = headers[idx] if idx < len(headers) else ""
            key = map_header(h)
            row_dict[key] = val.strip()

        # Fallbacks if some keys are missing but raw headers exist
        if "Dog_Name" not in row_dict and "DOG" in row_dict:
            row_dict["Dog_Name"] = row_dict["DOG"]

        if "Box" not in row_dict and "BOX" in row_dict:
            row_dict["Box"] = row_dict["BOX"]

        if "Trainer" not in row_dict and "TRAINER" in row_dict:
            row_dict["Trainer"] = row_dict["TRAINER"]

        rows.append(row_dict)

    return rows


def extract_dog_tables(blocks, meeting_info):
    """
    Scan all table blocks and extract any that look like dog-entry grids,
    based on headers containing DOG/BOX/TAB/TRAINER.
    """
    all_rows = []

    for b in blocks:
        if b["type"] != "table":
            continue

        table_rows = b["rows"]
        if len(table_rows) < 2:
            continue

        header_row = [c.upper() for c in table_rows[0]]
        if any(x in header_row for x in ["DOG", "BOX", "TAB", "TRAINER"]):
            parsed = parse_dog_table_rows(table_rows, meeting_info)
            all_rows.extend(parsed)

    return all_rows


def parse_docx(path: str):
    """
    High-level orchestration for a single DOCX file.

    Returns:
        summary_df: pandas.DataFrame => one row per dog per meeting
        hist_rows:  List[Dict]       => one row per historical run per dog
    """
    blocks = read_docx_tables(path)
    meeting_info = parse_meeting_header(blocks, source_file=path)

    # 1) Dog summary rows
    dog_rows = extract_dog_tables(blocks, meeting_info)
    summary_df = pd.DataFrame(dog_rows)
    summary_df = normalize_summary_fields(summary_df)

    # 2) History rows (delegated to src.parse_history)
    hist_rows = parse_history_blocks(blocks, meeting_info, dog_rows)

    return summary_df, hist_rows
