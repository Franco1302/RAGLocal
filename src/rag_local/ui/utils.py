from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import orjson

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_filename(filename: str) -> str:
    """Normaliza un nombre de archivo para evitar caracteres inseguros."""
    base_name = Path(filename).name
    stem = Path(base_name).stem.strip()
    if not stem:
        stem = "documento"

    cleaned = _SAFE_FILENAME_RE.sub("_", stem).strip("._")
    if not cleaned:
        cleaned = "documento"

    return cleaned[:80]


def build_unique_pdf_path(raw_dir: Path, original_name: str) -> Path:
    """Construye una ruta unica y segura para un PDF subido por la UI."""
    suffix = Path(original_name).suffix.lower()
    if suffix != ".pdf":
        raise ValueError("Solo se aceptan archivos PDF")

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
    token = uuid.uuid4().hex[:8]
    safe_stem = sanitize_filename(original_name)

    return raw_dir / f"{safe_stem}_{timestamp}_{token}{suffix}"


def save_bytes_to_path(content: bytes, destination: Path) -> Path:
    """Guarda bytes en disco creando directorios padre si faltan."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return destination


def read_manifest(manifest_file: Path) -> dict[str, Any]:
    """Carga manifest.json de forma segura retornando dict vacio en errores."""
    if not manifest_file.exists():
        return {}

    try:
        payload = orjson.loads(manifest_file.read_bytes())
    except orjson.JSONDecodeError:
        return {}

    return payload if isinstance(payload, dict) else {}


def recent_sources(metadata_file: Path, limit: int = 10) -> list[str]:
    """Retorna fuentes recientes deduplicadas a partir de metadata del indice."""
    if limit <= 0 or not metadata_file.exists():
        return []

    try:
        payload = orjson.loads(metadata_file.read_bytes())
    except orjson.JSONDecodeError:
        return []

    if not isinstance(payload, list):
        return []

    seen: set[str] = set()
    ordered_sources: list[str] = []

    for item in reversed(payload):
        if not isinstance(item, dict):
            continue

        source = str(item.get("source", "")).strip()
        if not source or source in seen:
            continue

        seen.add(source)
        ordered_sources.append(source)

        if len(ordered_sources) >= limit:
            break

    return ordered_sources
