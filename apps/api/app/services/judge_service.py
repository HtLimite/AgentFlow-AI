import re
from dataclasses import dataclass

from app.services.text_cleaner import clean_extracted_text

TERM_RE = re.compile(r"[\u4e00-\u9fff]{2,}|[a-zA-Z0-9_]{2,}")
STOP_TERMS = {"什么", "怎么", "如何", "是否", "what", "how", "the", "and"}


@dataclass
class JudgeResult:
    score: float
    reason: str
    mode: str
    matched_terms: int
    total_terms: int


class JudgeService:
    """LLM-as-Judge compatible scoring protocol with deterministic local fallback."""

    async def judge(self, question: str, answer: str, expected_answer: str, scoring_criteria: str, citation_count: int) -> JudgeResult:
        cleaned_answer = clean_extracted_text(answer)
        terms = self._terms(f"{expected_answer} {scoring_criteria}")
        if terms:
            hits = sum(1 for term in terms if term.lower() in cleaned_answer.lower())
            score = round((hits / len(terms)) * 100, 2)
            reason = f"matched_terms={hits}/{len(terms)}"
        else:
            hits = 1 if cleaned_answer else 0
            score = 100.0 if cleaned_answer else 0.0
            reason = "no_expected_terms; answer_presence_score"
        if citation_count == 0:
            score = min(score, 60.0)
            reason += "; no_citations_cap=60"
        if not cleaned_answer:
            score = 0.0
            reason += "; empty_answer"
        return JudgeResult(score=score, reason=reason, mode="heuristic_judge", matched_terms=hits, total_terms=len(terms))

    def _terms(self, text: str) -> set[str]:
        return {item for item in TERM_RE.findall(clean_extracted_text(text)) if item.lower() not in STOP_TERMS}


judge_service = JudgeService()
