import faiss
import numpy as np

def create_index(embeddings):
    embeddings = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

def search(index, query_vec, k):
    query_vec = np.array(query_vec).astype("float32")
    _, indices = index.search(query_vec, k)
    return indices
