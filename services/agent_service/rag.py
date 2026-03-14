import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

DOC_DIR = "documents"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

documents = []

for file in os.listdir(DOC_DIR):

    if file.endswith(".txt"):
        with open(os.path.join(DOC_DIR, file), "r", encoding="utf-8") as f:
            documents.append(f.read())

if documents:

    embeddings = model.encode(documents)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(np.array(embeddings))

else:

    index = None


def query_documents(query):
    if not index:
        return None

    q = model.encode([query])

    distances, ids = index.search(np.array(q), 1)

    score = distances[0][0]

    if score > 1.2:
        return None

    return documents[ids[0][0]]
