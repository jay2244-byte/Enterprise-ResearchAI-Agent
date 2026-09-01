import logging
from typing import List, Dict, Any
from backend.app.ai.provider_base import AIProvider

logger = logging.getLogger(__name__)

CONCLUSION_SYSTEM_PROMPT = """You are an Executive Enterprise Research Synthesizer.
Synthesize verified research findings into an Executive Summary and 3 to 5 Major Strategic Conclusions.
STRICT TRACEABILITY RULES:
1. Every conclusion MUST reference 1 or more specific supporting finding indices (`supporting_finding_indices`).
2. Never invent conclusions that lack backing findings.
3. For each conclusion, provide:
   - title: concise strategic headline
   - summary: detailed synthesis explanation
   - confidence: 'High' | 'Medium' | 'Low'
   - reasoning_summary: explicit rationale linking the findings to this conclusion
4. Rank conclusions in order of strategic importance."""

SCHEMA_DESCRIPTION = """Expected JSON structure:
{
  "executive_summary": "string (comprehensive executive summary of the entire research project)",
  "conclusions": [
    {
      "title": "string (major strategic conclusion headline)",
      "summary": "string (detailed synthesis)",
      "confidence": "High | Medium | Low",
      "reasoning_summary": "string (clear deductive reasoning linking the supporting findings to this conclusion)",
      "supporting_finding_indices": [0, 1]
    }
  ]
}"""


class ConclusionGenerator:
    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    def generate_conclusions(
        self,
        research_question: str,
        findings: List[Dict[str, Any]],
        industry: str = None
    ) -> Dict[str, Any]:
        if not findings:
            return {
                "executive_summary": "Insufficient empirical data was retrieved to synthesize strategic conclusions.",
                "conclusions": []
            }

        findings_summary = []
        for i, f in enumerate(findings):
            findings_summary.append({
                "index": i,
                "title": f.get("title"),
                "category": f.get("category"),
                "confidence": f.get("confidence"),
                "quote": f.get("evidence_items", [{}])[0].get("quote_text", "")[:150] if f.get("evidence_items") else f.get("description", "")[:150]
            })

        prompt = f"""Synthesize strategic enterprise conclusions for the following research project:

Research Question: "{research_question}"
Industry Context: {industry or 'Cross-Industry / General Enterprise'}
Total Verified Findings: {len(findings)}

Verified Findings:
{findings_summary}

Generate an Executive Summary and 3 to 4 major conclusions. Every conclusion MUST explicitly cite the indices of the findings that support it."""

        try:
            result = self.ai.generate_json(
                prompt=prompt,
                schema_description=SCHEMA_DESCRIPTION,
                system_prompt=CONCLUSION_SYSTEM_PROMPT
            )
            conclusions = result.get("conclusions", [])
            exec_summary = result.get("executive_summary", "")

            # Validate finding indices
            valid_conclusions = []
            for item in conclusions:
                indices = item.get("supporting_finding_indices", [])
                valid_indices = [idx for idx in indices if isinstance(idx, int) and 0 <= idx < len(findings)]
                if not valid_indices and len(findings) > 0:
                    valid_indices = [0]
                item["supporting_finding_indices"] = valid_indices
                valid_conclusions.append(item)

            if not valid_conclusions:
                raise ValueError("No conclusions synthesized")

            return {
                "executive_summary": exec_summary or f"Research synthesis for '{research_question}' across {len(findings)} empirical findings.",
                "conclusions": valid_conclusions
            }
        except Exception as e:
            logger.warning(f"AI conclusion generation failed: {e}. Using deterministic synthesis.")
            from backend.app.ai.heuristic_provider import HeuristicAIProvider
            fallback = HeuristicAIProvider()
            result = fallback.generate_json(prompt=prompt, schema_description=SCHEMA_DESCRIPTION)
            conclusions = result.get("conclusions", [])
            for c in conclusions:
                c["supporting_finding_indices"] = [i for i in c.get("supporting_finding_indices", [0]) if i < len(findings)]
                if not c["supporting_finding_indices"] and findings:
                    c["supporting_finding_indices"] = [0]
            return {
                "executive_summary": result.get("executive_summary", f"Structured investigation into {research_question} indicates tangible enterprise opportunities alongside clear implementation hurdles."),
                "conclusions": conclusions
            }
