import re
import urllib.parse
from typing import Dict, Any


class SourceEvaluator:
    """
    Structured, rule-based reliability evaluation engine.
    Calculates transparent scores from 0-100 based on objective domain signals,
    publisher reputation, recency, relevance, and substantive depth.
    """

    HIGH_AUTHORITY_DOMAINS = {
        "gov", "mil", "edu", "ac.uk", "europa.eu", "who.int", "un.org",
        "nist.gov", "whitehouse.gov", "nature.com", "science.org",
        "ieee.org", "acm.org", "arxiv.org", "wikipedia.org"
    }

    ESTABLISHED_INDUSTRY_ANALYSTS = {
        "gartner", "forrester", "mckinsey", "bain", "bcg", "pwc", "deloitte",
        "kpmg", "accenture", "weforum", "brookings", "idc", "mit", "stanford",
        "reuters", "bloomberg", "wsj", "ft", "economist", "harvard"
    }

    KNOWN_TECH_ENTERPRISES = {
        "microsoft", "google", "aws", "amazon", "ibm", "nvidia", "intel",
        "cisco", "oracle", "siemens", "ge", "sap", "salesforce"
    }

    def evaluate_source(
        self,
        url: str,
        title: str,
        source_type: str,
        content_text: str,
        word_count: int,
        publication_date: str = None,
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Computes structured reliability score (0-100), level (High/Medium/Low),
        and a detailed point breakdown.
        """
        breakdown = {}
        domain = urllib.parse.urlparse(url).netloc.lower()
        domain_clean = re.sub(r"^www\.", "", domain)

        # 1. Domain Authority & Source Type (0 - 35 points)
        type_score = 0
        is_high_tld = any(domain_clean.endswith(f".{tld}") or f".{tld}." in domain_clean for tld in self.HIGH_AUTHORITY_DOMAINS)
        is_analyst = any(pub in domain_clean for pub in self.ESTABLISHED_INDUSTRY_ANALYSTS)
        is_tech_corp = any(corp in domain_clean for corp in self.KNOWN_TECH_ENTERPRISES)

        if is_high_tld or source_type in ["government", "academic"]:
            type_score = 35
            breakdown["domain_authority"] = {"score": 35, "max": 35, "rationale": "High-authority academic or governmental domain (.edu, .gov, peer-reviewed)"}
        elif is_analyst or source_type in ["research_organisation", "industry_report"]:
            type_score = 30
            breakdown["domain_authority"] = {"score": 30, "max": 35, "rationale": "Established research analyst, major consultancy, or institutional publisher"}
        elif is_tech_corp or source_type == "company":
            type_score = 24
            breakdown["domain_authority"] = {"score": 24, "max": 35, "rationale": "Verified enterprise vendor with primary technical documentation"}
        elif source_type == "news":
            type_score = 22
            breakdown["domain_authority"] = {"score": 22, "max": 35, "rationale": "Commercial news publication with journalistic editorial standards"}
        else:
            type_score = 15
            breakdown["domain_authority"] = {"score": 15, "max": 35, "rationale": "General web publication without specific institutional affiliation"}

        # 2. Content Depth & Evidence Density (0 - 25 points)
        depth_score = 0
        if word_count > 1500:
            depth_score = 25
            breakdown["content_depth"] = {"score": 25, "max": 25, "rationale": "In-depth comprehensive report (>1,500 words)"}
        elif word_count > 700:
            depth_score = 20
            breakdown["content_depth"] = {"score": 20, "max": 25, "rationale": "Substantial article with detailed empirical discourse (700-1,500 words)"}
        elif word_count > 250:
            depth_score = 14
            breakdown["content_depth"] = {"score": 14, "max": 25, "rationale": "Moderate length summary or article (250-700 words)"}
        elif word_count > 0:
            depth_score = 8
            breakdown["content_depth"] = {"score": 8, "max": 25, "rationale": "Brief snippet or condensed abstract (<250 words)"}
        else:
            depth_score = 2
            breakdown["content_depth"] = {"score": 2, "max": 25, "rationale": "Search snippet only, full text unreachable"}

        # 3. Recency / Temporal Validity (0 - 20 points)
        recency_score = 0
        if publication_date:
            year_match = re.search(r"\b(202[3-6])\b", str(publication_date))
            older_year = re.search(r"\b(202[0-2])\b", str(publication_date))
            if year_match:
                recency_score = 20
                breakdown["recency"] = {"score": 20, "max": 20, "rationale": f"Current, fresh data ({publication_date})"}
            elif older_year:
                recency_score = 14
                breakdown["recency"] = {"score": 14, "max": 20, "rationale": f"Recent data (2020-2022)"}
            else:
                recency_score = 8
                breakdown["recency"] = {"score": 8, "max": 20, "rationale": f"Historical publication ({publication_date})"}
        else:
            # Undated, neutral score
            recency_score = 12
            breakdown["recency"] = {"score": 12, "max": 20, "rationale": "Publication date not explicitly specified in metadata"}

        # 4. Relevance to Query (0 - 20 points)
        relevance_score = 0
        if query:
            q_terms = [t for t in re.findall(r"\b\w{4,}\b", query.lower()) if t not in ["what", "which", "where", "when", "does", "with"]]
            title_text = (title + " " + (content_text[:500] if content_text else "")).lower()
            matched = sum(1 for t in q_terms if t in title_text)
            match_ratio = (matched / len(q_terms)) if q_terms else 1.0

            if match_ratio >= 0.7:
                relevance_score = 20
                breakdown["topical_relevance"] = {"score": 20, "max": 20, "rationale": f"Strong alignment ({matched}/{len(q_terms)} query terms in title/lead)"}
            elif match_ratio >= 0.4:
                relevance_score = 15
                breakdown["topical_relevance"] = {"score": 15, "max": 20, "rationale": f"Moderate direct alignment with research question"}
            else:
                relevance_score = 10
                breakdown["topical_relevance"] = {"score": 10, "max": 20, "rationale": f"Contextual or adjacent topical relevance"}
        else:
            relevance_score = 15
            breakdown["topical_relevance"] = {"score": 15, "max": 20, "rationale": "Standard query match"}

        # Total Calculation
        total_score = float(type_score + depth_score + recency_score + relevance_score)
        total_score = min(100.0, max(0.0, total_score))

        # Classification
        if total_score >= 70:
            level = "High"
        elif total_score >= 45:
            level = "Medium"
        else:
            level = "Low"

        norm_relevance = min(1.0, max(0.2, (relevance_score + depth_score) / 45.0))

        return {
            "reliability_score": round(total_score, 1),
            "reliability_level": level,
            "relevance_score": round(norm_relevance, 2),
            "breakdown": breakdown
        }
