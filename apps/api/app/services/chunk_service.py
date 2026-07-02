from app.services.text_cleaner import clean_extracted_text


class ChunkService:
    def split_text(self, text: str, chunk_size: int = 800, overlap: int = 150) -> list[dict[str, object]]:
        if chunk_size <= overlap:
            raise ValueError("chunk_size must be greater than overlap")

        cleaned_text = clean_extracted_text(text)
        chunks: list[dict[str, object]] = []
        start = 0
        index = 0
        while start < len(cleaned_text):
            end = min(start + chunk_size, len(cleaned_text))
            content = clean_extracted_text(cleaned_text[start:end])
            if content:
                chunks.append({"chunk_index": index, "content": content, "token_count": max(1, len(content) // 2)})
                index += 1
            if end == len(cleaned_text):
                break
            start = end - overlap
        return chunks


chunk_service = ChunkService()
