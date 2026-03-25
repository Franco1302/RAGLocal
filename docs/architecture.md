# Arquitectura Tecnica

## Componentes
- Cliente Ollama: encapsula llamadas HTTP a `/api/embed` y `/api/generate`.
- Ingestion Pipeline: carga documentos, trocea, embeddea e indexa.
- Vector Store (FAISS): persistencia local de embeddings normalizados.
- Retriever: recupera top-k y filtra por umbral de score.
- Prompt Builder: arma prompt final con contexto y trazabilidad.
- RAG Service: orquesta retrieval + generation.
- CLI: interfaz operativa para health, ingest y query.

## Flujo de datos
1. Entrada: archivos en `data/raw`.
2. Parsing: texto plano por documento.
3. Chunking: bloques de `RAG_CHUNK_SIZE` con `RAG_CHUNK_OVERLAP`.
4. Embeddings: vectorizacion remota por Ollama.
5. Indexado: FAISS `IndexFlatIP` con normalizacion L2.
6. Consulta: embedding de la pregunta.
7. Recuperacion: top-k por similitud.
8. Generacion: respuesta con prompt contextual.

## Decisiones de diseño
- FAISS local para minimizar dependencia externa y costo operativo.
- Ollama remoto en LAN para separar carga de inferencia.
- Metadatos desacoplados en JSON para inspeccion y auditoria.
- CLI para operacion simple y automatizable por cron/CI.

## Escalabilidad
- Vertical: incrementar RAM/CPU del nodo que indexa.
- Horizontal: separar nodo de ingesta y nodo de consulta.
- Al crecer documentos: migrar a vector DB con ANN persistente distribuido.

## Riesgos y mitigaciones
- Latencia de red a Ollama: mantener host en misma subred o VLAN de baja latencia.
- Drift de embeddings por cambio de modelo: versionar indice por modelo.
- Hallucinations: responder solo con evidencia y fallback de insuficiencia.
