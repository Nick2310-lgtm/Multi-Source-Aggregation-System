import requests
import pandas as pd
import re
from xml.etree import ElementTree
from src.config import *

def normalize_author(name):
    name = name.lower()
    name = re.sub(r'[^a-z\s]', '', name)
    return " ".join(name.split())

def load_local_dataset(path="data/papers.csv"):
    try:
        data = pd.read_csv(path).to_dict(orient="records")
        for p in data:
            authors = p.get("authors", "")
            p["authors"] = ", ".join([normalize_author(a) for a in authors.split(",")])
            p["source"] = p.get("source", "LocalDataset")
        return data
    except:
        return []

def fetch_arxiv(query, limit):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results={limit}"
    root = ElementTree.fromstring(requests.get(url, timeout=10).content)

    papers = []
    for e in root.findall("{http://www.w3.org/2005/Atom}entry"):
        authors = [normalize_author(a.find("{http://www.w3.org/2005/Atom}name").text)
                   for a in e.findall("{http://www.w3.org/2005/Atom}author")]

        papers.append({
            "source": "arXiv",
            "title": e.find("{http://www.w3.org/2005/Atom}title").text.strip(),
            "authors": ", ".join(authors),
            "year": e.find("{http://www.w3.org/2005/Atom}published").text[:4],
            "abstract": e.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        })
    return papers

def fetch_semantic(query, limit):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,authors,year,abstract"
    data = requests.get(url, timeout=10).json()

    papers = []
    for p in data.get("data", []):
        if p.get("abstract"):
            authors = [normalize_author(a["name"]) for a in p.get("authors", [])]

            papers.append({
                "source": "SemanticScholar",
                "title": p.get("title", ""),
                "authors": ", ".join(authors),
                "year": p.get("year", ""),
                "abstract": p.get("abstract", "")
            })
    return papers

def fetch_dblp(query):
    url = f"https://dblp.org/search/publ/api?q={query}&format=xml"
    root = ElementTree.fromstring(requests.get(url, timeout=10).content)

    return [{
        "source": "DBLP",
        "title": info.findtext("title", ""),
        "authors": ", ".join([normalize_author(a.text) for a in info.findall("authors/author")]),
        "year": info.findtext("year", ""),
        "abstract": ""
    } for info in [h.find("info") for h in root.findall(".//hit")]]

def fetch_data(query):
    papers = []
    per_source = max(1, MAX_RESULTS // 3)

    if USE_LOCAL_DATASET:
        papers += load_local_dataset()
    if USE_ARXIV:
        papers += fetch_arxiv(query, per_source)
    if USE_SEMANTIC:
        papers += fetch_semantic(query, per_source)
    if USE_DBLP:
        papers += fetch_dblp(query)

    return papers[:MAX_RESULTS]

def preprocess(papers):
    return [
        f"Title: {p['title']}\nAuthors: {p['authors']}\nYear: {p['year']}\nAbstract: {p['abstract']}"
        for p in papers
    ]
