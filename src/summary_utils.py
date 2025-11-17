import pandas as pd
import re


def normalize_summary_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize key dog-level fields so they match SUMMARY_COLUMNS exactly.
    This introduces no schema creep and keeps legacy fields intact.

    Fields normalized:
        - WT (kg)
        - A/S
        - Prize_Money
        - Career_W-P-S
    """

    out = df.copy()

    # -------------------------------------------
    # 1. Weight → WT (kg)
    # -------------------------------------------
    if "Weight_kg" in out.columns and "WT (kg)" not in out.columns:
        out["WT (kg)"] = out["Weight_kg"].astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
    elif "WT (kg)" in out.columns:
        out["WT (kg)"] = out["WT (kg)"].astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
    else:
        out["WT (kg)"] = ""

    # -------------------------------------------
    # 2. Age + Sex → A/S
    # -------------------------------------------
    age_col = None
    sex_col = None

    for c in out.columns:
        if c.lower() in ["age", "age_months", "age_mths", "dog_age"]:
            age_col = c
        if c.lower() in ["sex", "gender"]:
            sex_col = c

    age_val = out[age_col].astype(str) if age_col else ""
    sex_val = out[sex_col].astype(str).str.upper().str[0] if sex_col else ""

    if age_col or sex_col:
        out["A/S"] = (age_val + sex_val).str.strip()
    else:
        out["A/S"] = ""

    # -------------------------------------------
    # 3. Prize Money → Prize_Money
    # -------------------------------------------
    if "PrizeMoney" in out.columns:
        source = out["PrizeMoney"]
    elif "Prize" in out.columns:
        source = out["Prize"]
    else:
        source = ""

    cleaned = (
        source.astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+\.?\d*)", expand=False)
    )

    out["Prize_Money"] = cleaned.fillna("")

    # -------------------------------------------
    # 4. Career fields → Career_W-P-S
    # -------------------------------------------
    wins = out["Wins"].astype(str) if "Wins" in out.columns else ""
    places = out["Places"].astype(str) if "Places" in out.columns else ""
    starts = out["Starts"].astype(str) if "Starts" in out.columns else ""

    if "Wins" in out.columns or "Places" in out.columns or "Starts" in out.columns:
        out["Career_W-P-S"] = wins + "-" + places + "-" + starts
        out["Career_W-P-S"] = out["Career_W-P-S"].str.strip("-")
    else:
        out["Career_W-P-S"] = ""

    # Fill missing columns if they don't exist yet
    for col in ["WT (kg)", "A/S", "Prize_Money", "Career_W-P-S"]:
        if col not in out.columns:
            out[col] = ""

    return out
