import re

from app.services.text_cleaner import clean_extracted_text

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


class ChunkService:
    def split_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> list[dict[str, object]]:
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")

        cleaned_text = clean_extracted_text(text)
        if not cleaned_text:
            return []

        if self._looks_like_markdown(cleaned_text):
            chunks = self._split_markdown(cleaned_text, chunk_size)
        else:
            chunks = self._split_plain_text(cleaned_text, chunk_size, overlap)

        return [
            {"chunk_index": index, "content": content, "token_count": max(1, len(content) // 2)}
            for index, content in enumerate(chunks)
            if content
        ]

    def _looks_like_markdown(self, text: str) -> bool:
        return "\n#" in text or "```" in text or "\n- " in text or "\n|" in text

    def _split_markdown(self, text: str, chunk_size: int) -> list[str]:
        sections = self._markdown_sections(text)
        chunks: list[str] = []
        current = ""
        for section in sections:
            if len(section) > chunk_size:
                if current:
                    chunks.append(clean_extracted_text(current))
                    current = ""
                chunks.extend(self._split_long_section(section, chunk_size))
                continue
            if current and len(current) + len(section) + 2 > chunk_size:
                chunks.append(clean_extracted_text(current))
                current = section
            else:
                current = f"{current}\n\n{section}" if current else section
        if current:
            chunks.append(clean_extracted_text(current))
        return chunks

    def _markdown_sections(self, text: str) -> list[str]:
        sections: list[str] = []
        current_lines: list[str] = []
        heading_stack: list[str] = []

        for line in text.splitlines():
            match = HEADING_RE.match(line)
            if match:
                if current_lines:
                    sections.append(clean_extracted_text("\n".join(current_lines)))
                    current_lines = []
                level = len(match.group(1))
                title = match.group(2).strip()
                heading_stack = heading_stack[: level - 1]
                heading_stack.append(title)
                current_lines.append(" > ".join(heading_stack))
                continue
            current_lines.append(line)

        if current_lines:
            sections.append(clean_extracted_text("\n".join(current_lines)))
        return [section for section in sections if section]

    def _split_long_section(self, section: str, chunk_size: int) -> list[str]:
        parts = re.split(r"\n\s*\n", section)
        chunks: list[str] = []
        current = ""
        heading = parts[0] if parts and len(parts[0]) < 160 else ""
        for part in parts:
            part = clean_extracted_text(part)
            if not part:
                continue
            if len(part) > chunk_size:
                if current:
                    chunks.append(clean_extracted_text(current))
                    current = ""
                chunks.extend(self._split_plain_text(f"{heading}\n{part}" if heading and heading not in part else part, chunk_size, overlap=0))
                continue
            if current and len(current) + len(part) + 2 > chunk_size:
                chunks.append(clean_extracted_text(current))
                current = f"{heading}\n{part}" if heading and heading not in part else part
            else:
                current = f"{current}\n\n{part}" if current else part
        if current:
            chunks.append(clean_extracted_text(current))
        return chunks

    def _split_plain_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            if end < len(text):
                boundary = max(text.rfind("\n\n", start, end), text.rfind("。", start, end), text.rfind("\n", start, end))
                if boundary > start + chunk_size // 2:
                    end = boundary + 1
            content = clean_extracted_text(text[start:end])
            if content:
                chunks.append(content)
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)
        return chunks


chunk_service = ChunkService()
