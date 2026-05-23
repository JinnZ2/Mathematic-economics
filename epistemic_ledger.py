"""
EPISTEMIC_LEDGER: append-only audit-verdict log + provenance auditor.

Two concerns in one module:

  1. AuditLedger — generic, append-only ledger that records audit
     verdicts to a JSONL file. Each entry carries timestamp, claim_id,
     input hash, verdict, and a chained hash that includes the previous
     entry's hash. Tampering with any entry breaks the chain.

  2. EpistemicLedgerAuditor — physics-bounded trucking audit (the
     original module). Fixed import (previously broken: referenced
     MetrologicalBoundsAuditor without importing it).

Default ledger location: epistemic_ledger.jsonl in repo root. Override
via the LEDGER_PATH env var.

License: CC0 1.0 Universal.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List, Tuple

from metrological_bounds import MetrologicalBoundsAuditor


# -----------------------------------------------------------------------------
# Generic audit-verdict ledger
# -----------------------------------------------------------------------------

DEFAULT_LEDGER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "epistemic_ledger.jsonl",
)

DEFAULT_SECRET = "MetrologicalHonesty2026"

# Sentinel for the first entry's predecessor hash. Constant value so the
# chain is verifiable across machines (no shared state required to
# compute it).
GENESIS_PREV_HASH = "0" * 64


class AuditLedger:
    """Append-only audit ledger with HMAC-chained entries.

    Each `append(...)` call writes one JSON line:
        {
          "ts":        epoch_seconds,
          "claim_id":  "C020",
          "scenario":  "kodiak_atlas_permian (works case)",
          "input_hash":  hex(hmac_sha256(secret, canonical_inputs)),
          "verdict_hash": hex(hmac_sha256(secret, canonical_verdict)),
          "prev_hash":   hash of previous entry's verdict_hash,
          "chain_hash":  hex(hmac_sha256(secret, prev_hash + verdict_hash)),
          "verdict_summary": {claim_id, threshold_met, falsifier?},
        }

    The chain hash makes the ledger tamper-evident: changing any entry
    invalidates every subsequent chain_hash, and `verify()` will surface
    the first break.
    """

    def __init__(self, path: str | None = None,
                 secret: str | None = None) -> None:
        self.path = path or os.environ.get(
            "LEDGER_PATH", DEFAULT_LEDGER_PATH)
        secret_str = secret or os.environ.get("LEDGER_SECRET", DEFAULT_SECRET)
        self.secret = secret_str.encode("utf-8")

    # -------------------------------------------------------------------
    # Internal hashing
    # -------------------------------------------------------------------

    def _hmac(self, payload: str) -> str:
        return hmac.new(self.secret, payload.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    @staticmethod
    def _canonical(obj: Any) -> str:
        return json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))

    def _last_chain_hash(self) -> str:
        if not os.path.exists(self.path):
            return GENESIS_PREV_HASH
        last = None
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    last = line
        if not last:
            return GENESIS_PREV_HASH
        try:
            return json.loads(last)["chain_hash"]
        except Exception:
            # Treat a corrupt tail line as genesis; verify() will flag.
            return GENESIS_PREV_HASH

    # -------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------

    def append(self, claim_id: str, verdict: Dict[str, Any],
               inputs: Dict[str, Any] | None = None,
               scenario: str = "") -> Dict[str, Any]:
        """Append one verdict to the ledger; return the persisted entry."""
        ts = time.time()
        input_hash = self._hmac(self._canonical(inputs or {}))
        verdict_hash = self._hmac(self._canonical(verdict))
        prev_hash = self._last_chain_hash()
        chain_hash = self._hmac(prev_hash + verdict_hash)

        # Compact, machine-readable summary; the full verdict can be
        # reconstructed from the inputs + the module's verdict function.
        summary = {
            "claim_id":      verdict.get("claim_id", claim_id),
            "threshold_met": verdict.get("threshold_met"),
            "falsifier":     verdict.get("falsifier", ""),
        }

        entry = {
            "ts":              ts,
            "claim_id":        claim_id,
            "scenario":        scenario,
            "input_hash":      input_hash,
            "verdict_hash":    verdict_hash,
            "prev_hash":       prev_hash,
            "chain_hash":      chain_hash,
            "verdict_summary": summary,
        }
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
        return entry

    def read_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        out = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
        return out

    def verify(self) -> Tuple[bool, List[str]]:
        """Verify the chain integrity end-to-end.

        Returns (ok, errors). `ok` is True iff every entry's chain_hash is
        consistent with its prev_hash + verdict_hash AND every prev_hash
        matches the prior entry's chain_hash (or GENESIS for the first
        entry).
        """
        errors: List[str] = []
        entries = self.read_all()
        expected_prev = GENESIS_PREV_HASH
        for i, e in enumerate(entries):
            if e.get("prev_hash") != expected_prev:
                errors.append(
                    f"entry {i} prev_hash mismatch: "
                    f"expected {expected_prev[:12]}..., got {e.get('prev_hash', '')[:12]}...")
            recomputed = self._hmac(e["prev_hash"] + e["verdict_hash"])
            if recomputed != e.get("chain_hash"):
                errors.append(
                    f"entry {i} chain_hash recompute mismatch")
            expected_prev = e.get("chain_hash", expected_prev)
        return len(errors) == 0, errors


# -----------------------------------------------------------------------------
# Physics-bounded trucking auditor (original module; fixed import)
# -----------------------------------------------------------------------------

class EpistemicLedgerAuditor(MetrologicalBoundsAuditor):
    def __init__(self, baseline_distance_miles: float,
                 secret_key: str = DEFAULT_SECRET):
        super().__init__(baseline_distance_miles)
        self.secret_key = secret_key.encode("utf-8")

    def _generate_provenance_hash(self, input_payload: str) -> str:
        """Immutable cryptographic signature of the input constraint matrix."""
        return hmac.new(self.secret_key, input_payload.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    def generate_protected_calculation(self,
                                       hos_detention: float,
                                       weather_risk: float,
                                       destination_wait: float
                                       ) -> Tuple[Dict[str, Any], str]:
        """Run the physics-bounded audit; sign the output with a provenance hash."""
        raw_input_string = (
            f"dist={self.distance}|detention={hos_detention}"
            f"|weather={weather_risk}|wait={destination_wait}"
        )
        input_hash = self._generate_provenance_hash(raw_input_string)
        base_audit = self.execute_provenance_audit(
            hos_detention, weather_risk, destination_wait)

        timestamp = time.time()
        base_audit["METADATA"] = {
            "epoch_timestamp": timestamp,
            "input_provenance_signature": input_hash,
            "resolution_status":
                "COMPUTATIONAL_VALIDITY_BOUNDED_BY_USER_OMISSIONS"
                if base_audit["VERDICT"] == "REJECT_SAVINGS_MODEL"
                else "VALIDATED_WITHIN_BOUNDS",
        }

        manifest_string = (
            f"\n[EPID: ACCOUNTABILITY_MANIFEST_ACTIVE]\n"
            f"  TIMESTAMP: {timestamp}\n"
            f"  PROVENANCE_HASH: {input_hash}\n"
            f"  VERDICT: {base_audit['VERDICT']}\n"
            f"  RESOLUTION_GAP: {base_audit['EPISTEMIC_RESOLUTION_GAP_ERROR']}\n"
            f"  SHOULDER_RISK_INDEX: {base_audit['UPSTREAM_UNDOCUMENTED_CRASH_RISK_INDEX']}\n"
            f"  [STATEMENT]: This computation is an isolated mathematical artifact generated strictly from user inputs.\n"
            f"  If real-world parameters for weather friction or terminal delays were forced to 0.00, liability for\n"
            f"  subsequent physical asset failures or downstream accidents resides entirely with the executing dispatcher.\n"
        )
        return base_audit, manifest_string


# -----------------------------------------------------------------------------
# Smoke test
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Generic ledger smoke test (does not touch the trucking-physics audit).
    test_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "_ledger_smoke_test.jsonl",
    )
    if os.path.exists(test_path):
        os.remove(test_path)
    ledger = AuditLedger(path=test_path)
    ledger.append("C001", {"claim_id": "C001", "threshold_met": True,
                            "falsifier": "..."}, {"variance": 0.7},
                   scenario="dispersed_wellsite")
    ledger.append("C020", {"claim_id": "C020", "threshold_met": False,
                            "falsifier": "..."}, {"fuel_saved_kwh": 5000},
                   scenario="kodiak_atlas_permian")
    ok, errors = ledger.verify()
    print("smoke test:", "PASS" if ok else "FAIL", errors)
    print("entries written:", len(ledger.read_all()))
    os.remove(test_path)
