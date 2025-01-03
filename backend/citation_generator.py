from article_info_scrapers import *
import validators

class Citation_gen:
    #Citation generator in selected style, can be called without adding to graph prior to calling
    
    """
    @params int.style:citation style selection, str.link:link for article, dict.scraped_attributes: author, year, title, journal, issue, pages, doi (can be null), bool.processed:has issue been processed?
    """
    def __init__(self, style, link, scraped_attributes):
        self.style = style
        self.attr = scraped_attributes
        self.link = link
        
    #Map input from frontend to function in selected style, concatenate scarped info to form citation in given style
    def generate_citation(self) -> str:
        style_function_map = {
            'apa': self.apa,
            'chicago': self.chicago,
            'cse': self.cse,
            'harvard': self.harvard
        }
        for category in self.attr:
            if self.attr[category] is None:
                self.attr[category] = category.upper()
        func = style_function_map.get(self.style)
        if func:
            citation = func()
            return citation
        else:
            print(f"Invalid style: {self.style}")
            return "INVALID"
    
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