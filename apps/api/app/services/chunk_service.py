class ChunkService:
    def split_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> list[dict[str, object]]:
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")
        chunks: list[dict[str, object]] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            content = text[start:end]
            chunks.append({"chunk_index": index, "content": content, "token_count": max(1, len(content) // 2)})
            if end == len(text):
                break
            start = end - overlap
            index += 1
        return chunks


chunk_service = ChunkService()
