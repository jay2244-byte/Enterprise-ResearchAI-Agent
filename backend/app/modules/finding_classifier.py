import re
from typing import List

VALID_CATEGORIES = [
    "Technology",
    "Business Benefit",
    "Operational Impact",
    "Cost",
    "Risk",
    "Workforce",
    "Customer Experience",
    "Implementation Challenge",
    "Regulation",
    "Future Trend"
]


class FindingClassifier:
    """Classifies and normalizes finding categories across the enterprise taxonomy."""

    def __init__(self, allowed_categories: List[str] = None):
        self.categories = allowed_categories or VALID_CATEGORIES

    def classify(self, text: str, initial_category: str = None) -> str:
        if initial_category and initial_category in self.categories:
            return initial_category

        text_lower = text.lower()

        patterns = {
            "Cost": [r"\bcost\b", r"\bcapital\b", r"\bbudget\b", r"\bexpensive\b", r"\bpricing\b", r"\bfinancial investment\b"],
            "Risk": [r"\brisk\b", r"\bsecurity\b", r"\bvulnerab", r"\bbreach\b", r"\bliability\b", r"\bsafety hazard\b"],
            "Workforce": [r"\bworkforce\b", r"\bworker", r"\bemployee", r"\bhuman capital\b", r"\btalent\b", r"\breskilling\b", r"\bjob\b"],
            "Regulation": [r"\bregulation\b", r"\bcompliance\b", r"\blegal\b", r"\bgovernance\b", r"\bpolicy\b", r"\baudit\b"],
            "Implementation Challenge": [r"\bchallenge\b", r"\bbarrier\b", r"\bdifficulty\b", r"\bbottleneck\b", r"\blegacy system\b", r"\bintegration hurdle\b"],
            "Business Benefit": [r"\brevenue\b", r"\broi\b", r"\bgrowth\b", r"\bmarket advantage\b", r"\bprofit\b", r"\bvalue creation\b"],
            "Customer Experience": [r"\bcustomer\b", r"\bclient\b", r"\buser satisfaction\b", r"\bconsumer\b", r"\bpersonalization\b"],
            "Technology": [r"\balgorithm\b", r"\barchitecture\b", r"\bneural\b", r"\bplatform\b", r"\bhardware\b", r"\bllm\b", r"\bmodel\b"],
            "Future Trend": [r"\bfuture\b", r"\bemerging trend\b", r"\bnext decade\b", r"\boutlook\b", r"\bprojection\b", r"\broadmap\b"],
            "Operational Impact": [r"\befficiency\b", r"\bthroughput\b", r"\bdowntime\b", r"\bmaintenance\b", r"\bprocess\b", r"\boperations\b"]
        }

        for cat, pats in patterns.items():
            if cat in self.categories and any(re.search(p, text_lower) for p in pats):
                return cat

        return "Operational Impact"
