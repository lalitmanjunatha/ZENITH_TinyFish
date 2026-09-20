"""
Knowledge Engine: Evidence tracking, verification, contradiction detection,
knowledge graph, and claim management.
"""
import re
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from .models import (
    Evidence, Claim, KnowledgeGap, Source, EvidenceType, SourceType
)
from .events import EventBus, EventType, create_event
from .config import ResearchConfig


class KnowledgeGraph:
    """Lightweight knowledge graph for entities and relationships."""

    def __init__(self):
        self.entities: Dict[str, Dict] = {}  # id -> {name, type, metadata}
        self.relationships: List[Dict] = []  # [{from, to, type, metadata}]

    def add_entity(self, name: str, entity_type: str, metadata: Dict = None) -> str:
        entity_id = name.lower().replace(" ", "_")
        self.entities[entity_id] = {
            "name": name,
            "type": entity_type,
            "metadata": metadata or {},
        }
        return entity_id

    def add_relationship(
        self, from_entity: str, to_entity: str,
        rel_type: str, metadata: Dict = None
    ):
        self.relationships.append({
            "from": from_entity.lower().replace(" ", "_"),
            "to": to_entity.lower().replace(" ", "_"),
            "type": rel_type,
            "metadata": metadata or {},
        })

    def get_entity(self, name: str) -> Optional[Dict]:
        return self.entities.get(name.lower().replace(" ", "_"))

    def get_relationships(self, entity_id: str) -> List[Dict]:
        entity_id = entity_id.lower().replace(" ", "_")
        return [
            r for r in self.relationships
            if r["from"] == entity_id or r["to"] == entity_id
        ]

    def to_dict(self) -> Dict:
        return {
            "entities": len(self.entities),
            "relationships": len(self.relationships),
            "entity_list": list(self.entities.values()),
            "relationship_list": self.relationships[:100],
        }


