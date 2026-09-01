import re
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.models.schema import ResearchProject, Source, Finding, Conclusion
from backend.app.schemas.api_schemas import KnowledgeSearchResponse, KnowledgeSearchItem

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


@router.get("/search", response_model=KnowledgeSearchResponse)
def search_knowledge_base(
    q: str = Query(..., min_length=2, description="Search query term or phrase"),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query_str = f"%{q.strip()}%"
    items: List[KnowledgeSearchItem] = []

    # 1. Search Findings
    findings = db.query(Finding).filter(
        or_(
            Finding.title.ilike(query_str),
            Finding.description.ilike(query_str),
            Finding.category.ilike(query_str)
        )
    ).limit(limit).all()

    for f in findings:
        items.append(KnowledgeSearchItem(
            type="finding",
            id=f.id,
            project_id=f.project_id,
            project_question=f.project.question if f.project else "",
            title=f.title,
            snippet=f.description[:250],
            category=f.category,
            url=f.source.url if f.source else None,
            reliability_level=f.source.reliability_level if f.source else None
        ))

    # 2. Search Conclusions
    conclusions = db.query(Conclusion).filter(
        or_(
            Conclusion.title.ilike(query_str),
            Conclusion.summary.ilike(query_str),
            Conclusion.reasoning_summary.ilike(query_str)
        )
    ).limit(limit).all()

    for c in conclusions:
        items.append(KnowledgeSearchItem(
            type="conclusion",
            id=c.id,
            project_id=c.project_id,
            project_question=c.project.question if c.project else "",
            title=c.title,
            snippet=c.summary[:250],
            category=f"Confidence: {c.confidence}",
            url=None,
            reliability_level=c.confidence
        ))

    # 3. Search Sources
    sources = db.query(Source).filter(
        or_(
            Source.title.ilike(query_str),
            Source.publisher.ilike(query_str),
            Source.source_type.ilike(query_str),
            Source.url.ilike(query_str)
        )
    ).limit(limit).all()

    for s in sources:
        items.append(KnowledgeSearchItem(
            type="source",
            id=s.id,
            project_id=s.project_id,
            project_question=s.project.question if s.project else "",
            title=s.title,
            snippet=f"Publisher: {s.publisher} | Type: {s.source_type} | Reliability: {s.reliability_level} ({s.reliability_score}/100)",
            category=s.source_type,
            url=s.url,
            reliability_level=s.reliability_level
        ))

    # 4. Search Projects
    projects = db.query(ResearchProject).filter(
        or_(
            ResearchProject.question.ilike(query_str),
            ResearchProject.industry.ilike(query_str),
            ResearchProject.executive_summary.ilike(query_str)
        )
    ).limit(limit).all()

    for p in projects:
        items.append(KnowledgeSearchItem(
            type="project",
            id=p.id,
            project_id=p.id,
            project_question=p.question,
            title=p.question,
            snippet=p.executive_summary[:250] if p.executive_summary else f"Status: {p.status}",
            category=p.industry or "General",
            url=None,
            reliability_level=p.status
        ))

    return KnowledgeSearchResponse(
        query=q,
        total_results=len(items),
        results=items[:limit]
    )
