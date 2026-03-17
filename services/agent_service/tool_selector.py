from sentence_transformers import SentenceTransformer
import numpy as np

from services.agent_service.tools.tool_registry import TOOLS


model = SentenceTransformer("all-MiniLM-L6-v2")


class ToolSelector:

    def __init__(self):

        self.tools = []
        self.embeddings = []

        for name, tool in TOOLS.items():

            text = f"{name} {tool['description']}"

            emb = model.encode(text)

            self.tools.append(name)
            self.embeddings.append(emb)

        self.embeddings = np.array(self.embeddings)

    def select(self, query, top_k=3):

        q = model.encode(query)

        sims = np.dot(self.embeddings, q)

        idx = sims.argsort()[-top_k:][::-1]

        return [self.tools[i] for i in idx]


tool_selector = ToolSelector()