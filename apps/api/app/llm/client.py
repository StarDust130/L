from google import genai
from groq import AsyncGroq

from app.core.config import get_settings

settings = get_settings()

# 🤖 Create one async LLM client for the application.
groq_client = AsyncGroq(
    api_key=settings.groq_api_key,
)

# 🌟 Gemini client
gemini_client = genai.Client(
    api_key=settings.gemini_api_key
)
