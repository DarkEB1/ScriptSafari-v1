
from difflib import SequenceMatcher

def journal_similarity(journal, found_match, threshold=0.87) -> bool:
    #Difflib sequencematcher, this returns a similarityscore between two text entries, if they are similar enough, it returns true
    return SequenceMatcher(a=journal, b=found_match).ratio()>threshold

#Return the line number of where the journal is found, this will be used in the ranking later
def fetch_journal_rank(journal) -> int:
    rank = -1
    with open('/workspaces/ScriptSafari-v1/backend/journals.csv', "r") as rank_list:
        for line in rank_list:
            rank += 1   
            start = line.find('"')
            cutoff = line[start+1:]
            end = cutoff.find('"')
            title = cutoff[:end]
            if journal_similarity(journal.lower(), title.lower()):
                return rank
        return 0