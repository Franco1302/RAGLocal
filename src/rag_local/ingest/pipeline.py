from __future__ import annotations

from pathlib import Path

import orjson
from tqdm import tqdm

from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.ingest.chunker import chunk_text
from rag_local.ingest.loader import load_documents
from rag_local.vectorstores.faiss_store import FaissStore


def run_ingestion(
    source_dir: Path,
    processed_dir: Path,
    vector_index_dir: Path,
    embedding_service: EmbeddingService,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    docs = load_documents(source_dir)
    if not docs:
        return 0

    processed_dir.mkdir(parents=True, exist_ok=True)

    chunks: list[str] = []
    metadata: list[dict] = []

    for doc in docs:
        doc_chunks = chunk_text(doc.text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for i, content in enumerate(doc_chunks):
            chunks.append(content)
            metadata.append(
                {
                    "source": doc.source,
                    "chunk_id": i,
                    "content": content,
                }
            )

    vectors = []
    for chunk in tqdm(chunks, desc="Embedding chunks"):
        vectors.append(embedding_service.embed_text(chunk))

    store = FaissStore(index_dir=vector_index_dir)
    store.build(vectors=vectors, metadata=metadata)

    manifest = {
        "documents": len(docs),
        "chunks": len(chunks),
        "source_dir": str(source_dir),
    }
    (processed_dir / "manifest.json").write_bytes(orjson.dumps(manifest, option=orjson.OPT_INDENT_2))

    return len(chunks)
