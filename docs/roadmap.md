# Roadmap Tecnico

## Fase 1 (actual)
- Pipeline base de ingesta y consulta.
- FAISS local + Ollama remoto en LAN.
- CLI operativa con healthcheck.

## Fase 2
- Evaluacion automatizada de calidad de respuestas.
- Cache de embeddings por hash de contenido.
- Soporte incremental de ingesta sin reindexado total.

## Fase 3
- Re-ranking con modelo cross-encoder.
- Multi-tenant por coleccion de documentos.
- API HTTP para integracion con frontends internos.

## Fase 4
- Observabilidad completa (metrics, traces, alertas).
- CI/CD con pruebas de regresion semantica.
- Politicas avanzadas de seguridad y auditoria.
