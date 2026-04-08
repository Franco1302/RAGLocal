from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import faiss
import numpy as np
import orjson


class FaissStore:
    """Gestiona construccion, persistencia y busqueda sobre un indice FAISS."""

    def __init__(self, index_dir: Path) -> None:
        """Configura rutas de indice y metadatos dentro del directorio objetivo."""
        self.index_dir = index_dir
        self.index_file = self.index_dir / "vectors.faiss"
        self.meta_file = self.index_dir / "metadata.json"
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []

    def _ensure_dir(self) -> None:
        """Crea el directorio de salida si aun no existe."""
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def build(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        """Construye un indice normalizado a partir de vectores y metadatos asociados."""
        if not vectors:
            raise ValueError("No vectors provided")
        self._ensure_dir()

        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)

        dim = matrix.shape[1]
        index = cast(Any, faiss.IndexFlatIP(dim))
        index.add(matrix)

        self.index = index
        self.metadata = metadata
        self.persist()

    def append(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        """Agrega vectores y metadatos al indice existente sin reconstruirlo completo."""
        if not vectors:
            return

        if self.index is None:
            self.load()
        if self.index is None:
            raise RuntimeError("Vector index is not loaded")

        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)

        append_index = cast(Any, self.index)
        index_dim = int(getattr(append_index, "d"))
        if matrix.shape[1] != index_dim:
            raise ValueError(
                f"Embedding dimension mismatch. Existing index={index_dim}, incoming={matrix.shape[1]}"
            )

        append_index.add(matrix)
        self.metadata.extend(metadata)
        self.persist()

    def persist(self) -> None:
        """Guarda indice y metadatos en disco."""
        if self.index is None:
            raise ValueError("Index not initialized")
        self._ensure_dir()
        faiss.write_index(self.index, str(self.index_file))
        self.meta_file.write_bytes(orjson.dumps(self.metadata))

    def load(self) -> None:
        """Carga desde disco un indice previamente generado."""
        if not self.index_file.exists() or not self.meta_file.exists():
            raise FileNotFoundError("Vector index not found. Run ingestion first.")
        self.index = faiss.read_index(str(self.index_file))
        self.metadata = orjson.loads(self.meta_file.read_bytes())

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        """Busca los top-k chunks mas similares y devuelve score junto a metadata."""
        if self.index is None:
            self.load()
        if self.index is None:
            raise RuntimeError("Vector index is not loaded")

        query = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query)

        search_index = cast(Any, self.index)
        distances, indices = search_index.search(query, top_k)
        results: list[dict] = []

        for score, idx in zip(distances[0], indices[0], strict=False):
            if idx < 0:
                continue
            item = dict(self.metadata[idx])
            # La distancia provista es Cosine Similarity [-1, 1]
            # La mapeamos matematicamente al rango [0, 100] de "Relevancia Ponderada"
            # para que la puntuacion sea mas interpretable humanamente.
            base_score = float(score)
            relevance_percentage = ((base_score + 1.0) / 2.0) * 100
            
            # Penalizacion o empuje si el prefijo documental concuerda
            item["score"] = round(relevance_percentage, 2)
            item["raw_cosine"] = base_score
            results.append(item)

        return results
