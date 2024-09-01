import requests
from bs4 import BeautifulSoup
import json
import re
import requests
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

def arxiv_match(url: str) -> str:
    arxiv_pattern = re.compile(r'https?://(www\.)?arxiv\.org/(abs|pdf)/([a-z\-]+/[0-9]{7}|[0-9]+\.[0-9]+)(\.pdf)?', re.IGNORECASE)
    match = re.match(arxiv_pattern, url)
    if match:
        return match.group(3)
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
            aff['name']
            for author in raw.get("author", [])
            for aff in author.get('affiliation', [])
        ]
        attributes = {
            "title": raw.get('title'),
            "authors": authors,
            "affiliations": affiliations,
            "publication_date": (raw.get("issued").get("date-parts")[0])[0] if raw.get("issued") else "N/A",
            "journal_name": raw.get('container-title'),
            "journal_volume": raw.get('volume'),
            "journal_pages": raw.get('page'),
            "doi": doi
        }
        return attributes
    else:
        return None



def arxiv_scrape(arxiv_id: str) -> dict:
    arxiv_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    response = requests.get(arxiv_url)
    
    if response.status_code == 200:
        root = et.fromstring(response.content)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")
        authors = []
        affiliations = []
        
        title = entry.find(".//{http://www.w3.org/2005/Atom}title").text.strip()
        
        publication_date = root.find(".//{http://www.w3.org/2005/Atom}published").text
        publication_year = publication_date.split("-")[0] if publication_date else None

        for author in root.findall(".//{http://www.w3.org/2005/Atom}author"):
            name = author.find("{http://www.w3.org/2005/Atom}name").text
            affiliation = author.find("{http://arxiv.org/schemas/atom}affiliation")
            authors.append(name)
            affiliations.append(affiliation.text if affiliation is not None else None)

        doi = root.find(".//{http://arxiv.org/schemas/atom}doi")
        doi = doi.text if doi is not None else None
        
        journal_ref = root.find(".//{http://arxiv.org/schemas/atom}journal_ref")
        journal_name = None
        journal_volume = None
        journal_pages = None
        
        if journal_ref is not None and journal_ref.text:
            journal_parts = journal_ref.text.split(',')
            if len(journal_parts) > 0:
                journal_name = journal_parts[0].strip()
            if len(journal_parts) > 1:
                journal_volume = journal_parts[1].strip()
            if len(journal_parts) > 2:
                journal_pages = journal_parts[2].strip().split()[0]

        attributes = {
            "title": title,
            "authors": authors,
            "affiliations": affiliations,
            "publication_year": publication_year,
            "journal_name": journal_name,
            "journal_volume": journal_volume,
            "journal_pages": journal_pages,
            "doi": doi
        }
        
        return attributes
    else:
        return None

def clean_affiliation(affiliation) -> str:

    patterns = [
        r'.*?(University of [^,]+)',      
        r'.*?(Institute of [^,]+)',        
        r'.*?([A-Za-z\s]+ College)',        
        r'.*?([A-Za-z\s]+ University)',     
        r'.*?([A-Za-z\s]+ Institute)',      
        r'.*?([A-Za-z\s]+ Institute [^,]+)',  
        r'.*?(School of [^,]+)',           
        r'.*?(Faculty of [^,]+)',          
        r'.*?(National Laboratory of [^,]+)',
        r'.*?(Laboratory of [^,]+)',        
        r'.*?(Center for [^,]+)',           
        r'.*?(Hospital of [^,]+)',          
        r'.*?([A-Za-z\s]+ Research Institute)', 
        r'.*?([A-Za-z\s]+ Research Center)', 
        r'.*?(Medical Center of [^,]+)',    
        r'.*?([A-Za-z\s]+ Center [^,]+)',    
        r'.*?(Corporation of [^,]+)',       
        r'.*?([A-Za-z\s]+ Academy)',      
        r'.*?([A-Za-z\s]+ Foundation)',      
        r'.*?([A-Za-z\s]+ Labs?)',          
        r'.*?([A-Za-z\s]+ Clinic)',          
    ]
    
    for pattern in patterns:
        match = re.search(pattern, affiliation)
        if match:
            return match.group(1).strip()
    
    # If no patterns matched, return the original string
    return affiliation.strip()

def scrape(url):
    doi = extract_doi(url)
    arxiv = arxiv_match(url)
    print(arxiv)
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
        aff = article_data["affiliations"]
        article_data["affiliations"] = clean_affiliation(aff)
        return article_data
    else:
        print("Failed to scrape the article. Enter Manually?")

