import re
from typing import Any

from app.services.text_cleaner import clean_extracted_text

CJK_RE = re.compile(r"[\u4e00-\u9fff]+")
WORD_RE = re.compile(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]*")
STOP_TERMS = {"什么", "怎么", "如何", "是否", "一个", "这个", "项目", "介绍", "what", "how", "the", "and", "for", "with"}


class RerankService:
    """Lightweight rerank stage that can be replaced by a real rerank provider later."""

    def rerank(self, question: str, candidates: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        terms = self._terms(question)
        normalized_question = clean_extracted_text(question).lower()
        ranked: list[dict[str, Any]] = []
        for index, item in enumerate(candidates):
            content = clean_extracted_text(str(item.get("content", "")))
            normalized_content = content.lower()
            lexical_boost = self._coverage(terms, normalized_content)
            intent_boost = self._intent_boost(normalized_question, normalized_content)
            base_score = float(item.get("score") or 0)
            vector_score = float(item.get("vector_score") or 0)
            rerank_score = round(base_score * 0.72 + lexical_boost * 0.14 + vector_score * 0.04 + intent_boost * 0.1, 4)
            ranked.append(
                {
                    **item,
                    "rerank_score": rerank_score,
                    "rerank_reason": f"base={base_score}; lexical_boost={round(lexical_boost, 4)}; intent_boost={round(intent_boost, 4)}; vector={round(vector_score, 4)}; original_rank={index + 1}",
                }
            )
        return sorted(ranked, key=lambda row: float(row.get("rerank_score") or row.get("score") or 0), reverse=True)[:top_k]

    def _terms(self, text: str) -> set[str]:
        cleaned = clean_extracted_text(text).lower()
        terms = {item for item in WORD_RE.findall(cleaned) if item not in STOP_TERMS and len(item) > 1}
        for block in CJK_RE.findall(cleaned):
            if block not in STOP_TERMS and len(block) > 1:
                terms.add(block)
            for size in (2, 3, 4):
                for index in range(0, max(len(block) - size + 1, 0)):
                    token = block[index : index + size]
                    if token not in STOP_TERMS:
                        terms.add(token)
        return terms

    def _coverage(self, terms: set[str], content: str) -> float:
        if not terms:
            return 0.0
        hits = sum(1 for term in terms if term in content)
        return hits / len(terms)

    def _intent_boost(self, question: str, content: str) -> float:
        score = 0.0
        if "ai devops control panel" in question and "ai devops control panel" in content:
            score += 0.2
        if any(keyword in question for keyword in ("一句话", "介绍", "定位")):
            if "一句话介绍" in content or "最终定位" in content:
                score += 0.5
            if "面向" in content and "控制台" in content:
                score += 0.3
        if "mvp" in question and "mvp" in content:
            score += 0.2
        if "简历" in question and "简历" in content:
            score += 0.2
        return min(1.0, score)


rerank_service = RerankService()
