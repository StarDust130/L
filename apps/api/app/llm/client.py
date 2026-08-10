from app.core.config import get_settings
from groq import AsyncGroq

settings = get_settings()

# 🤖 Create one async LLM client for the application.
client = AsyncGroq(
    api_key=settings.groq_api_key,
)
