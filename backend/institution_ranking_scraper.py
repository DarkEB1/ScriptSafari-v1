from get_journal_ranking import journal_similarity

def fetch_institution_rank(instiution) -> int:
    rank = -1
    with open('institutions.csv', "r") as rank_list:
        for line in rank_list:
            rank += 1   
            start = line.find(',')
            cutoff = line[start+1:]
            end = cutoff.find(',')
            title = cutoff[:end]
            if journal_similarity(instiution.lower(), title.lower()):
                return rank
        return 0
    
