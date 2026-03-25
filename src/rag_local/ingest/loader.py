from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class LoadedDocument:
    source: str
    text: str


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_documents(source_dir: Path) -> list[LoadedDocument]:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source_dir}")

    documents: list[LoadedDocument] = []

    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = _read_pdf(path) if path.suffix.lower() == ".pdf" else _read_text(path)
        if text.strip():
            documents.append(LoadedDocument(source=str(path), text=text))

    return documents
