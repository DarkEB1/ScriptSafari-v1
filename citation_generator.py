class Citation_gen:
    #Citation generator in selected style, can be called without adding to graph prior to calling
    
    """
    @params int.style:citation style selection, str.link:link for article, list.scraped_attributes: authors, year, title, journal, issue, pages (can be null), bool.processed:has issue been processed?
    """
    def __init__(self, style, link, scraped_attributes, processed) -> str:
        self.style = style
        if processed:
            self.attr = scraped_attributes
            self.link = link
        else:
            if validators.url(link):
                self.link = link
                self.attr = #CALL SCRAPERS HERE
            else: 
                out = "Invalid paper link"
                return out
        citation = generate_citation():
        return citation

    def generate_citation(self) -> str:
        #Check for null in attributes, if any null, ask for these parameters to be entered
        #When all entered, generate according to style
        #return according to style