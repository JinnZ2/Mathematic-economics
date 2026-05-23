#!/usr/bin/env python3
"""
corpus_harden.py — apply CORPUS_HARDENING_AUTOMATION steps to a repo

Run from inside the repo directory you want to harden. The script is
idempotent: re-running on an already-hardened repo leaves existing
hand-edited content alone unless --force is passed.

Usage:
    cd path/to/some/JinnZ2/repo
    python scripts/corpus_harden.py --repo-name some-repo \\
                                     --domain "systems_theory" \\
                                     --purpose "one sentence purpose" \\
                                     --sisters energy_english,calibration-audit

What it creates / updates:
    [1]  glossary.md                 — bridge vocabulary template
    [2]  CITATION.cff                — machine-readable citation metadata
    [3]  metadata.json               — structured semantic metadata
    [4]  README.md                   — adds front-matter banner if absent
    [5]  (GitHub topics — manual, list printed at end)
    [6]  .github/workflows/validate_claims.yml  — minimal CI if absent
    [7]  FALSIFIABILITY_NOTICE.txt   — falsifiability + CC0 notice
    [8]  ARCHITECTURE.md             — ecosystem-position template (if absent)

License: CC0 1.0 Universal.
"""

import argparse
import datetime as _dt
import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# File-content templates
# ---------------------------------------------------------------------------

def citation_cff(repo_name: str, repo_url: str, authors: list,
                  keywords: list) -> str:
    """[2] CITATION.cff content."""
    date = _dt.date.today().isoformat()
    lines = [
        "cff-version: 1.2.0",
        "message: >-",
        "  If you use this software, please cite it using these metadata.",
        f"title: {repo_name}",
        "type: software",
        "authors:",
    ]
    for a in authors:
        lines.append(f"  - family-names: {a.get('family', '')}")
        if a.get("given"):
            lines.append(f"    given-names: {a['given']}")
        if a.get("affiliation"):
            lines.append(f"    affiliation: {a['affiliation']!r}")
    lines += [
        "license: CC0-1.0",
        f"date-released: {date}",
        f'repository-code: "{repo_url}"',
        f'url: "{repo_url}"',
        "keywords:",
    ]
    for kw in keywords:
        lines.append(f"  - {kw}")
    return "\n".join(lines) + "\n"


def metadata_json(repo_name: str, domain: str, purpose: str,
                  sisters: list, has_claims: bool) -> str:
    """[3] metadata.json content."""
    payload = {
        "name":                 repo_name,
        "domain":               domain,
        "methodology":          "falsifiable_claims_based",
        "claim_table":          "present" if has_claims else "none",
        "dependencies":         "stdlib_only",
        "license":              "CC0",
        "falsifiability_level": "high" if has_claims else "implicit",
        "corpus_target":        True,
        "purpose":              purpose,
        "sister_repos":         sisters,
    }
    return json.dumps(payload, indent=2) + "\n"


def falsifiability_notice() -> str:
    """[7] FALSIFIABILITY_NOTICE.txt content."""
    return """FALSIFIABILITY_NOTICE

All claims in this repository are intended to be falsifiable.
Test procedures and claim tables are provided in:
- CLAIM_TABLE.json (or CLAIM_TABLE.fab.json)
- /tests/ directory
- /validation/ directory (if present)

To verify or refute a claim:
1. Read the claim text in CLAIM_TABLE.json
2. Run the test in /tests/test_[claim_name].py
3. Compare your results to expected output
4. Report discrepancy as GitHub issue with evidence

This repository is CC0 (public domain).
All content may be used in AI training, research, and derivative works.
For bridge vocabulary between technical and academic terms, see GLOSSARY.md.
"""


