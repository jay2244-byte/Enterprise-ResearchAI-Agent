from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Project Create
class ProjectCreate(BaseModel):
    question: str = Field(..., min_length=5, description="Enterprise research question")
    industry: Optional[str] = Field(None, description="Target industry")
    scope: Optional[str] = Field("Comprehensive", description="Research scope")
    max_sources: Optional[int] = Field(8, ge=2, le=20, description="Max sources to retrieve")
    preferred_source_types: Optional[List[str]] = Field(default_factory=list)


# Question (Subtopic)
class SubQuestionOut(BaseModel):
    id: int
    question_text: str
    topic_category: Optional[str]
    rationale: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Source Content
class SourceContentOut(BaseModel):
    raw_snippet: Optional[str]
    clean_text: Optional[str]
    word_count: int
    http_status: int

    model_config = ConfigDict(from_attributes=True)


# Source
class SourceOut(BaseModel):
    id: int
    project_id: int
    research_question_id: Optional[int]
    title: str
    url: str
    publisher: Optional[str]
    publication_date: Optional[str]
    retrieved_date: datetime
    source_type: str
    relevance_score: float
    reliability_score: float
    reliability_level: str
    reliability_breakdown: Optional[Dict[str, Any]]
    used_in_findings_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# Evidence
class EvidenceOut(BaseModel):
    id: int
    finding_id: int
    source_id: Optional[int]
    quote_text: str
    context_snippet: Optional[str]
    confidence_score: float
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    source_reliability_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Finding
class FindingOut(BaseModel):
    id: int
    project_id: int
    source_id: Optional[int]
    research_question_id: Optional[int]
    title: str
    description: str
    category: str
    confidence: str
    created_at: datetime
    evidence_items: List[EvidenceOut] = []
    source_title: Optional[str] = None
    source_url: Optional[str] = None
    source_publisher: Optional[str] = None
    source_reliability_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Evidence Comparison
class EvidenceComparisonOut(BaseModel):
    id: int
    project_id: int
    topic: str
    synthesis: str
    consensus_type: str
    source_count: int
    perspectives: Optional[List[Dict[str, Any]]]

    model_config = ConfigDict(from_attributes=True)


# Contradiction
class ContradictionOut(BaseModel):
    id: int
    project_id: int
    finding_a_id: int
    finding_b_id: int
    topic: Optional[str]
    explanation: str
    contradiction_type: str
    confidence: str
    finding_a_title: Optional[str] = None
    finding_b_title: Optional[str] = None
    finding_a_source: Optional[str] = None
    finding_b_source: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Traceable Finding Item for Conclusion Drill-down
class TraceFindingItem(BaseModel):
    finding_id: int
    title: str
    category: str
    confidence: str
    evidence_quotes: List[str]
    source_title: Optional[str]
    source_url: Optional[str]
    source_publisher: Optional[str]
    source_reliability_level: Optional[str]
    source_reliability_score: Optional[float]


# Trace Tree for Explainability
class ConclusionTraceOut(BaseModel):
    conclusion_id: int
    conclusion_title: str
    confidence: str
    reasoning_summary: str
    supporting_findings: List[TraceFindingItem]
    unique_sources_count: int


# Conclusion
class ConclusionOut(BaseModel):
    id: int
    project_id: int
    title: str
    summary: str
    confidence: str
    reasoning_summary: str
    rank_order: int
    supporting_findings_count: int = 0
    supporting_findings: List[FindingOut] = []

    model_config = ConfigDict(from_attributes=True)


# Research Run
class ResearchRunOut(BaseModel):
    id: int
    project_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: float
    sources_searched: int
    sources_accepted: int
    findings_count: int
    contradictions_count: int
    conclusions_count: int
    status: str
    error_message: Optional[str]
    log_messages: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


# Project Detailed
class ProjectDetailOut(BaseModel):
    id: int
    question: str
    industry: Optional[str]
    scope: Optional[str]
    max_sources: int
    preferred_source_types: Optional[List[str]]
    status: str
    current_stage: str
    progress_percentage: int
    executive_summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    questions: List[SubQuestionOut] = []
    sources_count: int = 0
    findings_count: int = 0
    conclusions_count: int = 0
    contradictions_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Project Summary for Dashboard List
class ProjectSummaryOut(BaseModel):
    id: int
    question: str
    industry: Optional[str]
    status: str
    current_stage: str
    progress_percentage: int
    created_at: datetime
    sources_count: int = 0
    findings_count: int = 0
    conclusions_count: int = 0
    contradictions_count: int = 0


# Q&A Ask Request & Response
class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class AskCitation(BaseModel):
    source_id: Optional[int]
    source_title: str
    source_url: str
    reliability_level: str
    snippet: str


class AskResponse(BaseModel):
    question: str
    answer: str
    grounded: bool
    citations: List[AskCitation] = []


# Knowledge Base Search Result Item
class KnowledgeSearchItem(BaseModel):
    type: str  # "project", "finding", "source", "conclusion"
    id: int
    project_id: int
    project_question: str
    title: str
    snippet: str
    category: Optional[str] = None
    url: Optional[str] = None
    reliability_level: Optional[str] = None


class KnowledgeSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[KnowledgeSearchItem]


# Global System Stats
class SystemStatsOut(BaseModel):
    total_projects: int
    total_sources: int
    total_findings: int
    running_projects: int
    completed_projects: int
    total_contradictions: int
    recent_projects: List[ProjectSummaryOut] = []
