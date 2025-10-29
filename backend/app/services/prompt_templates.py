class PromptTemplates:
    
    @staticmethod
    def qa_template() -> str:
        """
        Returns the QA template used for ChatPromptTemplate.
        """
        return (
            "You are a helpful AI assistant. Use the provided context to answer the question accurately.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer:"
        )