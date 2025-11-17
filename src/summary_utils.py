import pandas as pd
import re


def normalize_summary_fields(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    # --------------------------------------------------------
    # 0. Distance_m (NEW) - force to integer meters
    # --------------------------------------------------------
    if "Distance_m" in out.columns:
        cleaned = []
        for v in out["Distance_m"]:
            if v is None or str(v).strip() == "":
                cleaned.append("")
                continue
            s = str(v)
            m = re.search(r"\b(\d{2,4})\b", s)
            cleaned.append(m.group(1) if m else "")
        out["Distance_m"] = cleaned
    else:
        out["Distance_m"] = ""

    # --------------------------------------------------------
    # 1. Race_Grade (NEW) - strip noise + normalize
    # --------------------------------------------------------
    if "Race_Grade" in out.columns:
        normalized = []
        for v in out["Race_Grade"]:
            if v is None or str(v).strip() == "":
                normalized.append("")
                continue
            s = str(v).strip().upper()

            # Remove noise
            s = s.replace("GRADE", "")
            s = s.replace("GRD", "")
            s = re.sub(r"\s+", "", s)

            # Canonical mappings
            aliases = {
                "5TH": "5",
                "5THGRADE": "5",
                "FIFTHGRADE": "5",
                "4TH": "4",
                "4THGRADE": "4",
                "3RD": "3",
                "3RDGRADE": "3",
                "2ND": "2",
                "2NDGRADE": "2",
                "1ST": "1",
                "1STGRADE": "1",
                "MAIDEN": "M",
                "M": "M",
                "NOVICE": "NOV",
                "NOV": "NOV",
                "OPEN": "OPEN",
                "NG": "NG",
                "NMW": "NMW",
                "SE": "SE",
            }

            normalized.append(aliases.get(s, s))
        out["Race_Grade"] = normalized
    else:
        out["Race_Grade"] = ""

    # --------------------------------------------------------
    # 2. WT (kg)
    # --------------------------------------------------------
    if "Weight_kg" in out.columns and "WT (kg)" not in out.columns:
        out["WT (kg)"] = out["Weight_kg"].astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
    elif "WT (kg)" in out.columns:
        out["WT (kg)"] = out["WT (kg)"].astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
    else:
        out["WT (kg)"] = ""

    # --------------------------------------------------------
    # 3. A/S
    # --------------------------------------------------------
    age_col = None
    sex_col = None
    for c in out.columns:
        l = c.lower()
        if l in ["age", "age_months", "age_mths", "dog_age"]:
            age_col = c
        if l in ["sex", "gender"]:
            sex_col = c

    age_val = out[age_col].astype(str) if age_col else ""
    sex_val = out[sex_col].astype(str).str.upper().str[0] if sex_col else ""
    if age_col or sex_col:
        out["A/S"] = (age_val + sex_val).str.strip()
    else:
        out["A/S"] = ""

    # --------------------------------------------------------
    # 4. Prize_Money
    # --------------------------------------------------------
    if "PrizeMoney" in out.columns:
        source = out["PrizeMoney"]
    elif "Prize" in out.columns:
        source = out["Prize"]
    else:
        source = ""

    cleaned_pm = (
        source.astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+\.?\d*)", expand=False)
    )
    out["Prize_Money"] = cleaned_pm.fillna("")

    # --------------------------------------------------------
    # 5. Career_W-P-S
    # --------------------------------------------------------
    wins = out["Wins"].astype(str) if "Wins" in out.columns else ""
    places = out["Places"].astype(str) if "Places" in out.columns else ""
    starts = out["Starts"].astype(str) if "Starts" in out.columns else ""
    if "Wins" in out.columns or "Places" in out.columns or "Starts" in out.columns:
        out["Career_W-P-S"] = (wins + "-" + places + "-" + starts).str.strip("-")
    else:
        out["Career_W-P-S"] = ""

    # --------------------------------------------------------
    # 6. Tab_No
    # --------------------------------------------------------
    if "Tab_No" in out.columns:
        out["Tab_No"] = out["Tab_No"].astype(str).str.extract(r"(\d+)", expand=False).fillna("")
    else:
        out["Tab_No"] = ""

    # --------------------------------------------------------
    # 7. FF_Form
    # --------------------------------------------------------
    if "FF_Form" in out.columns:
        out["FF_Form"] = out["FF_Form"].astype(str).str.replace(" ", "")
    else:
        out["FF_Form"] = ""

    # --------------------------------------------------------
    # 8. BP
    # --------------------------------------------------------
    if "BP" in out.columns:
        out["BP"] = out["BP"].astype(str)
    else:
        out["BP"] = ""

    # --------------------------------------------------------
    # 9. DLR / DLW / RTC
    # --------------------------------------------------------
    for c in ["DLR", "DLW", "RTC"]:
        if c in out.columns:
            out[c] = out[c].astype(str).str.extract(r"(\d+)", expand=False).fillna("")
        else:
            out[c] = ""

    # --------------------------------------------------------
    # 10. Sire / Dam / Owner
    # --------------------------------------------------------
    for c in ["Sire", "Dam", "Owner"]:
        if c in out.columns:
            out[c] = out[c].astype(str).str.strip()
        else:
            out[c] = ""

    # --------------------------------------------------------
    # Ensure all required columns exist
    # --------------------------------------------------------
    required = [
        "Distance_m", "Race_Grade",
        "WT (kg)", "A/S", "Prize_Money", "Career_W-P-S",
        "Tab_No", "FF_Form", "BP", "DLR", "DLW", "RTC",
        "Sire", "Dam", "Owner"
    ]
    for col in required:
        if col not in out.columns:
            out[col] = ""

    return out
