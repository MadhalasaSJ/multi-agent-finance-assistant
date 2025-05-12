from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RetrieverAgent:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        self.docs = []

    def add_documents(self, texts):
        vectors = self.model.encode(texts)
        self.index.add(np.array(vectors))
        self.docs.extend(texts)

    def retrieve(self, query, top_k=2):
        q_vec = self.model.encode([query])
        D, I = self.index.search(np.array(q_vec), top_k)
        return [self.docs[i] for i in I[0]]
    
if __name__ == "__main__":
    agent = RetrieverAgent()
    docs = [
        "TSMC beat earnings by 4%.",
        "Samsung missed estimates by 2%.",
        "Alibaba earnings coming soon."
    ]
    agent.add_documents(docs)
    results = agent.retrieve("earnings surprises")
    print(results)    
