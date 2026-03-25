from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class LoadedDocument:
    """Representa un documento listo para ser troceado e indexado."""

    source: str
    text: str


def _read_pdf(path: Path) -> str:
    """Extrae texto de todas las paginas de un PDF."""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_text(path: Path) -> str:
    """Lee archivos de texto plano o markdown ignorando errores de decodificacion."""
    return path.read_text(encoding="utf-8", errors="ignore")


def load_documents(source_dir: Path) -> list[LoadedDocument]:
    """Carga documentos soportados desde un directorio de origen de forma recursiva."""
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
