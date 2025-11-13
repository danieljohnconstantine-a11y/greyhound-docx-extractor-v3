import os
import pandas as pd
from typing import List, Dict, Tuple

from . import columns as C


def _ensure_schema(rows: List[Dict[str, str]]) -> pd.DataFrame:
    # Ensure all keys exist and extra keys are ignored; no assumptions -> blanks for missing
    normalized = []
    for r in rows:
        row = {k: r.get(k, "") for k in C.SUMMARY_COLUMNS}
        normalized.append(row)
    df = pd.DataFrame(normalized, columns=C.SUMMARY_COLUMNS)
    # Avoid NaN in exports
    return df.fillna("")


def _ensure_history_schema(rows: List[Dict[str, str]]) -> pd.DataFrame:
    normalized = []
    for r in rows:
        row = {k: r.get(k, "") for k in C.HISTORY_COLUMNS}
        normalized.append(row)
    df = pd.DataFrame(normalized, columns=C.HISTORY_COLUMNS)
    return df.fillna("")


def _dedupe_sort(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Deduplicate on (Track, Race_Date, Race_No, Box, Dog_Name)
    df = df.drop_duplicates(subset=list(C.DEDUPE_KEYS), keep="first")

    # Sorting keys: Track → Race_Date → Race_No → Box
    df["_Race_No"] = pd.to_numeric(df["Race_No"], errors="coerce")
    df["_Box"] = pd.to_numeric(df["Box"], errors="coerce")
    df = df.sort_values(by=["Track", "Race_Date", "_Race_No", "_Box"], kind="mergesort")
    df = df.drop(columns=["_Race_No", "_Box"])
    return df


def enforce_schema_and_export(
    summary_rows: List[Dict], history_rows: List[Dict]
) -> Tuple[Dict[str, str], pd.DataFrame, pd.DataFrame]:
    os.makedirs("outputs", exist_ok=True)

    summary_df = _ensure_schema(summary_rows)
    summary_df = _dedupe_sort(summary_df)

    history_df = _ensure_history_schema(history_rows)

    # Export
    excel_path = os.path.join("outputs", "all_dogs_master.xlsx")
    csv_path = os.path.join("outputs", "all_dogs_master.csv")

    # CSV must match Dog_Summary sheet exactly
    summary_df.to_csv(csv_path, index=False)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Dog_Summary", index=False)
        history_df.to_excel(writer, sheet_name="Race_History", index=False)

    return {"excel": excel_path, "csv": csv_path}, summary_df, history_df
