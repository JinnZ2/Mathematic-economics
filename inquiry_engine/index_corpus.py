#!/usr/bin/env python3
"""
index_corpus.py – Crawl repositories and build a unified claim index.
CC0. Stdlib only.

Looks for CLAIM_TABLE.json, CLAIM_TABLE.fab.json, and equations.yaml
in every subdirectory of a given root, then assembles a unified claims
catalog and a contradictions report.

Usage:
  python inquiry_engine/index_corpus.py --root ~/repos --output unified_claims.json
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

def find_claim_files(root: str) -> List[str]:
    """Walk the root directory and find all claim-related files."""
    claim_files = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if fname in ("CLAIM_TABLE.json", "CLAIM_TABLE.fab.json"):
                claim_files.append(os.path.join(dirpath, fname))
    return claim_files

def load_claims(filepath: str) -> List[Dict[str, Any]]:
    """Load claims from a JSON file, handling both list and dict formats."""
    with open(filepath, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Some claim tables are dicts with claim IDs as keys
        return [{"id": k, **v} for k, v in data.items()]
    return []

def extract_claims_from_yaml(filepath: str) -> List[Dict[str, Any]]:
    """Extract claim references from equations.yaml (simple parser)."""
    # Since we can't rely on a YAML parser, we'll do a basic text extraction
    claims = []
    with open(filepath, "r") as f:
        lines = f.readlines()
    current_claim = None
    for line in lines:
        line = line.strip()
        if line.startswith("C") and ":" in line:
            # Crude extraction of claim ID and maybe description
            cid = line.split(":")[0].strip()
            claims.append({"id": cid, "source": filepath})
    return claims

def build_index(root: str) -> Dict[str, Any]:
    claim_files = find_claim_files(root)
    all_claims = []
    for cf in claim_files:
        try:
            claims = load_claims(cf)
            all_claims.extend(claims)
            print(f"  Loaded {len(claims)} claims from {cf}")
        except Exception as e:
            print(f"  Skipped {cf}: {e}")

    # Index by claim ID
    index = defaultdict(list)
    for claim in all_claims:
        cid = claim.get("id", claim.get("claim_id", "unknown"))
        index[cid].append(claim)

    # Detect possible contradictions: claims with the same ID but different statuses
    contradictions = []
    for cid, entries in index.items():
        if len(entries) > 1:
            statuses = {e.get("status", e.get("state", "")) for e in entries}
            if len(statuses) > 1:
                contradictions.append({
                    "claim_id": cid,
                    "statuses": list(statuses),
                    "sources": [e.get("source", "unknown") for e in entries],
                })

    unified = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_directory": root,
        "total_claims_unique": len(index),
        "total_claim_files": len(claim_files),
        "contradictions": contradictions,
        "claims": {cid: entries for cid, entries in index.items()},
    }
    return unified

def main():
    parser = argparse.ArgumentParser(description="Cross-repo claim indexer.")
    parser.add_argument("--root", required=True, help="Root directory containing repos")
    parser.add_argument("--output", default="unified_claims.json", help="Output JSON file")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"Error: {args.root} is not a directory.")
        return

    print(f"Crawling {args.root} for claim files...")
    index = build_index(args.root)
    with open(args.output, "w") as f:
        json.dump(index, f, indent=2)
    print(f"\nUnified index written to {args.output}")
    if index["contradictions"]:
        print(f"\n⚠️  Contradictions detected ({len(index['contradictions'])}):")
        for c in index["contradictions"]:
            print(f"  {c['claim_id']}: statuses {c['statuses']} across sources {c['sources']}")
    else:
        print("No contradictions detected.")

if __name__ == "__main__":
    main()
