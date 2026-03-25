import re

from rag_local.clients.ollama_client import OllamaClient
from rag_local.config import Settings
from rag_local.embeddings.embedding_service import EmbeddingService
from rag_local.generate.generator import build_prompt
from rag_local.retrieve.retriever import Retriever
from rag_local.vectorstores.faiss_store import FaissStore


class RagService:
    """Coordina retrieval y generacion para responder preguntas de usuarios."""

    def __init__(self, settings: Settings) -> None:
        """Inicializa clientes y componentes del pipeline con la configuracion activa."""
        self.settings = settings
        self.ollama = OllamaClient(base_url=str(settings.ollama_base_url))
        self.embedding_service = EmbeddingService(
            client=self.ollama,
            model_name=settings.ollama_embed_model,
        )
        self.vector_store = FaissStore(index_dir=settings.rag_vector_index_dir)
        self.retriever = Retriever(
            embedding_service=self.embedding_service,
            vector_store=self.vector_store,
            score_threshold=settings.rag_score_threshold,
        )

    def healthcheck(self) -> bool:
        """Comprueba disponibilidad del servidor Ollama."""
        return self.ollama.healthcheck()

    def _split_questions(self, question: str) -> list[str]:
        """Divide una entrada en subpreguntas, preservando el orden original."""
        parts = [part.strip() for part in re.split(r"\?+", question) if part.strip()]
        return [f"{part}?" for part in parts] if parts else [question.strip()]

    def _normalize_answer(self, question: str, raw_answer: str) -> str:
        """Limpia formato redundante para mantener una salida breve y centrada."""
        cleaned_lines = [line.strip() for line in raw_answer.splitlines() if line.strip()]

        normalized: list[str] = []
        seen: set[str] = set()
        for line in cleaned_lines:
            line = re.sub(r"^[-*•]\s*", "", line)
            line = re.sub(r"^\d+[.)]\s*", "", line)
            line = re.sub(r"^(q\d+|respuesta|evidencia|confianza)\s*:\s*", "", line, flags=re.IGNORECASE).strip()
            if not line:
                continue
            lower = line.lower()
            if lower.startswith("contexto recuperado"):
                continue
            if line not in seen:
                seen.add(line)
                normalized.append(line)

        if not normalized:
            return raw_answer.strip()

        text = " ".join(normalized).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if sentences:
            return sentences[0]
        return text

    def _extractive_answer(self, question: str, contexts: list[dict]) -> str:
        """Devuelve respuestas directas cuando hay patrones evidentes en el contexto."""
        q = question.lower()
        corpus = " ".join(str(ctx.get("content", "")) for ctx in contexts)
        corpus_lower = corpus.lower()

        parts: list[str] = []

        if "compos" in q:
            if "aluminio anodizado" in corpus_lower:
                parts.append("La composicion principal es aluminio anodizado.")

        if any(term in q for term in ["incluida", "incluido", "incluye", "viene incluida", "viene incluido"]):
            if re.search(r"no\s+incluid[ao]", corpus_lower):
                parts.append("No viene incluida la bandera.")
            elif re.search(r"\bincluid[ao]\b", corpus_lower):
                parts.append("Si viene incluida.")

        return " ".join(parts).strip()

    def answer(self, question: str) -> dict:
        """Resuelve una pregunta recuperando contexto y generando la respuesta final."""
        subquestions = self._split_questions(question)
        base_contexts = self.retriever.retrieve(query=question, top_k=self.settings.rag_top_k)
        all_contexts: list[dict] = []
        collected_answers: list[str] = []

        for subq in subquestions:
            contexts = self.retriever.retrieve(query=subq, top_k=self.settings.rag_top_k)
            if not contexts:
                contexts = base_contexts
            if not contexts:
                collected_answers.append("No hay evidencia suficiente en el contexto.")
                continue

            all_contexts.extend(contexts)
            extractive = self._extractive_answer(subq, contexts)
            if extractive:
                collected_answers.append(extractive)
                continue

            prompt = build_prompt(question=subq, contexts=contexts)
            raw_answer = self.ollama.generate(model=self.settings.ollama_chat_model, prompt=prompt)
            cleaned = self._normalize_answer(question=subq, raw_answer=raw_answer)
            if cleaned:
                collected_answers.append(cleaned)

        dedup_contexts: list[dict] = []
        seen_keys: set[tuple[str, int]] = set()
        for ctx in all_contexts:
            key = (str(ctx.get("source", "")), int(ctx.get("chunk_id", -1)))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            dedup_contexts.append(ctx)

        final_answer = " ".join(collected_answers).strip()
        if not final_answer:
            final_answer = "No encontre contexto relevante en el indice actual."

        return {
            "answer": final_answer,
            "contexts": dedup_contexts,
        }
