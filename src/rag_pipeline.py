from src.data_processing import fetch_data, preprocess
from src.retriever import generate_embeddings, embed_query
from src.vector_store import create_index, search
from src.config import *
import numpy as np

class RAGSystem:
    def __init__(self):
        self.papers = []
        self.index = None
        self.embeddings = None

    def build(self):
        papers = fetch_data("")  # build once using dataset
        if not papers:
            return

        docs = preprocess(papers)
        embeddings = generate_embeddings(docs)

        self.papers = papers
        self.embeddings = embeddings
        self.index = create_index(embeddings)

    def query(self, query):
        if not query.strip():
            return []

        # ✅ Build ONLY ONCE
        if self.index is None:
            self.build()

        if self.index is None or not self.papers:
            return []

        query_words = set(query.lower().split())
        q_vec = embed_query(query)

        # ✅ Fast FAISS search (dataset)
        indices = search(self.index, np.array(q_vec), TOP_K_RESULTS * 10)

        scored = []

        for i in indices[0]:
            if i >= len(self.papers):
                continue

            paper = self.papers[i]
            text = (paper.get("title","") + " " + paper.get("abstract","")).lower()

            keyword_score = sum(1 for w in query_words if w in text)
            similarity = float(np.dot(q_vec[0], self.embeddings[i]))

            total_score = similarity + (keyword_score * 0.1)
            scored.append((total_score, paper))

        # ✅ Add API results (lightweight, no rebuild)
        api_papers = fetch_data(query)[-15:]

        if api_papers:
            api_docs = preprocess(api_papers)
            api_embeddings = generate_embeddings(api_docs)

            for i, paper in enumerate(api_papers):
                text = (paper.get("title","") + " " + paper.get("abstract","")).lower()

                keyword_score = sum(1 for w in query_words if w in text)
                similarity = float(np.dot(q_vec[0], api_embeddings[i]))

                total_score = similarity + (keyword_score * 0.1)
                scored.append((total_score, paper))

        # ✅ Sort by relevance
        scored.sort(key=lambda x: x[0], reverse=True)

        # ✅ Balanced multi-source output
        results = []
        source_count = {}

        for score, paper in scored:
            src = paper.get("source", "Unknown")

            if source_count.get(src, 0) >= 2:
                continue

            results.append(paper)
            source_count[src] = source_count.get(src, 0) + 1

            if len(results) >= TOP_K_RESULTS:
                break

        return results
