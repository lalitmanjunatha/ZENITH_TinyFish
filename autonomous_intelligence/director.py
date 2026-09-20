"""
Research Director: Orchestrates entire autonomous research sessions.
This is the main entry point for the Autonomous Intelligence Engine.
"""
import os
import json
import time
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import ResearchConfig
from .models import (
    ResearchSession, ResearchTask, Evidence, Claim,
    KnowledgeGap, ResearchReport, TaskStatus, EvidenceType,
    ResearchPhase, Source, SourceType, BrowserTab,
)
from .events import EventBus, EventType, create_event
from .planner import ResearchPlanner
from .web_engine import WebResearchEngine
from .local_engine import LocalIntelligenceEngine
from .knowledge import KnowledgeEngine
from .permissions import PermissionManager, PermissionLevel


class ResearchDirector:
    """
    Main orchestrator for autonomous research.
    
    Usage:
        director = ResearchDirector(config)
        session = director.start_research("Research topic X and find improvements for Y")
        # ... research runs autonomously ...
        report = director.get_report()
    """

    def __init__(self, config: ResearchConfig = None):
        self.config = config or ResearchConfig()
        self.events = EventBus()
        self.permissions = PermissionManager(PermissionLevel(self.config.permission_level))
        self.planner = ResearchPlanner(self.events)
        self.web = WebResearchEngine(self.config, self.events, self.permissions)
        self.local = LocalIntelligenceEngine(self.config, self.events, self.permissions)
        self.knowledge = KnowledgeEngine(self.config, self.events)

        self.session: Optional[ResearchSession] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start_research(self, objective: str) -> ResearchSession:
        """Start an autonomous research session."""
        self.session = ResearchSession(objective=objective)
        self._running = True
        self._stop_event.clear()

        self.events.emit(create_event(
            EventType.RESEARCH_STARTED,
            session_id=self.session.id,
            objective=objective,
        ))

        # Build local file index
        self.local.build_index()

        # Generate research plan
        self.session.phase = ResearchPhase.PLANNING
        self.session.tasks = self.planner.generate_plan(objective)

        self.events.emit(create_event(
            EventType.PLAN_CREATED,
            session_id=self.session.id,
            tasks_count=len(self.session.tasks),
        ))

        # Run the research loop in background
        self._thread = threading.Thread(
            target=self._research_loop,
            daemon=True,
            name="zenith-research"
        )
        self._thread.start()

        return self.session

    def stop_research(self) -> str:
        """Stop the current research session."""
        self._stop_event.set()
        self._running = False
        if self.session:
            self.session.phase = ResearchPhase.COMPLETED
            self.session.end_time = datetime.now().isoformat()
        return "Research stopped."

    def pause_research(self) -> str:
        """Pause the current research session."""
        if self.session:
            self.session.phase = ResearchPhase.PAUSED
        return "Research paused."

    def resume_research(self) -> str:
        """Resume a paused research session."""
        if self.session:
            self.session.phase = ResearchPhase.RESEARCHING
        return "Research resumed."

    def get_status(self) -> Dict[str, Any]:
        """Get current research status."""
        if not self.session:
            return {"status": "no active session"}

        completed = sum(1 for t in self.session.tasks if t.status == TaskStatus.COMPLETED)
        total = len(self.session.tasks)
        current_task = next(
            (t for t in self.session.tasks if t.status == TaskStatus.IN_PROGRESS),
            None
        )

        elapsed = 0
        if self.session.start_time:
            start = datetime.fromisoformat(self.session.start_time)
            elapsed = (datetime.now() - start).total_seconds()

        return {
            "session_id": self.session.id,
            "objective": self.session.objective,
            "phase": self.session.phase.value,
            "running": self._running,
            "tasks_completed": completed,
            "tasks_total": total,
            "current_task": current_task.title if current_task else None,
            "evidence_count": len(self.knowledge.evidence),
            "claims_count": len(self.knowledge.claims),
            "contradictions": sum(1 for c in self.knowledge.claims if c.contradictions),
            "knowledge_gaps": sum(1 for g in self.knowledge.knowledge_gaps if not g.addressed),
            "sources_count": len(self.session.sources),
            "open_tabs": len(self.web.get_open_tabs()),
            "elapsed_seconds": int(elapsed),
            "errors": len([t for t in self.session.tasks if t.status == TaskStatus.FAILED]),
        }

    def get_live_activity(self) -> Dict[str, Any]:
        """Get live activity for UI display."""
        recent_events = self.events.get_recent(limit=20)
        return {
            "status": self.get_status(),
            "recent_events": recent_events,
            "open_tabs": self.web.get_open_tabs(),
            "knowledge_summary": self.knowledge.get_summary(),
        }

    def get_report(self) -> Optional[ResearchReport]:
        """Get the final research report."""
        if self.session and self.session.report:
            return self.session.report
        return None

    def get_session_history(self) -> List[Dict]:
        """Get all events from the current session."""
        return self.events.get_recent(limit=200)

    def save_session(self, path: str = None) -> str:
        """Save the current session to disk."""
        if not self.session:
            return "No active session."

        path = path or os.path.join(
            self.config.storage_dir,
            f"session_{self.session.id}.json"
        )
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data = {
            "session": {
                "id": self.session.id,
                "objective": self.session.objective,
                "phase": self.session.phase.value,
                "start_time": self.session.start_time,
                "end_time": self.session.end_time,
                "stats": self.session.stats,
            },
            "tasks": [
                {
                    "id": t.id, "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority,
                    "results": t.results,
                }
                for t in self.session.tasks
            ],
            "knowledge": self.knowledge.to_json(),
            "events": self.events.get_recent(limit=500),
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        return f"Session saved: {path}"

    def _research_loop(self):
        """Core autonomous research loop."""
        try:
            start_time = time.time()
            max_seconds = self.config.max_runtime_minutes * 60
            iteration = 0

            while (self._running and
                   not self._stop_event.is_set() and
                   iteration < self.config.max_iterations):

                elapsed = time.time() - start_time
                if elapsed > max_seconds:
                    break

                if self.session.phase == ResearchPhase.PAUSED:
                    time.sleep(1)
                    continue

                self.session.phase = ResearchPhase.RESEARCHING

                # Get next task
                task = self.planner.get_next_task(self.session.tasks)
                if not task:
                    break

                # Execute the task
                task.status = TaskStatus.IN_PROGRESS
                self.events.emit(create_event(
                    EventType.TASK_STARTED,
                    session_id=self.session.id,
                    task_id=task.id,
                    title=task.title,
                ))

                try:
                    self._execute_task(task)
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now().isoformat()

                    self.events.emit(create_event(
                        EventType.TASK_COMPLETED,
                        session_id=self.session.id,
                        task_id=task.id,
                        title=task.title,
                    ))

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)[:200]
                    self.events.emit(create_event(
                        EventType.TASK_FAILED,
                        session_id=self.session.id,
                        task_id=task.id,
                        error=str(e)[:200],
                    ))

                # Periodically detect contradictions and gaps
                if iteration % 3 == 0:
                    self.knowledge.detect_contradictions()
                    gaps = self.knowledge.identify_knowledge_gaps(self.session.objective)
                    if gaps:
                        self.session.tasks = self.planner.adapt_plan(
                            self.session.tasks,
                            [{"question": g.question, "context": g.context, "priority": g.priority}
                             for g in gaps if not g.addressed],
                            self.knowledge.get_summary(),
                        )

                iteration += 1

                # Update stats
                self.session.stats = {
                    "iterations": iteration,
                    "elapsed_seconds": int(elapsed),
                    **self.knowledge.get_summary(),
                }

            # Generate final report
            self.session.phase = ResearchPhase.REPORTING
            self.session.report = self._generate_report()

            self.session.phase = ResearchPhase.COMPLETED
            self.session.end_time = datetime.now().isoformat()
            self._running = False

            self.events.emit(create_event(
                EventType.RESEARCH_COMPLETED,
                session_id=self.session.id,
                stats=self.session.stats,
            ))

            # Save session
            self.save_session()

        except Exception as e:
            self.session.phase = ResearchPhase.ERROR
            self.session.error = str(e)
            self._running = False
            self.events.emit(create_event(
                EventType.RESEARCH_ERROR,
                session_id=self.session.id if self.session else "",
                error=str(e)[:300],
            ))

    def _execute_task(self, task: ResearchTask):
        """Execute a single research task."""
        # Execute web searches
        for query in task.search_queries:
            if self._stop_event.is_set():
                break

            results = self.web.search(query)
            task.results.extend([r.get("url", "") for r in results])

            # Visit and read top results
            for result in results[:3]:
                if self._stop_event.is_set():
                    break

                url = result.get("url", "")
                if not url:
                    continue

                tab = self.web.open_page(url)
                if tab:
                    content = self.web.get_cached_content(url)
                    if content:
                        # Extract knowledge from content
                        source = Source(
                            source_type=SourceType.WEB_PAGE,
                            url=url,
                            title=result.get("title", ""),
                            domain=result.get("domain", ""),
                        )
                        self.session.sources.append(source)

                        # Create evidence from the content
                        self._extract_knowledge(content, source, query)

                    # Extract links for follow-up
                    links = self.web.extract_links(url)
                    for link in links[:2]:
                        if not self._stop_event.is_set():
                            link_content = self.web.read_page(link)
                            if link_content:
                                link_source = Source(
                                    source_type=SourceType.WEB_PAGE,
                                    url=link,
                                    domain=link.split("//")[-1].split("/")[0],
                                )
                                self.session.sources.append(link_source)
                                self._extract_knowledge(link_content, link_source, query)

        # Execute local searches
        for query in task.local_searches:
            if self._stop_event.is_set():
                break

            results = self.local.search(query)
            for result in results[:3]:
                content = self.local.read_file(result["path"])
                if content and content.startswith("["):
                    continue  # Skip error messages

                source = Source(
                    source_type=SourceType.LOCAL_FILE,
                    path=result["path"],
                    title=result.get("name", ""),
                )
                self.session.sources.append(source)
                self._extract_knowledge(content, source, query)

        # Visit explicitly requested URLs
        for url in task.urls_to_visit:
            if self._stop_event.is_set():
                break
            content = self.web.read_page(url)
            if content:
                source = Source(
                    source_type=SourceType.WEB_PAGE,
                    url=url,
                )
                self.session.sources.append(source)
                self._extract_knowledge(content, source, "")

    def _extract_knowledge(self, content: str, source: Source, query: str):
        """Extract knowledge claims from content."""
        if not content or len(content) < 50:
            return

        # Simple sentence-level claim extraction
        sentences = content.replace("\n", " ").split(".")
        query_terms = set(query.lower().split()) if query else set()

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 30 or len(sentence) > 500:
                continue

            # Check relevance to query
            if query_terms:
                relevance = sum(1 for t in query_terms if t in sentence.lower())
                if relevance == 0:
                    continue

            # Determine confidence based on source type and content quality
            confidence = 0.5
            if source.source_type == SourceType.WEB_PAGE:
                if any(d in source.domain for d in ["arxiv.org", "github.com", "docs."]):
                    confidence = 0.7
                elif any(d in source.domain for d in [".edu", ".gov", ".org"]):
                    confidence = 0.65

            # Check for hedging language
            hedging = ["may", "might", "could", "possibly", "perhaps", "suggests", "indicates"]
            if any(h in sentence.lower() for h in hedging):
                confidence *= 0.8

            # Check for strong assertions
            strong = ["demonstrates", "proves", "confirms", "establishes", "shows"]
            if any(s in sentence.lower() for s in strong):
                confidence = min(confidence * 1.2, 0.9)

            evidence = self.knowledge.add_evidence(
                claim_text=sentence.strip(),
                source=source,
                context=query,
                confidence=confidence,
                evidence_type=EvidenceType.INFERENCE if confidence < 0.6 else EvidenceType.FACT,
            )

            self.knowledge.add_claim(
                text=sentence.strip(),
                confidence=confidence,
                source_ids=[source.id],
            )

            self.events.emit(create_event(
                EventType.KNOWLEDGE_EXTRACTED,
                claim=sentence.strip()[:200],
                source=source.url or source.path,
                confidence=confidence,
            ))

    def _generate_report(self) -> ResearchReport:
        """Generate the final research report."""
        summary = self.knowledge.get_summary()

        # Gather findings
        external_findings = []
        local_findings = []
        for ev in self.knowledge.evidence:
            if ev.source:
                if ev.source.source_type == SourceType.WEB_PAGE:
                    external_findings.append(ev.claim)
                elif ev.source.source_type in (SourceType.LOCAL_FILE, SourceType.LOCAL_CODE):
                    local_findings.append(ev.claim)

        # Deduplicate
        external_findings = list(dict.fromkeys(external_findings))[:20]
        local_findings = list(dict.fromkeys(local_findings))[:15]

        # Get contradictions
        contradictions = []
        for c in self.knowledge.claims:
            if c.contradictions:
                contradictions.append(c.text)

        # Source list
        sources = list(dict.fromkeys([
            s.url or s.path
            for s in self.session.sources
            if s.url or s.path
        ]))[:30]

        # Timeline
        timeline = []
        for t in self.session.tasks:
            if t.status == TaskStatus.COMPLETED:
                timeline.append(f"Completed: {t.title}")
            elif t.status == TaskStatus.FAILED:
                timeline.append(f"Failed: {t.title} - {t.error[:50]}")

        # Confidence assessment
        avg_conf = summary.get("average_confidence", 0)
        if avg_conf >= 0.7:
            confidence = "HIGH"
        elif avg_conf >= 0.5:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # Knowledge gaps
        gaps_text = [
            g.question for g in self.knowledge.knowledge_gaps
            if not g.addressed
        ]

        # Build report text
        report_text = self._format_report_text(
            self.session.objective,
            external_findings,
            local_findings,
            contradictions,
            gaps_text,
            sources,
            confidence,
            summary,
        )

        report = ResearchReport(
            title=f"Intelligence Report: {self.session.objective[:80]}",
            objective=self.session.objective,
            executive_summary=f"Research completed with {summary['total_evidence']} evidence items from {len(sources)} sources.",
            key_findings=external_findings[:10],
            local_findings=local_findings[:10],
            external_findings=external_findings[:15],
            comparison=self._generate_comparison(external_findings, local_findings),
            evidence_summary=[f"{e.evidence_type.value}: {e.claim[:100]}" for e in self.knowledge.evidence[:15]],
            contradictions=contradictions[:5],
            knowledge_gaps=gaps_text[:5],
            confidence=confidence,
            recommendations=self._generate_recommendations(),
            sources=sources,
            timeline=timeline[:15],
            full_text=report_text,
        )

        self.events.emit(create_event(
            EventType.REPORT_GENERATED,
            session_id=self.session.id,
            confidence=confidence,
            sources_count=len(sources),
        ))

        return report

    def _format_report_text(self, objective, external, local, contradictions, gaps, sources, confidence, summary):
        """Format the full report text."""
        lines = []
        lines.append("=" * 60)
        lines.append("ZENITH AUTONOMOUS INTELLIGENCE REPORT")
        lines.append("=" * 60)
        lines.append(f"\nOBJECTIVE:\n{objective}\n")
        lines.append(f"CONFIDENCE LEVEL: {confidence}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        lines.append("-" * 40)
        lines.append("EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Analyzed {summary['total_evidence']} pieces of evidence from {len(sources)} sources.")
        lines.append(f"Identified {summary['total_claims']} claims with {summary['contradictions']} contradictions.\n")

        if external:
            lines.append("-" * 40)
            lines.append("EXTERNAL FINDINGS")
            lines.append("-" * 40)
            for i, f in enumerate(external[:10], 1):
                lines.append(f"{i}. {f[:200]}\n")

        if local:
            lines.append("-" * 40)
            lines.append("LOCAL PROJECT FINDINGS")
            lines.append("-" * 40)
            for i, f in enumerate(local[:10], 1):
                lines.append(f"{i}. {f[:200]}\n")

        if contradictions:
            lines.append("-" * 40)
            lines.append("CONTRADICTIONS DETECTED")
            lines.append("-" * 40)
            for c in contradictions[:5]:
                lines.append(f"! {c[:200]}\n")

        if gaps:
            lines.append("-" * 40)
            lines.append("KNOWLEDGE GAPS")
            lines.append("-" * 40)
            for g in gaps[:5]:
                lines.append(f"? {g}\n")

        if sources:
            lines.append("-" * 40)
            lines.append("SOURCES")
            lines.append("-" * 40)
            for i, s in enumerate(sources[:15], 1):
                lines.append(f"{i}. {s}\n")

        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _generate_comparison(self, external, local) -> str:
        if not external and not local:
            return "No findings to compare."
        if not local:
            return "External research found information but no related local files were identified."
        if not external:
            return "Local files were analyzed but no external research was completed."
        return f"Compared {len(external)} external findings with {len(local)} local findings."

    def _generate_recommendations(self) -> List[str]:
        recs = []
        summary = self.knowledge.get_summary()
        if summary["contradictions"] > 0:
            recs.append("Investigate contradictory claims with additional sources")
        if summary["unresolved_gaps"] > 0:
            recs.append("Address identified knowledge gaps")
        if summary["average_confidence"] < 0.5:
            recs.append("Increase source diversity to improve confidence")
        if summary["total_evidence"] < 10:
            recs.append("Conduct deeper research for more comprehensive coverage")
        recs.append("Review findings and validate against project requirements")
        return recs
