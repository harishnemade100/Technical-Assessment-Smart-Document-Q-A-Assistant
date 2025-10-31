class TextSplitter:
    """
    Splits text into smaller chunks for embedding.
    Each chunk overlaps to preserve context.
    """

    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text: str) -> list[str]:
        """
        Splits text into overlapping chunks.
        """
        try:
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
        except Exception as e:
            raise ValueError(f"Text splitting failed: {str(e)}")