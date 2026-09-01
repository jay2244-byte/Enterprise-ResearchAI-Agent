import time
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.ai.factory import get_ai_provider
from backend.app.models.schema import (
    ResearchProject, ResearchQuestion, Source, SourceContent,
    Finding, Evidence, EvidenceComparison, Contradiction,
    Conclusion, ResearchRun
)
from backend.app.modules.research_planner import ResearchPlanner
from backend.app.modules.source_search import SourceSearcher
from backend.app.modules.source_evaluator import SourceEvaluator
from backend.app.modules.information_extractor import InformationExtractor
from backend.app.modules.finding_classifier import FindingClassifier
from backend.app.modules.evidence_comparator import EvidenceComparator
from backend.app.modules.contradiction_detector import ContradictionDetector
from backend.app.modules.conclusion_generator import ConclusionGenerator

logger = logging.getLogger(__name__)


class ResearchOrchestrator:
    """
    Executes the end-to-end 11-stage research workflow:
    Research Question → Research Planning → Source Search → Information Collection →
    Source Storage → Finding Extraction → Evidence Comparison → Finding Classification →
    Contradiction Detection → Conclusion Generation → Traceable Results
    """

    def __init__(self, db: Session):
        self.db = db
        self.ai = get_ai_provider()
        self.planner = ResearchPlanner(self.ai)
        self.searcher = SourceSearcher()
        self.evaluator = SourceEvaluator()
        self.extractor = InformationExtractor(self.ai)
        self.classifier = FindingClassifier()
        self.comparator = EvidenceComparator(self.ai)
        self.contradiction_detector = ContradictionDetector(self.ai)
        self.conclusion_gen = ConclusionGenerator(self.ai)

    def _log_step(self, run: ResearchRun, stage: str, message: str, level: str = "INFO"):
        logger.info(f"[{stage}] {message}")
        if run.log_messages is None:
            run.log_messages = []
        # Update logs array safely for SQLAlchemy JSON
        logs = list(run.log_messages)
        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": stage,
            "message": message,
            "level": level
        })
        run.log_messages = logs

    def run_pipeline(self, project_id: int) -> ResearchProject:
        project = self.db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        start_time = time.time()
        project.status = "running"
        project.current_stage = "Research Planning"
        project.progress_percentage = 5

        # Initialize Run record
        run = ResearchRun(
            project_id=project.id,
            started_at=datetime.now(timezone.utc),
            status="running",
            log_messages=[]
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(project)
        self.db.refresh(run)

        try:
            # -------------------------------------------------------------
            # Stage 1: Research Planning
            # -------------------------------------------------------------
            self._log_step(run, "Research Planning", f"Deconstructing question: '{project.question}'")
            project.current_stage = "Research Planning"
            project.progress_percentage = 10
            self.db.commit()

            sub_qs_data = self.planner.plan_research(
                question=project.question,
                industry=project.industry,
                scope=project.scope or "Comprehensive"
            )

            created_sub_qs = []
            for item in sub_qs_data:
                sub_q = ResearchQuestion(
                    project_id=project.id,
                    question_text=item.get("question_text"),
                    topic_category=item.get("topic_category"),
                    rationale=item.get("rationale")
                )
                self.db.add(sub_q)
                created_sub_qs.append(sub_q)
            self.db.commit()
            for sq in created_sub_qs:
                self.db.refresh(sq)

            self._log_step(run, "Research Planning", f"Generated {len(created_sub_qs)} targeted sub-questions.")

            # -------------------------------------------------------------
            # Stage 2 & 3: Source Search & Information Collection
            # -------------------------------------------------------------
            project.current_stage = "Source Search"
            project.progress_percentage = 25
            self.db.commit()
            self._log_step(run, "Source Search", "Executing web searches for sub-questions...")

            max_sources = project.max_sources or 8
            seen_urls = set()
            raw_sources = []

            for sub_q in created_sub_qs:
                if len(raw_sources) >= max_sources:
                    break
                search_results = self.searcher.search_query(sub_q.question_text, max_results=2)
                for res in search_results:
                    url = res["url"]
                    if url not in seen_urls and len(raw_sources) < max_sources:
                        seen_urls.add(url)
                        raw_sources.append({
                            "sub_q": sub_q,
                            "meta": res
                        })

            run.sources_searched = len(raw_sources)
            self._log_step(run, "Information Collection", f"Retrieved {len(raw_sources)} unique search candidates. Fetching full content...")
            project.current_stage = "Information Collection"
            project.progress_percentage = 35
            self.db.commit()

            # -------------------------------------------------------------
            # Stage 4: Source Storage & Reliability Evaluation
            # -------------------------------------------------------------
            project.current_stage = "Source Storage"
            project.progress_percentage = 45
            self.db.commit()

            saved_sources = []
            for item in raw_sources:
                sub_q = item["sub_q"]
                meta = item["meta"]
                url = meta["url"]

                content_info = self.searcher.fetch_page_content(url)
                clean_text = content_info["clean_text"]
                word_count = content_info["word_count"]
                pub_date = content_info["publication_date"] or meta.get("publication_date")

                eval_result = self.evaluator.evaluate_source(
                    url=url,
                    title=meta["title"],
                    source_type=meta["source_type"],
                    content_text=clean_text,
                    word_count=word_count,
                    publication_date=pub_date,
                    query=sub_q.question_text
                )

                source_record = Source(
                    project_id=project.id,
                    research_question_id=sub_q.id,
                    title=meta["title"][:500],
                    url=url[:1000],
                    publisher=meta.get("publisher", "Web Publisher"),
                    publication_date=str(pub_date) if pub_date else None,
                    source_type=meta["source_type"],
                    relevance_score=eval_result["relevance_score"],
                    reliability_score=eval_result["reliability_score"],
                    reliability_level=eval_result["reliability_level"],
                    reliability_breakdown=eval_result["breakdown"]
                )
                self.db.add(source_record)
                self.db.commit()
                self.db.refresh(source_record)

                # Store content
                source_content = SourceContent(
                    source_id=source_record.id,
                    raw_snippet=meta.get("snippet", "")[:1000],
                    clean_text=clean_text,
                    word_count=word_count,
                    http_status=content_info["http_status"]
                )
                self.db.add(source_content)
                self.db.commit()

                saved_sources.append(source_record)

            run.sources_accepted = len(saved_sources)
            self._log_step(run, "Source Storage", f"Evaluated and persisted {len(saved_sources)} verified sources.")

            # -------------------------------------------------------------
            # Stage 5 & 6: Finding Extraction & Finding Classification
            # -------------------------------------------------------------
            project.current_stage = "Finding Extraction"
            project.progress_percentage = 60
            self.db.commit()
            self._log_step(run, "Finding Extraction", "Extracting structured findings with verbatim evidence...")

            saved_findings = []
            for src in saved_sources:
                content_obj = src.content
                text_to_parse = (content_obj.clean_text if content_obj and content_obj.clean_text else content_obj.raw_snippet) if content_obj else src.title
                sub_q_text = src.research_question.question_text if src.research_question else project.question

                extracted = self.extractor.extract_findings(
                    source_title=src.title,
                    source_url=src.url,
                    content_text=text_to_parse or "",
                    question_text=sub_q_text,
                    category=src.research_question.topic_category if src.research_question else "Operational Impact"
                )

                for f_item in extracted:
                    # Classify category
                    normalized_cat = self.classifier.classify(f_item.get("description", ""), f_item.get("category"))

                    finding_record = Finding(
                        project_id=project.id,
                        source_id=src.id,
                        research_question_id=src.research_question_id,
                        title=f_item.get("title", "Key Empirical Finding")[:500],
                        description=f_item.get("description", "")[:2000],
                        category=normalized_cat,
                        confidence=f_item.get("confidence", "Medium")
                    )
                    self.db.add(finding_record)
                    self.db.commit()
                    self.db.refresh(finding_record)

                    # Store Evidence Quote
                    quote = f_item.get("evidence_quote") or f_item.get("description", "")[:250]
                    evidence_record = Evidence(
                        finding_id=finding_record.id,
                        source_id=src.id,
                        quote_text=quote[:1000],
                        context_snippet=text_to_parse[:300] if text_to_parse else "",
                        confidence_score=0.9 if f_item.get("confidence") == "High" else 0.7
                    )
                    self.db.add(evidence_record)
                    self.db.commit()

                    saved_findings.append(finding_record)

            run.findings_count = len(saved_findings)
            self._log_step(run, "Finding Extraction", f"Extracted and categorized {len(saved_findings)} findings across {len(saved_sources)} sources.")

            # -------------------------------------------------------------
            # Stage 7: Evidence Comparison
            # -------------------------------------------------------------
            project.current_stage = "Evidence Comparison"
            project.progress_percentage = 75
            self.db.commit()
            self._log_step(run, "Evidence Comparison", "Comparing cross-source evidence and perspectives...")

            findings_dicts = []
            for f in saved_findings:
                findings_dicts.append({
                    "id": f.id,
                    "title": f.title,
                    "description": f.description,
                    "category": f.category,
                    "confidence": f.confidence,
                    "source_title": f.source.title if f.source else "Source",
                    "evidence_items": [{"quote_text": e.quote_text} for e in f.evidence_items]
                })

            comparisons_data = self.comparator.compare_evidence(findings_dicts)
            for comp in comparisons_data:
                comp_record = EvidenceComparison(
                    project_id=project.id,
                    topic=comp.get("topic", "Cross-Source Evidence Comparison")[:200],
                    synthesis=comp.get("synthesis", ""),
                    consensus_type=comp.get("consensus_type", "nuanced"),
                    source_count=comp.get("source_count", len(comp.get("perspectives", []))),
                    perspectives=comp.get("perspectives", [])
                )
                self.db.add(comp_record)
            self.db.commit()
            self._log_step(run, "Evidence Comparison", f"Generated {len(comparisons_data)} multi-perspective synthesis clusters.")

            # -------------------------------------------------------------
            # Stage 8: Contradiction Detection
            # -------------------------------------------------------------
            project.current_stage = "Contradiction Detection"
            project.progress_percentage = 85
            self.db.commit()
            self._log_step(run, "Contradiction Detection", "Evaluating potential conflicts and contextual tensions...")

            contradictions_data = self.contradiction_detector.detect_contradictions(findings_dicts)
            created_contradictions = 0
            for item in contradictions_data:
                idx_a = item.get("finding_a_index", 0)
                idx_b = item.get("finding_b_index", 1)
                if idx_a < len(saved_findings) and idx_b < len(saved_findings) and idx_a != idx_b:
                    f_a = saved_findings[idx_a]
                    f_b = saved_findings[idx_b]

                    contra = Contradiction(
                        project_id=project.id,
                        finding_a_id=f_a.id,
                        finding_b_id=f_b.id,
                        topic=item.get("topic", "Contextual Disparity"),
                        explanation=item.get("explanation", ""),
                        contradiction_type=item.get("contradiction_type", "different_context"),
                        confidence=item.get("confidence", "Medium")
                    )
                    self.db.add(contra)
                    created_contradictions += 1
            self.db.commit()
            run.contradictions_count = created_contradictions
            self._log_step(run, "Contradiction Detection", f"Identified {created_contradictions} contextual tensions or contradictions.")

            # -------------------------------------------------------------
            # Stage 9: Conclusion Generation & Traceability
            # -------------------------------------------------------------
            project.current_stage = "Conclusion Generation"
            project.progress_percentage = 92
            self.db.commit()
            self._log_step(run, "Conclusion Generation", "Synthesizing executive conclusions linked to supporting evidence...")

            concl_result = self.conclusion_gen.generate_conclusions(
                research_question=project.question,
                findings=findings_dicts,
                industry=project.industry
            )

            project.executive_summary = concl_result.get("executive_summary", "")

            conclusions_list = concl_result.get("conclusions", [])
            for rank, c_item in enumerate(conclusions_list, start=1):
                concl_record = Conclusion(
                    project_id=project.id,
                    title=c_item.get("title", f"Strategic Conclusion {rank}")[:500],
                    summary=c_item.get("summary", "")[:2000],
                    confidence=c_item.get("confidence", "High"),
                    reasoning_summary=c_item.get("reasoning_summary", "")[:2000],
                    rank_order=rank
                )
                self.db.add(concl_record)
                self.db.flush()

                # Explicit Traceability Link: Conclusion <-> Findings
                indices = c_item.get("supporting_finding_indices", [])
                for idx in indices:
                    if idx < len(saved_findings):
                        concl_record.findings.append(saved_findings[idx])

            self.db.commit()
            run.conclusions_count = len(conclusions_list)

            # -------------------------------------------------------------
            # Completed Pipeline
            # -------------------------------------------------------------
            duration = round(time.time() - start_time, 2)
            run.completed_at = datetime.now(timezone.utc)
            run.duration_seconds = duration
            run.status = "completed"

            project.status = "completed"
            project.current_stage = "Completed"
            project.progress_percentage = 100
            self._log_step(run, "Completed", f"Research pipeline completed successfully in {duration}s.")
            self.db.commit()

            return project

        except Exception as e:
            logger.error(f"Pipeline failed for project {project_id}: {e}", exc_info=True)
            self.db.rollback()
            duration = round(time.time() - start_time, 2)
            project.status = "failed"
            project.current_stage = f"Failed: {str(e)[:80]}"
            run.status = "failed"
            run.error_message = str(e)
            run.duration_seconds = duration
            self._log_step(run, "Error", f"Execution error: {str(e)}", level="ERROR")
            self.db.commit()
            raise
