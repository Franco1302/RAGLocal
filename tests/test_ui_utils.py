from pathlib import Path

import orjson
import pytest

from rag_local.ui.utils import (
    build_unique_pdf_path,
    read_manifest,
    recent_sources,
    sanitize_filename,
)


def test_sanitize_filename_removes_unsafe_chars() -> None:
    assert sanitize_filename("../Mi documento?.pdf") == "Mi_documento"


def test_build_unique_pdf_path_uses_pdf_suffix(tmp_path: Path) -> None:
    target = build_unique_pdf_path(tmp_path, "manual final.PDF")

    assert target.parent == tmp_path
    assert target.suffix == ".pdf"
    assert "manual_final" in target.name


def test_build_unique_pdf_path_rejects_non_pdf(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        build_unique_pdf_path(tmp_path, "notas.txt")


def test_read_manifest_returns_empty_for_invalid_json(tmp_path: Path) -> None:
    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text("{json invalido", encoding="utf-8")

    assert read_manifest(manifest_file) == {}


def test_recent_sources_deduplicates_and_limits(tmp_path: Path) -> None:
    metadata_file = tmp_path / "metadata.json"
    metadata = [
        {"source": "data/raw/a.pdf"},
        {"source": "data/raw/b.pdf"},
        {"source": "data/raw/a.pdf"},
    ]
    metadata_file.write_bytes(orjson.dumps(metadata))

    assert recent_sources(metadata_file=metadata_file, limit=2) == [
        "data/raw/a.pdf",
        "data/raw/b.pdf",
    ]
