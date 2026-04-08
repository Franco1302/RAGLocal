from __future__ import annotations


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Divide un texto en bloques con solapamiento para preservar continuidad semantica."""
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    words = cleaned.split(" ")
    chunks: list[str] = []
    
    current_chunk = []
    current_length = 0
    
    i = 0
    while i < len(words):
        word = words[i]
        
        if current_length + len(word) + (1 if current_length > 0 else 0) > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            overlap_length = 0
            overlap_words = []
            for w in reversed(current_chunk):
                if overlap_length + len(w) + (1 if overlap_length > 0 else 0) <= chunk_overlap:
                    overlap_words.insert(0, w)
                    overlap_length += len(w) + 1
                else:
                    break
            
            current_chunk = overlap_words
            current_length = sum(len(w) for w in current_chunk) + max(0, len(current_chunk) - 1)
        
        current_chunk.append(word)
        current_length += len(word) + (1 if len(current_chunk) > 1 else 0)
        i += 1
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