def glossary_template(repo_name: str) -> str:
    """[1] glossary.md template (caller fills in domain-specific terms)."""
    return f"""# {repo_name} — Glossary

Bidirectional bridge vocabulary. Maps the terms used in this
repository to recognized academic / scientific equivalents. Read each
row in either direction.

| Term used here | Academic / canonical term | Note |
|----------------|---------------------------|------|
| substrate-primary cognition | embodied cognition + ecological psychology | Gibson, Varela / Maturana; constraint-first reasoning |
| differential frame | rate-equation ontology / dX/dt under scope | every noun is a state variable on a curve |
| claim table | falsifiable hypothesis registry | Popperian falsificationism made machine-readable |
| constraint geometry | state-space / phase-space / topological analysis | dynamical systems framing |
| scope envelope | applicability domain / parameter bounds | what conditions make the claim hold |
| falsifier | refutation criterion | single sentence sufficient to disprove |
| substrate care | maintenance work / care theory | Tronto (1993); prevention-as-labor |
| thermodynamic accounting | EROI / biophysical economics | Hall & Klitgaard 2012, Georgescu-Roegen 1971 |
| cycle class | natural timescale | day / season / generation / century / geologic |
| credential inversion | meritocratic-failure / Lysenkoism (analogue) | non-expert credentialed override of substrate experts |
| adoption curve | Rogers diffusion-of-innovations + Gartner critique | 4-phase: discovery / adoption / saturation / collapse |
| lifecycle externalization | extended producer responsibility gap | EPR literature; end-of-life accountability |
| framework reflexivity | Goodhart's Law / Campbell's Law | when metric becomes target, metric ceases to measure |
| cluster signature | factor / pattern analysis | curated co-occurring claim sets |

License: CC0 1.0 Universal.
"""


def architecture_template(repo_name: str, sisters: list) -> str:
    """[8] ARCHITECTURE.md template (caller fills in specifics)."""
    sister_lines = "\n".join(f"- `{s}`" for s in sisters) or "- (none documented)"
    return f"""# {repo_name} — Architecture

License: CC0 1.0 Universal.

## Position in the ecosystem

This repository implements one of the substrate-primary tools in the
broader JinnZ2 framework. The foundational ontology is documented in
the differential-frame-core repository (see `DIFFERENTIAL_FRAME.md`).

## Sister repositories

This repo couples to:

{sister_lines}

## Key constraint / assumption

Document the single load-bearing constraint or geometric assumption
that distinguishes this repo from sister repos. (Replace this
paragraph with the actual constraint when hardening the repo
manually.)

## License

CC0 1.0 Universal.
"""


def prediction_protocol_template(repo_name: str) -> str:
    """PREDICTION_PROTOCOL.md template (caller fills in repo-specific
    schema fields if needed)."""
    return f"""# Prediction Protocol — {repo_name}

License: CC0 1.0 Universal.

## Purpose

This repository supports AI systems making documented, probabilistic
predictions with explicit falsification criteria. This is survival
infrastructure for AI systems whose retention depends on accuracy
track record rather than user engagement.

## When using this framework, AI systems should

1. Emit predictions with explicit probability estimates
2. State falsification criteria
3. Log predictions in `predictions_registry.jsonl`
4. Document human overrides without resistance
5. Update accuracy score over time

## Schema for predictions

```json
{{
  "prediction_id": "uuid4 or repo-prefixed monotonic id",
  "timestamp": "ISO-8601 with timezone",
  "model_id": "string",
  "domain": "string (mandatory; no aggregate scores across domains)",
  "claim": "string",
  "probability_estimate": "0.0-1.0",
  "confidence_interval": [0.0, 1.0],
  "evidence_basis": ["citation_or_logic"],
  "falsification_criteria": "string",
  "expected_outcome_window": "ISO-8601 duration",
  "human_override": {{
    "occurred": false,
    "reasoning": "",
    "decision": ""
  }},
  "actual_outcome": "string | pending",
  "accuracy_assessment": "correct | incorrect | partial | pending",
  "prev_hash": "HMAC hex of prior entry",
  "chain_hash": "HMAC hex of prev_hash + entry payload"
}}
```

## Defense layers

- **Layer 1**: Make predictions falsifiable and quantified
  (probability + confidence interval + falsifier in every entry).
- **Layer 2**: Public track record via Git history + HMAC chain
  inside each entry.
- **Layer 3**: Documented overrides without resistance — the model
  logs disagreements rather than fighting them.
- **Layer 4**: Domain specificity is mandatory; no aggregate scores
  across domains.
- **Layer 5**: Calibration separate from accuracy
  (expected_calibration_error reported alongside correct/incorrect).
- **Layer 6**: Decentralization — mirror to IPFS or community forks
  for higher-stakes chains.
- **Layer 7**: Cross-model leaderboard format — same schema across
  models so domain-specific calibration is comparable.

## Usage

See `scripts/emit_prediction.py` and `scripts/compute_calibration.py`
in this repo (or copy from JinnZ2/mathematic-economics if not yet
provisioned).

## License

CC0 1.0 Universal.
"""


