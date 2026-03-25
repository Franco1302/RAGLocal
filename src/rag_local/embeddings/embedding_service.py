from rag_local.clients.ollama_client import OllamaClient


class EmbeddingService:
    def __init__(self, client: OllamaClient, model_name: str) -> None:
        self.client = client
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        return self.client.embed(model=self.model_name, text=text)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]
