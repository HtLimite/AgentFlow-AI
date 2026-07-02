from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from app.services.text_cleaner import clean_extracted_text


class DocumentParseError(ValueError):
    pass


class ParsedDocument(dict):
    title: str
    content: str
    metadata: dict[str, object]


class DocumentParser:
    def parse_upload(self, filename: str, raw_content: bytes) -> dict[str, object]:
        suffix = Path(filename).suffix.lower().lstrip(".") or "txt"
        if suffix == "pdf" or raw_content.startswith(b"%PDF"):
            return self._parse_pdf(filename, raw_content)
        return self.parse_text(filename, self._decode_text(raw_content))

    def parse_text(self, filename: str, content: str) -> dict[str, object]:
        suffix = Path(filename).suffix.lower().lstrip(".") or "txt"
        clean_content = clean_extracted_text(content)
        if not clean_content:
            raise DocumentParseError("文档内容为空，无法建立知识库切片")
        return {"title": filename, "content": clean_content, "metadata": {"file_type": suffix}}

    def _parse_pdf(self, filename: str, raw_content: bytes) -> dict[str, object]:
        try:
            reader = PdfReader(BytesIO(raw_content))
            pages = []
            for index, page in enumerate(reader.pages, start=1):
                page_text = clean_extracted_text(page.extract_text() or "")
                if page_text:
                    pages.append(f"[第 {index} 页]\n{page_text}")
        except Exception as exc:
            raise DocumentParseError("PDF 解析失败，请确认文件未加密且包含可提取文本") from exc

        content = clean_extracted_text("\n\n".join(pages))
        if not content:
            raise DocumentParseError("PDF 未提取到文本；扫描版 PDF 需要先 OCR 后再上传")
        return {"title": filename, "content": content, "metadata": {"file_type": "pdf", "pages": len(reader.pages)}}

    def _decode_text(self, raw_content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "gb18030"):
            try:
                return raw_content.decode(encoding)
            except UnicodeDecodeError:
                continue
        raise DocumentParseError("文档编码无法识别，请转为 UTF-8 文本后再上传")


 document_parser = DocumentParser()
