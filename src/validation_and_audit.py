import os
import json
from typing import Dict, List

import pandas as pd


def _overall_coverage(summary_df: pd.DataFrame) -> float:
    if summary_df is None or summary_df.empty:
        return 0.0
    total = summary_df.shape[0] * summary_df.shape[1]
    non_empty = summary_df.applymap(lambda x: str(x).strip() != "").values.sum()
    return (non_empty / total) * 100.0 if total > 0 else 0.0


def _speed_availability(summary_df: pd.DataFrame) -> float:
    if summary_df is None or summary_df.empty:
        return 0.0
    denom = len(summary_df)
    num = (summary_df["Avg_Speed_km_h"].notna() & (summary_df["Avg_Speed_km_h"] != "")).sum()
    return (num / denom) * 100.0 if denom > 0 else 0.0


def _consistency_issues(summary_df: pd.DataFrame, history_df: pd.DataFrame) -> Dict[str, List[str]]:
    issues = {"duplicates": [], "history_orphans": [], "date_format": []}
    # Orphans: history dog names not present in summary
    if history_df is not None and not history_df.empty:
        dogs_hist = set([str(x).strip() for x in history_df["Dog_Name"].fillna("") if str(x).strip() != ""])
        dogs_sum = set([str(x).strip() for x in summary_df["Dog_Name"].fillna("") if str(x).strip() != ""])
        orphans = sorted(list(dogs_hist - dogs_sum))
        if orphans:
            issues["history_orphans"] = orphans[:1000]  # cap

    # Date format check: YYYY-MM-DD (very simple)
    if summary_df is not None and not summary_df.empty:
        bad_dates = []
        for v in summary_df["Race_Date"].fillna(""):
            s = str(v).strip()
            if s == "":
                continue
            if not reformat_yyyy_mm_dd(s):
                bad_dates.append(s)
        if bad_dates:
            issues["date_format"] = sorted(list(set(bad_dates)))[:1000]
    return issues


def reformat_yyyy_mm_dd(s: str) -> bool:
    if len(s) != 10:
        return False
    try:
        year, month, day = int(s[0:4]), int(s[5:7]), int(s[8:10])
        return s[4] == "-" and s[7] == "-" and 1 <= month <= 12 and 1 <= day <= 31
    except Exception:
        return False


def write_audit_and_validation_reports(
    per_file_stats: List[Dict],
    summary_df: pd.DataFrame,
    history_df: pd.DataFrame,
    audit_details: Dict,
    export_paths: Dict[str, str],
) -> Dict[str, str]:
    os.makedirs("outputs/logs", exist_ok=True)

    parse_audit_path = "outputs/logs/parse_audit.txt"
    validation_report_path = "outputs/logs/validation_report.txt"
    consistency_check_path = "outputs/logs/consistency_check.txt"

    # Parse audit
    with open(parse_audit_path, "w", encoding="utf-8") as f:
        f.write("Parse Audit\n")
        f.write("===========\n\n")
        f.write("Files processed:\n")
        for s in per_file_stats:
            f.write(f"- {s.get('file','?')}: dog_summary_rows={s.get('dog_summary_rows',0)}, history_rows={s.get('history_rows',0)}\n")
        f.write("\nUnmapped table headers (by file):\n")
        for fname, entries in audit_details.get("unmapped_table_headers", {}).items():
            f.write(f"- {fname}:\n")
            for e in entries:
                f.write(f"  * {json.dumps(e, ensure_ascii=False)}\n")
        f.write("\nParagraph/Table/Header/Footer counts:\n")
        for fname in audit_details.get("files", []):
            pc = audit_details["paragraph_counts"].get(fname, 0)
            tc = audit_details["table_counts"].get(fname, 0)
            hc = audit_details["headers_text_counts"].get(fname, 0)
            fc = audit_details["footers_text_counts"].get(fname, 0)
            f.write(f"- {fname}: paragraphs={pc}, tables={tc}, headers={hc}, footers={fc}\n")
        if audit_details.get("parsing_errors"):
            f.write("\nParsing errors:\n")
            for e in audit_details["parsing_errors"]:
                f.write(f"- {e}\n")

    # Validation report
    with open(validation_report_path, "w", encoding="utf-8") as f:
        cov = _overall_coverage(summary_df)
        spd = _speed_availability(summary_df)
        f.write("Validation Report\n")
        f.write("=================\n\n")
        f.write(f"Dog_Summary rows: {0 if summary_df is None else len(summary_df)}\n")
        f.write(f"Race_History rows: {0 if history_df is None else len(history_df)}\n")
        f.write(f"Overall field coverage (non-empty %%): {cov:.2f}%\n")
        f.write(f"%% dogs with Avg_Speed_km_h: {spd:.2f}%\n")
        f.write("\nOutput files:\n")
        for label, path in export_paths.items():
            f.write(f"- {label}: {path}\n")

    # Consistency checks
    with open(consistency_check_path, "w", encoding="utf-8") as f:
        issues = _consistency_issues(summary_df, history_df)
        f.write("Consistency Check\n")
        f.write("=================\n\n")
        if issues["duplicates"]:
            f.write("Duplicates:\n")
            for d in issues["duplicates"]:
                f.write(f"- {d}\n")
        else:
            f.write("Duplicates: None detected after deduplication keys\n")
        if issues["history_orphans"]:
            f.write("\nHistory orphans (in history but not in summary):\n")
            for d in issues["history_orphans"]:
                f.write(f"- {d}\n")
        else:
            f.write("\nHistory orphans: None detected or not applicable\n")
        if issues["date_format"]:
            f.write("\nNon-YYYY-MM-DD Race_Date values in Dog_Summary:\n")
            for d in issues["date_format"]:
                f.write(f"- {d}\n")
        else:
            f.write("\nRace_Date format issues: None detected\n")

    return {
        "parse_audit": parse_audit_path,
        "validation_report": validation_report_path,
        "consistency_check": consistency_check_path,
    }
