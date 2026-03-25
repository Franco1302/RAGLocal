from __future__ import annotations

from pathlib import Path

import faiss
import numpy as np
import orjson


class FaissStore:
    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.index_file = self.index_dir / "vectors.faiss"
        self.meta_file = self.index_dir / "metadata.json"
        self.index: faiss.IndexFlatIP | None = None
        self.metadata: list[dict] = []

    def _ensure_dir(self) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def build(self, vectors: list[list[float]], metadata: list[dict]) -> None:
        if not vectors:
            raise ValueError("No vectors provided")
        self._ensure_dir()

        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)

        dim = matrix.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(matrix)

        self.index = index
        self.metadata = metadata
        self.persist()

    def persist(self) -> None:
        if self.index is None:
            raise ValueError("Index not initialized")
        self._ensure_dir()
        faiss.write_index(self.index, str(self.index_file))
        self.meta_file.write_bytes(orjson.dumps(self.metadata))

    def load(self) -> None:
        if not self.index_file.exists() or not self.meta_file.exists():
            raise FileNotFoundError("Vector index not found. Run ingestion first.")
        self.index = faiss.read_index(str(self.index_file))
        self.metadata = orjson.loads(self.meta_file.read_bytes())

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        if self.index is None:
            self.load()
        if self.index is None:
            raise RuntimeError("Vector index is not loaded")

        query = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(query)

        distances, indices = self.index.search(query, top_k)
        results: list[dict] = []

        for score, idx in zip(distances[0], indices[0], strict=False):
            if idx < 0:
                continue
            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)

        return results
