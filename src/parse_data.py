import re
import pandas as pd
from docx import Document
from datetime import datetime
from src.summary_utils import normalize_summary_fields


def read_docx_tables(path):
    doc = Document(path)
    blocks = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            blocks.append({"type": "paragraph", "text": t})
    for tbl in doc.tables:
        rows = []
        for r in tbl.rows:
            cells = [c.text.strip() for c in r.cells]
            if any(x for x in cells):
                rows.append(cells)
        if rows:
            blocks.append({"type": "table", "rows": rows})
    return blocks


def parse_meeting_header(blocks, source_file):
    info = {
        "Track": "",
        "Race_Date": "",
        "Race_No": "",
        "Distance_m": "",
        "Race_Name": "",
        "Grade": "",
        "Data_Source_File": source_file,
    }

    for b in blocks:
        if b["type"] != "paragraph":
            continue
        t = b["text"]

        m = re.search(r"(Race\s*No\.?\s*(\d+))", t, re.I)
        if m:
            info["Race_No"] = m.group(2)

        m = re.search(r"(\d{1,2}\s*[A-Za-z]{3}\s*\d{2,4})", t)
        if m:
            info["Race_Date"] = m.group(1)

        m = re.search(r"((?:ALBANY|ANGLE PARK|BALLARAT|BENDIGO|CANBERRA|CANNINGTON|CAPALABA|DUBBO|DAWSON|GRAFTON|GOSFORD|HEALESVILLE|HORSHAM|IPSWICH|LAUNCESTON|MANDURAH|MURRAY BRIDGE|NORTHAM|RICHMOND|SALE|SANDOWN|TAREE|THE MEADOWS|TOWNSVILLE|TRARALGON|WAGGA|WARRAGUL|WARRNAMBOOL|WENTWORTH PARK|YOUNG))", t, re.I)
        if m:
            info["Track"] = m.group(1).upper()

        m = re.search(r"(\d{3,4})m", t)
        if m:
            info["Distance_m"] = m.group(1)

        m = re.search(r"(Grade\s*[A-Z0-9/ -]+)", t)
        if m:
            info["Grade"] = m.group(1)

        if not info["Race_Name"]:
            if " " in t and len(t.split()) >= 3:
                info["Race_Name"] = t

    if info["Race_Date"]:
        try:
            info["Race_Date"] = pd.to_datetime(info["Race_Date"], dayfirst=True).strftime("%Y-%m-%d")
        except:
            pass

    return info


def parse_dog_table_rows(table_rows, meeting_info):
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

        if "Dog_Name" not in row_dict:
            if "DOG" in row_dict:
                row_dict["Dog_Name"] = row_dict["DOG"]

        if "Box" not in row_dict:
            if "BOX" in row_dict:
                row_dict["Box"] = row_dict["BOX"]

        if "Trainer" not in row_dict:
            if "TRAINER" in row_dict:
                row_dict["Trainer"] = row_dict["TRAINER"]

        rows.append(row_dict)

    return rows


def map_header(h):
    h = h.upper()
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
    if "BP" == h or "BOX NO" in h:
        return "BP"
    if "AGE" in h:
        return "Age"
    if "SEX" in h or "GENDER" in h:
        return "Sex"
    if "SIRE" in h:
        return "Sire"
    if "DAM" in h:
        return "Dam"
    if "OWNER" in h:
        return "Owner"
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
    return h.title()


def extract_dog_tables(blocks, meeting_info):
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


def parse_history_blocks(blocks, meeting_info):
    hist = []
    for b in blocks:
        if b["type"] != "table":
            continue
        for row in b["rows"]:
            if len(row) < 5:
                continue

            date = None
            if re.match(r"\d{1,2}/\d{1,2}/\d{2,4}", row[0]):
                date = row[0]

            if date:
                d = {
                    "Dog_Name": "",
                    "Hist_Date": date,
                    "Hist_Track": "",
                    "Hist_Distance": "",
                    "Hist_Finish_Pos": "",
                    "Hist_Margin_L": "",
                    "Hist_Race_Time": "",
                    "Hist_Sec_Time": "",
                    "Hist_Sec_Time_Adj": "",
                    "Hist_SOT": "",
                    "Hist_RST": "",
                    "Hist_BP": "",
                    "Hist_Odds": "",
                    "Hist_API": "",
                    "Hist_Prize_Won": "",
                    "Hist_Winner": "",
                    "Hist_2nd_Place": "",
                    "Hist_3rd_Place": "",
                    "Hist_Settled_Turn": "",
                    "Hist_Ongoing_Winners": "",
                    "Hist_Track_Direction": "",
                    "Data_Source_File": meeting_info["Data_Source_File"],
                }
                hist.append(d)

    return hist


def parse_docx(path):
    blocks = read_docx_tables(path)
    meeting_info = parse_meeting_header(blocks, source_file=path)
    dog_rows = extract_dog_tables(blocks, meeting_info)
    hist_rows = parse_history_blocks(blocks, meeting_info)

    df = pd.DataFrame(dog_rows)
    df = normalize_summary_fields(df)

    return df, hist_rows
