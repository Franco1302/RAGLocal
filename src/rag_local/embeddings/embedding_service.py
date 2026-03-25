from rag_local.clients.ollama_client import OllamaClient


class EmbeddingService:
    def __init__(self, client: OllamaClient, model_name: str) -> None:
        self.client = client
        self.model_name = model_name

    # Envía una solicitud a la API de embed de Ollama para obtener el vector de embedding de un texto dado.
    def embed_text(self, text: str) -> list[float]:
        return self.client.embed(model=self.model_name, text=text)

    # Envía solicitudes a la API de embed de Ollama para obtener los vectores de embedding de una lista de textos.
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]
