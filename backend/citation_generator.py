from article_info_scrapers import *
import validators

class Citation_gen:
    #Citation generator in selected style, can be called without adding to graph prior to calling
    
    """
    @params int.style:citation style selection, str.link:link for article, dict.scraped_attributes: author, year, title, journal, issue, pages, doi (can be null), bool.processed:has issue been processed?
    """
    def __init__(self, style, link, scraped_attributes, processed) -> str:
        self.style = style
        if processed:
            self.attr = scraped_attributes
            self.link = link
        else:
            if validators.url(link):
                self.link = link
                self.attr = scrape(link)
            else: 
                out = "Invalid paper link"
                return out
        citation = self.generate_citation()
        return citation

    def generate_citation(self) -> str:
        style_function_map = {
            0: 'apa',
            1: 'chicago',
            2: 'cse',
            3: 'harvard'
        }
        for category in self.attr:
            if self.attr[category] is None:
                self.attr[category] = category.upper()
        func = style_function_map.get(self.style)
        if func:
            citation = func(self)
            return citation
        else:
            print(f"Invalid style: {self.style}")
    
    def apa(self) -> str:
        citation = self.attr['author'] + '. (' + self.attr['date'] + '). ' + self.attr['title'] + '. ' + self.attr['journal'] + ', ' + self.attr['issue'] + ', ' + self.attr['pages'] + '.\n' + self.link
        return citation

    def chicago(self) -> str:
        citation = self.attr['author'] + '. ' + self.attr['date'] + '. "' + self.attr['title'] + '." ' + self.attr['journal'] + ', no. ' + self.attr['issue'] + ': ' + self.attr['pages'] + '.\n' + self.link
        return citation

    def cse(self) -> str:
        citation = self.attr['author'] + '. ' + self.attr['date'] + '. ' + self.attr['title'] + '. ' + self.attr['journal'] + '. ' + self.attr['issue'] + ': ' + self.attr['pages'] + '.'
        return citation
    
    def harvard(self) -> str:
        citation = self.attr['author'] + '. (' + self.attr['date'] + '). \'' + self.attr['title'] + '\', ' + self.attr['journal'] + ', ' + self.attr['issue'] + ', pp. ' + self.attr['pages'] + '.\ndoi:' + self.attr['doi']
        return citation