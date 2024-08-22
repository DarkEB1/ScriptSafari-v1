import requests
from bs4 import BeautifulSoup
import json
import re
import xml.etree.ElementTree as et

def get_soup(url)  -> object:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as er:
        print(f"Error fetching the URL: {er}")
        return None

#meta tag scraping
def extract_meta_content(soup, name=None, property=None) -> str:
    if name:
        meta_tag = soup.find("meta", {"name": name})
    else:
        meta_tag = soup.find("meta", {"property": property})
    if meta_tag:
        return meta_tag.get("content")
    return None

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
        if author_tags:
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
            if isinstance(json_data.get("author", []), list):
                authors = [author.get("name", "") for author in json_data.get("author", [])]
                affiliations = [author.get("affiliation", {}).get("name", "") for author in json_data.get("author", []) if author.get("affiliation")]
            pub_date = json_data.get("datePublished", pub_date)
            journal_volume = json_data.get("volumeNumber", journal_volume)
            journal_pages = json_data.get("pagination", journal_pages)
        except json.JSONDecodeError as err:
            print(f"Error parsing JSON-LD: {err}")

    if soup.find("meta", property="og:site_name"):
        journal_name = extract_meta_content(soup, name="citation_journal_title") or soup.find("meta", property="og:site_name").get("content")
    else:
        journal_name = None

    if not affiliations:
        affiliation_meta_tags = soup.find_all("meta", {"name": "citation_author_institution"})
        affiliations = [tag["content"] for tag in affiliation_meta_tags] if affiliation_meta_tags else None
    
    doi = extract_meta_content(soup, name="citation_doi") or extract_meta_content(soup, name="dc.Identifier") or extract_meta_content(soup, property="og:doi")

    attributes = {
        "title": title,
        "authors": authors,
        "affiliations": affiliations,
        "publication_date": pub_date,
        "journal_name": journal_name,
        "journal_volume": journal_volume,
        "journal_pages": journal_pages,
        "doi": doi
    }
    return attributes

def extract_doi(url) -> str:
    doi_pattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
    match = doi_pattern.search(url)
    if match:
        return match.group(0)
    else:
        return None

def arxiv_match(url) -> bool:
    arxiv_pattern = re.compile(r'https?://(www\.)?arxiv\.org/(abs|pdf)/([0-9]+\.[0-9]+)(\.pdf)?', re.IGNORECASE)
    match = re.match(arxiv_pattern, url)
    if match:
        return match.group(3)
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
        authors = [author['family'] + ", " + author.get('given', '') for author in raw.get("author", [])]
        affiliations = [
            [aff['name'] for aff in author.get('affiliation', [])]
            for author in raw.get("author", [])
            ]
        attributes = {
            "title": raw.get('title'),
            "authors": authors,
            "affiliations": affiliations,
            "publication_date": raw.get("issued").get("date-parts")[0] if raw.get("issued") else "N/A",
            "journal_name": raw.get('container-title'),
            "journal_volume": raw.get('volume'),
            "journal_pages": raw.get('page'),
            "doi": doi
        }
        return attributes
    else:
        return None

def arxiv_scrape(arxiv_id) -> dict:
    arxiv_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(arxiv_url)
    
    if response.status_code == 200:
        root = et.fromstring(response.content)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")
        authors = []
        title = entry.find(".//{http://www.w3.org/2005/Atom}title").text.strip()
        publication_date = root.find(".//{http://www.w3.org/2005/Atom}published").text
        
        for author in root.findall(".//{http://www.w3.org/2005/Atom}author"):
            name = author.find("{http://www.w3.org/2005/Atom}name").text
            authors.append(name)

        doi = root.find(".//{http://arxiv.org/schemas/atom}doi")
        doi = doi.text if doi is not None else None
           
        attributes = {
            "title": title,
            "authors": authors,
            "affiliations": None,
            "publication_date": publication_date,
            "journal_name": None,
            "journal_volume": None,
            "journal_pages": None,
            "doi": doi
        }
        
        return attributes
    else:
        return None


url = "https://www.tandfonline.com/doi/epdf/10.1080/0025570X.1985.11977137?needAccess=true"
doi = extract_doi(url)
arxiv = arxiv_match(url)

if doi:
    article_data = doi_scrape(doi) 
elif arxiv:
    article_data = arxiv_scrape(arxiv)
else:
    article_data = generic_scrape(url) or None

if not doi and article_data:
    if article_data["doi"]:
        article_data = doi_scrape(article_data["doi"])

if article_data:
    print(json.dumps(article_data, indent=2))
else:
    print("Failed to scrape the article. Enter Manually?")
    #Prompt user for manual information entry