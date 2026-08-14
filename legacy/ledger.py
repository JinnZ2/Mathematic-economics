#!/usr/bin/env python3
"""legacy/ledger.py -- reader and validator for LEGACY LEDGER records.

The ledger is the repo's retirement record: one entry per artifact that
was superseded, absorbed, reframed, extracted, relocated, or discarded.
It exists because this repository runs the falsification cycle
(hypothesize -> run -> result -> edit claim -> search unknowns -> rerun)
and the *previous* state of a claim is evidence, not garbage. See
`legacy/README.md` for the doctrine.

This module makes the ledger falsifiable rather than decorative. A
retirement note that points at a successor which no longer exists, or
that claims an artifact is retained when the file is absent, is a
broken audit trail -- and these checks fail on it.

Gates enforced:
    G1  every record parses and carries all required fields
    G2  verdict is one of the six declared values
    G3  `retained_at`, when non-null, is under legacy/ and exists
    G4  every `successor` path exists in the working tree
    G5  only DISCARDED records may have an empty successor list
    G6  `precedence` is non-empty -- the load-bearing field; a record
        that cannot say what still carries forward is not a retirement
        record, it is a deletion with extra steps
    G7  `retired_in` is a 40-hex commit sha or the literal "pending"
    G8  record_ids are unique and `retired_at` parses as ISO date
    G9  every unknown carries a non-empty question and a known status;
        a `resolved` unknown must state its resolution, so the cycle
        cannot be closed by assertion alone

Run directly to validate:  python legacy/ledger.py

Dependencies: stdlib only.
License: CC0 1.0 Universal.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

LEDGER_PATH = Path(__file__).resolve().parent / "LEDGER.jsonl"
REPO_ROOT = Path(__file__).resolve().parent.parent

#: Retirement verdicts. These are epistemically distinct, not stylistic
#: variants -- the verdict determines what a future reader owes the
#: retired artifact.
VERDICTS = {
    # A better implementation of the same claim replaced it. The claim
    # stands; only the code was retired.
    "SUPERSEDED",
    # Its distinctive contribution was merged into another module. The
    # precedence is the origin of that feature.
    "ABSORBED",
    # The *claim itself* changed. The old framing is the fallback
    # position if the successor's framing is falsified. This is the
    # verdict that carries the most weight.
    "REFRAMED",
    # Content was promoted out of a container that was then dropped.
    "EXTRACTED",
    # Address changed, content did not. No epistemic event.
    "RELOCATED",
    # No content, therefore no precedence. Recorded so the deletion is
    # not mistaken for a lost artifact.
    "DISCARDED",
}

REQUIRED_FIELDS = (
    "record_id",
    "artifact",
    "retained_at",
    "retired_at",
    "retired_in",
    "verdict",
    "hypothesis",
    "run",
    "result",
    "successor",
    "precedence",
    "unknowns_surfaced",
    "rerun",
    "reversible",
)

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

#: An unknown is `open` until a rerun answers it. Resolving one requires
#: stating *how* it was answered -- see gate G9.
UNKNOWN_STATUSES = {"open", "resolved"}


@dataclass
class Unknown:
    """A question a retirement surfaced but did not answer.

    This is the "search for unknowns" step of the falsification cycle
    made durable. An unknown that is never written down is
    indistinguishable from one that was never noticed.
    """

    question: str
    status: str = "open"
    resolution: Optional[str] = None
    resolved_at: Optional[str] = None

    @classmethod
    def from_any(cls, data: Any) -> "Unknown":
        """Accept either a bare question string or the full object."""
        if isinstance(data, str):
            return cls(question=data)
        return cls(
            question=data.get("question", ""),
            status=data.get("status", "open"),
            resolution=data.get("resolution"),
            resolved_at=data.get("resolved_at"),
        )

    @property
    def is_open(self) -> bool:
        return self.status == "open"


@dataclass
class LedgerRecord:
    """One retirement. Field names mirror the JSONL keys exactly."""

    record_id: str
    artifact: str
    retained_at: Optional[str]
    retired_at: str
    retired_in: str
    verdict: str
    hypothesis: str
    run: str
    result: str
    successor: List[str]
    precedence: str
    unknowns_surfaced: List[Unknown]
    rerun: str
    reversible: bool
    also_retired: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerRecord":
        missing = [k for k in REQUIRED_FIELDS if k not in data]
        if missing:
            raise ValueError(
                f"record {data.get('record_id', '<no id>')} missing "
                f"required field(s): {', '.join(missing)}"
            )
        payload = {
            k: data[k] for k in REQUIRED_FIELDS + ("also_retired",) if k in data
        }
        payload["unknowns_surfaced"] = [
            Unknown.from_any(u) for u in data["unknowns_surfaced"]
        ]
        return cls(**payload)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"record_id": self.record_id, "artifact": self.artifact}
        out["also_retired"] = self.also_retired
        for key in REQUIRED_FIELDS:
            if key not in out:
                out[key] = getattr(self, key)
        out["unknowns_surfaced"] = [
            {
                "question": u.question,
                "status": u.status,
                "resolution": u.resolution,
                "resolved_at": u.resolved_at,
            }
            for u in self.unknowns_surfaced
        ]
        return out

    @property
    def is_retained(self) -> bool:
        """True if the artifact's bytes live under legacy/ in this repo."""
        return self.retained_at is not None


