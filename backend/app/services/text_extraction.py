from PyPDF2 import PdfReader
from fastapi import HTTPException


class TextExtractor:
    """
    Extracts text content from supported document formats.
    """

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Extracts text depending on file type.
        """
        try:
            ext = file_path.split(".")[-1].lower()

            if ext == "pdf":
                return TextExtractor._extract_pdf_text(file_path)
            elif ext == "txt":
                return TextExtractor._extract_txt_text(file_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    @staticmethod
    def _extract_pdf_text(file_path: str) -> str:
        """
        Extracts text from PDF using PyPDF2.
        """
        try:
            text = ""
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF extraction error: {str(e)}")

    @staticmethod
    def _extract_txt_text(file_path: str) -> str:
        """
        Extracts text from plain .txt files.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TXT extraction error: {str(e)}")