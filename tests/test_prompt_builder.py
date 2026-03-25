from rag_local.generate.generator import build_prompt


def test_prompt_includes_question_and_context() -> None:
    prompt = build_prompt(
        question="Que version usa el sistema?",
        contexts=[
            {
                "source": "docs/arquitectura.md",
                "score": 0.92,
                "content": "La version es 1.0",
            }
        ],
    )

    assert "Que version usa el sistema?" in prompt
    assert "La version es 1.0" in prompt
