# Operacion y Runbook

## Preparacion inicial
1. Copiar `.env.example` a `.env`.
2. Configurar URL y modelos Ollama.
3. Instalar dependencias.
4. Validar conectividad con `rag health`.

## Ingestion
- Depositar documentos en `data/raw`.
- Ejecutar:
  ```bash
  rag ingest --source-dir data/raw
  ```
- Verificar artefactos:
  - `data/vector_index/vectors.faiss`
  - `data/vector_index/metadata.json`
  - `data/processed/manifest.json`

## Consultas
```bash
rag query --question "Pregunta sobre la documentacion"
```

## Mantenimiento
- Reindexar tras cambios relevantes de documentacion.
- Reindexar al cambiar modelo de embeddings.
- Respaldar periodicamente `data/vector_index`.

## Incidencias comunes
- Error de conexion a Ollama:
  - Revisar `OLLAMA_BASE_URL`.
  - Probar reachability por red y firewall.
- Pocas respuestas relevantes:
  - Incrementar `RAG_TOP_K`.
  - Reducir `RAG_SCORE_THRESHOLD`.
  - Ajustar chunk size/overlap.
- Ingesta lenta:
  - Revisar latencia al host Ollama.
  - Procesar por lotes de documentos.
