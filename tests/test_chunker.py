from rag_local.ingest.chunker import chunk_text


def test_chunk_text_returns_chunks() -> None:
    text = "a" * 2000
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chunk_overlap_must_be_lower_than_chunk_size() -> None:
    try:
        chunk_text("texto", chunk_size=100, chunk_overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        assert True
