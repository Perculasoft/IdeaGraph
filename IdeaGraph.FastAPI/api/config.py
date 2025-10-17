from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Graph API
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ORG_ID  = os.getenv("OPENAI_ORG_ID", "")
EMBED_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# ChromaDB
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT  = os.getenv("CHROMA_TENANT", "")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "IdeaGraph")

# FastAPI
X_API_KEY = os.getenv("X_API_KEY", "")
ALLOW_ORIGINS  = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# GitHub API
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = "https://api.github.com"

# KiGate API
KIGATE_API_URL = os.getenv("KIGATE_API_URL", "")
KIGATE_BEARER_TOKEN = os.getenv("KIGATE_BEARER_TOKEN", "")