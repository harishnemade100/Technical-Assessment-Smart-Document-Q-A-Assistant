import fitz  # PyMuPDF


class TextExtractor:
    """Extracts text from supported file types."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = file_path.split(".")[-1].lower()
        if ext == "pdf":
            return TextExtractor._extract_pdf_text(file_path)
        elif ext == "txt":
            return TextExtractor._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text.strip()

    @staticmethod
    def _extract_txt_text(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()