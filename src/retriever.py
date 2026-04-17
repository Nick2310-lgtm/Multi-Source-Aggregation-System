from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(docs):
    return model.encode(docs)

def embed_query(query):
    return model.encode([query])
