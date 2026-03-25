from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    # Confirma que el servicio de Ollama está disponible haciendo una solicitud simple a la API de tags.
    def healthcheck(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
            return response.status_code == 200
        except httpx.HTTPError:
            return False
    # Envía una solicitud POST a la API de embed de Ollama con el texto a ser embebido y devuelve el vector de embedding resultante.
    def embed(self, model: str, text: str) -> list[float]:
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
    # Envía una solicitud POST a la API de generate de Ollama con el prompt y devuelve la respuesta generada por el modelo.
    def generate(self, model: str, prompt: str) -> str:
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
