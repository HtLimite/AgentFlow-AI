import re
import unicodedata

_CONTROL_PLACEHOLDER = " "
_CJK_RANGE = "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff"


def clean_extracted_text(text: str) -> str:
    """Normalize text extracted from PDFs before chunking or rendering.

    PDF parsers often return invisible control characters (for example ``\x01``),
    compatibility CJK glyphs, repeated spaces and broken newlines. Those characters
    pollute chunks and make RAG answers look like binary garbage even when the PDF
    itself was parsed successfully.
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\ufeff", "").replace("\ufffd", "")

    chars: list[str] = []
    for char in normalized:
        if char in "\n\r\t":
            chars.append(char)
            continue
        category = unicodedata.category(char)
        if category.startswith("C"):
            chars.append(_CONTROL_PLACEHOLDER)
            continue
        chars.append(char)

    cleaned = "".join(chars)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[\t\x0b\x0c ]+", " ", cleaned)
    cleaned = re.sub(fr"(?<=[{_CJK_RANGE}])\s+(?=[{_CJK_RANGE}])", "", cleaned)
    cleaned = re.sub(fr"(?<=[{_CJK_RANGE}])\s+(?=[,.;:!?，。；：！？、）】》])", "", cleaned)
    cleaned = re.sub(fr"(?<=[（【《])\s+(?=[{_CJK_RANGE}])", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
    return cleaned.strip()


def make_snippet(text: str, max_length: int = 360) -> str:
    cleaned = clean_extracted_text(text)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 1].rstrip() + "…"
