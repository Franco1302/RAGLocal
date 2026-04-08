from pathlib import Path

import typer
from rich.console import Console

from rag_local.config import get_settings
from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.ingest.pipeline import run_ingestion
from rag_local.logging_utils import configure_logging
from rag_local.rag_service import RagService

# Punto de entrada CLI del proyecto.
app = typer.Typer(add_completion=False, help="CLI para RAG local con Ollama remoto")
console = Console()


@app.command()
def health() -> None:
    """Comprueba si el servidor Ollama configurado responde correctamente."""
    settings = get_settings()
    configure_logging(settings.log_level)
    service = RagService(settings)

    if service.healthcheck():
        console.print("[green]Ollama accesible y operativo[/green]")
    else:
        console.print("[red]No se pudo acceder a Ollama. Revisa OLLAMA_BASE_URL[/red]")
        raise typer.Exit(code=1)


@app.command()
def ingest(
    source_dir: Path = typer.Option(..., help="Directorio con documentacion"),
    force: bool = typer.Option(False, "--force", "-f", help="Fuerza un reindexado completo desde cero"),
) -> None:
    """Ejecuta la ingesta completa: carga, chunking, embeddings e indexado."""
    settings = get_settings()
    configure_logging(settings.log_level)

    service = RagService(settings)
    embedding_service = EmbeddingService(
        client=service.ollama,
        model_name=settings.ollama_embed_model,
    )

    total_chunks = run_ingestion(
        source_dir=source_dir,
        processed_dir=settings.rag_data_processed_dir,
        vector_index_dir=settings.rag_vector_index_dir,
        embedding_service=embedding_service,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
        force_rebuild=force,
    )

    console.print(f"[green]Ingestion completada. Chunks indexados: {total_chunks}[/green]")


@app.command()
def query(question: str = typer.Option(..., help="Pregunta para el asistente")) -> None:
    """Responde una pregunta usando retrieval sobre el indice FAISS."""
    settings = get_settings()
    configure_logging(settings.log_level)
    service = RagService(settings)

    result = service.answer(question)

    console.print("\n[bold cyan]Respuesta[/bold cyan]")
    console.print(result["answer"])

    if result["contexts"]:
        console.print("\n[bold yellow]Contexto recuperado[/bold yellow]")
        for i, item in enumerate(result["contexts"], start=1):
            console.print(f"{i}. {item['source']} (score={item['score']:.3f})")


if __name__ == "__main__":
    app()
