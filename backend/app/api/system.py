from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database import get_db
from backend.app.models.schema import ResearchProject, Source, Finding, Contradiction
from backend.app.schemas.api_schemas import SystemStatsOut, ProjectSummaryOut
from backend.app.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/stats", response_model=SystemStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_projects = db.query(ResearchProject).count()
    total_sources = db.query(Source).count()
    total_findings = db.query(Finding).count()
    running_projects = db.query(ResearchProject).filter(ResearchProject.status == "running").count()
    completed_projects = db.query(ResearchProject).filter(ResearchProject.status == "completed").count()
    total_contradictions = db.query(Contradiction).count()

    recent = db.query(ResearchProject).order_by(desc(ResearchProject.created_at)).limit(6).all()
    recent_out = []
    for p in recent:
        recent_out.append(ProjectSummaryOut(
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

    return SystemStatsOut(
        total_projects=total_projects,
        total_sources=total_sources,
        total_findings=total_findings,
        running_projects=running_projects,
        completed_projects=completed_projects,
        total_contradictions=total_contradictions,
        recent_projects=recent_out
    )


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "ai_provider": settings.DEFAULT_AI_PROVIDER
    }
