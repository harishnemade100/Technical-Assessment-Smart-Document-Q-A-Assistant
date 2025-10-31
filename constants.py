# Constants for settings

# This file defines default configuration constants used
# across the text processing or embedding modules.

# Default number of characters in each text chunk.
# Larger values mean fewer chunks but risk cutting off context.
DEFAULT_CHUNK_SIZE = 800  

# Number of overlapping characters between consecutive chunks.
# Helps preserve context between split text segments.
DEFAULT_OVERLAP = 100  


# -----------------------------------------------------------
# Default configuration constants for FAISS vector storage
# -----------------------------------------------------------


# Model Configuration
# Default Hugging Face or OpenAI embedding model used for text embeddings.
# (384 dimensions for 'all-MiniLM-L6-v2', 768 for 'BERT-base', etc.)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# Default path to store or load FAISS index files.
# You can change this if you move your index folder.
DEFAULT_FAISS_INDEX_PATH = "data/faiss_index.index"

# Default embedding vector dimension used for FAISS index.
# Must match the dimension of the model's output embeddings
# (e.g., 384 for 'all-MiniLM-L6-v2', 768 for 'BERT-base').
DEFAULT_EMBEDDING_DIM = 384

# Default number of top results to retrieve in FAISS search.
DEFAULT_TOP_K_RESULTS = 5



# -----------------------------------------------------------
# Constants for the QuestionAnsweringService and its components
# -----------------------------------------------------------

# Vector Store Configuration
DEFAULT_FAISS_INDEX_PATH = "data/faiss_index.index"

# Embedding Model Configuration
# Model used for creating text embeddings.
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM (Groq) Configuration
# Default Groq model and its parameters
DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_LLM_TEMPERATURE = 0.2

# Query/QA Configuration
DEFAULT_TOP_K_RESULTS = 5


