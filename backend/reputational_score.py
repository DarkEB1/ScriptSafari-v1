"""
NOTE: Full Network rankings (nearest neighbour score) is recalculated recursively (calculate for every connection starting from node with one connection, and don't revisit nodes) every epoch (addition of tot/10 nodes) or on command
Nodes without neighbours are given a default score of (50) for the nearest neighbour score
For author: Store top citation, calculate as percentage of top citation
General ranking: aggregate all sub scores, find as percentage of maximum possible score
"""

def defaultscore(articleinfo, maingraph):
    article = articleinfo['title']
    affiliations = articleinfo['affiliations']
    journal = articleinfo['journal_name']
    authors = articleinfo['authors']
    tot_aff_score = 0
    tot_auth_score = 0
    journalscore = (fetch_journal_rank(journal)/29166)*100
    for author in authors:
        cits = fetch_author_citations(author)
        if cits<authortopscore:
            tot_auth_score += (cits/authortopscore)*100
        else:
            authortopscore = cits
            tot_auth_score += (cits/authortopscore)*100
    tot_auth_score/len(authors)
    for affiliation in affiliations:
        tot_aff_score += (fetch_institution_rank(affiliation)/9055)*100
    tot_aff_score/len(affiliations)
    finalscore = (tot_aff_score+tot_auth_score+journalscore)/3
    finalscore = nearest_neighbour(article, maingraph, finalscore)
    return {article: finalscore}

def nearest_neighbour(article, maingraph, currentscore, visited=None):
    if visited is None:
        visited = set()
    visited.add(article)
    tocheck = maingraph.findconnections(article)
    avg = 0
    if tocheck == {}:
        return 50
    else:
        for node in tocheck:
            avg += maingraph.fetch_score(node)
        avg = avg/len(tocheck)
        currentscore = (currentscore+avg)/2
        maingraph.update_score(currentscore, article)
        for node in tocheck:
            if node not in visited:
                nearest_neighbour(node, maingraph, maingraph.fetch_score(node), visited)
