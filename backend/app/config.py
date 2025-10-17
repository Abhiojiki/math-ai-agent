"""
Production-ready configuration with environment variable support.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get paths
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load environment variables
env_path = BACKEND_DIR.parent / ".env"
load_dotenv(env_path)

class Settings:
    """Application settings with production defaults."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    WOLFRAM_APP_ID: str = os.getenv("WOLFRAM_APP_ID", "")
    
    # Qdrant Cloud Settings
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "math_knowledge_base")
    
    # Paths
    BASE_DIR: Path = BACKEND_DIR
    DATA_DIR: Path = DATA_DIR
    DATASET_PATH: Path = DATA_DIR / "math_kb.json"
    DATABASE_PATH: Path = DATA_DIR / "conversations.db"
    
    # Model Settings
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Search Settings
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    SCORE_THRESHOLD: float = float(os.getenv("SCORE_THRESHOLD", "0.5"))
    
    # Server Settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # CORS - Updated for production
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://*.vercel.app"
    ).split(",")
    
    def validate(self):
        """Validate required settings."""
        errors = []
        
        if not self.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY not set")
        if not self.QDRANT_URL:
            errors.append("QDRANT_URL not set")
        if not self.QDRANT_API_KEY:
            errors.append("QDRANT_API_KEY not set")
        
        if errors:
            raise ValueError(f"Missing configuration: {', '.join(errors)}")
        
        # Create data directory
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✅ Config validated. Data dir: {self.DATA_DIR}")

settings = Settings()
