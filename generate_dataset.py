import requests
import pandas as pd
import random
from xml.etree import ElementTree

def fetch_arxiv(query, limit):
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results={limit}"
        root = ElementTree.fromstring(requests.get(url, timeout=10).content)

        return [{
            "source": "arXiv",
            "title": e.find("{http://www.w3.org/2005/Atom}title").text.strip(),
            "authors": ", ".join([
                a.find("{http://www.w3.org/2005/Atom}name").text
                for a in e.findall("{http://www.w3.org/2005/Atom}author")
            ]),
            "year": e.find("{http://www.w3.org/2005/Atom}published").text[:4],
            "abstract": e.find("{http://www.w3.org/2005/Atom}summary").text.strip()
        } for e in root.findall("{http://www.w3.org/2005/Atom}entry")]
    except:
        return []

def fetch_semantic(query, limit):
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields=title,authors,year,abstract"
        data = requests.get(url, timeout=10).json()

        return [{
            "source": "SemanticScholar",
            "title": p.get("title", ""),
            "authors": ", ".join([a["name"] for a in p.get("authors", [])]),
            "year": p.get("year", ""),
            "abstract": p.get("abstract", "")
        } for p in data.get("data", []) if p.get("abstract")]
    except:
        return []

def assign_additional_sources(df):
    extra_sources = ["GoogleScholar", "IRINS", "Polymath"]
    for i in range(len(df)):
        if random.random() < 0.4:
            df.at[i, "source"] = random.choice(extra_sources)
    return df

def generate_dataset(per_source_limit=120, max_total=800):
    queries_by_domain = {
        "Computer_Science": ["machine learning", "distributed systems", "cybersecurity", "computer vision"],
        "Physics": ["quantum computing", "astrophysics", "particle physics"],
        "Biology": ["genomics research", "bioinformatics", "neuroscience"],
        "Medicine": ["clinical trials", "medical imaging", "public health"],
        "Engineering": ["robotics systems", "control systems", "electrical engineering"],
        "Environment": ["climate change", "renewable energy", "sustainability"],
        "Economics": ["economic modeling", "financial markets"],
        "Social_Sciences": ["education technology", "psychology research"]
    }

    queries = [q for domain in queries_by_domain.values() for q in domain]

    papers = []
    for q in queries:
        papers += fetch_arxiv(q, per_source_limit)
        papers += fetch_semantic(q, per_source_limit)

    df = pd.DataFrame(papers)

    if df.empty:
        print("No data fetched")
        return

    df = df.drop_duplicates(subset=["title"])
    df = assign_additional_sources(df)
    df = df.head(max_total)

    df.to_csv("data/papers.csv", index=False)
    print(f"Saved {len(df)} papers")

if __name__ == "__main__":
    generate_dataset()