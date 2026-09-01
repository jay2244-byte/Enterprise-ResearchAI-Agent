import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.database import init_db, SessionLocal
from backend.app.models.schema import ResearchProject, Source, Finding, Evidence, Conclusion
from backend.app.api.research import get_conclusion_trace


def test_conclusion_traceability_lineage():
    init_db()
    db = SessionLocal()

    # Create dummy project
    p = ResearchProject(question="Traceability Verification Question", status="completed")
    db.add(p)
    db.commit()
    db.refresh(p)

    # Create source
    s = Source(
        project_id=p.id,
        title="MIT Tech Review Empirical Study",
        url="https://mit.edu/research/study",
        publisher="MIT Press",
        source_type="academic",
        reliability_score=85.0,
        reliability_level="High"
    )
    db.add(s)
    db.commit()
    db.refresh(s)

    # Create finding
    f = Finding(
        project_id=p.id,
        source_id=s.id,
        title="Predictive analytics reduces component failures",
        description="Detailed study of manufacturing sensor telemetry.",
        category="Technology",
        confidence="High"
    )
    db.add(f)
    db.commit()
    db.refresh(f)

    # Create evidence
    e = Evidence(
        finding_id=f.id,
        source_id=s.id,
        quote_text="Predictive telemetry models reduced failure rates by 27%."
    )
    db.add(e)
    db.commit()

    # Create conclusion linked to finding
    c = Conclusion(
        project_id=p.id,
        title="Predictive Modeling Delivers Empirical Reliability",
        summary="Sensors paired with machine learning prevent catastrophic downtime.",
        confidence="High",
        reasoning_summary="Corroborated by MIT empirical data."
    )
    c.findings.append(f)
    db.add(c)
    db.commit()
    db.refresh(c)

    # Verify trace endpoint logic
    trace = get_conclusion_trace(p.id, c.id, db)
    assert trace.conclusion_id == c.id
    assert len(trace.supporting_findings) == 1
    assert trace.supporting_findings[0].source_title == "MIT Tech Review Empirical Study"
    assert trace.supporting_findings[0].source_url == "https://mit.edu/research/study"
    assert trace.supporting_findings[0].evidence_quotes[0] == "Predictive telemetry models reduced failure rates by 27%."
