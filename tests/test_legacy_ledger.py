#!/usr/bin/env python3
"""Falsification tests for legacy/ledger.py.

The ledger's job is to keep the retirement trail honest. A validator
that cannot fail is decoration, so most of these tests assert that a
gate *bites* on a deliberately broken record -- not merely that the
real ledger passes.

Run: python tests/test_legacy_ledger.py

License: CC0 1.0 Universal.
"""

import copy
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for path in (ROOT, os.path.join(ROOT, "legacy")):
    if path not in sys.path:
        sys.path.insert(0, path)

from ledger import (  # noqa: E402
    LEDGER_PATH,
    UNKNOWN_STATUSES,
    VERDICTS,
    LedgerRecord,
    Unknown,
    by_verdict,
    load,
    unknowns,
    validate,
)


def _template():
    """A minimal record that passes every gate, for mutation."""
    return {
        "record_id": "T001",
        "artifact": "some/old/path.py",
        "also_retired": [],
        "retained_at": "legacy/ledger.py",
        "retired_at": "2026-01-01",
        "retired_in": "0" * 40,
        "verdict": "SUPERSEDED",
        "hypothesis": "h",
        "run": "r",
        "result": "res",
        "successor": ["legacy/README.md"],
        "precedence": "what still carries",
        "unknowns_surfaced": [],
        "rerun": "true",
        "reversible": True,
    }


def _fails(mutate=None):
    data = _template()
    if mutate:
        mutate(data)
    return validate([LedgerRecord.from_dict(data)])


class GateBitesTests(unittest.TestCase):
    """Each gate must reject the input it exists to reject."""

    def test_template_itself_is_clean(self):
        # Guards the other tests: if the template failed, they would
        # pass for the wrong reason.
        self.assertEqual(_fails(), [])

    def test_g2_unknown_verdict_rejected(self):
        out = _fails(lambda d: d.update(verdict="DELETED"))
        self.assertTrue(any("verdict" in f for f in out), out)

    def test_g3_retained_artifact_must_exist(self):
        out = _fails(lambda d: d.update(retained_at="legacy/does_not_exist.py"))
        self.assertTrue(any("does not exist" in f for f in out), out)

    def test_g3_retained_artifact_must_be_under_legacy(self):
        out = _fails(lambda d: d.update(retained_at="audit/field_system.py"))
        self.assertTrue(any("not under legacy/" in f for f in out), out)

    def test_g4_vanished_successor_breaks_the_trail(self):
        # The load-bearing check: retiring a file whose successor was
        # later deleted leaves a dangling pointer, and that must fail.
        out = _fails(lambda d: d.update(successor=["gone/module.py"]))
        self.assertTrue(any("does not exist in the working tree" in f for f in out), out)

    def test_g5_only_discarded_may_have_no_successor(self):
        out = _fails(lambda d: d.update(successor=[]))
        self.assertTrue(any("requires at least one successor" in f for f in out), out)

    def test_g5_discarded_may_have_no_successor(self):
        self.assertEqual(
            _fails(lambda d: d.update(successor=[], verdict="DISCARDED")), []
        )

    def test_g6_empty_precedence_rejected(self):
        # A record that cannot say what carries forward is a deletion
        # with extra steps.
        out = _fails(lambda d: d.update(precedence="   "))
        self.assertTrue(any("precedence is empty" in f for f in out), out)

    def test_g7_malformed_commit_ref_rejected(self):
        out = _fails(lambda d: d.update(retired_in="abc123"))
        self.assertTrue(any("40-hex sha" in f for f in out), out)

    def test_g7_pending_is_allowed(self):
        self.assertEqual(_fails(lambda d: d.update(retired_in="pending")), [])

    def test_g8_bad_date_rejected(self):
        out = _fails(lambda d: d.update(retired_at="yesterday"))
        self.assertTrue(any("ISO date" in f for f in out), out)

    def test_g8_duplicate_record_ids_rejected(self):
        rec = LedgerRecord.from_dict(_template())
        out = validate([rec, copy.deepcopy(rec)])
        self.assertTrue(any("duplicate record_id" in f for f in out), out)

    def test_g9_resolved_unknown_needs_a_resolution(self):
        # The cycle cannot be closed by assertion.
        out = _fails(
            lambda d: d.update(
                unknowns_surfaced=[
                    {"question": "q", "status": "resolved", "resolution": ""}
                ]
            )
        )
        self.assertTrue(any("states no resolution" in f for f in out), out)

    def test_g9_unknown_status_rejected(self):
        out = _fails(
            lambda d: d.update(unknowns_surfaced=[{"question": "q", "status": "maybe"}])
        )
        self.assertTrue(any("status" in f for f in out), out)

    def test_g9_empty_question_rejected(self):
        out = _fails(lambda d: d.update(unknowns_surfaced=[{"question": "  "}]))
        self.assertTrue(any("empty question" in f for f in out), out)

    def test_g1_missing_required_field_raises(self):
        data = _template()
        del data["precedence"]
        with self.assertRaises(ValueError):
            LedgerRecord.from_dict(data)


