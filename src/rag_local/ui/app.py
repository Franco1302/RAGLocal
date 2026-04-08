from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from rag_local.config import Settings, get_settings
from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.ingest.pipeline import run_ingestion
from rag_local.logging_utils import configure_logging
from rag_local.rag_service import RagService
from rag_local.ui.utils import (
    build_unique_pdf_path,
    read_manifest,
    recent_sources,
    save_bytes_to_path,
)

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024


@st.cache_resource(show_spinner=False)
def get_runtime() -> tuple[Settings, RagService]:
    """Inicializa configuracion y servicios una sola vez por sesion de servidor."""
    settings = get_settings()
    configure_logging(settings.log_level)
    service = RagService(settings)
    return settings, service


def init_session_state() -> None:
    """Declara estado minimo para chat y resultado de acciones de la UI."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "health_ok" not in st.session_state:
        st.session_state.health_ok = None
    if "last_ingestion" not in st.session_state:
        st.session_state.last_ingestion = None


def run_upload_ingestion(
    uploads: list[Any],
    settings: Settings,
    service: RagService,
    force_rebuild: bool,
) -> tuple[int, list[Path], list[str]]:
    """Guarda archivos subidos y ejecuta la ingesta sobre el directorio de entrada."""
    saved_files: list[Path] = []
    errors: list[str] = []
    max_upload_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)

    for uploaded_file in uploads:
        file_name = str(getattr(uploaded_file, "name", "archivo.pdf"))
        file_size = int(getattr(uploaded_file, "size", 0))

        if file_size <= 0:
            errors.append(f"{file_name}: archivo vacio")
            continue

        if file_size > MAX_UPLOAD_SIZE_BYTES:
            errors.append(f"{file_name}: excede el limite de {max_upload_mb} MB")
            continue

        try:
            target_path = build_unique_pdf_path(settings.rag_data_raw_dir, file_name)
            content = uploaded_file.getvalue()
            save_bytes_to_path(content=content, destination=target_path)
            saved_files.append(target_path)
        except Exception as exc:  # pragma: no cover - defensivo para UX
            errors.append(f"{file_name}: no se pudo guardar ({exc})")

    if not saved_files:
        return 0, saved_files, errors

    embedding_service = EmbeddingService(
        client=service.ollama,
        model_name=settings.ollama_embed_model,
    )

    indexed_chunks = run_ingestion(
        source_dir=settings.rag_data_raw_dir,
        processed_dir=settings.rag_data_processed_dir,
        vector_index_dir=settings.rag_vector_index_dir,
        embedding_service=embedding_service,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        force_rebuild=force_rebuild,
    )

    return indexed_chunks, saved_files, errors


def render_sidebar(service: RagService, settings: Settings) -> None:
    """Muestra controles globales y estado rapido en barra lateral."""
    st.sidebar.header("Sistema")

    if st.sidebar.button("Probar conexion Ollama", use_container_width=True):
        st.session_state.health_ok = service.healthcheck()

    health_status = st.session_state.get("health_ok")
    if health_status is True:
        st.sidebar.success("Ollama disponible")
    elif health_status is False:
        st.sidebar.error("Sin conexion con Ollama")
    else:
        st.sidebar.info("Conexion no comprobada")

    st.sidebar.caption(f"Chat model: {settings.ollama_chat_model}")
    st.sidebar.caption(f"Embed model: {settings.ollama_embed_model}")


def render_upload_tab(settings: Settings, service: RagService) -> None:
    """Vista para cargar PDFs e indexarlos en el pipeline existente."""
    st.subheader("Subida de PDFs")
    st.caption("Formatos aceptados: PDF. Tamano maximo por archivo: 25 MB")

    uploads = st.file_uploader(
        "Selecciona uno o varios archivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
    )
    force_rebuild = st.checkbox("Forzar reindexado completo", value=False)

    run_disabled = not uploads
    if st.button("Guardar e indexar", type="primary", disabled=run_disabled):
        with st.spinner("Guardando archivos e iniciando ingestion..."):
            try:
                indexed_chunks, saved_files, errors = run_upload_ingestion(
                    uploads=uploads or [],
                    settings=settings,
                    service=service,
                    force_rebuild=force_rebuild,
                )
            except Exception as exc:
                st.error(f"No se pudo completar la ingesta: {exc}")
                return

        if saved_files:
            st.success(
                "Archivos guardados: "
                f"{len(saved_files)}. Chunks indexados en esta ejecucion: {indexed_chunks}."
            )
            st.session_state.last_ingestion = {
                "saved": [str(path) for path in saved_files],
                "indexed_chunks": indexed_chunks,
            }

        if errors:
            st.warning("Algunos archivos no se procesaron correctamente:")
            for err in errors:
                st.write(f"- {err}")

    last_ingestion = st.session_state.get("last_ingestion")
    if last_ingestion:
        st.markdown("**Ultima ingestion**")
        st.write(f"Chunks indexados: {last_ingestion['indexed_chunks']}")
        for file_path in last_ingestion["saved"]:
            st.write(f"- {Path(file_path).name}")


def _render_assistant_contexts(contexts: list[dict]) -> None:
    """Renderiza fuentes de contexto de una respuesta del asistente."""
    if not contexts:
        return

    with st.expander("Fuentes recuperadas"):
        for item in contexts:
            source = Path(str(item.get("source", "desconocido"))).name
            score = item.get("score", "-")
            st.write(f"- {source} (score={score})")


def render_chat_tab(service: RagService) -> None:
    """Vista de chat con historial de sesion y respuestas RAG."""
    st.subheader("Chat RAG")

    if st.button("Limpiar historial", use_container_width=False):
        st.session_state.messages = []
        st.rerun()

    for message in st.session_state.messages:
        role = str(message.get("role", "assistant"))
        with st.chat_message(role):
            st.markdown(str(message.get("content", "")))
            if role == "assistant":
                _render_assistant_contexts(message.get("contexts", []))

    question = st.chat_input("Haz una pregunta sobre los documentos indexados")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Buscando evidencia y generando respuesta..."):
            try:
                result = service.answer(question)
                answer = str(result.get("answer", "No hubo respuesta."))
                contexts = result.get("contexts", [])
            except FileNotFoundError:
                answer = "No existe un indice vectorial. Sube PDFs y ejecuta la ingesta primero."
                contexts = []
            except Exception as exc:
                answer = f"No se pudo responder la pregunta: {exc}"
                contexts = []

        st.markdown(answer)
        _render_assistant_contexts(contexts)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "contexts": contexts,
        }
    )


def render_status_tab(settings: Settings) -> None:
    """Vista de estado operativo del indice y manifest de ingestion."""
    st.subheader("Estado del sistema")

    manifest_file = settings.rag_data_processed_dir / "manifest.json"
    metadata_file = settings.rag_vector_index_dir / "metadata.json"
    index_file = settings.rag_vector_index_dir / "vectors.faiss"

    manifest = read_manifest(manifest_file)

    docs_count = int(manifest.get("documents", 0))
    chunks_count = int(manifest.get("chunks", 0))
    indexed_this_run = int(manifest.get("chunks_indexed_this_run", 0))

    col1, col2, col3 = st.columns(3)
    col1.metric("Documentos", docs_count)
    col2.metric("Chunks indexados", chunks_count)
    col3.metric("Ultima ingestion", indexed_this_run)

    if index_file.exists() and metadata_file.exists():
        st.success("Indice FAISS disponible")
    else:
        st.warning("Indice FAISS no encontrado. Ejecuta una ingestion desde Upload.")

    sources = recent_sources(metadata_file=metadata_file, limit=10)
    if sources:
        st.markdown("**Fuentes recientes en metadata**")
        for source in sources:
            st.write(f"- {Path(source).name}")

    if manifest:
        with st.expander("Manifest actual"):
            st.json(manifest)


def main() -> None:
    """Punto de entrada principal de la aplicacion Streamlit."""
    st.set_page_config(page_title="PruebaRAG UI", page_icon=":books:", layout="wide")
    st.title("PruebaRAG - Streamlit")
    st.caption("Sube PDFs, ejecuta ingestion y consulta el sistema RAG en modo chat.")

    try:
        settings, service = get_runtime()
    except Exception as exc:
        st.error(f"No se pudo inicializar la aplicacion: {exc}")
        st.stop()

    init_session_state()
    render_sidebar(service=service, settings=settings)

    upload_tab, chat_tab, status_tab = st.tabs(["Upload", "Chat", "Estado"])

    with upload_tab:
        render_upload_tab(settings=settings, service=service)
    with chat_tab:
        render_chat_tab(service=service)
    with status_tab:
        render_status_tab(settings=settings)


if __name__ == "__main__":
    main()
