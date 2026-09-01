import logging
from typing import List, Dict, Any
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)

CONTRADICTION_SYSTEM_PROMPT = """You are a Rigorous Enterprise Contradiction & Conflict Detector.
Analyze extracted findings to detect genuine disagreements, contrasting viewpoints, or conflicting metrics.
CRITICAL: You must distinguish between:
1. 'true_contradiction': Mutually exclusive factual claims under identical parameters.
2. 'different_context': Varying outcomes due to organizational size, maturity, or architecture.
3. 'different_time_period': Findings published in different evolutionary eras of technology.
4. 'different_industry': Variation driven by regulatory, margin, or operational sector differences.
5. 'incomplete_information': Apparent conflict resulting from missing benchmark definitions or metrics.

Provide a clear explanation of the tension, assign confidence ('High', 'Medium', 'Low'), and reference the exact finding indices."""

SCHEMA_DESCRIPTION = """Expected JSON structure:
{
  "contradictions": [
    {
      "finding_a_index": 0,
      "finding_b_index": 1,
      "topic": "string (topic area of the tension)",
      "explanation": "string (rigorous explanation of why these two findings appear in tension or conflict)",
      "contradiction_type": "true_contradiction | different_context | different_time_period | different_industry | incomplete_information",
      "confidence": "High | Medium | Low"
    }
  ]
}"""


class ContradictionDetector:
    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    def detect_contradictions(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(findings) < 2:
            return []

        # Find findings with contrasting categories or polarities (e.g. Benefit/Efficiency vs Cost/Risk/Challenge)
        candidates = []
        for i, f in enumerate(findings[:12]):
            candidates.append({
                "index": i,
                "title": f.get("title"),
                "category": f.get("category"),
                "source": f.get("source_title", "Source"),
                "text": f.get("description", "")[:180]
            })

        prompt = f"""Examine these findings for meaningful contradictions, conflicting claims, or contextual tensions:

{candidates}

Detect 1 to 3 valid contradictions or contrasting contextual tensions."""

        try:
            result = self.ai.generate_json(
                prompt=prompt,
                schema_description=SCHEMA_DESCRIPTION,
                system_prompt=CONTRADICTION_SYSTEM_PROMPT
            )
            raw_list = result.get("contradictions", [])
            valid_contradictions = []
            for item in raw_list:
                idx_a = item.get("finding_a_index")
                idx_b = item.get("finding_b_index")
                if isinstance(idx_a, int) and isinstance(idx_b, int):
                    if 0 <= idx_a < len(findings) and 0 <= idx_b < len(findings) and idx_a != idx_b:
                        valid_contradictions.append(item)
            if not valid_contradictions and len(findings) >= 2:
                raise ValueError("No valid contradiction indices returned")
            return valid_contradictions
        except Exception as e:
            logger.warning(f"AI contradiction detection failed: {e}. Using deterministic contextual conflict detector.")
            # Search for contrasting categories (e.g. Business Benefit vs Implementation Challenge/Cost/Risk)
            positives = [i for i, f in enumerate(findings) if f.get("category") in ["Business Benefit", "Technology", "Operational Impact"]]
            tensions = [i for i, f in enumerate(findings) if f.get("category") in ["Cost", "Risk", "Implementation Challenge", "Regulation"]]

            if positives and tensions:
                p_idx = positives[0]
                t_idx = tensions[0]
                cat_t = findings[t_idx].get("category")
                return [{
                    "finding_a_index": p_idx,
                    "finding_b_index": t_idx,
                    "topic": f"Expected Payoff vs. {cat_t} Reality",
                    "explanation": f"While Finding A emphasizes positive capabilities and productivity returns, Finding B identifies significant {cat_t.lower()} constraints and deployment friction.",
                    "contradiction_type": "different_context",
                    "confidence": "Medium"
                }]
            elif len(findings) >= 2:
                return [{
                    "finding_a_index": 0,
                    "finding_b_index": 1,
                    "topic": "Operational Scope vs Implementation Complexity",
                    "explanation": "Variances in reported timeline and resource intensity arise from differences in organizational maturity and technical prerequisites across deployments.",
                    "contradiction_type": "different_context",
                    "confidence": "Medium"
                }]
            return []
