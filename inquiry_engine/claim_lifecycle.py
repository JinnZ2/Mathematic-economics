#!/usr/bin/env python3
"""
claim_lifecycle.py – Formal state machine for falsifiable claims.
CC0. Stdlib only.

Usage:
  from claim_lifecycle import ClaimLifecycle, ClaimState
  
  claim = ClaimLifecycle("I001", "DICE damage function is smooth.")
  claim.propose()
  claim.activate()
  claim.survive_round(evidence={"source": "simulation", "result": "passed"})
  claim.falsify(evidence={"source": "peer-reviewed paper", "result": "contradicts"})
  print(claim.to_dict())
"""

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class ClaimState(Enum):
    PROPOSED = auto()
    UNDER_REVIEW = auto()
    ACTIVE = auto()
    SURVIVED = auto()          # survived at least one test round
    FALSIFIED = auto()
    SUPERSEDED = auto()
    RETIRED = auto()


VALID_TRANSITIONS = {
    ClaimState.PROPOSED:    {ClaimState.UNDER_REVIEW, ClaimState.RETIRED},
    ClaimState.UNDER_REVIEW:{ClaimState.ACTIVE, ClaimState.FALSIFIED, ClaimState.RETIRED},
    ClaimState.ACTIVE:      {ClaimState.SURVIVED, ClaimState.FALSIFIED, ClaimState.SUPERSEDED, ClaimState.RETIRED},
    ClaimState.SURVIVED:    {ClaimState.SURVIVED, ClaimState.FALSIFIED, ClaimState.SUPERSEDED, ClaimState.RETIRED},
    ClaimState.FALSIFIED:   {ClaimState.RETIRED, ClaimState.PROPOSED},  # can be re-proposed with revision
    ClaimState.SUPERSEDED:  {ClaimState.RETIRED},
    ClaimState.RETIRED:     set(),
}


@dataclass
class EvidenceEntry:
    timestamp: str = ""
    evidence_type: str = ""   # simulation, experiment, literature_review, data_update, observation
    result: str = ""          # passed, failed, inconclusive, contradicts
    source: str = ""          # file, DOI, URL, session ID
    notes: str = ""

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "type": self.evidence_type,
            "result": self.result,
            "source": self.source,
            "notes": self.notes,
        }


@dataclass
class ClaimLifecycle:
    claim_id: str
    statement: str
    falsifier: str = ""
    state: ClaimState = ClaimState.PROPOSED
    rounds_survived: int = 0
    evidence_log: List[EvidenceEntry] = field(default_factory=list)
    superseded_by: Optional[str] = None
    proposed_by: str = ""
    created_at: str = ""
    last_modified: str = ""
    dependencies: List[str] = field(default_factory=list)  # IDs of claims this one depends on
    dependents: List[str] = field(default_factory=list)     # IDs of claims that depend on this one

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.last_modified:
            self.last_modified = now

    def _set_state(self, new_state: ClaimState, evidence: Optional[Dict[str, str]] = None):
        if new_state not in VALID_TRANSITIONS.get(self.state, set()):
            raise ValueError(
                f"Invalid transition: {self.state.name} → {new_state.name}. "
                f"Allowed: {[s.name for s in VALID_TRANSITIONS.get(self.state, set())]}"
            )
        self.state = new_state
        self.last_modified = datetime.now(timezone.utc).isoformat()
        if evidence:
            entry = EvidenceEntry(
                timestamp=self.last_modified,
                evidence_type=evidence.get("type", ""),
                result=evidence.get("result", ""),
                source=evidence.get("source", ""),
                notes=evidence.get("notes", ""),
            )
            self.evidence_log.append(entry)

    def propose(self, proposed_by: str = ""):
        self.proposed_by = proposed_by
        self._set_state(ClaimState.PROPOSED)

    def under_review(self):
        self._set_state(ClaimState.UNDER_REVIEW)

    def activate(self):
        self._set_state(ClaimState.ACTIVE)

    def survive_round(self, evidence: Optional[Dict[str, str]] = None):
        self.rounds_survived += 1
        self._set_state(ClaimState.SURVIVED, evidence)

    def falsify(self, evidence: Dict[str, str]):
        self._set_state(ClaimState.FALSIFIED, evidence)

    def supersede(self, new_claim_id: str):
        self.superseded_by = new_claim_id
        self._set_state(ClaimState.SUPERSEDED)

    def retire(self, evidence: Optional[Dict[str, str]] = None):
        self._set_state(ClaimState.RETIRED, evidence)

    def add_evidence(self, evidence: Dict[str, str]):
        entry = EvidenceEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            evidence_type=evidence.get("type", ""),
            result=evidence.get("result", ""),
            source=evidence.get("source", ""),
            notes=evidence.get("notes", ""),
        )
        self.evidence_log.append(entry)
        self.last_modified = entry.timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.claim_id,
            "statement": self.statement,
            "falsifier": self.falsifier,
            "state": self.state.name,
            "rounds_survived": self.rounds_survived,
            "evidence_log": [e.to_dict() for e in self.evidence_log],
            "superseded_by": self.superseded_by,
            "proposed_by": self.proposed_by,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
        }

    def from_dict(cls, data: Dict[str, Any]) -> "ClaimLifecycle":
        claim = cls(
            claim_id=data["id"],
            statement=data["statement"],
            falsifier=data.get("falsifier", ""),
            state=ClaimState[data["state"]],
            rounds_survived=data.get("rounds_survived", 0),
            superseded_by=data.get("superseded_by"),
            proposed_by=data.get("proposed_by", ""),
            created_at=data.get("created_at", ""),
            last_modified=data.get("last_modified", ""),
            dependencies=data.get("dependencies", []),
            dependents=data.get("dependents", []),
        )
        for ev in data.get("evidence_log", []):
            claim.evidence_log.append(EvidenceEntry(
                timestamp=ev.get("timestamp", ""),
                evidence_type=ev.get("type", ""),
                result=ev.get("result", ""),
                source=ev.get("source", ""),
                notes=ev.get("notes", ""),
            ))
        return claim

    def print_status(self):
        print(f"Claim {self.claim_id}: [{self.state.name}] {self.statement}")
        print(f"  Falsifier: {self.falsifier}")
        print(f"  Rounds survived: {self.rounds_survived}")
        if self.superseded_by:
            print(f"  Superseded by: {self.superseded_by}")
        print(f"  Evidence entries: {len(self.evidence_log)}")
        if self.dependencies:
            print(f"  Depends on: {self.dependencies}")
        if self.dependents:
            print(f"  Dependents: {self.dependents}")


# ----------------------------------------------------------------------
# Claim registry (in-memory, with JSON file persistence)
# ----------------------------------------------------------------------
class ClaimRegistry:
    """Manages a collection of ClaimLifecycle objects."""
    def __init__(self, storage_path: str = "claims_registry.json"):
        self.storage_path = storage_path
        self.claims: Dict[str, ClaimLifecycle] = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for cid, cdata in data.items():
                    self.claims[cid] = ClaimLifecycle.from_dict(cdata)

    def save(self):
        with open(self.storage_path, "w") as f:
            json.dump({cid: c.to_dict() for cid, c in self.claims.items()}, f, indent=2)

    def add(self, claim: ClaimLifecycle):
        self.claims[claim.claim_id] = claim
