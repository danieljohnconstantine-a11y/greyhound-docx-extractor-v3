# src/parse_data.py

import re
from datetime import datetime
from summary_utils import normalize_summary_fields
from columns import SUMMARY_COLUMNS

def parse_meeting_info(paragraphs):
    """
    Extract meeting-level fields from the DOCX paragraphs.
    Returns a dict with Race_Date, Track, Race_No, Race_Name, Distance_m, Race_Grade, etc.
    """
    meeting_info = {}
    text = " ".join(p.text for p in paragraphs if p.text.strip())
    
    # Example regex patterns (customize as needed):
    # Date: look for dd/mm/yyyy
    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
    if date_match:
        raw_date = date_match.group(1)
        # Convert to YYYY-MM-DD
        meeting_info["Race_Date"] = datetime.strptime(raw_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    # Track: assume a known track name appears after date
    track_match = re.search(r'\d{1,2}/\d{1,2}/\d{4}\s+([A-Za-z]+)', text)
    if track_match:
        meeting_info["Track"] = track_match.group(1)
    # Race Number and Name: typically near top as "Race X. NAME"
    race_match = re.search(r'Race\s*No\.?\s*(\d+).*?Name:\s*([^0-9]+)', text)
    if race_match:
        meeting_info["Race_No"] = int(race_match.group(1))
        meeting_info["Race_Name"] = race_match.group(2).strip()
    # Distance: look for number followed by "m"
    dist_match = re.search(r'Distance\s*(\d+)\s*m', text)
    if dist_match:
        meeting_info["Distance_m"] = int(dist_match.group(1))
    # Grade: e.g. "GR 5/6 Race"
    grade_match = re.search(r'GR\s*([\d/]+)', text)
    if grade_match:
        meeting_info["Race_Grade"] = grade_match.group(1)
    # Race time (if given as time of day, e.g. "Race Time 14:30")
    time_match = re.search(r'Race Time\s*([0-9]{1,2}:[0-9]{2})', text)
    if time_match:
        meeting_info["Race_Time"] = time_match.group(1)  # already HH:MM
    return meeting_info

def parse_dog_section(dog_text):
    """
    Parse a block of text corresponding to one dog in the race summary.
    Returns a dict of extracted fields for that dog.
    """
    dog_info = {}
    # Dog Name is usually the first line (all caps, may include spaces)
    lines = [line.strip() for line in dog_text.strip().splitlines() if line.strip()]
    if not lines:
        return dog_info
    
    # First line should be the dog name
    dog_info["Dog_Name"] = lines[0].strip().title()
    
    # Attempt to parse the line with weight, age, colour, box, sex, trainer, career stats
    # e.g. "0kg (4) bl 2 D TrainerName Horse: 7-22-56 12%-51%"
    pattern = re.compile(
        r'(?P<weight>\d+kg)?\s*\((?P<age>\d+)\)\s+'
        r'(?P<colour>[A-Za-z/]+)\s+'
        r'(?P<box>\d+)\s+'
        r'(?P<sex>[DB])\s+'
        r'(?P<trainer>[A-Za-z ]+?)\s+Horse:\s+'
        r'(?P<stats>(\d+-)+\d+)\s+'
        r'(?P<win_pct>\d+)%-(?P<place_pct>\d+)%'
    )
    detail_line = lines[1] if len(lines) > 1 else ""
    m = pattern.search(detail_line)
    if m:
        dog_info["Age"] = int(m.group("age"))
        dog_info["ColourCode"] = m.group("colour")
        dog_info["Box"] = int(m.group("box"))
        dog_info["Sex"] = m.group("sex")
        dog_info["Trainer"] = m.group("trainer").strip().title()
        # Parse career stats
        stats_str = m.group("stats")  # e.g. "7-22-56"
        stats_parts = stats_str.split('-')
        if len(stats_parts) == 3:
            dog_info["Career_Wins"] = int(stats_parts[0])
            dog_info["Career_Seconds"] = int(stats_parts[1])
            dog_info["Career_Thirds"] = 0  # If not provided, default 0
            dog_info["Career_Starters"] = int(stats_parts[2])
        dog_info["Win_Percent"] = int(m.group("win_pct"))
        dog_info["Place_Percent"] = int(m.group("place_pct"))
    # Owner: often on the line after trainer/stats
    for line in lines:
        if line.startswith("Owner:"):
            owner_name = line.split("Owner:")[1].strip()
            dog_info["Owner"] = owner_name.title()
            break
    
    # Prize and odds for this race (from a line like "Prize $X Odds Y Trainer ...")
    race_line = next((l for l in lines if "Prize" in l and "Odds" in l), "")
    prize_match = re.search(r'Prize\s*\$(?P<prize>\d+)', race_line)
    if prize_match:
        dog_info["PrizeMoneyWon"] = int(prize_match.group("prize"))
    odds_match = re.search(r'Odds\s*([\d\.]+)', race_line)
    if odds_match:
        dog_info["Odds"] = float(odds_match.group(1))
    return dog_info

def parse_data(doc):
    """
    Main function to parse a DOCX race file and extract summary fields.
    Returns a list of dicts, one per dog, with keys from SUMMARY_COLUMNS.
    """
    from docx import Document
    document = Document(doc)
    paragraphs = document.paragraphs
    
    # Extract meeting-level info
    meeting_info = parse_meeting_info(paragraphs)
    
    records = []
    # Split the document into sections for each dog (based on known markers, e.g. dog names or sequence numbers)
    text = "\n".join(p.text for p in paragraphs)
    dog_sections = re.split(r'\n\d+\.\s*\n', text)  # split on patterns like "1." "2." etc.
    for section in dog_sections:
        section = section.strip()
        if not section:
            continue
        dog_info = parse_dog_section(section)
        if not dog_info.get("Dog_Name"):
            continue
        # Combine meeting and dog info, then normalize
        record = {**meeting_info, **dog_info}
        # Ensure all expected keys exist; fill missing with empty string
        for key in SUMMARY_COLUMNS:
            record.setdefault(key, "")
        # Normalize and append
        records.append(normalize_summary_fields(record))
    return records
