def build_prompt(question: str, contexts: list[dict]) -> str:
    context_block = "\n\n".join(
        [
            f"[Fuente: {item['source']} | score={item['score']:.3f}]\n{item['content']}"
            for item in contexts
        ]
    )

    return (
        "Eres un asistente tecnico. Responde en espanol basandote solo en el contexto. "
        "Si no hay contexto suficiente, indicalo explicitamente.\n\n"
        f"Contexto:\n{context_block}\n\n"
        f"Pregunta: {question}\n"
        "Respuesta:"
    )
