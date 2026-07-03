from typing import Any


def repair_mojibake_text(value: str) -> str:
    """Repair common UTF-8 text that was decoded as GB18030/GBK.

    Example: "璇疯皟鐢�" -> "请调用".
    If repair is not possible or does not improve the text, return the original value.
    """
    if not value:
        return value
    try:
        candidate = value.encode("gb18030").decode("utf-8")
    except UnicodeError:
        return value
    return candidate if _looks_better(candidate, value) else value


def repair_mojibake(value: Any) -> Any:
    if isinstance(value, str):
        return repair_mojibake_text(value)
    if isinstance(value, list):
        return [repair_mojibake(item) for item in value]
    if isinstance(value, tuple):
        return tuple(repair_mojibake(item) for item in value)
    if isinstance(value, dict):
        return {repair_mojibake(key): repair_mojibake(item) for key, item in value.items()}
    return value


def _looks_better(candidate: str, original: str) -> bool:
    if candidate == original:
        return False
    original_score = _mojibake_score(original)
    candidate_score = _mojibake_score(candidate)
    if candidate_score < original_score:
        return True
    return _cjk_count(candidate) >= _cjk_count(original) and candidate_score == 0 and original_score > 0


def _mojibake_score(value: str) -> int:
    markers = "锟斤拷烫屯�"
    suspicious_chars = set("璇鐢煡嗗簱宸叿鍥炵瓟鎶攢娴佺▼粈涔堬紵")
    return sum(2 for char in value if char in markers) + sum(1 for char in value if char in suspicious_chars or "\ue000" <= char <= "\uf8ff")


def _cjk_count(value: str) -> int:
    return sum(1 for char in value if "\u4e00" <= char <= "\u9fff")
