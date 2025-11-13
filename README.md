# greyhound-docx-extractor-v3

A complete DOCX-to-Excel/CSV extraction system for Australian greyhound race forms. Guaranteed 100% data capture into a strict 58-column schema, including dog summaries, race metadata, historical performance records, and validation/audit reports. Built clean from scratch for reliability and accuracy.

## Project Objective

Create an automated pipeline that:

- Reads all .DOCX race form files placed in the `/data/` folder.
- Extracts 100% of visible data from the documents (text, tables, headers/footers) for each dog entry and its full history.
- Produces two main outputs:
  - `outputs/all_dogs_master.xlsx` (single workbook, two sheets: Dog_Summary & Race_History)
  - `outputs/all_dogs_master.csv` (matching the Dog_Summary sheet exactly)
- Uses a strict locked schema (58 columns) defined in `src/columns.py`, in the exact order.
- Includes audit logs and validation reports to verify coverage, correctness, and data quality — no assumed values, no defaults.

## Architecture

- `src/read_docx.py`: Loads each .docx file, extracts paragraphs, tables, headers/footers.
- `src/parse_data.py`: Parses meeting header, dog entry tables, and history sections.
- `src/aggregate_history.py`: Computes per-dog history aggregates (count and speeds) using only valid time+distance rows.
- `src/merge_sort_export.py`: Enforces schema, dedupes, sorts, and exports Excel/CSV.
- `src/validation_and_audit.py`: Writes `outputs/logs/parse_audit.txt`, `validation_report.txt`, `consistency_check.txt`.
- `main.py`: Orchestrates end-to-end run.

## Data Guarantees

- No assumptions: Missing/unavailable fields remain blank.
- 100% capture of visible DOCX data (paragraphs, tables, headers/footers). Any unmapped items are logged.
- Speed metrics computed only when both distance (m) and time (s) exist.
- Deduplication on `(Track, Race_Date, Race_No, Box, Dog_Name)`.

## Running Locally

1. Place `.docx` files into `./data`.
2. Create a Python 3.11 environment.
3. Install requirements: `pip install -r requirements.txt`.
4. Run: `python main.py`.
5. Outputs are written to `./outputs`, logs to `./outputs/logs`.

## CI

A GitHub Actions workflow runs the pipeline on pull requests to `main`, uploads artifacts, and posts a PR comment with a run summary.
