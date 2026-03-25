from rag_local.clients.ollama_client import OllamaClient


class EmbeddingService:
    """Encapsula la generacion de embeddings para textos individuales o en lote."""

    def __init__(self, client: OllamaClient, model_name: str) -> None:
        """Recibe cliente de Ollama y nombre del modelo de embeddings."""
        self.client = client
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        """Genera el embedding de un unico texto."""
        return self.client.embed(model=self.model_name, text=text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Genera embeddings para varios textos manteniendo el orden de entrada."""
        return [self.embed_text(text) for text in texts]
