import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.modules.source_evaluator import SourceEvaluator


def test_source_evaluator_high_authority():
    evaluator = SourceEvaluator()
    res = evaluator.evaluate_source(
        url="https://www.nist.gov/topics/artificial-intelligence",
        title="NIST Artificial Intelligence Risk Management Framework",
        source_type="government",
        content_text="The NIST AI Risk Management Framework provides guidelines for trustworthy AI systems." * 50,
        word_count=1600,
        publication_date="2024-02-10",
        query="AI risk framework"
    )
    assert res["reliability_level"] == "High"
    assert res["reliability_score"] >= 80.0
    assert "domain_authority" in res["breakdown"]


def test_source_evaluator_medium_news():
    evaluator = SourceEvaluator()
    res = evaluator.evaluate_source(
        url="https://www.techcrunch.com/2024/01/01/ai-manufacturing/",
        title="AI Adoption Trends in Industry",
        source_type="news",
        content_text="Commercial news report discussing AI adoption." * 15,
        word_count=450,
        publication_date="2023-05-01",
        query="AI manufacturing"
    )
    assert res["reliability_level"] in ["Medium", "High"]
    assert res["reliability_score"] >= 45.0
