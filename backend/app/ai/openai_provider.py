import json
import logging
import re
from typing import Dict, Any, List
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(AIProvider):
    """Provider for OpenAI, Groq, Ollama, OpenRouter, or any OpenAI-compatible API."""

    def __init__(self, api_key: str, base_url: str = None, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.client = None

        if api_key:
            try:
                from openai import OpenAI
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                self.client = OpenAI(**kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def get_name(self) -> str:
        return f"OpenAI Compatible ({self.model_name})"

    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.2) -> str:
        if not self.client:
            raise RuntimeError("OpenAI API key is not configured.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def generate_json(self, prompt: str, schema_description: str = "", system_prompt: str = "") -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI API key is not configured.")

        formatting_instruction = (
            "\n\nCRITICAL: Respond ONLY with valid JSON conforming to the schema. "
            "Do not include any introductory remarks, markdown codeblock ticks, or trailing text."
        )
        full_system = f"{system_prompt}\n{schema_description}\n{formatting_instruction}"

        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt}
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"} if "gpt-" in self.model_name else None,
            temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()

        try:
            return json.loads(text)
        except Exception as e:
            logger.warning(f"OpenAI JSON parse error: {e}. Raw text: {text[:200]}")
            first_brace = text.find("{")
            last_brace = text.rfind("}")
            if first_brace != -1 and last_brace != -1:
                return json.loads(text[first_brace:last_brace + 1])
            raise

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        from backend.app.ai.heuristic_provider import HeuristicAIProvider
        return HeuristicAIProvider().get_embeddings(texts)
