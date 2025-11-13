import os
import glob
from tqdm import tqdm

from src import columns
from src.read_docx import load_docx
from src.parse_data import parse_meeting_header, parse_dog_entries, parse_history
from src.aggregate_history import aggregate_speeds
from src.merge_sort_export import enforce_schema_and_export
from src.validation_and_audit import write_audit_and_validation_reports


def ensure_directories():
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/logs", exist_ok=True)


def main():
    ensure_directories()

    docx_files = sorted(glob.glob(os.path.join("data", "*.docx")))
    per_file_stats = []
    all_summary_rows = []
    all_history_rows = []
    audit_details = {
        "files": [],
        "unmapped_table_headers": {},
        "parsing_errors": [],
        "paragraph_counts": {},
        "table_counts": {},
        "headers_text_counts": {},
        "footers_text_counts": {},
    }

    if not docx_files:
        print("No DOCX files found in ./data. Place files there and re-run.")
    else:
        print(f"Found {len(docx_files)} DOCX file(s). Processing...")

    for fp in tqdm(docx_files, desc="Processing DOCX files"):
        file_name = os.path.basename(fp)
        try:
            doc_data = load_docx(fp)
            audit_details["files"].append(file_name)
            audit_details["paragraph_counts"][file_name] = len(doc_data.get("paragraphs", []))
            audit_details["table_counts"][file_name] = len(doc_data.get("tables", []))
            audit_details["headers_text_counts"][file_name] = len(doc_data.get("headers", []))
            audit_details["footers_text_counts"][file_name] = len(doc_data.get("footers", []))

            meeting = parse_meeting_header(doc_data)

            dog_rows, unmapped_headers = parse_dog_entries(doc_data, meeting)
            for k, v in unmapped_headers.items():
                audit_details["unmapped_table_headers"].setdefault(file_name, []).append({k: v})

            history_rows = parse_history(doc_data, meeting)

            all_summary_rows.extend(dog_rows)
            all_history_rows.extend(history_rows)

            per_file_stats.append(
                {
                    "file": file_name,
                    "dog_summary_rows": len(dog_rows),
                    "history_rows": len(history_rows),
                }
            )
        except Exception as e:
            audit_details["parsing_errors"].append(f"{file_name}: {repr(e)}")

    # Aggregate per-dog speed metrics (dependent on history)
    all_summary_rows = aggregate_speeds(all_summary_rows, all_history_rows)

    # Export and enforce schema
    export_paths, summary_df, history_df = enforce_schema_and_export(
        all_summary_rows, all_history_rows
    )

    # Validation + Audit
    reports = write_audit_and_validation_reports(
        per_file_stats=per_file_stats,
        summary_df=summary_df,
        history_df=history_df,
        audit_details=audit_details,
        export_paths=export_paths,
    )

    # Print console summary matching the PR comment requirements
    num_files = len(docx_files)
    num_dog_rows = len(summary_df) if summary_df is not None else 0
    num_history_rows = len(history_df) if history_df is not None else 0
    speed_availability = 0.0
    if num_dog_rows > 0:
        speed_availability = (
            (summary_df["Avg_Speed_km_h"].notna() & (summary_df["Avg_Speed_km_h"] != "")).sum()
            / num_dog_rows
            * 100.0
        )

    print("\nPipeline Summary")
    print("----------------")
    print(f"Number of files processed: {num_files}")
    print(f"Number of dog summary rows: {num_dog_rows}")
    print(f"Number of history rows: {num_history_rows}")
    print(f"% of dogs with valid speed data: {speed_availability:.2f}%")
    print("Outputs:")
    for label, path in export_paths.items():
        print(f"- {label}: {path}")
    print("Logs:")
    for label, path in reports.items():
        print(f"- {label}: {path}")


if __name__ == "__main__":
    main()