def load(path: Path = LEDGER_PATH) -> List[LedgerRecord]:
    """Parse LEDGER.jsonl into records. Blank lines are skipped."""
    records: List[LedgerRecord] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{lineno}: bad JSON: {exc}") from exc
            records.append(LedgerRecord.from_dict(payload))
    return records


def by_verdict(records: List[LedgerRecord], verdict: str) -> List[LedgerRecord]:
    return [r for r in records if r.verdict == verdict]


def unknowns(
    records: List[LedgerRecord], status: Optional[str] = None
) -> Iterator[tuple]:
    """Yield (record_id, Unknown) across all records.

    These are the "search for unknowns" output of the falsification
    cycle: questions each retirement raised. Pass `status="open"` for
    the live work queue, `status="resolved"` for the answered ones.
    Enumerating them is the point of keeping the ledger.
    """
    for record in records:
        for unknown in record.unknowns_surfaced:
            if status is None or unknown.status == status:
                yield record.record_id, unknown


def validate(records: List[LedgerRecord], repo_root: Path = REPO_ROOT) -> List[str]:
    """Return a list of gate failures. Empty list means the trail holds."""
    failures: List[str] = []
    seen_ids: Dict[str, int] = {}

    for record in records:
        rid = record.record_id

        # G8 -- unique ids, parseable dates
        seen_ids[rid] = seen_ids.get(rid, 0) + 1
        try:
            _dt.date.fromisoformat(record.retired_at)
        except ValueError:
            failures.append(f"{rid}: retired_at {record.retired_at!r} is not an ISO date")

        # G2 -- known verdict
        if record.verdict not in VERDICTS:
            failures.append(
                f"{rid}: verdict {record.verdict!r} not in {sorted(VERDICTS)}"
            )

        # G3 -- retained artifacts must actually be here
        if record.retained_at is not None:
            if not record.retained_at.startswith("legacy/"):
                failures.append(
                    f"{rid}: retained_at {record.retained_at!r} is not under legacy/"
                )
            elif not (repo_root / record.retained_at).is_file():
                failures.append(
                    f"{rid}: retained_at {record.retained_at!r} does not exist"
                )

        # G4 -- successors must exist, or the trail dead-ends
        for succ in record.successor:
            if not (repo_root / succ).exists():
                failures.append(
                    f"{rid}: successor {succ!r} does not exist in the working tree"
                )

        # G5 -- only DISCARDED may dead-end deliberately
        if not record.successor and record.verdict != "DISCARDED":
            failures.append(
                f"{rid}: verdict {record.verdict} requires at least one successor"
            )

        # G6 -- precedence is the load-bearing field
        if not str(record.precedence).strip():
            failures.append(f"{rid}: precedence is empty")

        # G7 -- resolvable commit reference
        if record.retired_in != "pending" and not _SHA_RE.match(record.retired_in):
            failures.append(
                f"{rid}: retired_in {record.retired_in!r} is neither a 40-hex sha "
                f"nor 'pending'"
            )

        # G9 -- an unknown cannot be closed by assertion
        for idx, unknown in enumerate(record.unknowns_surfaced):
            if not unknown.question.strip():
                failures.append(f"{rid}: unknown #{idx} has an empty question")
            if unknown.status not in UNKNOWN_STATUSES:
                failures.append(
                    f"{rid}: unknown #{idx} status {unknown.status!r} not in "
                    f"{sorted(UNKNOWN_STATUSES)}"
                )
            if unknown.status == "resolved" and not (unknown.resolution or "").strip():
                failures.append(
                    f"{rid}: unknown #{idx} is marked resolved but states no "
                    f"resolution"
                )

    for rid, count in seen_ids.items():
        if count > 1:
            failures.append(f"{rid}: duplicate record_id ({count} occurrences)")

    return failures


def _report(records: List[LedgerRecord]) -> None:
    print(f"legacy ledger: {len(records)} retirement record(s)\n")
    for verdict in sorted(VERDICTS):
        hits = by_verdict(records, verdict)
        if hits:
            ids = ", ".join(r.record_id for r in hits)
            print(f"  {verdict:<12} {len(hits):>2}   {ids}")

    retained = [r for r in records if r.is_retained]
    print(f"\n  retained in-tree: {len(retained)}/{len(records)}")

    still_open = list(unknowns(records, status="open"))
    resolved = list(unknowns(records, status="resolved"))
    print(f"  unknowns:         {len(still_open)} open / {len(resolved)} resolved")

    if still_open:
        print("\n  OPEN -- the work queue this ledger exists to keep visible:")
        for rid, unknown in still_open:
            print(f"    [{rid}] {unknown.question}")
    if resolved:
        print("\n  RESOLVED:")
        for rid, unknown in resolved:
            print(f"    [{rid}] {unknown.question}")
            print(f"           -> {unknown.resolution}")


def main() -> int:
    records = load()
    _report(records)
    failures = validate(records)
    print()
    if failures:
        print(f"FAIL: {len(failures)} broken link(s) in the audit trail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASS: every retirement resolves to an existing successor "
          "and every retained artifact is present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
