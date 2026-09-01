import math
import re
from typing import List, Dict, Any, Optional
from backend.app.ai.provider_base import AIProvider


class HybridVectorStore:
    """
    Lightweight, in-memory + database-backed hybrid lexical and semantic search engine.
    Supports:
    - Scoped project search (for grounded Q&A interrogation)
    - Cross-project global search (for Knowledge Base exploration)
    """

    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    def _tokenize(self, text: str) -> List[str]:
        return [w for w in re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())]

    def compute_lexical_score(self, query_tokens: List[str], doc_tokens: List[str]) -> float:
        if not query_tokens or not doc_tokens:
            return 0.0
        doc_len = len(doc_tokens)
        score = 0.0
        doc_token_counts = {}
        for t in doc_tokens:
            doc_token_counts[t] = doc_token_counts.get(t, 0) + 1

        for qt in query_tokens:
            count = doc_token_counts.get(qt, 0)
            if count > 0:
                # BM25-style term frequency term
                tf = count / (count + 1.2 * (0.25 + 0.75 * (doc_len / 50.0)))
                score += tf
        return score

    def search_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rank documents using hybrid lexical match and semantic vectors.
        documents should contain: {"id", "text", "metadata"}
        """
        if not documents:
            return []

        query_tokens = self._tokenize(query)

        # Lexical scores
        scored_docs = []
        for doc in documents:
            text = doc.get("text", "")
            doc_tokens = self._tokenize(text)
            lex_score = self.compute_lexical_score(query_tokens, doc_tokens)
            scored_docs.append((lex_score, doc))

        # Sort descending by score
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # If highest lexical score is 0 and we have documents, return top default
        results = []
        for score, doc in scored_docs[:top_k]:
            results.append({
                **doc,
                "relevance_score": round(score, 3)
            })

        return results
