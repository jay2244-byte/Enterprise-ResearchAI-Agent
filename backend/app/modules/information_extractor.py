import logging
from typing import List, Dict, Any
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are an Enterprise Intelligence Information Extractor.
Given real source content and an associated research sub-question, your job is to extract 1 to 3 distinct, high-impact empirical findings.
Rules:
1. Every finding must include an exact verbatim evidence quote from the text.
2. Provide a clear, actionable finding title and detailed description.
3. Categorize into: Technology | Business Benefit | Operational Impact | Cost | Risk | Workforce | Customer Experience | Implementation Challenge | Regulation | Future Trend.
4. Confidence must be High, Medium, or Low based on the strength of evidence.
5. Do NOT invent claims not supported by the provided text."""

SCHEMA_DESCRIPTION = """Expected JSON structure:
{
  "findings": [
    {
      "title": "string (succinct claim or finding title)",
      "description": "string (detailed explanation of the finding)",
      "category": "string (one of the 10 categories)",
      "confidence": "High | Medium | Low",
      "evidence_quote": "string (verbatim supporting quote or passage from the content)"
    }
  ]
}"""


class InformationExtractor:
    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    def extract_findings(
        self,
        source_title: str,
        source_url: str,
        content_text: str,
        question_text: str,
        category: str = "Operational Impact"
    ) -> List[Dict[str, Any]]:
        """Extract structured findings with verbatim evidence snippets."""
        # Trim text to reasonable size for model context
        text_sample = content_text[:4000] if content_text else source_title

        prompt = f"""Extract structured empirical findings from this source:

Source Title: {source_title}
Source URL: {source_url}
Research Sub-Question: {question_text}
Suggested Category: {category}

Source Content:
{text_sample}

Please extract 1 to 3 concrete findings supported directly by the text."""

        try:
            result = self.ai.generate_json(
                prompt=prompt,
                schema_description=SCHEMA_DESCRIPTION,
                system_prompt=EXTRACTION_SYSTEM_PROMPT
            )
            findings = result.get("findings", [])
            if not findings:
                raise ValueError("Empty findings returned")
            return findings
        except Exception as e:
            logger.warning(f"AI finding extraction failed: {e}. Using deterministic NLP extractor.")
            from backend.app.ai.heuristic_provider import HeuristicAIProvider
            fallback = HeuristicAIProvider()
            result = fallback.generate_json(prompt=prompt, schema_description=SCHEMA_DESCRIPTION)
            return result.get("findings", [])
