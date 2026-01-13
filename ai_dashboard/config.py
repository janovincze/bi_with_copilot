"""
Configuration management for Copilot Analytics.
Supports multiple LLM backends: GitHub Copilot, OpenAI, Ollama.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DBT_PROJECT_DIR = BASE_DIR / "dbt_project"
DATABASE_PATH = DBT_PROJECT_DIR / "jaffle_shop.duckdb"

# LLM Configuration
# Default to GitHub Copilot via copilot-api
COPILOT_API_URL = os.getenv("COPILOT_API_URL", "http://localhost:4141/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4.1")

# Alternative: OpenAI directly
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1"

# Alternative: Ollama (local)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ChromaDB configuration (for RAG vector storage)
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_data"


def get_llm_config():
    """
    Returns the appropriate LLM configuration based on environment.
    Priority: OpenAI API key > Ollama > Copilot API
    """
    if OPENAI_API_KEY:
        return {
            "type": "openai",
            "api_key": OPENAI_API_KEY,
            "base_url": OPENAI_API_URL,
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        }

    # Default to Copilot API
    return {
        "type": "copilot",
        "api_key": "copilot",  # Any value works with copilot-api
        "base_url": COPILOT_API_URL,
        "model": LLM_MODEL,
    }


def print_config():
    """Print current configuration for debugging."""
    config = get_llm_config()
    print(f"LLM Backend: {config['type']}")
    print(f"Base URL: {config['base_url']}")
    print(f"Model: {config['model']}")
    print(f"Database: {DATABASE_PATH}")
    print(f"ChromaDB: {CHROMA_PERSIST_DIR}")


if __name__ == "__main__":
    print_config()
