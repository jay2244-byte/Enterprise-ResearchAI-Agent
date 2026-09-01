import logging
from typing import List, Dict, Any
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)

PLANNING_SYSTEM_PROMPT = """You are an Enterprise Research Director.
Your job is to deconstruct a high-level enterprise research question into 4 to 6 focused, analytical research sub-questions.
The sub-questions should cover:
1. Core technologies and architectures
2. Measurable operational impact & business benefits
3. Technical hurdles, cost structures, and implementation challenges
4. Operational risks, workforce/human factors, and regulatory implications
5. Emerging market trends and future evolution

Do not generate vague questions. Focus on empirical, real-world business and technical aspects."""

SCHEMA_DESCRIPTION = """Expected JSON structure:
{
  "sub_questions": [
    {
      "question_text": "string (specific subtopic question)",
      "topic_category": "string (Technology | Business Benefit | Operational Impact | Implementation Challenge | Risk | Future Trend)",
      "rationale": "string (why this question is critical for enterprise decision makers)"
    }
  ]
}"""


class ResearchPlanner:
    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    def plan_research(self, question: str, industry: str = None, scope: str = "Comprehensive") -> List[Dict[str, Any]]:
        prompt = f"""Deconstruct the following enterprise research question:
Research Question: "{question}"
Industry Context: {industry or 'Cross-Industry / General Enterprise'}
Scope: {scope}

Generate 4 to 6 focused sub-questions for empirical investigation."""

        try:
            result = self.ai.generate_json(
                prompt=prompt,
                schema_description=SCHEMA_DESCRIPTION,
                system_prompt=PLANNING_SYSTEM_PROMPT
            )
            sub_questions = result.get("sub_questions", [])
            if not sub_questions or not isinstance(sub_questions, list):
                raise ValueError("No sub_questions returned or invalid structure")
            return sub_questions
        except Exception as e:
            logger.warning(f"AI planning failed: {e}. Using deterministic fallback planner.")
            from backend.app.ai.heuristic_provider import HeuristicAIProvider
            fallback = HeuristicAIProvider()
            result = fallback.generate_json(prompt=prompt, schema_description=SCHEMA_DESCRIPTION)
            return result.get("sub_questions", [])