class KnowledgeEngine:
    """Manages evidence, claims, verification, and knowledge graph."""

    def __init__(
        self,
        config: ResearchConfig,
        event_bus: EventBus,
    ):
        self.config = config
        self.events = event_bus
        self.evidence: List[Evidence] = []
        self.claims: List[Claim] = []
        self.knowledge_gaps: List[KnowledgeGap] = []
        self.graph = KnowledgeGraph()
        self._source_evidence_map: Dict[str, List[str]] = defaultdict(list)

    def add_evidence(
        self,
        claim_text: str,
        source: Source,
        context: str = "",
        confidence: float = 0.5,
        evidence_type: EvidenceType = EvidenceType.INFERENCE,
    ) -> Evidence:
        """Add a piece of evidence."""
        ev = Evidence(
            claim=claim_text,
            evidence_type=evidence_type,
            source=source,
            context=context,
            confidence=confidence,
        )
        self.evidence.append(ev)

        if source.id:
            self._source_evidence_map[source.id].append(ev.id)

        self.events.emit(create_event(
            EventType.EVIDENCE_FOUND,
            evidence_id=ev.id,
            claim=claim_text[:200],
            source=source.url or source.path,
            confidence=confidence,
            type=evidence_type.value,
        ))

        # Auto-extract entities for knowledge graph
        self._extract_entities(claim_text, source)

        return ev

    def add_claim(
        self,
        text: str,
        evidence_type: EvidenceType = EvidenceType.INFERENCE,
        confidence: float = 0.5,
        source_ids: List[str] = None,
    ) -> Claim:
        """Add a claim."""
        claim = Claim(
            text=text,
            evidence_type=evidence_type,
            confidence=confidence,
            source_ids=source_ids or [],
        )
        self.claims.append(claim)

        self.events.emit(create_event(
            EventType.CLAIM_CREATED,
            claim_id=claim.id,
            text=text[:200],
            confidence=confidence,
            type=evidence_type.value,
        ))

        return claim

    def detect_contradictions(self) -> List[Tuple[Claim, Claim, str]]:
        """Detect contradictions between claims."""
        contradictions = []

        for i, claim_a in enumerate(self.claims):
            for claim_b in self.claims[i+1:]:
                similarity = self._text_similarity(claim_a.text, claim_b.text)
                if similarity > 0.6 and claim_a.confidence > 0.3 and claim_b.confidence > 0.3:
                    # Claims are similar but check if they contradict
                    if self._are_contradictory(claim_a.text, claim_b.text):
                        reason = f"Claims are similar ({similarity:.0%}) but differ in key details"
                        contradictions.append((claim_a, claim_b, reason))

                        claim_a.contradictions.append(claim_b.id)
                        claim_b.contradictions.append(claim_a.id)

                        claim_a.evidence_type = EvidenceType.CONFLICTING
                        claim_b.evidence_type = EvidenceType.CONFLICTING

                        self.events.emit(create_event(
                            EventType.CONTRADICTION_FOUND,
                            claim_a=claim_a.text[:150],
                            claim_b=claim_b.text[:150],
                            reason=reason,
                        ))

        return contradictions

    def identify_knowledge_gaps(self, objective: str) -> List[KnowledgeGap]:
        """Identify gaps in current knowledge relative to the objective."""
        gaps = []

        # Check if we have enough evidence
        if len(self.evidence) < 3:
            gaps.append(KnowledgeGap(
                question=f"Insufficient evidence for: {objective}",
                context=f"Only {len(self.evidence)} evidence items collected",
                priority=8,
            ))

        # Check for unverified claims
        unverified = [c for c in self.claims if not c.verified and c.confidence > 0.5]
        if unverified:
            gaps.append(KnowledgeGap(
                question=f"{len(unverified)} high-confidence claims need verification",
                context="Claims with confidence > 0.5 should be verified",
                priority=7,
            ))

        # Check for conflicting claims
        conflicting = [c for c in self.claims if c.evidence_type == EvidenceType.CONFLICTING]
        if conflicting:
            gaps.append(KnowledgeGap(
                question=f"{len(conflicting)} conflicting claims need resolution",
                context="Contradictory evidence requires additional sources",
                priority=9,
            ))

        # Check source diversity
        domains = set()
        for ev in self.evidence:
            if ev.source and ev.source.domain:
                domains.add(ev.source.domain)
        if len(domains) < 2 and len(self.evidence) > 0:
            gaps.append(KnowledgeGap(
                question="Need more diverse sources",
                context=f"Only {len(domains)} unique domains consulted",
                priority=6,
            ))

        self.knowledge_gaps.extend(gaps)

        for gap in gaps:
            self.events.emit(create_event(
                EventType.KNOWLEDGE_GAP_IDENTIFIED,
                question=gap.question,
                priority=gap.priority,
            ))

        return gaps

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all knowledge collected."""
        evidence_by_type = defaultdict(int)
        for ev in self.evidence:
            evidence_by_type[ev.evidence_type.value] += 1

        claims_by_type = defaultdict(int)
        for c in self.claims:
            claims_by_type[c.evidence_type.value] += 1

        avg_confidence = 0
        if self.claims:
            avg_confidence = sum(c.confidence for c in self.claims) / len(self.claims)

        return {
            "total_evidence": len(self.evidence),
            "evidence_by_type": dict(evidence_by_type),
            "total_claims": len(self.claims),
            "claims_by_type": dict(claims_by_type),
            "verified_claims": sum(1 for c in self.claims if c.verified),
            "contradictions": sum(1 for c in self.claims if c.contradictions),
            "knowledge_gaps": len(self.knowledge_gaps),
            "unresolved_gaps": sum(1 for g in self.knowledge_gaps if not g.addressed),
            "average_confidence": avg_confidence,
            "entities_in_graph": len(self.graph.entities),
            "relationships_in_graph": len(self.graph.relationships),
        }

    def to_json(self) -> str:
        """Serialize knowledge to JSON."""
        return json.dumps({
            "evidence": [
                {
                    "id": e.id, "claim": e.claim,
                    "type": e.evidence_type.value,
                    "confidence": e.confidence,
                    "source": e.source.url if e.source else "",
                    "verified": e.verified,
                }
                for e in self.evidence
            ],
            "claims": [
                {
                    "id": c.id, "text": c.text,
                    "type": c.evidence_type.value,
                    "confidence": c.confidence,
                    "verified": c.verified,
                    "contradictions": len(c.contradictions),
                }
                for c in self.claims
            ],
            "summary": self.get_summary(),
        }, indent=2)

    def _extract_entities(self, text: str, source: Source):
        """Extract simple entities from text for the knowledge graph."""
        # Simple entity extraction based on capitalization patterns
        words = text.split()
        potential_entities = []
        for i, word in enumerate(words):
            if word[0:1].isupper() and len(word) > 2 and word.isalpha():
                potential_entities.append(word)

        # Add common tech entities
        tech_terms = [
            "Python", "JavaScript", "TypeScript", "React", "Vue", "Angular",
            "TensorFlow", "PyTorch", "LiveKit", "Gemini", "GPT", "Claude",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP",
            "SQLite", "PostgreSQL", "MongoDB", "Redis",
            "REST", "GraphQL", "gRPC", "WebSocket",
            "DAG", "LLM", "RAG", "RLHF", "MCP",
        ]

        for term in tech_terms:
            if term.lower() in text.lower():
                self.graph.add_entity(term, "technology")

    def _text_similarity(self, text_a: str, text_b: str) -> float:
        """Simple word-overlap similarity."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / len(union) if union else 0.0

    def _are_contradictory(self, text_a: str, text_b: str) -> bool:
        """Simple contradiction detection based on negation patterns."""
        negations_a = len(re.findall(r'\b(not|no|never|cannot|cannot|isn\'t|aren\'t|won\'t|don\'t|doesn\'t)\b', text_a.lower()))
        negations_b = len(re.findall(r'\b(not|no|never|cannot|cannot|isn\'t|aren\'t|won\'t|don\'t|doesn\'t)\b', text_b.lower()))

        # If one is negated and the other isn't, likely contradictory
        if (negations_a > 0) != (negations_b > 0):
            return True

        # Check for opposing quantitative claims
        numbers_a = re.findall(r'(\d+(?:\.\d+)?)\s*(%|percent)', text_a.lower())
        numbers_b = re.findall(r'(\d+(?:\.\d+)?)\s*(%|percent)', text_b.lower())
        if numbers_a and numbers_b:
            try:
                val_a = float(numbers_a[0][0])
                val_b = float(numbers_b[0][0])
                if abs(val_a - val_b) > 30:
                    return True
            except ValueError:
                pass

        return False
