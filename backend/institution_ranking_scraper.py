import csv
from get_journal_ranking import journal_similarity
import re

def parse_institution_string(institution_str):
    # Regex pattern for parsing institutions
    pattern = re.compile(r"""
        (?P<institution>.*?),\s*   # Matches institution name before the first comma
        (?P<city>[^\d,]+),\s*      # Matches city name before the zip code
        (?P<state_zip_country>.*)   # Matches the rest
    """, re.VERBOSE)
    match = pattern.match(institution_str)
    if match:
        institution = match.group('institution').strip()
        city = match.group('city').strip()
        state_zip_country = match.group('state_zip_country').strip()
        parts = state_zip_country.split(',')
        if len(parts) == 1:
            state = None
            zip_code = None
            country = parts[0].strip()
        else:
            state_zip = parts[0].strip().split()
            if len(state_zip) == 2:
                state = state_zip[0]
                zip_code = state_zip[1]
            else:
                state = None
                zip_code = state_zip[0]
            country = parts[1].strip() if len(parts) > 1 else None
        
        return {
            'institution': institution,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'country': country
        }
    
    return None

def fetch_institution_rank(institution: str) -> int:
    rank = 0 
    out = parse_institution_string(institution)
    institution = out["institution"]
    institution2 = out["city"]
    with open('/workspaces/ScriptSafari-v1/backend/institutions.csv', "r") as rank_list:
        csv_reader = csv.reader(rank_list)
        for line in csv_reader:
            rank += 1
            if len(line) > 1:
                title = line[1].strip()
                if journal_similarity(institution.lower(), title.lower()) or journal_similarity(institution2.lower(), title.lower()):
                    return rank
        return 0