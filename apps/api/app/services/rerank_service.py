import re
from typing import Any

from app.services.text_cleaner import clean_extracted_text

TERM_RE = re.compile(r"[\u4e00-\u9fff]{2,}|[a-zA-Z0-9_]{2,}")
STOP_TERMS = {"什么", "怎么", "如何", "是否", "what", "how", "the", "and"}


class RerankService:
    """Lightweight rerank stage that can be replaced by a real rerank provider later."""

    def rerank(self, question: str, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        terms = self._terms(question)
        ranked: list[dict[str, Any]] = []
        for index, item in enumerate(candidates):
            content = clean_extracted_text(str(item.get("content", "")))
            lexical_boost = self._coverage(terms, content)
            base_score = float(item.get("score") or 0)
            vector_score = float(item.get("vector_score") or 0)
            rerank_score = round(base_score * 0.7 + lexical_boost * 0.2 + vector_score * 0.1, 4)
            ranked.append(
                {
                    **item,
                    "rerank_score": rerank_score,
                    "rerank_reason": f"base={base_score}; lexical_boost={round(lexical_boost, 4)}; vector={round(vector_score, 4)}; original_rank={index + 1}",
                }
            )
        return sorted(ranked, key=lambda row: float(row.get("rerank_score") or row.get("score") or 0), reverse=True)[:top_k]

    def _terms(self, text: str) -> set[str]:
        return {item.lower() for item in TERM_RE.findall(clean_extracted_text(text)) if item.lower() not in STOP_TERMS}

    def _coverage(self, terms: set[str], content: str) -> float:
        if not terms:
            return 0.0
        lower_content = content.lower()
        hits = sum(1 for term in terms if term in lower_content)
        return hits / len(terms)


rerank_service = RerankService()
