import re
from typing import Any

from app.services.text_cleaner import clean_extracted_text, make_snippet

CODE_BLOCK_RE = re.compile(r"```(?:[a-zA-Z0-9_-]+)?\s*(.*?)```", re.DOTALL)
INTRO_LABEL_RE = re.compile(r"(?:一句话介绍|项目描述|项目简介|最终定位)\s*[:：]?\s*(.*)", re.IGNORECASE)
SENTENCE_END_RE = re.compile(r"(?<=[。！？.!?])\s*")


class RagAnswerService:
    def build_answer(self, question: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        cleaned_question = clean_extracted_text(question)
        if not chunks:
            return {
                "summary": f"知识库中没有找到与“{cleaned_question}”直接相关的内容。",
                "answer": f"知识库中没有找到与“{cleaned_question}”直接相关的内容。请确认已上传对应文档，或换一个知识库后再问。",
                "evidence": [],
            }

        summary = self._extract_direct_answer(cleaned_question, chunks) or make_snippet(str(chunks[0].get("content", "")), 180)
        evidence = [self._build_evidence_item(item, index) for index, item in enumerate(chunks, start=1)]
        answer = self._render_markdown_answer(summary, evidence)
        return {"summary": summary, "answer": answer, "evidence": evidence}

    def _extract_direct_answer(self, question: str, chunks: list[dict[str, Any]]) -> str | None:
        normalized_question = clean_extracted_text(question).lower()
        for item in chunks:
            content = clean_extracted_text(str(item.get("content", "")))
            if any(keyword in normalized_question for keyword in ("一句话", "介绍", "定位", "是什么")):
                extracted = self._extract_intro_answer(content)
                if extracted:
                    return extracted
        return None

    def _extract_intro_answer(self, content: str) -> str | None:
        lines = [line.strip() for line in content.splitlines()]
        for index, line in enumerate(lines):
            if "一句话介绍" not in line and "项目描述" not in line and "项目简介" not in line:
                continue
            inline = INTRO_LABEL_RE.search(line)
            if inline and inline.group(1).strip():
                return make_snippet(inline.group(1).strip(), 260)
            following = "\n".join(lines[index + 1 : index + 8]).strip()
            code_match = CODE_BLOCK_RE.search(following)
            if code_match:
                return make_snippet(clean_extracted_text(code_match.group(1)), 260)
            for candidate in lines[index + 1 : index + 8]:
                if candidate and not candidate.startswith("```") and not candidate.startswith("#"):
                    return make_snippet(candidate, 260)
        for sentence in SENTENCE_END_RE.split(content):
            cleaned = clean_extracted_text(sentence)
            if "面向" in cleaned and "控制台" in cleaned:
                return make_snippet(cleaned, 260)
        return None

    def _build_evidence_item(self, item: dict[str, Any], index: int) -> dict[str, Any]:
        content = clean_extracted_text(str(item.get("content", "")))
        return {
            "index": index,
            "document": str(item.get("document") or "unknown"),
            "content": make_snippet(content, 360),
            "score": item.get("score"),
            "lexical_score": item.get("lexical_score"),
            "vector_score": item.get("vector_score"),
            "rerank_score": item.get("rerank_score"),
            "strategy": item.get("strategy"),
        }

    def _render_markdown_answer(self, summary: str, evidence: list[dict[str, Any]]) -> str:
        if not evidence:
            return summary
        lines = ["## 答案", summary, "", "## 依据"]
        for item in evidence[:3]:
            lines.append(f"### 来源 {item['index']} · {item['document']}")
            lines.append(str(item["content"]))
            lines.append("")
        return "\n".join(lines).strip()


rag_answer_service = RagAnswerService()
