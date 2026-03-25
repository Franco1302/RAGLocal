# Ollama en Red Local (LAN)

## Topologia recomendada
- Nodo A: Ollama + modelos.
- Nodo B: Aplicacion RAG (este proyecto).
- Ambos en VLAN de servidores internos o segmento controlado.

## Checklist de conectividad
1. Confirmar IP fija o reserva DHCP para Nodo A.
2. Abrir puerto TCP 11434 solo desde Nodo B.
3. Validar conectividad desde Nodo B:
   ```bash
   curl http://IP_OLLAMA:11434/api/tags
   ```
4. Configurar `.env`:
   - `OLLAMA_BASE_URL=http://IP_OLLAMA:11434`

## Recomendaciones
- Evitar Wi-Fi para trafico intensivo de embeddings.
- Si hay saltos entre subredes, medir latencia y perdida.
- Usar DNS interno para no depender de IP fija en codigo.

## Capacity planning
- Embeddings pueden generar alto trafico si hay mucha ingesta.
- Dimensionar CPU/GPU del Nodo A segun volumen y SLA.
- Programar ingestas en ventanas de baja demanda.
