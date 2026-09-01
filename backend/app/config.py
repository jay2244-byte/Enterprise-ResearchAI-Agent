import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file from root or backend directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseModel):
    PROJECT_NAME: str = "Enterprise AI Research Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research_agent.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "auto")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    MAX_SEARCH_RESULTS_PER_QUERY: int = int(os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", "4"))
    MAX_FETCH_SOURCES: int = int(os.getenv("MAX_FETCH_SOURCES", "12"))
    SEARCH_TIMEOUT_SECONDS: int = int(os.getenv("SEARCH_TIMEOUT_SECONDS", "10"))


settings = Settings()
