import os
import glob
from typing import List, Dict

import pandas as pd

from src.parse_data import parse_docx
from src.aggregate_history import aggregate_speeds
from src.snapshot_joiner import inject_snapshot
from src.merge_sort_export import enforce_schema_and_export


DATA_DIR = "data"
OUTPUT_PREFIX = os.path.join("outputs", "all_dogs_master")


def find_docx_files(data_dir: str = DATA_DIR) -> List[str]:
    """
    Find all .docx files under data_dir (recursively).
    """
    pattern = os.path.join(data_dir, "**", "*.docx")
    files = glob.glob(pattern, recursive=True)
    return sorted(files)


def main():
    docx_files = find_docx_files()
    if not docx_files:
        print(f"⚠ No DOCX files found under {DATA_DIR}/")
        return

    all_summary_rows: List[Dict] = []
    all_history_rows: List[Dict] = []

    print("📄 Processing DOCX files:")
    for path in docx_files:
        print(f"  - {path}")
        try:
            summary_df, hist_rows = parse_docx(path)
        except Exception as e:
            print(f"    ❌ Error parsing {path}: {e}")
            continue

        # Collect summary rows as dicts
        if not summary_df.empty:
            all_summary_rows.extend(summary_df.to_dict(orient="records"))

        # Collect history rows (already list[dict])
        if hist_rows:
            all_history_rows.extend(hist_rows)

    if not all_summary_rows:
        print("⚠ No dog summary rows parsed from any DOCX file.")
        return

    print(f"✅ Parsed {len(all_summary_rows)} dog summary rows from {len(docx_files)} files.")
    print(f"✅ Parsed {len(all_history_rows)} history rows total.")

    # --------------------------------------------------
    # 1) Aggregate speeds from history → summary rows
    # --------------------------------------------------
    all_summary_rows = aggregate_speeds(all_summary_rows, all_history_rows)

    # --------------------------------------------------
    # 2) Inject most recent run snapshot into summary
    # --------------------------------------------------
    all_summary_rows = inject_snapshot(all_summary_rows, all_history_rows)

    # --------------------------------------------------
    # 3) Enforce schema, sort, export CSV + Excel
    # --------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PREFIX), exist_ok=True)
    df_out = enforce_schema_and_export(all_summary_rows, OUTPUT_PREFIX)

    # --------------------------------------------------
    # 4) Basic validation / console summary
    #    (NO invented race data – just counts and %)
    # --------------------------------------------------
    total_rows = len(df_out)
    print(f"\n📊 Final Dog_Summary rows: {total_rows}")

    # Unique dogs by (Race_Date, Track, Race_No, Dog_Name)
    uniq_cols = ["Race_Date", "Track", "Race_No", "Dog_Name"]
    unique_dogs = df_out[uniq_cols].drop_duplicates().shape[0]
    print(f"📌 Unique dogs (Race_Date, Track, Race_No, Dog_Name): {unique_dogs}")

    # Dogs with ≥1 history row (Hist_Count > 0)
    if "Hist_Count" in df_out.columns:
        hist_counts = pd.to_numeric(df_out["Hist_Count"], errors="coerce").fillna(0)
        dogs_with_hist = (hist_counts > 0).sum()
        pct_hist = (dogs_with_hist / total_rows) * 100 if total_rows else 0
        print(f"📈 Dogs with history (Hist_Count > 0): {dogs_with_hist} ({pct_hist:.1f}%)")
    else:
        print("⚠ Hist_Count column missing in output (check aggregate_history.py).")

    # Dogs with valid Avg_Speed_km/h (NOTE: correct slash name)
    if "Avg_Speed_km/h" in df_out.columns:
        has_speed = df_out["Avg_Speed_km/h"].apply(lambda x: str(x).strip() != "").sum()
        pct_speed = (has_speed / total_rows) * 100 if total_rows else 0
        print(f"🚀 Dogs with Avg_Speed_km/h populated: {has_speed} ({pct_speed:.1f}%)")
    else:
        print("⚠ Avg_Speed_km/h column missing in output (check aggregate_history.py).")

    print("\n🎯 Pipeline complete.")


if __name__ == "__main__":
    main()
