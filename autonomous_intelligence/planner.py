"""
Research Planner: Generates and adapts research plans from objectives.
"""
from typing import Any, Dict, List, Optional
from .models import ResearchTask, TaskStatus
from .events import EventBus, EventType, create_event


class ResearchPlanner:
    """Generates and manages research task plans."""

    def __init__(self, event_bus: EventBus):
        self.events = event_bus

    def generate_plan(self, objective: str, existing_knowledge: str = "") -> List[ResearchTask]:
        """Generate a research plan from an objective."""
        tasks = []

        # Phase 1: Understand the objective
        tasks.append(ResearchTask(
            title="Define research scope",
            description=f"Break down the objective into specific questions: {objective}",
            priority=10,
            search_queries=[self._extract_search_query(objective)],
        ))

        # Phase 2: Web research - broad
        tasks.append(ResearchTask(
            title="Broad web research",
            description="Search for general information and overviews",
            priority=9,
            search_queries=self._generate_search_queries(objective, "overview"),
        ))

        # Phase 3: Web research - specific
        tasks.append(ResearchTask(
            title="Specific web research",
            description="Search for detailed technical information",
            priority=8,
            search_queries=self._generate_search_queries(objective, "technical"),
        ))

        # Phase 4: Academic/research sources
        tasks.append(ResearchTask(
            title="Academic research",
            description="Search for papers, documentation, and official sources",
            priority=7,
            search_queries=self._generate_search_queries(objective, "academic"),
        ))

        # Phase 5: Implementation examples
        tasks.append(ResearchTask(
            title="Implementation research",
            description="Search for code examples, implementations, and projects",
            priority=7,
            search_queries=self._generate_search_queries(objective, "implementation"),
        ))

        # Phase 6: Local intelligence
        tasks.append(ResearchTask(
            title="Local file search",
            description="Search local project files for related information",
            priority=6,
            local_searches=self._generate_local_queries(objective),
        ))

        # Phase 7: Compare and synthesize
        tasks.append(ResearchTask(
            title="Cross-reference sources",
            description="Compare findings from different sources for consistency",
            priority=6,
        ))

        # Phase 8: Verify key claims
        tasks.append(ResearchTask(
            title="Verify important claims",
            description="Search for independent confirmation of key findings",
            priority=5,
        ))

        # Phase 9: Gap analysis
        tasks.append(ResearchTask(
            title="Identify knowledge gaps",
            description="Determine what information is still missing",
            priority=4,
        ))

        # Phase 10: Generate report
        tasks.append(ResearchTask(
            title="Generate intelligence report",
            description="Compile all findings into a cited report",
            priority=3,
        ))

        self.events.emit(create_event(
            EventType.PLAN_CREATED,
            objective=objective,
            tasks_count=len(tasks),
        ))

        return tasks

    def adapt_plan(
        self,
        tasks: List[ResearchTask],
        new_gaps: List[Dict],
        evidence_summary: Dict,
    ) -> List[ResearchTask]:
        """Adapt the plan based on new discoveries."""
        new_tasks = []

        for gap in new_gaps:
            if gap.get("priority", 0) >= 6:
                new_tasks.append(ResearchTask(
                    title=f"Address gap: {gap.get('question', 'unknown')[:60]}",
                    description=gap.get("context", ""),
                    priority=gap.get("priority", 5),
                    search_queries=[gap.get("question", "")],
                ))

        if new_tasks:
            self.events.emit(create_event(
                EventType.PLAN_UPDATED,
                new_tasks_added=len(new_tasks),
                total_tasks=len(tasks) + len(new_tasks),
            ))

        return tasks + new_tasks

    def get_next_task(self, tasks: List[ResearchTask]) -> Optional[ResearchTask]:
        """Get the next task to execute based on priority and status."""
        pending = [
            t for t in tasks
            if t.status == TaskStatus.PENDING
        ]
        if not pending:
            return None
        pending.sort(key=lambda t: -t.priority)
        return pending[0]

    def _extract_search_query(self, objective: str) -> str:
        """Extract a good initial search query from the objective."""
        # Remove common phrases
        remove = [
            "research", "investigate", "analyze", "study",
            "determine", "find out", "look into", "explore",
            "how can", "what are", "what is", "tell me about",
            "understand", "learn about",
        ]
        query = objective.lower()
        for phrase in remove:
            query = query.replace(phrase, "")
        query = " ".join(query.split()).strip()
        if len(query) < 5:
            query = objective
        return query

    def _generate_search_queries(self, objective: str, style: str) -> List[str]:
        """Generate search queries based on style."""
        base = self._extract_search_query(objective)

        if style == "overview":
            return [
                f"{base} overview",
                f"{base} introduction",
                f"what is {base}",
            ]
        elif style == "technical":
            return [
                f"{base} architecture",
                f"{base} implementation details",
                f"{base} technical deep dive",
            ]
        elif style == "academic":
            return [
                f"{base} research paper",
                f"{base} survey paper",
                f"{base} documentation",
            ]
        elif style == "implementation":
            return [
                f"{base} github",
                f"{base} open source",
                f"{base} code example",
            ]
        return [base]

    def _generate_local_queries(self, objective: str) -> List[str]:
        """Generate local search queries from objective."""
        keywords = objective.lower().split()
        # Remove common stop words
        stop = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                 "being", "have", "has", "had", "do", "does", "did", "will",
                 "would", "could", "should", "may", "might", "shall", "can",
                 "and", "or", "but", "in", "on", "at", "to", "for", "of",
                 "with", "by", "from", "as", "into", "through", "during",
                 "before", "after", "above", "below", "between", "under",
                 "again", "further", "then", "once", "here", "there",
                 "when", "where", "why", "how", "all", "each", "every",
                 "both", "few", "more", "most", "other", "some", "such",
                 "no", "nor", "not", "only", "own", "same", "so",
                 "than", "too", "very", "just", "because", "if", "about"}
        keywords = [w for w in keywords if w not in stop and len(w) > 2]
        return keywords[:5]
