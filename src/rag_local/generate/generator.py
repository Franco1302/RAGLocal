"""Utilidades para construir prompts con respuestas acotadas por evidencia."""


def build_prompt(question: str, contexts: list[dict], max_context_chars: int = 7000) -> str:
    """Construye un prompt estricto con contexto trazable y reglas anti-alucinacion."""
    safe_question = " ".join((question or "").split())
    if not safe_question:
        safe_question = "Sin pregunta"

    context_parts: list[str] = []
    used_chars = 0

    for i, item in enumerate(contexts, start=1):
        source = str(item.get("source", "desconocido"))
        score = float(item.get("score", 0.0))
        content = " ".join(str(item.get("content", "")).split())

        if not content:
            continue

        block = (
            f"[DOC D{i}]\n"
            f"source: {source}\n"
            f"score: {score:.3f}\n"
            f"content: {content}\n"
        )

        if used_chars + len(block) > max_context_chars:
            break

        context_parts.append(block)
        used_chars += len(block)

    context_block = "\n".join(context_parts) if context_parts else "[SIN CONTEXTO]"
    """
    You are an AI assistant. Provide ac
    curate responses based STRICTLY on the provided search results.

CONTEXT:
{retrieved_documents}

QUESTION:
{user_question}

STRICT GUIDELINES:
1. ONLY answer using information explicitly found in the CONTEXT
2. Citations are MANDATORY for every factual statement: [chunk_id]
3. If CONTEXT doesn't contain information to fully answer, state: 
"I cannot fully answer this question based on the available information" 
and explain what's missing
4. Do not infer, assume, or add external knowledge
5. Match the language of the user's QUESTION
6. Include relevant direct quotes from CONTEXT with citations
7. Do not preface with "based on the context" - simply provide cited answer

If CONTEXT is irrelevant or insufficient: 
"I cannot answer this question as the provided context 
does not contain relevant information about [specific topic]."
    """
    return (
        "ROL:\n"
        "Eres un asistente tecnico experto. Tu objetivo es dar respuestas estructuradas, claras y altamente legibles.\n\n"
        "REGLAS:\n"
        "1) Responde basandote UNICAMENTE en el CONTEXTO provisto.\n"
        "2) Si el contexto no contiene la informacion, di exactamente: 'No hay evidencia suficiente en el contexto'.\n"
        "3) NO inventes datos, rutas, ni dimensiones.\n"
        "4) IMPORTANTE: Usa siempre Markdown. Estructura la respuesta usando:\n"
        "   - Negritas para datos clave (ej. **50 cm**).\n"
        "   - Listas con viñetas para dimensiones o caracteristicas.\n"
        "5) Cita tus fuentes al final de la respuesta (ej. *Fuente: [DOC D1]*).\n\n"
        f"CONTEXTO:\n{context_block}\n\n"
        f"PREGUNTA:\n{safe_question}\n"
        "RESPUESTA ESTRUCTURADA EN MARKDOWN:\n"
    )
