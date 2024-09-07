from scholarly import scholarly

#Use google's scholarly package to make an api call to google scholar and return number of citations
def fetch_author_citations(author_id):
    search_query = scholarly.search_author(author_id)
    author = next(search_query, None)
    
    if not author:
        return 0

    author_filled = scholarly.fill(author)
    if 'citedby' in author_filled:
        return int(author_filled['citedby'])
    else:
        return 0
