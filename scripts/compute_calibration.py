#!/usr/bin/env python3
"""
compute_calibration.py — read predictions_registry.jsonl, produce attestation

Walks the HMAC chain (per PREDICTION_PROTOCOL.md), verifies integrity,
and computes per-domain accuracy + calibration score (expected
calibration error). Optionally writes the attestation to
prediction_attestation.json.

Output schema matches PREDICTION_PROTOCOL.md "Schema for accuracy
attestation". Per-domain accuracy is computed independently; no
aggregate scores across domains (Layer 4: domain specificity).

Usage:
    python scripts/compute_calibration.py
    python scripts/compute_calibration.py --write-attestation

License: CC0 1.0 Universal.
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
from collections import defaultdict
from pathlib import Path


REGISTRY_PATH = Path(__file__).resolve().parent.parent / "predictions_registry.jsonl"
ATTESTATION_PATH = Path(__file__).resolve().parent.parent / "prediction_attestation.json"
DEFAULT_SECRET = "JinnZ2-prediction-registry-2026"
GENESIS_PREV_HASH = "0" * 64


def _hmac(secret: bytes, payload: str) -> str:
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _canonical_for_chain(entry: dict) -> str:
    e = {k: v for k, v in entry.items() if k not in ("prev_hash", "chain_hash")}
    return json.dumps(e, sort_keys=True, default=str, separators=(",", ":"))


def load_entries(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def verify_chain(entries: list, secret: str = DEFAULT_SECRET) -> tuple:
    """Walk the chain end-to-end. Returns (ok, errors)."""
    s = secret.encode("utf-8")
    errors = []
    expected_prev = GENESIS_PREV_HASH
    for i, e in enumerate(entries):
        prev = e.get("prev_hash")
        if prev != expected_prev:
            errors.append(f"entry {i} prev_hash mismatch: "
                          f"expected {expected_prev[:12]}, got {(prev or '')[:12]}")
        # Recompute the chain_hash
        recomputed = _hmac(s, (prev or "") + _canonical_for_chain(e))
        if recomputed != e.get("chain_hash"):
            errors.append(f"entry {i} chain_hash recompute mismatch "
                          f"(prediction_id={e.get('prediction_id')})")
        expected_prev = e.get("chain_hash", expected_prev)
    return len(errors) == 0, errors


def per_domain_accuracy(entries: list) -> dict:
    """Compute per-domain accuracy + calibration. Returns the
    attestation `domain_accuracy` map."""
    by_domain = defaultdict(lambda: {
        "total_predictions": 0,
        "correct":           0,
        "incorrect":         0,
        "partial":           0,
        "pending":           0,
        # Calibration tracking
        "_bin_counts":  defaultdict(lambda: [0, 0]),    # bin -> [n, n_correct]
    })
    for e in entries:
        d = e.get("domain", "unknown")
        b = by_domain[d]
        b["total_predictions"] += 1
        assessment = e.get("accuracy_assessment", "pending")
        if assessment in ("correct", "incorrect", "partial", "pending"):
            b[assessment] += 1
        else:
            b["pending"] += 1
        # Calibration bins (10 bins of width 0.1)
        if assessment in ("correct", "incorrect"):
            p = float(e.get("probability_estimate", 0.5))
            bin_idx = min(9, int(p * 10))
            b["_bin_counts"][bin_idx][0] += 1
            if assessment == "correct":
                b["_bin_counts"][bin_idx][1] += 1

    out = {}
    for d, b in by_domain.items():
        n = b["total_predictions"]
        decided = b["correct"] + b["incorrect"]
        # Expected calibration error (Naeini et al. 2015):
        # ECE = sum over bins of (|bin| / N) * |bin_acc - bin_conf|
        bins = b.pop("_bin_counts")
        ece_terms = []
        for bin_idx, (count, correct) in bins.items():
            if count == 0:
                continue
            bin_conf = (bin_idx + 0.5) / 10.0
            bin_acc = correct / count
            ece_terms.append((count / max(1, decided)) * abs(bin_acc - bin_conf))
        ece = sum(ece_terms) if ece_terms else 0.0
        out[d] = {
            "total_predictions": n,
            "correct":           b["correct"],
            "incorrect":         b["incorrect"],
            "partial":           b["partial"],
            "pending":           b["pending"],
            "decided":           decided,
            "accuracy":          b["correct"] / decided if decided else None,
            "expected_calibration_error": ece,
            "calibration_score": max(0.0, 1.0 - ece),
        }
    return out


def override_outcomes(entries: list) -> dict:
    counts = {
        "human_overrode_and_was_right": 0,
        "human_overrode_and_was_wrong": 0,
        "model_was_uncertain_and_correct": 0,
        "model_was_certain_and_correct":   0,
    }
    for e in entries:
        ho = e.get("human_override") or {}
        if ho.get("occurred"):
            assessment = e.get("accuracy_assessment", "pending")
            if assessment == "correct":
                # Model was right; human overrode -> human was wrong
                counts["human_overrode_and_was_wrong"] += 1
            elif assessment == "incorrect":
                # Model was wrong; human overrode -> human was right
                counts["human_overrode_and_was_right"] += 1
        else:
            # No override; just count model accuracy banded by confidence
            p = float(e.get("probability_estimate", 0.5))
            if e.get("accuracy_assessment") == "correct":
                if p >= 0.80:
                    counts["model_was_certain_and_correct"] += 1
                else:
                    counts["model_was_uncertain_and_correct"] += 1
    return counts


def compose_attestation(entries: list, model_id: str | None = None) -> dict:
    return {
        "model_id":         model_id or (entries[-1].get("model_id")
                                          if entries else "unknown"),
        "registry_size":    len(entries),
        "domain_accuracy":  per_domain_accuracy(entries),
        "override_outcomes": override_outcomes(entries),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", default=str(REGISTRY_PATH))
    ap.add_argument("--write-attestation", action="store_true",
                    help="write prediction_attestation.json alongside the registry")
    ap.add_argument("--secret", default=os.environ.get(
        "LEDGER_SECRET", DEFAULT_SECRET))
    args = ap.parse_args()

    entries = load_entries(Path(args.path))
    ok, errors = verify_chain(entries, args.secret)
    if not ok:
        print("CHAIN INTEGRITY: FAIL")
        for e in errors:
            print(f"  {e}")
    else:
        print(f"CHAIN INTEGRITY: OK ({len(entries)} entries)")

    attestation = compose_attestation(entries)
    print()
    print(json.dumps(attestation, indent=2))

    if args.write_attestation:
        with open(ATTESTATION_PATH, "w") as f:
            json.dump(attestation, f, indent=2)
        print(f"\nattestation written to {ATTESTATION_PATH}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
