# src/validation_and_audit.py

import os
import json
import pandas as pd
from datetime import datetime
from src.columns import SUMMARY_COLUMNS

AUDIT_DIR = "outputs/audit"


def _ensure_audit_dir():
    if not os.path.exists(AUDIT_DIR):
        os.makedirs(AUDIT_DIR, exist_ok=True)


def audit_pipeline(summary_df: pd.DataFrame,
                   history_rows: list,
                   unparsed_lines: list,
                   processed_files: list):
    """
    Perform validation + audit AFTER export.
    Produces:
        - audit_summary.json
        - audit_summary.txt
        - rejects_unparsed.txt
        - coverage_stats.json

    STRICT RULES:
        * No schema changes
        * No value mutation
        * Read-only — only reports issues
    """

    _ensure_audit_dir()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------
    # 1. Basic counts
    # -------------------------
    total_files = len(processed_files)
    total_dogs = len(summary_df)
    total_history = len(history_rows)
    unique_dogs = summary_df[["Race_Date", "Track", "Race_No", "Dog_Name", "Box"]].drop_duplicates()
    unique_dog_count = len(unique_dogs)

    # -------------------------
    # 2. Speed coverage
    # -------------------------
    speed_available = summary_df["Avg_Speed_km/h"].notna() & (summary_df["Avg_Speed_km/h"] != "")
    pct_speed = round((speed_available.sum() / total_dogs) * 100, 2) if total_dogs else 0

    # -------------------------
    # 3. History coverage
    # -------------------------
    pct_with_history = round((summary_df["Hist_Count"].astype(str) != "0").sum() / total_dogs * 100, 2) if total_dogs else 0

    # -------------------------
    # 4. Snapshot coverage
    # -------------------------
    snapshot_fields = [
        "Hist_Date", "Hist_Track", "Hist_Distance", "Hist_Finish_Pos", "Hist_Margin_L",
        "Hist_Race_Time", "Hist_Sec_Time", "Hist_Sec_Time_Adj", "Hist_Speed_km/h",
        "Hist_SOT", "Hist_RST", "Hist_BP", "Hist_Odds", "Hist_API", "Hist_Prize_Won",
        "Hist_Winner", "Hist_2nd_Place", "Hist_3rd_Place", "Hist_Settled_Turn",
        "Hist_Ongoing_Winners", "Hist_Track_Direction"
    ]
    any_snapshot = summary_df[snapshot_fields].notna().any(axis=1)
    pct_snapshot = round((any_snapshot.sum() / total_dogs) * 100, 2) if total_dogs else 0

    # -------------------------
    # 5. Missing critical identifiers
    # -------------------------
    missing_track = summary_df["Track"].eq("").sum()
    missing_rd = summary_df["Race_Date"].eq("").sum()
    missing_raceno = summary_df["Race_No"].eq("").sum()
    missing_dog = summary_df["Dog_Name"].eq("").sum()
    missing_box = summary_df["Box"].eq("").sum()

    # -------------------------
    # 6. Unparsed lines
    # -------------------------
    rejects_path = os.path.join(AUDIT_DIR, "rejects_unparsed.txt")
    with open(rejects_path, "w", encoding="utf-8") as f:
        for line in unparsed_lines:
            f.write(line.strip() + "\n")

    # -------------------------
    # 7. JSON audit summary
    # -------------------------
    audit_json = {
        "timestamp": now,
        "files_processed": total_files,
        "dogs_parsed": total_dogs,
        "unique_dogs": unique_dog_count,
        "history_rows": total_history,
        "pct_with_history": pct_with_history,
        "pct_with_speed": pct_speed,
        "pct_with_snapshot": pct_snapshot,
        "missing_fields": {
            "Track": int(missing_track),
            "Race_Date": int(missing_rd),
            "Race_No": int(missing_raceno),
            "Dog_Name": int(missing_dog),
            "Box": int(missing_box)
        },
        "rejects_file": rejects_path
    }

    json_path = os.path.join(AUDIT_DIR, "audit_summary.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(audit_json, jf, indent=4)

    # -------------------------
    # 8. TXT human-readable summary
    # -------------------------
    txt_path = os.path.join(AUDIT_DIR, "audit_summary.txt")
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write("GREYHOUND DOCX → EXCEL AUDIT REPORT\n")
        tf.write("====================================\n\n")
        tf.write(f"Timestamp: {now}\n\n")
        tf.write(f"Files processed: {total_files}\n")
        tf.write(f"Dogs parsed: {total_dogs}\n")
        tf.write(f"Unique dogs: {unique_dog_count}\n")
        tf.write(f"History rows: {total_history}\n\n")
        tf.write(f"% Dogs with ≥1 history row: {pct_with_history}%\n")
        tf.write(f"% Dogs with Avg_Speed_km/h: {pct_speed}%\n")
        tf.write(f"% Dogs with snapshot fields: {pct_snapshot}%\n\n")
        tf.write("Missing critical identifiers:\n")
        tf.write(f"  Track: {missing_track}\n")
        tf.write(f"  Race_Date: {missing_rd}\n")
        tf.write(f"  Race_No: {missing_raceno}\n")
        tf.write(f"  Dog_Name: {missing_dog}\n")
        tf.write(f"  Box: {missing_box}\n\n")
        tf.write("Unparsed lines written to rejects_unparsed.txt\n")

    return audit_json
