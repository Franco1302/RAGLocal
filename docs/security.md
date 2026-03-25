# Seguridad

## Principios
- Mantener el servicio Ollama solo en red privada.
- Aplicar segmentacion de red y minimo privilegio.
- No indexar informacion sensible sin clasificacion previa.

## Controles recomendados
- Firewall por IP origen hacia puerto 11434.
- Registro de accesos y errores en `logs`.
- Separar datasets por nivel de sensibilidad.
- Enmascarar o excluir secretos antes de ingestar.

## Hardening de host Ollama
- Ejecutar en host dedicado o aislado.
- Actualizar Ollama y modelos de forma controlada.
- Monitorear consumo de recursos y reinicios.

## Hardening del cliente RAG
- Variables de entorno fuera de control de versiones.
- Sanitizar entradas para evitar prompts maliciosos.
- Mantener dependencias con parches de seguridad.

## Gobierno
- Definir responsable de datos indexados.
- Mantener inventario de fuentes documentales.
- Establecer caducidad y politica de borrado de indices.
