from typing import List


class TextSplitter:
    """Splits text into chunks with configurable size and overlap."""

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()
            chunks.append(chunk)
            start += self.chunk_size - self.overlap
        return chunks
