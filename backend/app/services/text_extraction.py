from fastapi import HTTPException
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)
from langchain_core.documents import Document


class TextExtractor:
    """
    LangChain-based document text extractor.

    Uses official LangChain loaders to ensure:
    - Standard Document objects
    - Page-level metadata
    - Compatibility with chunking and RAG pipelines
    """

    @staticmethod
    def extract(file_path: str) -> list[Document]:
        """
        Extracts content from supported file types and
        returns LangChain Document objects.

        :param file_path: Path to the input file.
        :type file_path: str
        :return: List of extracted Document objects.
        """
        try:
            ext = file_path.split(".")[-1].lower()

            if ext == "pdf":
                return TextExtractor._extract_pdf(file_path)
            elif ext == "txt":
                return TextExtractor._extract_txt(file_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {ext}"
                )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Text extraction failed: {str(e)}"
            )

    @staticmethod
    def _extract_pdf(file_path: str) -> list[Document]:
        """
        Extracts text from PDF using LangChain PyPDFLoader.
        Each page becomes a Document with metadata.

        :param file_path: Path to the PDF file.
        :type file_path: str
        :return: List of Document objects for each page.
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = file_path

            return documents

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF extraction error: {str(e)}"
            )

    @staticmethod
    def _extract_txt(file_path: str) -> list[Document]:
        """
        Extracts text from TXT using LangChain TextLoader.
        :param file_path: Path to the TXT file.
        :type file_path: str
        :return: List of Document objects.
        """
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()

            for doc in documents:
                doc.metadata["source"] = file_path

            return documents

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"TXT extraction error: {str(e)}"
            )
