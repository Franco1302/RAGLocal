from rag_local.clients.ollama_client import OllamaClient
from rag_local.config import Settings
from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.generate.generator import build_prompt
from rag_local.retrieve.retriever import Retriever
from rag_local.vectorstores.faiss_store import FaissStore


class RagService:
    """Coordina retrieval y generacion para responder preguntas de usuarios."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa clientes y componentes del pipeline con la configuracion activa."""
        self.settings = settings
        self.ollama = OllamaClient(base_url=str(settings.ollama_base_url))
        self.embedding_service = EmbeddingService(
            client=self.ollama,
            model_name=settings.ollama_embed_model,
        )
        self.vector_store = FaissStore(index_dir=settings.rag_vector_index_dir)
        self.retriever = Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            score_threshold=settings.rag_score_threshold,
        )

    def healthcheck(self) -> bool:
        """Comprueba disponibilidad del servidor Ollama."""
        return self.ollama.healthcheck()

    def answer(self, question: str) -> dict:
        """Resuelve una pregunta recuperando contexto y generando la respuesta final."""
        contexts = self.retriever.retrieve(query=question, top_k=self.settings.rag_top_k)
        if not contexts:
            return {
                "answer": "No encontre contexto relevante en el indice actual.",
                "contexts": [],
            }

        prompt = build_prompt(question=question, contexts=contexts)
        answer = self.ollama.generate(model=self.settings.ollama_chat_model, prompt=prompt)
        return {
            "answer": answer.strip(),
            "contexts": contexts,
        }
