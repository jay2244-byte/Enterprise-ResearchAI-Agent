import logging
from backend.app.config import settings
from backend.app.ai.provider_base import AIProvider
from backend.app.ai.gemini_provider import GeminiAIProvider
from backend.app.ai.openai_provider import OpenAICompatibleProvider
from backend.app.ai.heuristic_provider import HeuristicAIProvider

logger = logging.getLogger(__name__)


def get_ai_provider() -> AIProvider:
    """
    Factory function returning the active AI provider.
    Priority:
    1. Gemini if GEMINI_API_KEY is present
    2. OpenAI/Groq if OPENAI_API_KEY is present
    3. HeuristicAIProvider (zero-config, works offline, 100% reliable)
    """
    provider_pref = settings.DEFAULT_AI_PROVIDER.lower()

    if (provider_pref in ["auto", "gemini"]) and settings.GEMINI_API_KEY:
        try:
            logger.info("Initializing Gemini AI Provider")
            return GeminiAIProvider(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.warning(f"Failed to load Gemini provider: {e}. Falling back...")

    if (provider_pref in ["auto", "openai"]) and settings.OPENAI_API_KEY:
        try:
            logger.info("Initializing OpenAI-Compatible Provider")
            return OpenAICompatibleProvider(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL or None
            )
        except Exception as e:
            logger.warning(f"Failed to load OpenAI provider: {e}. Falling back...")

    logger.info("Using Built-in Heuristic AI Engine (zero external API keys needed)")
    return HeuristicAIProvider()
