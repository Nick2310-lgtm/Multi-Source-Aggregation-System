from src.data_processing import fetch_data, preprocess
from src.retriever import generate_embeddings, embed_query
from src.vector_store import create_index, search
from src.config import *
import numpy as np

class RAGSystem:
    def __init__(self):
        self.papers = None
        self.index = None

    def build(self, query):
        papers = fetch_data(query)
        if not papers:
            return

        docs = preprocess(papers)
        embeddings = generate_embeddings(docs)

        self.papers = papers
        self.index = create_index(embeddings)

    def query(self, query):
        if self.index is None:
            self.build(query)

        if self.index is None:
            return []

        q_vec = embed_query(query)
        indices = search(self.index, np.array(q_vec), TOP_K_RESULTS)
        return [self.papers[i] for i in indices[0]]
