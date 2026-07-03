import hashlib
import math


class VectorService:
    """Lightweight deterministic vector service for local RAG demos.

    The production path can replace this with real embedding providers and pgvector.
    """

    def embed(self, text: str, dimensions: int = 64) -> list[float]:
        vector = [0.0] * dimensions
        tokens = [token for token in text.lower().replace("，", " ").replace("。", " ").split() if token]
        if not tokens:
            tokens = list(text.lower())[:dimensions]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimensions
            value = (digest[4] / 255.0) * 2 - 1
            vector[index] += value
        norm = math.sqrt(sum(item * item for item in vector)) or 1.0
        return [round(item / norm, 6) for item in vector]

    def cosine(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        return round(sum(left[index] * right[index] for index in range(size)), 6)


vector_service = VectorService()
