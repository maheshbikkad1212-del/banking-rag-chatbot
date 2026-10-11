import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Banking Smart Document Understanding Chatbot (Groq RAG)"
    VERSION: str = "2.0.0"
    
    # Ingestion & Chunking parameters
    CHUNK_SIZE_TOKENS: int = 550      # Target 500-600 tokens
    CHUNK_OVERLAP_TOKENS: int = 75     # Target 50-100 tokens
    
    # Embedding model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # Retrieval parameters
    TOP_K_DENSE: int = 10
    TOP_K_SPARSE: int = 10
    TOP_K_FINAL: int = 4
    MMR_LAMBDA: float = 0.6            # Balance relevance vs diversity
    
    # Groq API Settings (Exclusive LLM Provider)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    
    # Redis / Memory Cache
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    USE_REDIS: bool = False

settings = Settings()
