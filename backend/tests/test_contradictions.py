import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.modules.contradiction_detector import ContradictionDetector
from backend.app.ai.heuristic_provider import HeuristicAIProvider


def test_contradiction_detection():
    detector = ContradictionDetector(HeuristicAIProvider())
    findings = [
        {
            "id": 1,
            "title": "Automated maintenance yields immediate 30% reduction in downtime",
            "category": "Operational Impact",
            "description": "Empirical plant deployments report rapid efficiency gains within 3 months.",
            "source_title": "Industrial Automation Journal"
        },
        {
            "id": 2,
            "title": "High upfront capital requirements create multi-year ROI latency",
            "category": "Cost",
            "description": "Integration debt and legacy hardware retrofitting require prolonged capital amortization.",
            "source_title": "Enterprise Risk Review"
        }
    ]

    results = detector.detect_contradictions(findings)
    assert len(results) >= 1
    assert "contradiction_type" in results[0]
    assert results[0]["contradiction_type"] in [
        "true_contradiction", "different_context", "different_time_period", "different_industry", "incomplete_information"
    ]
