import requests
from bs4 import BeautifulSoup
import json
import re

def get_soup(url)  -> object:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as er:
        print(f"Error fetching the URL: {er}")
        return None

#meta tag scraping called by generic scrape
def extract_meta_content(soup, name=None, property=None) -> str:
    if name:
        meta_tag = soup.find("meta", {"name": name})
    else:
        meta_tag = soup.find("meta", {"property": property})
    if meta_tag:
        return meta_tag.get("content")
    return None

    #Generic scraper for non-DOI journal articles.
def generic_scrape(url) -> dict:
    soup = get_soup(url)
    if not soup:
        return None
    
    if soup.find("h1"):
        title = extract_meta_content(soup, name="citation_title") or extract_meta_content(soup, property="og:title") or soup.find("h1").get_text(strip=True)  
    else:
        title = None

    author_meta_tags = soup.find_all("meta", {"name": "citation_author"})
    if author_meta_tags:
        for tag in author_meta_tags:
        authors = tag["content"] 
    else:
        authors = None
    if not authors:
        author_tags = soup.select(".author-name, .authors-name, .author, .contributor")
        if author_meta_tags:
            for tag in author_tags:
                authors = tag.get_text(strip=True)
        else:
            authors = None

    pub_date = extract_meta_content(soup, name="citation_publication_date") or extract_meta_content(soup, name="citation_date") or extract_meta_content(soup, property="article:published_time") or None

    if soup.find("meta", {"property": "og:journal_volume"}):
        journal_volume = extract_meta_content(soup, name="citation_volume") or soup.find("meta", {"property": "og:journal_volume"})["content"]
    else:
        journal_volume = None

    if extract_meta_content(soup, name="citation_firstpage") and extract_meta_content(soup, name="citation_lastpage"):
        journal_pages = extract_meta_content(soup, name="citation_firstpage") + "-" + extract_meta_content(soup, name="citation_lastpage")
    else:
        journal_pages = None

    # Attempt to find JSON-LD structured data
    json_ld_data = soup.find('script', type='application/ld+json')
    if json_ld_data:
        try:
            json_data = json.loads(json_ld_data.string)
            title = json_data.get("headline", title)
            if isinstance(json_data.get("author", []), list)
                authors = [author.get("name", "") for author in json_data.get("author", [])]
            pub_date = json_data.get("datePublished", pub_date)
            journal_volume = json_data.get("volumeNumber", journal_volume)
            journal_pages = json_data.get("pagination", journal_pages)
        except json.JSONDecodeError as err:
            print(f"Error parsing JSON-LD: {err}")

    if soup.find("meta", property="og:site_name"):
        journal_name = extract_meta_content(soup, name="citation_journal_title") or soup.find("meta", property="og:site_name").get("content")
    else:
        journal_name = None
    
    attributes = {
        "title": title,
        "authors": authors,
        "publication_date": pub_date,
        "journal_name": journal_name,
        "journal_volume": journal_volume,
        "journal_pages": journal_pages
    }
    return attributes

def extract_doi(url):
    doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
    match = doi_pattern.search(url)
    if match:
        return match.group(0)
    else:
        return None

def doi_scrape(doi) -> dict:
    header = {
        "Accept": "application/vnd.citationstyles.csl+json"
    }
    doiapi = f"https://doi.org/{doi}"
    response = requests.get(doiapi, headers=header)
    if response.status_code == 200:
        raw = response.json()
        attributes = {
            "title": raw.get('title'),
            "authors": [author['family'] + ", " + author.get('given', '') for author in raw.get("author", [])],
            "publication_date": raw.get("issued").get("date-parts")[0] if raw.get("issued") else "N/A",
            "journal_name": raw.get('container-title'),
            "journal_volume": raw.get('volume'),
            "journal_pages": raw.get('page')
        }
        return attributes
    else:
        return None


url = "https://example-academic-article.com"
doi = extract_doi(url)

if doi:
    article_data = doi_scrape(doi) 
else:
    article_data = arxiv_scrape(url) or google_scholar_scrape(url) or generic_scrape(url) or None

if article_data:
    print(json.dumps(article_data, indent=2))
else:
    print("Failed to scrape the article. Enter Manually?")
    #Prompt user for manual information entry
