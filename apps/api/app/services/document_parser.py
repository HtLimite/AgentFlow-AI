from pathlib import Path


class ParsedDocument(dict):
    title: str
    content: str
    metadata: dict[str, object]


class DocumentParser:
    def parse_text(self, filename: str, content: str) -> dict[str, object]:
        suffix = Path(filename).suffix.lower().lstrip(".") or "txt"
        return {"title": filename, "content": content.strip(), "metadata": {"file_type": suffix}}


document_parser = DocumentParser()