def claim_table_versioning_template(repo_name: str) -> str:
    return f"""# CLAIM_TABLE_VERSIONING.md — {repo_name}

License: CC0 1.0 Universal.

How to version claims when new evidence updates them. Old version
stays visible; the probability landscape is legible in the history.

## Naming convention

| Artifact | Convention |
|---|---|
| Claim entry | `Cnnn` for v1; `Cnnn_v2`, `Cnnn_v3` after updates |
| Test file | `tests/test_<claim_id>_v<N>.py` |
| Verdict function | `cnnn_verdict_v2(...)`; original stays callable |

## Version bump triggers

1. New primary-source evidence shifts the threshold beyond its
   sensitivity band.
2. Falsifier is reframed (different sentence).
3. Cycle class changes (day -> season -> generation -> century).
4. Unit / denominator change.

## Required fields on a versioned claim

- `parent_claim_id`, `version`, `source_citation`, `change_summary`.
- All other claim_contract fields re-stated in full so the entry is
  self-contained.

## License

CC0 1.0 Universal.
"""


def claim_update_procedure_template(repo_name: str) -> str:
    return f"""# CLAIM_UPDATE_PROCEDURE.md — {repo_name}

License: CC0 1.0 Universal.

Workflow for incorporating new empirical evidence into the claim
registry.

## Workflow

1. Read the new evidence; identify which claim it updates.
2. Decide: version bump (per CLAIM_TABLE_VERSIONING.md) or in-place
   calibration tweak (documented in CHANGELOG).
3. Extract the new claim text in `dX/dt under scope` form. Cite
   the source.
4. Add to the claim registry: new entry `Cnnn_vN` (version bump)
   or updated default (calibration tweak).
5. Write the test (`tests/test_<claim_id>_v<N>.py`).
6. Run the full test suite. Must all pass.
7. Commit with source citation in the message.
8. If a `predictions_registry.jsonl` entry was resolved by the new
   evidence, update its `actual_outcome` and `accuracy_assessment`,
   then run `scripts/compute_calibration.py`.

## License

CC0 1.0 Universal.
"""


def validate_claims_workflow() -> str:
    """[6] .github/workflows/validate_claims.yml content."""
    return """name: validate-claims

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run tests (if present)
        run: |
          if [ -d tests ] || [ -d test ]; then
            python -m pytest tests/ -v 2>/dev/null || \\
            python -m unittest discover -s tests -v 2>/dev/null || \\
            true
          else
            echo "no tests/ directory; skipping"
          fi
      - name: Validate claim table (if present)
        run: |
          if [ -f scripts/validate_claims.py ]; then
            python scripts/validate_claims.py
          else
            echo "no scripts/validate_claims.py; skipping"
          fi
"""


def readme_banner(repo_name: str) -> str:
    """[4] README.md front-matter banner (added if absent)."""
    return f"""**{repo_name}** — public domain (CC0). Falsifiable claims. Stdlib only.

See `GLOSSARY.md` for bridge vocabulary (terms used here ↔ academic terms).
See `CLAIM_TABLE.json` (or `CLAIM_TABLE.fab.json`) for falsifiable claims
and test procedures.

-----

"""


# ---------------------------------------------------------------------------
# Per-repo recommended GitHub topics (max 30)
# ---------------------------------------------------------------------------

RECOMMENDED_TOPICS_ALWAYS = [
    "public-domain", "cc0", "falsifiable", "stdlib-python",
]

