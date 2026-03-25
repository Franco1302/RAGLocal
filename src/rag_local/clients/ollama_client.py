from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    """Cliente HTTP para los endpoints de Ollama usados por el pipeline RAG."""

    def __init__(self, base_url: str, timeout_seconds: float = 60.0) -> None:
        """Guarda la configuracion de conexion y normaliza la URL base."""
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def healthcheck(self) -> bool:
        """Devuelve True cuando Ollama responde correctamente en /api/tags."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def embed(self, model: str, text: str) -> list[float]:
        """Genera un vector de embedding para un texto individual."""
        payload = {"model": model, "input": text}
        response = httpx.post(
            f"{self.base_url}/api/embed",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        embeddings = body.get("embeddings", [])
        if not embeddings:
            raise ValueError("Ollama did not return embeddings")
        return embeddings[0]

    def generate(self, model: str, prompt: str) -> str:
        """Genera una respuesta de texto para un prompt usando el modelo de chat."""
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return response.json().get("response", "")
