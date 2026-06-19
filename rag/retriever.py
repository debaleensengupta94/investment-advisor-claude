from rag.embedder import TFIDFEmbedder
from rag.knowledge_base import DOCUMENTS
from config.settings import config


class RAGRetriever:
    def __init__(self, embedder: TFIDFEmbedder | None = None, documents: list[str] | None = None):
        self._embedder = embedder or TFIDFEmbedder()
        self._documents = documents or DOCUMENTS
        self._embedder.fit(self._documents)
        self._doc_vectors = [self._embedder.transform(doc) for doc in self._documents]

    def retrieve(self, query: str, top_k: int | None = None) -> list[str]:
        k = top_k if top_k is not None else config.rag_top_k
        query_vec = self._embedder.transform(query)
        scores = [
            (self._embedder.cosine_similarity(query_vec, dv), doc)
            for dv, doc in zip(self._doc_vectors, self._documents)
        ]
        scores.sort(key=lambda x: x[0], reverse=True)
        return [
            doc for score, doc in scores[:k]
            if score >= config.rag_similarity_threshold
        ]
