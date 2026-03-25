from __future__ import annotations


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = start + chunk_size
        chunks.append(cleaned[start:end])
        if end >= len(cleaned):
            break
        start = end - chunk_overlap

    return chunks
