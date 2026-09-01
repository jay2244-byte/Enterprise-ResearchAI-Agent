import sys
import os

# Set utf-8 encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add workspace to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import init_db, SessionLocal
from backend.app.models.schema import ResearchProject, Source, Finding, Conclusion, Contradiction
from backend.app.orchestrator.research_pipeline import ResearchOrchestrator
from backend.app.modules.research_qa import ResearchQA
from backend.app.ai.factory import get_ai_provider


def main():
    print("==================================================")
    print("Starting Live End-to-End Enterprise Research Test")
    print("==================================================")

    init_db()
    db = SessionLocal()

    # Enter an enterprise research question
    question = "How is AI transforming manufacturing operations?"
    print(f"\n[1] Creating Research Project: '{question}'")

    project = ResearchProject(
        question=question,
        industry="Manufacturing & Industrial Automation",
        scope="Comprehensive",
        max_sources=4  # Keep fast for validation
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    print(f"-> Project ID: {project.id}")

    # Run Orchestrator
    orchestrator = ResearchOrchestrator(db)
    print("\n[2] Executing 11-Stage Research Pipeline...")
    completed_project = orchestrator.run_pipeline(project.id)

    print(f"\n[3] Pipeline Finished! Status: {completed_project.status}")
    print(f"-> Executive Summary:\n{completed_project.executive_summary}\n")

    # Verify Sources
    sources = db.query(Source).filter(Source.project_id == project.id).all()
    print(f"[4] Verified Sources Collected ({len(sources)}):")
    for s in sources:
        print(f"  - Title: {s.title}")
        print(f"    URL: {s.url}")
        print(f"    Publisher: {s.publisher} | Type: {s.source_type}")
        print(f"    Reliability: {s.reliability_level} ({s.reliability_score}/100) | Relevance: {s.relevance_score}")
        print(f"    Breakdown: {list(s.reliability_breakdown.keys()) if s.reliability_breakdown else {}}")

    assert len(sources) > 0, "ERROR: No sources were collected!"

    # Verify Findings
    findings = db.query(Finding).filter(Finding.project_id == project.id).all()
    print(f"\n[5] Structured Findings Extracted ({len(findings)}):")
    for f in findings:
        evidence_quote = f.evidence_items[0].quote_text if f.evidence_items else "N/A"
        print(f"  - [{f.category}] {f.title} (Confidence: {f.confidence})")
        print(f"    Source: {f.source.title if f.source else 'None'}")
        print(f"    Evidence Quote: \"{evidence_quote[:120]}...\"")

    assert len(findings) > 0, "ERROR: No findings were extracted!"

    # Verify Contradictions
    contradictions = db.query(Contradiction).filter(Contradiction.project_id == project.id).all()
    print(f"\n[6] Contradictions & Contextual Tensions Detected ({len(contradictions)}):")
    for c in contradictions:
        print(f"  - Topic: {c.topic} [{c.contradiction_type}] (Confidence: {c.confidence})")
        print(f"    Explanation: {c.explanation}")
        print(f"    Finding A: {c.finding_a.title if c.finding_a else 'N/A'}")
        print(f"    Finding B: {c.finding_b.title if c.finding_b else 'N/A'}")

    # Verify Conclusions & Traceability
    conclusions = db.query(Conclusion).filter(Conclusion.project_id == project.id).all()
    print(f"\n[7] Major Strategic Conclusions ({len(conclusions)}):")
    for c in conclusions:
        print(f"\n  ★ Conclusion: {c.title}")
        print(f"    Summary: {c.summary}")
        print(f"    Confidence: {c.confidence}")
        print(f"    Reasoning: {c.reasoning_summary}")
        print(f"    Traceability Chain:")
        for sf in c.findings:
            quote = sf.evidence_items[0].quote_text if sf.evidence_items else ""
            print(f"      └── Finding: {sf.title} (Category: {sf.category})")
            print(f"            └── Quote: \"{quote[:100]}...\"")
            print(f"                  └── Source: {sf.source.title if sf.source else 'N/A'}")
            print(f"                        └── URL: {sf.source.url if sf.source else 'N/A'}")
            print(f"                        └── Reliability: {sf.source.reliability_level if sf.source else 'N/A'} ({sf.source.reliability_score if sf.source else 0}/100)")

    assert len(conclusions) > 0, "ERROR: No conclusions were generated!"

    # Test Grounded Research Q&A
    print("\n[8] Testing Grounded Research Q&A:")
    qa_engine = ResearchQA(get_ai_provider())
    findings_dicts = []
    for f in findings:
        findings_dicts.append({
            "id": f.id,
            "title": f.title,
            "description": f.description,
            "category": f.category,
            "confidence": f.confidence,
            "source_id": f.source_id,
            "source_title": f.source.title if f.source else "Source",
            "source_url": f.source.url if f.source else "",
            "source_reliability_level": f.source.reliability_level if f.source else "Medium",
            "evidence_items": [{"quote_text": e.quote_text} for e in f.evidence_items]
        })

    test_q = "Which areas have the strongest evidence for AI adoption?"
    qa_result = qa_engine.answer_question(
        project_question=project.question,
        user_query=test_q,
        findings=findings_dicts,
        sources=[{"title": s.title, "url": s.url} for s in sources]
    )
    print(f"  User Query: {test_q}")
    print(f"  Answer: {qa_result['answer']}")
    print(f"  Citations ({len(qa_result['citations'])}):")
    for cit in qa_result["citations"]:
        print(f"    - [{cit['reliability_level']}] {cit['source_title']} -> {cit['source_url']}")

    print("\n==================================================")
    print("ALL END-TO-END VERIFICATION CHECKS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    main()
