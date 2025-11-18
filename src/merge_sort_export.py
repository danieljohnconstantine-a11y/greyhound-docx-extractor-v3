"""
merge_sort_export.py — Enforces the locked SUMMARY_COLUMNS schema,
sorts rows, dedupes, and writes CSV + Excel.

Updated for new leading column order:
Race_Date → Track → Race_No → Dog_Name → Box
"""

import pandas as pd
from datetime import datetime
from src.columns import SUMMARY_COLUMNS


def _ensure_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure the DataFrame has exactly the columns in SUMMARY_COLUMNS,
    in the correct locked order.

    Any missing columns are added as blank strings.
    Any extra columns are dropped.
    """

    # Insert missing columns
    for col in SUMMARY_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    # Keep only schema columns (drop everything else)
    df = df[SUMMARY_COLUMNS]

    return df


def _dedupe_sort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort and dedupe the summary rows.

    New sort order matches the new leading schema order:

        1. Race_Date
        2. Track
        3. Race_No
        4. Dog_Name
        5. Box

    This ensures stable ordering across runs and consistent export.
    """

    sort_keys = ["Race_Date", "Track", "Race_No", "Dog_Name", "Box"]

    # Convert Race_No to numeric where possible so race 10 > race 2
    if "Race_No" in df.columns:
        df["Race_No"] = pd.to_numeric(df["Race_No"], errors="ignore")

    df = df.sort_values(sort_keys, na_position="last")

    # Deduplicate on full key to avoid accidental duplicates
    df = df.drop_duplicates(subset=sort_keys, keep="first")

    return df


def enforce_schema_and_export(summary_rows: list[dict], output_prefix: str):
    """
    Main export function.

    summary_rows: list of dicts from aggregation layer
    output_prefix: file prefix used for Excel + CSV (e.g. "outputs/all_dogs_master")

    Produces:
        <prefix>.csv
        <prefix>.xlsx
    """

    df = pd.DataFrame(summary_rows)

    # 1. Ensure correct schema
    df = _ensure_schema(df)

    # 2. Sort + dedupe
    df = _dedupe_sort(df)

    # 3. Apply parse timestamp column (if exists)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "Parse_Timestamp" in df.columns:
        df["Parse_Timestamp"] = timestamp

    # 4. Write CSV + Excel
    csv_path = f"{output_prefix}.csv"
    xlsx_path = f"{output_prefix}.xlsx"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_excel(xlsx_path, index=False)

    print(f"✔ Exported CSV → {csv_path}")
    print(f"✔ Exported Excel → {xlsx_path}")

    return df
