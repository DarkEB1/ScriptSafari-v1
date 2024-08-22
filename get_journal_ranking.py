

def string_similarity(journal, found_match, threshold=0.87) -> bool:
    #Difflib sequencematcher
    return SequenceMatcher(a=journal, b=found_match).ratio()>threshold

def fetch_journal_rank(journal) -> int:
    rank = -1
    with open('scimagojr 2023.csv', "r") as rank_list:
        for line in rank_list:
            rank += 1   
            start = line.find('"')
            cutoff = line[start+1:]
            end = cutoff.find('"')
            title = cutoff[:end]
            if string_similarity(journal.lower(), title.lower()):
                return rank
            