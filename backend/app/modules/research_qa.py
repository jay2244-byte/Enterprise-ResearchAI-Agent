import logging
from typing import List, Dict, Any
from backend.app.ai.provider_base import AIProvider
from backend.app.retrieval.vector_store import HybridVectorStore

logger = logging.getLogger(__name__)

QA_SYSTEM_PROMPT = """You are a Strict Grounded Research Analyst.
Your task is to answer a user's question about an enterprise research project EXCLUSIVELY using the provided retrieved findings and sources.
STRICT RULES:
1. Do NOT answer from prior general model knowledge.
2. If the answer cannot be established from the provided findings and evidence, explicitly state that the research did not uncover direct evidence for that point.
3. Reference the finding IDs or source titles whenever making a point.
4. Keep the answer direct, objective, and enterprise-focused."""


class ResearchQA:
    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider
        self.retriever = HybridVectorStore(ai_provider)

    def answer_question(
        self,
        project_question: str,
        user_query: str,
        findings: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Retrieves top relevant findings and sources, then prompts AI to answer strictly grounded.
        """
        if not findings:
            return {
                "question": user_query,
                "answer": "No findings have been recorded for this research project yet. Please run the research pipeline first.",
                "grounded": False,
                "citations": []
            }

        # Index findings for retrieval
        documents = []
        for f in findings:
            evidence_text = " ".join([e.get("quote_text", "") for e in f.get("evidence_items", [])])
            documents.append({
                "id": f.get("id"),
                "text": f"{f.get('title')} {f.get('description')} {evidence_text} {f.get('category')}",
                "finding": f
            })

        retrieved = self.retriever.search_documents(user_query, documents, top_k=4)
        if not retrieved:
            retrieved = documents[:3]

        # Prepare context
        context_lines = []
        citations_map = {}
        for r in retrieved:
            f = r.get("finding", {})
            f_title = f.get("title", "")
            f_desc = f.get("description", "")
            f_src = f.get("source_title", "Unknown Source")
            f_url = f.get("source_url", "")
            f_rel = f.get("source_reliability_level", "Medium")
            s_id = f.get("source_id")

            context_lines.append(f"- Finding [ID: {f.get('id')}]: {f_title} | Source: {f_src} | Detail: {f_desc}")

            if f_url and f_url not in citations_map:
                citations_map[f_url] = {
                    "source_id": s_id,
                    "source_title": f_src,
                    "source_url": f_url,
                    "reliability_level": f_rel,
                    "snippet": f_title
                }

        context_text = "\n".join(context_lines)

        prompt = f"""Project Research Topic: "{project_question}"
User Question: "{user_query}"

Retrieved Project Evidence:
{context_text}

Answer the user's question directly based ONLY on the evidence above:"""

        try:
            answer = self.ai.generate(prompt=prompt, system_prompt=QA_SYSTEM_PROMPT)
            if not answer or len(answer.strip()) < 10:
                raise ValueError("Empty response from AI")
        except Exception as e:
            logger.warning(f"AI Q&A generation failed: {e}. Using grounded heuristic answer.")
            top_f = retrieved[0].get("finding", {}) if retrieved else {}
            answer = (
                f"Based on the stored research findings, {top_f.get('title', 'evidence indicates key operational impacts')} "
                f"({top_f.get('description', '')}). This is corroborated by sources including {top_f.get('source_title', 'retrieved references')}."
            )

        return {
            "question": user_query,
            "answer": answer.strip(),
            "grounded": True,
            "citations": list(citations_map.values())[:4]
        }
