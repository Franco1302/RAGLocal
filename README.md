# PruebaRAG

Implementacion profesional de un sistema RAG (Retrieval-Augmented Generation) para documentacion propia, con modelo local servido por Ollama en un equipo de la red LAN.

## Objetivos
- Ingestar documentacion interna (TXT, MD, PDF).
- Generar embeddings con Ollama remoto en red local.
- Indexar localmente en FAISS para baja latencia.
- Responder consultas con trazabilidad de contexto recuperado.

## Arquitectura
El flujo completo es:
1. Loader de documentos desde `data/raw`.
2. Chunking con solapamiento configurable.
3. Embedding por chunk mediante endpoint `/api/embed` de Ollama.
4. Indexado local en FAISS + metadatos en JSON.
5. Recuperacion semantica top-k por similitud coseno (IP normalizado).
6. Construccion de prompt con contexto citado.
7. Generacion final con endpoint `/api/generate`.

Consulta el detalle en `docs/architecture.md`.

## Requisitos
- Python 3.11 o superior.
- Acceso por red al host con Ollama.
- Modelos descargados en Ollama:
  - Chat model: configurar alias interno en `.env`
  - Embedding model: configurar alias interno en `.env`

## Inicializacion
```bash
cp .env.example .env
python -m pip install -e .[dev]
```

Ajusta en `.env`:
- `OLLAMA_BASE_URL` con IP y puerto reales del host Ollama.
- `OLLAMA_CHAT_MODEL` y `OLLAMA_EMBED_MODEL`.

## Uso rapido
```bash
rag health
rag ingest --source-dir data/raw
rag query --question "Que dice la politica de backups?"
```

## Interfaz web (Streamlit)
La UI permite subir PDFs y preguntar sobre el indice RAG sin usar comandos CLI.

```bash
make ui
```

Flujo recomendado:
1. Abrir la pestaña Upload en la UI.
2. Subir uno o varios PDFs.
3. Ejecutar la ingesta desde la misma pantalla.
4. Ir a la pestaña Chat para hacer preguntas.

## Estructura
- `src/rag_local`: codigo de aplicacion.
- `docs`: arquitectura, seguridad, operacion y runbooks.
- `config`: ejemplos de settings para entornos.
- `scripts`: utilidades CLI de bootstrap/ingesta/consulta.
- `tests`: pruebas unitarias base.
- `data`: almacenamiento local de entrada, artefactos y vector index.

## Calidad
```bash
make lint
make test
```

## Operacion en red local
- Verifica reachability al host Ollama desde este equipo.
- Limita el acceso al puerto 11434 por firewall a segmentos de confianza.
- No expongas Ollama a internet publica sin reverse proxy y autenticacion.

## Siguientes mejoras recomendadas
- Re-ranking cruzado para mejorar precision.
- Versionado de indices y rollback.
- Cache de embeddings por hash de chunk.
- Evaluacion automatizada con dataset de preguntas esperadas.
