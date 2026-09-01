import json
import logging
import re
from typing import Dict, Any, List
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)


class GeminiAIProvider(AIProvider):
    """Google Gemini AI Provider implementation using official google-genai library."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.client = None

        if api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def get_name(self) -> str:
        return f"Google Gemini ({self.model_name})"

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.2) -> str:
        if not self.client:
            raise RuntimeError("Gemini API key is not configured.")

        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
        )
        return response.text or ""

    def generate_json(self, prompt: str, schema_description: str = "", system_prompt: str = "") -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Gemini API key is not configured.")

        formatting_instruction = (
            "\n\nCRITICAL: Respond ONLY with valid JSON conforming to the schema. "
            "Do not include any introductory remarks, markdown codeblock ticks (no ```json or ```), or trailing text."
        )
        full_prompt = f"{system_prompt}\n{schema_description}\n\n{prompt}\n{formatting_instruction}"

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
        )
        text = response.text.strip()
        # Clean markdown ticks if present
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()

        try:
            return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini raw JSON parse error: {e}. Raw text: {text[:200]}")
            # Try finding first { and last }
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                return json.loads(text[first_brace:last_brace + 1])
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Fallback to local heuristic embeddings if text-embedding not available
        from backend.app.ai.heuristic_provider import HeuristicAIProvider
        return HeuristicAIProvider().get_embeddings(texts)
