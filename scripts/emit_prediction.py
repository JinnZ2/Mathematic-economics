#!/usr/bin/env python3
"""
emit_prediction.py — append an entry to predictions_registry.jsonl

Implements the schema in PREDICTION_PROTOCOL.md with HMAC chaining
(prev_hash + chain_hash) so any retroactive tampering is detectable.

Usage:
    python scripts/emit_prediction.py \\
      --domain autonomous_trucking_roi \\
      --claim "POR < 0.5 by 2028 in Permian deployment" \\
      --probability 0.78 \\
      --interval-low 0.65 --interval-high 0.88 \\
      --evidence "C056 default POR ~0.33" \\
      --falsifier "audited POR > 0.5 sustained 12mo" \\
      --window P3Y

Idempotency: each call produces a new monotonic prediction_id; the
script does not deduplicate (a re-emitted prediction is a new entry,
not an overwrite).

License: CC0 1.0 Universal.
"""

import argparse
import datetime as _dt
import hashlib
import hmac
import json
import os
import sys
import uuid
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parent.parent / "predictions_registry.jsonl"
DEFAULT_SECRET = "JinnZ2-prediction-registry-2026"
GENESIS_PREV_HASH = "0" * 64


def _hmac(secret: bytes, payload: str) -> str:
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _canonical_for_chain(entry: dict) -> str:
    """Canonical form for chain hashing: payload minus chain-prefix fields.

    Must match compute_calibration._canonical_for_chain exactly so the
    chain verifier reproduces the same hash.
    """
    e = {k: v for k, v in entry.items() if k not in ("prev_hash", "chain_hash")}
    return json.dumps(e, sort_keys=True, default=str, separators=(",", ":"))


def _last_chain_hash(path: Path) -> str:
    if not path.exists():
        return GENESIS_PREV_HASH
    last = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                last = line
    if not last:
        return GENESIS_PREV_HASH
    try:
        return json.loads(last)["chain_hash"]
    except Exception:
        return GENESIS_PREV_HASH


def emit(domain: str, claim: str, probability: float,
         interval_low: float, interval_high: float,
         evidence: list, falsifier: str, window: str,
         model_id: str, prediction_id: str | None = None,
         secret: str = DEFAULT_SECRET,
         path: Path = REGISTRY_PATH) -> dict:
    secret_b = secret.encode("utf-8")
    pid = prediction_id or f"P-{uuid.uuid4().hex[:12]}"
    payload = {
        "prediction_id":          pid,
        "timestamp":              _dt.datetime.utcnow().isoformat() + "Z",
        "model_id":               model_id,
        "domain":                 domain,
        "claim":                  claim,
        "probability_estimate":   round(float(probability), 4),
        "confidence_interval":    [round(float(interval_low), 4),
                                    round(float(interval_high), 4)],
        "evidence_basis":         evidence,
        "falsification_criteria": falsifier,
        "expected_outcome_window": window,
        "human_override": {
            "occurred":   False,
            "reasoning":  "",
            "decision":   "",
        },
        "actual_outcome":      "pending",
        "accuracy_assessment": "pending",
    }
    prev_hash = _last_chain_hash(path)
    payload["prev_hash"] = prev_hash
    payload["chain_hash"] = _hmac(secret_b,
                                    prev_hash + _canonical_for_chain(payload))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(payload) + "\n")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--claim", required=True)
    ap.add_argument("--probability", type=float, required=True)
    ap.add_argument("--interval-low", type=float, required=True)
    ap.add_argument("--interval-high", type=float, required=True)
    ap.add_argument("--evidence", action="append", default=[],
                    help="repeat for multiple evidence items")
    ap.add_argument("--falsifier", required=True)
    ap.add_argument("--window", required=True,
                    help="ISO-8601 duration, e.g. P3Y, P30D")
    ap.add_argument("--model-id",
                    default=os.environ.get("MODEL_ID", "unknown-model"))
    ap.add_argument("--prediction-id", default=None,
                    help="override auto-generated UUID")
    ap.add_argument("--secret",
                    default=os.environ.get("LEDGER_SECRET", DEFAULT_SECRET))
    ap.add_argument("--path", default=str(REGISTRY_PATH),
                    help="override registry file path")
    args = ap.parse_args()

    entry = emit(args.domain, args.claim, args.probability,
                  args.interval_low, args.interval_high,
                  args.evidence or ["unattested"], args.falsifier,
                  args.window, args.model_id,
                  prediction_id=args.prediction_id,
                  secret=args.secret,
                  path=Path(args.path))
    print(json.dumps(entry, indent=2))
    print(f"\nappended to {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