class UnknownShapeTests(unittest.TestCase):
    def test_bare_string_is_accepted_as_an_open_unknown(self):
        unknown = Unknown.from_any("just a question")
        self.assertEqual(unknown.question, "just a question")
        self.assertTrue(unknown.is_open)

    def test_object_form_round_trips(self):
        unknown = Unknown.from_any(
            {
                "question": "q",
                "status": "resolved",
                "resolution": "because X",
                "resolved_at": "2026-08-14",
            }
        )
        self.assertFalse(unknown.is_open)
        self.assertEqual(unknown.resolution, "because X")

    def test_record_to_dict_round_trips_through_from_dict(self):
        original = LedgerRecord.from_dict(_template())
        again = LedgerRecord.from_dict(original.to_dict())
        self.assertEqual(original.to_dict(), again.to_dict())


class RealLedgerTests(unittest.TestCase):
    """The shipped ledger must actually hold."""

    @classmethod
    def setUpClass(cls):
        cls.records = load()

    def test_ledger_file_exists_and_parses(self):
        self.assertTrue(LEDGER_PATH.is_file())
        self.assertGreater(len(self.records), 0)

    def test_shipped_ledger_passes_every_gate(self):
        self.assertEqual(validate(self.records), [])

    def test_every_verdict_is_declared(self):
        for record in self.records:
            self.assertIn(record.verdict, VERDICTS, record.record_id)

    def test_every_unknown_status_is_declared(self):
        for record in self.records:
            for unknown in record.unknowns_surfaced:
                self.assertIn(unknown.status, UNKNOWN_STATUSES, record.record_id)

    def test_reframed_records_state_a_fallback(self):
        # REFRAMED is the verdict that changes what the framework
        # asserts, so its precedence has to be substantive rather than
        # a restatement of the path.
        reframed = by_verdict(self.records, "REFRAMED")
        self.assertTrue(reframed, "expected at least one REFRAMED record")
        for record in reframed:
            self.assertGreater(len(record.precedence), 80, record.record_id)

    def test_retained_flag_matches_disk(self):
        for record in self.records:
            if record.is_retained:
                self.assertTrue(
                    os.path.isfile(os.path.join(ROOT, record.retained_at)),
                    record.record_id,
                )

    def test_open_and_resolved_partition_all_unknowns(self):
        total = len(list(unknowns(self.records)))
        split = len(list(unknowns(self.records, status="open"))) + len(
            list(unknowns(self.records, status="resolved"))
        )
        self.assertEqual(total, split)

    def test_legacy_tree_has_no_package_marker(self):
        # legacy/ is frozen and deliberately not importable as a
        # package; an __init__.py would invite live code to depend on it.
        for dirpath, _, filenames in os.walk(os.path.join(ROOT, "legacy")):
            self.assertNotIn("__init__.py", filenames, dirpath)


if __name__ == "__main__":
    unittest.main(verbosity=2)
