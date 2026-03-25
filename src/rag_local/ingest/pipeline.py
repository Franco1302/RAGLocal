from __future__ import annotations

import hashlib
from pathlib import Path

import orjson
from tqdm import tqdm

from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.ingest.chunker import chunk_text
from rag_local.ingest.loader import load_documents
from rag_local.vectorstores.faiss_store import FaissStore


def _build_document_signature(text: str) -> str:
    """Genera una firma estable por contenido para detectar cambios en documentos."""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _load_previous_signatures(manifest_file: Path) -> tuple[dict[str, str], bool]:
    """Carga firmas previas desde manifest y avisa si el formato incremental existe."""
    if not manifest_file.exists():
        return {}, False
    try:
        manifest = orjson.loads(manifest_file.read_bytes())
    except orjson.JSONDecodeError:
        return {}, False

    signatures = manifest.get("document_signatures")
    if isinstance(signatures, dict):
        return {str(k): str(v) for k, v in signatures.items()}, True
    return {}, False


def run_ingestion(
    source_dir: Path,
    processed_dir: Path,
    vector_index_dir: Path,
    embedding_service: EmbeddingService,
    chunk_size: int,
    chunk_overlap: int,
) -> int:
    """Orquesta la ingesta completa y devuelve la cantidad total de chunks indexados."""
    docs = load_documents(source_dir)
    if not docs:
        return 0

    processed_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = processed_dir / "manifest.json"

    store = FaissStore(index_dir=vector_index_dir)
    previous_signatures, has_incremental_manifest = _load_previous_signatures(manifest_file)
    current_signatures = {doc.source: _build_document_signature(doc.text) for doc in docs}

    new_docs = [doc for doc in docs if doc.source not in previous_signatures]
    modified_docs = [
        doc
        for doc in docs
        if doc.source in previous_signatures and previous_signatures[doc.source] != current_signatures[doc.source]
    ]
    removed_sources = [source for source in previous_signatures if source not in current_signatures]

    requires_full_rebuild = bool(modified_docs or removed_sources)

    # Primer run incremental sobre indice ya existente: reconstruimos para evitar duplicados.
    if not has_incremental_manifest and store.index_file.exists() and store.meta_file.exists():
        requires_full_rebuild = True

    docs_to_process = docs if requires_full_rebuild else new_docs
    if not docs_to_process:
        return 0

    chunks: list[str] = []
    metadata: list[dict] = []

    for doc in docs_to_process:
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

    if requires_full_rebuild or not (store.index_file.exists() and store.meta_file.exists()):
        store.build(vectors=vectors, metadata=metadata)
    else:
        store.append(vectors=vectors, metadata=metadata)

    total_chunks = len(store.metadata)

    manifest = {
        "documents": len(docs),
        "chunks": total_chunks,
        "chunks_indexed_this_run": len(chunks),
        "index_mode": "full_rebuild" if requires_full_rebuild else "incremental_append",
        "source_dir": str(source_dir),
        "document_signatures": current_signatures,
    }
    manifest_file.write_bytes(orjson.dumps(manifest, option=orjson.OPT_INDENT_2))

    return len(chunks)
