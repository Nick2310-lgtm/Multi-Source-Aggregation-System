import requests
import pandas as pd
import re
from xml.etree import ElementTree
from src.config import *

def normalize_author(name):
    if not name:
        return ""
    name = str(name).lower()
    name = re.sub(r'[^a-z\s]', '', name)
    return " ".join(name.split())

def load_local_dataset(path="data/papers.csv"):
    try:
        df = pd.read_csv(path).fillna("")  # ✅ FIX: remove NaN

        data = df.to_dict(orient="records")

        for p in data:
            authors = p.get("authors", "")
            p["authors"] = ", ".join([
                normalize_author(a) for a in str(authors).split(",")
            ])

        return data
    except:
        return []

def fetch_arxiv(query, limit):
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results={limit}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return []

        root = ElementTree.fromstring(response.content)

        papers = []
        for e in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = str(e.find("{http://www.w3.org/2005/Atom}title").text or "").strip()

            authors = ", ".join([
                str(a.find("{http://www.w3.org/2005/Atom}name").text or "")
                for a in e.findall("{http://www.w3.org/2005/Atom}author")
            ])

            year = str(e.find("{http://www.w3.org/2005/Atom}published").text[:4] or "")

            abstract = str(e.find("{http://www.w3.org/2005/Atom}summary").text or "").strip()

            papers.append({
                "source": "arXiv",
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract
            })

        return papers
    except:
        return []

def fetch_dblp(query):
    try:
        url = f"https://dblp.org/search/publ/api?q={query}&format=xml"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return []

        root = ElementTree.fromstring(response.content)

        papers = []
        for hit in root.findall(".//hit")[:10]:
            info = hit.find("info")
            if info is None:
                continue

            authors = [
                str(a.text or "")
                for a in info.findall("authors/author")
                if a.text
            ]

            papers.append({
                "source": "DBLP",
                "title": str(info.findtext("title", "") or ""),
                "authors": ", ".join(authors),
                "year": str(info.findtext("year", "") or ""),
                "abstract": ""
            })

        return papers
    except:
        return []

def fetch_data(query):
    papers = []

    # ✅ Load dataset (primary)
    if USE_LOCAL_DATASET:
        papers += load_local_dataset()

    # ✅ Add small API results
    if query:
        if USE_ARXIV:
            papers += fetch_arxiv(query, 10)

        if USE_DBLP:
            papers += fetch_dblp(query)

    # ✅ Remove duplicates
    seen = set()
    unique = []

    for p in papers:
        title = str(p.get("title", "") or "").strip()
        if title and title not in seen:
            seen.add(title)
            unique.append(p)

    return unique[:MAX_RESULTS]

def preprocess(papers):
    return [
        str(p.get("title", "") or "") + " " + str(p.get("abstract", "") or "")
        for p in papers
    ]