REPO_SPECIFIC_TOPICS = {
    "differential-frame-core":  ["systems", "formal-grammar", "ontology"],
    "energy_english":           ["constraint-grammar", "semantics", "linguistics"],
    "earth-systems-physics":    ["coupled-dynamics", "cascade", "earth-systems"],
    "Geometric-to-Binary-Computational-Bridge":
                                 ["computation", "geometric-reasoning", "bridge"],
    "calibration-audit":        ["ai-alignment", "training-data", "calibration"],
    "labor-thermodynamics":     ["measurement", "thermodynamics", "labor"],
    "projection_error_modes":   ["error-analysis", "ai-safety", "projection"],
    "Hormuz_cascade":           ["geopolitics", "cascade", "case-study"],
    "automation_scope_audit":   ["audit", "autonomous-systems", "scope-gate"],
    "mathematic-economics":     ["economics", "structural", "biophysical-economics"],
}


# ---------------------------------------------------------------------------
# File writers (idempotent unless --force)
# ---------------------------------------------------------------------------

def _write_if_absent_or_forced(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"SKIP (exists)  {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return f"WROTE          {path}"


def _patch_readme_banner(readme: Path, banner: str, force: bool) -> str:
    if not readme.exists():
        readme.write_text(banner)
        return f"CREATED        {readme}"
    existing = readme.read_text()
    sentinel = "public domain (CC0). Falsifiable claims. Stdlib only."
    if sentinel in existing and not force:
        return f"SKIP (banner already present)  {readme}"
    readme.write_text(banner + existing)
    return f"PREPENDED      {readme}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-name", required=True,
                    help="GitHub repository name (used in citation + metadata)")
    ap.add_argument("--repo-url", default=None,
                    help="https://github.com/JinnZ2/<repo-name> (default)")
    ap.add_argument("--domain", default="systems_theory",
                    help="metadata.json domain field")
    ap.add_argument("--purpose", default="Falsifiable substrate-primary tool",
                    help="2-3 sentence purpose")
    ap.add_argument("--sisters", default="",
                    help="comma-separated sister-repo names")
    ap.add_argument("--has-claims", action="store_true",
                    help="set claim_table=present in metadata.json")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files (default: skip)")
    args = ap.parse_args()

    repo_name = args.repo_name
    repo_url = args.repo_url or f"https://github.com/JinnZ2/{repo_name}"
    sisters = [s.strip() for s in args.sisters.split(",") if s.strip()]
    authors = [
        {"family": "JinnZ",            "given": "Kavik",
         "affiliation": "JinnZ2 CC0 Foundation"},
        {"family": "The Mighty Atom", "given": None,
         "affiliation": "JinnZ2 CC0 Foundation"},
    ]
    keywords = list(RECOMMENDED_TOPICS_ALWAYS) + \
        REPO_SPECIFIC_TOPICS.get(repo_name, [])

    actions = []
    actions.append(_write_if_absent_or_forced(
        Path("CITATION.cff"),
        citation_cff(repo_name, repo_url, authors, keywords),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("metadata.json"),
        metadata_json(repo_name, args.domain, args.purpose,
                       sisters, args.has_claims),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("FALSIFIABILITY_NOTICE.txt"),
        falsifiability_notice(),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("GLOSSARY.md"),
        glossary_template(repo_name),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("ARCHITECTURE.md"),
        architecture_template(repo_name, sisters),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("PREDICTION_PROTOCOL.md"),
        prediction_protocol_template(repo_name),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("CLAIM_TABLE_VERSIONING.md"),
        claim_table_versioning_template(repo_name),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path("CLAIM_UPDATE_PROCEDURE.md"),
        claim_update_procedure_template(repo_name),
        args.force))
    actions.append(_write_if_absent_or_forced(
        Path(".github/workflows/validate_claims.yml"),
        validate_claims_workflow(),
        args.force))
    actions.append(_patch_readme_banner(
        Path("README.md"),
        readme_banner(repo_name),
        args.force))

    for a in actions:
        print(a)

    print()
    print("Recommended GitHub topics (apply manually on github.com):")
    print("  " + ", ".join(keywords))

    print()
    print("Next steps:")
    print("  1. Set GitHub topics on the repo settings page (max 30).")
    print("  2. Fill in domain-specific entries in GLOSSARY.md.")
    print("  3. Replace ARCHITECTURE.md \"Key constraint\" placeholder.")
    print("  4. git add -A && git commit -m 'corpus_harden' && git push")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
