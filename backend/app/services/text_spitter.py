import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.app.settings.constants import DEFAULT_CHUNK_SIZE, DEFAULT_OVERLAP


class ChunkingService:
    """
    Structure-aware + semantic chunking service for splitting documents into smaller, manageable pieces.
    Uses recursive character splitting with custom chunk size and overlap.
    """

    def __init__(self, doc_type: str = "general"):
        self.chunk_size = DEFAULT_CHUNK_SIZE if doc_type == "legal" else 600
        self.chunk_overlap = DEFAULT_OVERLAP if doc_type == "legal" else 150

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def chunk(self, documents: list[Document]) -> list[Document]:
        '''
        Splits documents into smaller chunks while preserving structure.
        semantic chunking by first splitting on sections/headings,
        then applying recursive character splitting within those sections.
        
        
        :param self: Description
        :param documents: Description
        :type documents: list[Document]
        :return: Description
        :rtype: list[Document]

        '''
        chunks = []

        for doc in documents:
            sections = re.split(
                r"\n(?=[A-Z][^\n]{3,50}\n)",
                doc.page_content
            )

            for section in sections:
                for text in self.splitter.split_text(section):
                    chunks.append(
                        Document(
                            page_content=text,
                            metadata=doc.metadata
                        )
                    )

        return chunks