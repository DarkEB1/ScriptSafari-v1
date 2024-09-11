"""
NOTE: Full Network rankings (nearest neighbour score) is recalculated recursively (calculate for every connection starting from node with one connection, and don't revisit nodes) every epoch (addition of tot/10 nodes) or on command
Nodes without neighbours are given a default score of (50) for the nearest neighbour score
For author: Store top citation, calculate as percentage of top citation
General ranking: aggregate all sub scores, find as percentage of maximum possible score
"""

"""
Score from 1-100 on journal
Score from 1-100 on author based on number of citations (internal comparative ranking)
Score from 1-100 on Institution
Score from 1-100 by average score of connected nodes
Total score is aggregate of all/4
"""

from get_journal_ranking import *
from institution_ranking_scraper import *
from author_info_scraper import *
from graph import *

"""
This function generates the first time score for given node accordiong to scraped params, then calls neighbour score calc
"""
def defaultscore(articleinfo, maingraph, db):
    article = articleinfo['title']
    affiliations = articleinfo['affiliations'] or ''
    journal = articleinfo['journal_name'] or ''
    authors = articleinfo['authors']
    tot_aff_score = 0
    tot_auth_score = 0
    cursor = db.cursor()
    query = "SELECT content FROM graph WHERE cid = 3"
    cursor.execute(query)
    authortopscore = cursor.fetchone()
    cursor.close()
    authortopscore = int(authortopscore[0])
    journalscore = ((1-(fetch_journal_rank(journal)))/29166)*100
    print("journalscore"+str(journalscore))
    for author in authors:
        cits = fetch_author_citations(author) or 0
        if cits<authortopscore:
            tot_auth_score += (cits/authortopscore)*100
        else:
            authortopscore = cits
            cursor = db.cursor()
            query = "UPDATE graph SET content = %s WHERE cid = 3"
            cursor.execute(query, (str(authortopscore),))
            db.commit()
            cursor.close()
            tot_auth_score += (cits/authortopscore)*100
    tot_auth_score = tot_auth_score/len(authors) or 0
    print("authorscore"+str(tot_auth_score))
    for affiliation in affiliations:
        tot_aff_score += ((1-(fetch_institution_rank(affiliation)))/9055)*100
    if len(affiliations)==0:
        tot_aff_score = 0
    else:
        tot_aff_score = tot_aff_score/len(affiliations)
    print(tot_aff_score)
    finalscore = (tot_aff_score+tot_auth_score+journalscore)/3
    newscore = nearest_neighbour(article, maingraph, finalscore, db, visited=None)
    return {article: newscore}

#Recursively calculates score for each node as avg of nodes it is connected to, this recaclualtes the whole graph of nodes connected to the root node, stores the visited nodes so as not to revisit accidentally
def nearest_neighbour(article, maingraph, currentscore, db, visited=None):
    if visited is None:
        visited = set()
    visited.add(article)
    tocheck = maingraph.findconnections(article)
    avg = 0
    if len(tocheck) == 0:
        avg = 50
    else:
        for node in tocheck:
            avg += maingraph.fetch_score(node)
        avg = avg/len(tocheck)
    currentscore = (currentscore+avg)/2
    maingraph.update_score(currentscore, article)
    write_score(article, currentscore, db)
    for node in tocheck:
        if node not in visited:
            nearest_neighbour(node, maingraph, maingraph.fetch_score(node), db, visited)
    return currentscore
    #TODO write updated score to maingraph, and to database

#Write new score to database (Unfortunately quite inefficient as each request runs sequentially)
def write_score(article, score, db):
    cursor = db.cursor()
    update_query = """
            UPDATE `graph-entries`
            SET score = %s
            WHERE title = %s
        """
    cursor.execute(update_query, (score,article))
    db.commit()
    cursor.close()