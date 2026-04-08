from rag_local.clients.ollama_client import OllamaClient


class EmbeddingService:
    """Encapsula la generacion de embeddings para textos individuales o en lote."""

    def __init__(self, client: OllamaClient, model_name: str) -> None:
        """Recibe cliente de Ollama y nombre del modelo de embeddings."""
        self.client = client
        self.model_name = model_name

    def embed_text(self, text: str, task_type: str = "document") -> list[float]:
        """Genera el embedding de un unico texto. 
        task_type: 'document' o 'query' para usar el prefijo optimizado de nomic-embed-text."""
        prefix = "search_document: " if task_type == "document" else "search_query: "
        # Solo aplicar prefijo si usamos el modelo nomic y no esta ya presente
        if "nomic" in self.model_name.lower() and not text.startswith(prefix):
            final_text = f"{prefix}{text}"
        else:
            final_text = text
            
        return self.client.embed(model=self.model_name, text=final_text)

    def embed_texts(self, texts: list[str], task_type: str = "document") -> list[list[float]]:
        """Genera embeddings para varios textos manteniendo el orden de entrada."""
        return [self.embed_text(text, task_type) for text in texts]
