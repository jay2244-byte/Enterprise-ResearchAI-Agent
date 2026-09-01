import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db, SessionLocal
from backend.app.models.schema import (
    ResearchProject, ResearchQuestion, Source, Finding, Evidence,
    EvidenceComparison, Contradiction, Conclusion, ResearchRun
)
from backend.app.schemas.api_schemas import (
    ProjectCreate, ProjectDetailOut, ProjectSummaryOut, SubQuestionOut,
    SourceOut, FindingOut, EvidenceComparisonOut, ContradictionOut,
    ConclusionOut, ConclusionTraceOut, TraceFindingItem, ResearchRunOut,
    AskRequest, AskResponse
)
from backend.app.orchestrator.research_pipeline import ResearchOrchestrator
from backend.app.modules.research_qa import ResearchQA
from backend.app.ai.factory import get_ai_provider

router = APIRouter(prefix="/research", tags=["Research"])


def run_pipeline_task(project_id: int):
    """Background execution runner."""
    db = SessionLocal()
    try:
        orchestrator = ResearchOrchestrator(db)
        orchestrator.run_pipeline(project_id)
    except Exception as e:
        print(f"Background pipeline failed for {project_id}: {e}")
    finally:
        db.close()


@router.post("", response_model=ProjectDetailOut)
def create_research_project(payload: ProjectCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = ResearchProject(
        question=payload.question.strip(),
        industry=payload.industry.strip() if payload.industry else None,
        scope=payload.scope or "Comprehensive",
        max_sources=payload.max_sources or 8,
        preferred_source_types=payload.preferred_source_types or [],
        status="queued",
        current_stage="Queued",
        progress_percentage=0
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Automatically launch background pipeline run
    background_tasks.add_task(run_pipeline_task, project.id)

    return project


@router.get("", response_model=List[ProjectSummaryOut])
def list_research_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ResearchProject)
    if status:
        query = query.filter(ResearchProject.status == status)
    projects = query.order_by(desc(ResearchProject.created_at)).offset(skip).limit(limit).all()

    results = []
    for p in projects:
        results.append(ProjectSummaryOut(
            id=p.id,
            question=p.question,
            industry=p.industry,
            status=p.status,
            current_stage=p.current_stage,
            progress_percentage=p.progress_percentage,
            created_at=p.created_at,
            sources_count=len(p.sources),
            findings_count=len(p.findings),
            conclusions_count=len(p.conclusions),
            contradictions_count=len(p.contradictions)
        ))
    return results


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project_details(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectDetailOut(
        id=project.id,
        question=project.question,
        industry=project.industry,
        scope=project.scope,
        max_sources=project.max_sources,
        preferred_source_types=project.preferred_source_types,
        status=project.status,
        current_stage=project.current_stage,
        progress_percentage=project.progress_percentage,
        executive_summary=project.executive_summary,
        created_at=project.created_at,
        updated_at=project.updated_at,
        questions=[SubQuestionOut.model_validate(q) for q in project.questions],
        sources_count=len(project.sources),
        findings_count=len(project.findings),
        conclusions_count=len(project.conclusions),
        contradictions_count=len(project.contradictions)
    )


@router.post("/{project_id}/run")
def trigger_project_run(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status == "running":
        return {"message": "Project is already running", "project_id": project.id}

    background_tasks.add_task(run_pipeline_task, project.id)
    return {"message": "Pipeline run started", "project_id": project.id}


@router.get("/{project_id}/progress")
def get_project_progress(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    latest_run = db.query(ResearchRun).filter(ResearchRun.project_id == project_id).order_by(desc(ResearchRun.started_at)).first()

    return {
        "project_id": project.id,
        "status": project.status,
        "current_stage": project.current_stage,
        "progress_percentage": project.progress_percentage,
        "latest_run": ResearchRunOut.model_validate(latest_run) if latest_run else None
    }


@router.get("/{project_id}/sources", response_model=List[SourceOut])
def get_project_sources(project_id: int, db: Session = Depends(get_db)):
    sources = db.query(Source).filter(Source.project_id == project_id).all()
    results = []
    for s in sources:
        item = SourceOut.model_validate(s)
        item.used_in_findings_count = len(s.findings)
        results.append(item)
    return results


@router.get("/{project_id}/findings", response_model=List[FindingOut])
def get_project_findings(project_id: int, category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Finding).filter(Finding.project_id == project_id)
    if category:
        query = query.filter(Finding.category == category)
    findings = query.all()

    results = []
    for f in findings:
        item = FindingOut.model_validate(f)
        if f.source:
            item.source_title = f.source.title
            item.source_url = f.source.url
            item.source_publisher = f.source.publisher
            item.source_reliability_level = f.source.reliability_level
        results.append(item)
    return results


@router.get("/{project_id}/evidence-comparison", response_model=List[EvidenceComparisonOut])
def get_evidence_comparisons(project_id: int, db: Session = Depends(get_db)):
    comparisons = db.query(EvidenceComparison).filter(EvidenceComparison.project_id == project_id).all()
    return [EvidenceComparisonOut.model_validate(c) for c in comparisons]


@router.get("/{project_id}/contradictions", response_model=List[ContradictionOut])
def get_contradictions(project_id: int, db: Session = Depends(get_db)):
    contradictions = db.query(Contradiction).filter(Contradiction.project_id == project_id).all()
    results = []
    for c in contradictions:
        item = ContradictionOut.model_validate(c)
        if c.finding_a:
            item.finding_a_title = c.finding_a.title
            if c.finding_a.source:
                item.finding_a_source = c.finding_a.source.title
        if c.finding_b:
            item.finding_b_title = c.finding_b.title
            if c.finding_b.source:
                item.finding_b_source = c.finding_b.source.title
        results.append(item)
    return results


@router.get("/{project_id}/conclusions", response_model=List[ConclusionOut])
def get_conclusions(project_id: int, db: Session = Depends(get_db)):
    conclusions = db.query(Conclusion).filter(Conclusion.project_id == project_id).order_by(Conclusion.rank_order).all()
    results = []
    for c in conclusions:
        item = ConclusionOut.from_orm(c)
        item.supporting_findings_count = len(c.findings)
        # Populate supporting findings
        findings_out = []
        for f in c.findings:
            f_out = FindingOut.from_orm(f)
            if f.source:
                f_out.source_title = f.source.title
                f_out.source_url = f.source.url
                f_out.source_publisher = f.source.publisher
                f_out.source_reliability_level = f.source.reliability_level
            findings_out.append(f_out)
        item.supporting_findings = findings_out
        results.append(item)
    return results


@router.get("/{project_id}/trace/{conclusion_id}", response_model=ConclusionTraceOut)
def get_conclusion_trace(project_id: int, conclusion_id: int, db: Session = Depends(get_db)):
    """
    Explainability API: Returns full lineage:
    Conclusion -> Supporting Findings -> Evidence Quotes -> Sources with reliability scores
    """
    conclusion = db.query(Conclusion).filter(
        Conclusion.id == conclusion_id,
        Conclusion.project_id == project_id
    ).first()

    if not conclusion:
        raise HTTPException(status_code=404, detail="Conclusion not found")

    findings_items = []
    unique_source_urls = set()

    for f in conclusion.findings:
        quotes = [e.quote_text for e in f.evidence_items]
        src = f.source
        if src:
            unique_source_urls.add(src.url)

        findings_items.append(TraceFindingItem(
            finding_id=f.id,
            title=f.title,
            category=f.category,
            confidence=f.confidence,
            evidence_quotes=quotes,
            source_title=src.title if src else "Unknown Source",
            source_url=src.url if src else "",
            source_publisher=src.publisher if src else "Web Publisher",
            source_reliability_level=src.reliability_level if src else "Medium",
            source_reliability_score=src.reliability_score if src else 50.0
        ))

    return ConclusionTraceOut(
        conclusion_id=conclusion.id,
        conclusion_title=conclusion.title,
        confidence=conclusion.confidence,
        reasoning_summary=conclusion.reasoning_summary,
        supporting_findings=findings_items,
        unique_sources_count=len(unique_source_urls)
    )


@router.post("/{project_id}/ask", response_model=AskResponse)
def ask_project_research(project_id: int, payload: AskRequest, db: Session = Depends(get_db)):
    """Interrogate this specific research project. Strictly grounded in project findings."""
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    findings = db.query(Finding).filter(Finding.project_id == project_id).all()
    sources = db.query(Source).filter(Source.project_id == project_id).all()

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

    qa = ResearchQA(get_ai_provider())
    answer_data = qa.answer_question(
        project_question=project.question,
        user_query=payload.question,
        findings=findings_dicts,
        sources=[{"title": s.title, "url": s.url} for s in sources]
    )

    return AskResponse(**answer_data)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted", "id": project_id}
