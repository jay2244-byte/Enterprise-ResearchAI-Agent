from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, Table, JSON, Boolean
)
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

# Association Table: Conclusion <-> Finding
conclusion_findings = Table(
    "conclusion_findings",
    Base.metadata,
    Column("conclusion_id", Integer, ForeignKey("conclusions.id", ondelete="CASCADE"), primary_key=True),
    Column("finding_id", Integer, ForeignKey("findings.id", ondelete="CASCADE"), primary_key=True)
)


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    scope = Column(String(100), nullable=True, default="Comprehensive")
    max_sources = Column(Integer, default=8)
    preferred_source_types = Column(JSON, nullable=True)  # list of strings
    status = Column(String(50), default="queued", index=True)  # queued, planning, searching, extracting, comparing, contradictions, concluding, completed, failed
    current_stage = Column(String(100), default="Queued")
    progress_percentage = Column(Integer, default=0)
    executive_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    questions = relationship("ResearchQuestion", back_populates="project", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="project", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="project", cascade="all, delete-orphan")
    evidence_comparisons = relationship("EvidenceComparison", back_populates="project", cascade="all, delete-orphan")
    contradictions = relationship("Contradiction", back_populates="project", cascade="all, delete-orphan")
    conclusions = relationship("Conclusion", back_populates="project", cascade="all, delete-orphan")
    runs = relationship("ResearchRun", back_populates="project", cascade="all, delete-orphan")


class ResearchQuestion(Base):
    __tablename__ = "research_questions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(String(500), nullable=False)
    topic_category = Column(String(100), nullable=True)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="questions")
    sources = relationship("Source", back_populates="research_question")
    findings = relationship("Finding", back_populates="research_question")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    research_question_id = Column(Integer, ForeignKey("research_questions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False, index=True)
    publisher = Column(String(200), nullable=True)
    publication_date = Column(String(50), nullable=True)
    retrieved_date = Column(DateTime, default=utc_now)
    source_type = Column(String(100), default="web")  # government, academic, research_org, industry_report, company, news, web
    relevance_score = Column(Float, default=0.0)  # 0.0 to 1.0
    reliability_score = Column(Float, default=0.0)  # 0 to 100
    reliability_level = Column(String(20), default="Medium")  # High, Medium, Low
    reliability_breakdown = Column(JSON, nullable=True)  # Breakdown dictionary of scoring factors

    project = relationship("ResearchProject", back_populates="sources")
    research_question = relationship("ResearchQuestion", back_populates="sources")
    content = relationship("SourceContent", back_populates="source", uselist=False, cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="source")
    evidence_items = relationship("Evidence", back_populates="source")


class SourceContent(Base):
    __tablename__ = "source_contents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, unique=True)
    raw_snippet = Column(Text, nullable=True)
    clean_text = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    http_status = Column(Integer, default=200)

    source = relationship("Source", back_populates="content")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)
    research_question_id = Column(Integer, ForeignKey("research_questions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), default="Operational Impact", index=True)  # Technology, Business Benefit, Operational Impact, Cost, Risk, Workforce, Customer Experience, Implementation Challenge, Regulation, Future Trend
    confidence = Column(String(20), default="Medium")  # High, Medium, Low
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="findings")
    source = relationship("Source", back_populates="findings")
    research_question = relationship("ResearchQuestion", back_populates="findings")
    evidence_items = relationship("Evidence", back_populates="finding", cascade="all, delete-orphan")
    conclusions = relationship("Conclusion", secondary=conclusion_findings, back_populates="findings")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True, index=True)
    quote_text = Column(Text, nullable=False)
    context_snippet = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.8)

    finding = relationship("Finding", back_populates="evidence_items")
    source = relationship("Source", back_populates="evidence_items")


class EvidenceComparison(Base):
    __tablename__ = "evidence_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(200), nullable=False)
    synthesis = Column(Text, nullable=False)
    consensus_type = Column(String(50), default="high_consensus")  # high_consensus, divergent, nuanced, conflicting
    source_count = Column(Integer, default=1)
    perspectives = Column(JSON, nullable=True)  # List of perspective objects {source_title, viewpoint, stance}
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="evidence_comparisons")


class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_a_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    finding_b_id = Column(Integer, ForeignKey("findings.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(200), nullable=True)
    explanation = Column(Text, nullable=False)
    contradiction_type = Column(String(50), default="different_context")  # true_contradiction, different_context, different_time_period, different_industry, incomplete_information
    confidence = Column(String(20), default="Medium")  # High, Medium, Low
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="contradictions")
    finding_a = relationship("Finding", foreign_keys=[finding_a_id])
    finding_b = relationship("Finding", foreign_keys=[finding_b_id])


class Conclusion(Base):
    __tablename__ = "conclusions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    confidence = Column(String(20), default="High")  # High, Medium, Low
    reasoning_summary = Column(Text, nullable=False)
    rank_order = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now)

    project = relationship("ResearchProject", back_populates="conclusions")
    findings = relationship("Finding", secondary=conclusion_findings, back_populates="conclusions")


class ResearchRun(Base):
    __tablename__ = "research_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    sources_searched = Column(Integer, default=0)
    sources_accepted = Column(Integer, default=0)
    findings_count = Column(Integer, default=0)
    contradictions_count = Column(Integer, default=0)
    conclusions_count = Column(Integer, default=0)
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)
    log_messages = Column(JSON, default=list)  # list of {timestamp, stage, message, level}

    project = relationship("ResearchProject", back_populates="runs")
