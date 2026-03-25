from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.vectorstores.faiss_store import FaissStore


class Retriever:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: FaissStore,
        score_threshold: float,
    ) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.score_threshold = score_threshold

    def retrieve(self, query: str, top_k: int) -> list[dict]:
        query_vector = self.embedding_service.embed_text(query)
        matches = self.vector_store.search(query_vector=query_vector, top_k=top_k)
        return [item for item in matches if item["score"] >= self.score_threshold]
