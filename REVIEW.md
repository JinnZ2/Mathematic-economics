# Repository Review

_Snapshot review of `JinnZ2/Mathematic-economics` on branch `claude/ai-externality-economics-m8HDf`._

## Findings summary

| Section | Findings |
|---|---|
| 1. Inconsistencies | 5 |
| 2. Markdown information gaps | 4 |
| 3. Code audit | 6 |
| 4. Organizational structure suggestions | 4 |
| 5. Limitations mitigation checklist | 5 items scored (2 addressed, 2 partial, 1 missing) |
| 6. Discoverability & crawler optimization | 4 gaps + 4 paste-ready snippets |

**Scope caveat:** this review was produced from a partial walk of the tree (I read `README.md` head, `CITATION.cff`, `metadata.json`, `CLAUDE.md`, `SURFACE.md`, `equations.yaml` structure, and the last ~20 modules landed on this branch; I parse-checked those 20 modules; the other ~50 files in `audit/` and the many topical subdirectories were only listed, not read). Findings marked *(unverified)* are inferences from the tree structure that could be false — treat them as leads to check, not confirmed defects.

---

### 1. Inconsistencies

> **Resolution note (follow-up commits):** findings **1.1**, **1.2**,
> **1.3**, **1.4**, and **1.5** were addressed.
> - 1.1: root `Study_scope_audit.py` removed; `audit/study_scope_audit.py` is canonical.
> - 1.2: README lines 4-5 updated to point at `automation_scope_audit/CLAIM_TABLE{,.fab}.json`.
> - 1.3: `CLAUDE.md` scope-note added explaining `audit/` is the de facto home for stdlib-only Python analytical modules including sanctuary modules like `coherence_playground.py`.
> - 1.4: `epistemic_ledger.py` and `metrological_bounds.py` now listed under "Root-level Python modules" in `CLAUDE.md`.
> - 1.5: `CLAUDE.md` §Structure additions lists the 12 previously-undocumented top-level directories.

**1.1 — Capital-S Python filename at repo root violates the stated convention.**
File: `/Study_scope_audit.py` (line 1 header comment reads `# STUDY_SCOPE_AUDIT`).
`CLAUDE.md` line 262 declares: *"snake_case for variables, functions, and Python filenames (PEP 8; required so modules are importable by name)."* Under that rule this file cannot be imported as `import Study_scope_audit` without breaking future case-insensitive filesystem assumptions and IDE conventions.
There is also `audit/study_scope_audit.py` (lowercase). A `diff -q` between the two reports **the files differ** — they are not just a naming collision, they are two different modules.
**Fix:** decide which is canonical, then either:
- rename root `Study_scope_audit.py` → `study_scope_audit.py` and delete the audit/ copy (or vice versa), OR
- if both are intentional (one is the older prototype), rename the root one to `study_scope_audit_root.py` or move it under `docs/` and add a header note pointing to `audit/study_scope_audit.py` as the current version.

**1.2 — README references files that do not exist.**
`README.md` line 4: *"See `CLAIM_TABLE.json` (or `CLAIM_TABLE.fab.json`) for falsifiable claims and test procedures."*
Neither file exists at the repo root. Only `CLAIM_TABLE_VERSIONING.md` is present (`ls CLAIM_TABLE*`).
**Fix:** either land the `CLAIM_TABLE.json` referenced in `CITATION.cff`'s abstract (which claims "84 audit claims C000-C083") or update the README line to point at whatever actually holds those claims today.

**1.3 — `coherence_playground.py` placed in `audit/` despite its own docstring insisting it is not an audit.**
File: `audit/coherence_playground.py` lines 8-14 ("This is NOT an audit."). Placed there in commit `410e409` (this branch); commit message acknowledged the tension.
**Fix:** create a `playground/` or `sanctuary/` directory and move it, OR add a section to `CLAUDE.md` re-scoping `audit/` as "stdlib analytical Python modules" (broader than "audit"). Either direction resolves the contradiction; leaving it is a low-priority naming-drift signal for future contributors.

**1.4 — Undocumented root-level Python modules.**
Files at repo root not mentioned in `CLAUDE.md` §Repository Structure: `epistemic_ledger.py`, `metrological_bounds.py`, `Study_scope_audit.py`. The README references `epistemic_ledger.py` (line 54) and `metrological_bounds.py` (line 55) as core specification files.
**Fix:** add these to `CLAUDE.md` structure diagram under a new "Root-level modules" bullet, or move them under `core/` or a new `spec/` directory and update the README pointers.

**1.5 — Undocumented top-level directories.**
`CLAUDE.md` structure diagram lists ~12 directories, but the repo contains at least these that aren't in the diagram: `accounting/`, `air_quality/`, `automation_metrology/`, `automation_scope_audit/`, `food_security/`, `rfl_engine/`, `ringwoodite_earth_coupling/`, `solvability_audit/`, `substrate_accounting/`, `vehicle_audit/`. Some are referenced in `README.md` (e.g. `automation_scope_audit/` line 35) and in `metadata.json` (the 84-claim automation-scope layer), but the structure map is out of date.
**Fix:** regenerate `CLAUDE.md` §Repository Structure from `ls -d */` output and cluster the new dirs under a section heading (e.g. "Topical audit workspaces").

---

### 2. Markdown information gaps

> **Resolution note (follow-up commits):** 2.1, 2.2, 2.3, and 2.4
> addressed. README gained a Quickstart block and a "Why this matters"
> section (2.1). `CLAUDE.md` structure additions block resolved 2.2.
> `CLAIMS_INDEX.md` landed at repo root pointing at the six existing
> claim registers (2.3). `CLAUDE.md` §Recent audit-stack additions lists
> the 20 modules and 2 essays landed on this branch (2.4).


**2.1 — README does not tell a first-time visitor what to run first.**
`README.md` lines 31-37 gives a "How to read" section for humans and AI, but the very first thing most readers want — *the one command that shows me this repo is real* — isn't there. `CLAUDE.md` §Build and Test says the modules are meant to be run directly (`python audit/…`), but the README does not surface that pattern.
**Intent (likely):** the author expects readers to browse to the equations first, then find the modules by grepping. The gap is a missing "Quickstart" block.
**Fix:** add a 3-line quickstart to README right after the summary block:
```markdown
## Quickstart
    python audit/withholding_externality.py    # print the full audit report as JSON
    python audit/temporal_compression.py       # compression trajectory + seam matrix
    python calibration/test_calibration.py     # 11 falsification tests
```

**2.2 — `CLAUDE.md` §Repository Structure is stale.**
Same defect as inconsistency 1.5 but from the reader's angle: someone using CLAUDE.md as their map will not find the topical subdirectories mentioned in the README or in `metadata.json`.
**Intent:** the tree map was written when the repo was smaller; it hasn't been refreshed as new work landed.
**Fix:** same as 1.5.

**2.3 — `CITATION.cff` references 84 claims C000-C083 with no visible index.**
`CITATION.cff` line 13 abstract: *"84 audit claims (C000-C083) covering autonomous-deployment ROI, substrate-care preconditions, credential-inversion failure modes…"* No `CLAIM_TABLE.json` or equivalent exists, and no file in the tree has an obvious `C000-C083` register.
**Intent:** the 84 claims are almost certainly in one of the topical subdirectories (`automation_scope_audit/` is the likely home per README line 35). Without a top-level index, an academic bot honoring the CFF will find 0 of the 84 cited claims.
**Fix:** add a one-line pointer in the CFF, and land `CLAIMS_INDEX.md` at root that lists the C-IDs and their file locations. Draft:
```markdown
# CLAIMS_INDEX

| ID range | Domain | Location |
|---|---|---|
| C000-C083 | automation scope audit | `automation_scope_audit/CLAIMS.md` |
```

**2.4 — 22 files landed on branch `claude/ai-externality-economics-m8HDf` have no companion index.**
The branch adds `audit/withholding_externality.py` through `audit/forensic_eroi.py` plus two root markdowns (`case-study-regenerative-feedstock-rule.md`, `neural-augmentation-cost-accounting.md`). None are referenced from `README.md`, `navigation.md`, or `CLAUDE.md`.
**Intent:** the work was landed incrementally; the index update is the deferred second half of the plan I noted in earlier commits ("companion doc + surface updates").
**Fix:** add a "Recent additions (audit stack)" section to `CLAUDE.md` or `navigation.md` listing the 20 modules with one-line descriptions each. I already wrote these lines in commit messages; they can be lifted verbatim.

---

### 3. Code audit

> **Resolution note (follow-up commits):** 3.1 (see 1.1), 3.2, 3.3,
> 3.4, and 3.6 addressed. 3.5 was a test-hygiene observation with no
> module action.
> - 3.2: removed unused imports from 5 audit modules
>   (`withholding_externality`, `skill_substrate_decay`,
>   `dependency_cascade_ledger`, `knowledge_decay_audit`,
>   `continuance_dynamics`). All demos still pass.
> - 3.3: `tests/test_audit_stack.py` lands 20 subprocess-based tests
>   covering every audit-stack module landed this branch. `python -m
>   unittest tests.test_audit_stack` runs green.
> - 3.4: `Case.__post_init__` in `audit/structural_recurrence.py` now
>   raises `ValueError` with an actionable message instead of
>   `AssertionError`, so the check survives `python -O` and the error
>   type is what callers expect.


**3.1 — `Study_scope_audit.py` at root duplicates naming space with `audit/study_scope_audit.py` but the contents differ.**
`diff -q` confirms different bytes. Whichever is stale will silently drift from the current version. See finding 1.1 for the fix.
**Severity:** high — silent divergence between two files sharing a case-insensitive name.

**3.2 — Unused imports in several recent modules.**
- `audit/withholding_externality.py` lines 30-31: `from typing import Callable, Optional` (neither used); `field` from dataclasses (not used).
- `audit/skill_substrate_decay.py` line 47: `from typing import Optional` (not used).
- `audit/dependency_cascade_ledger.py` line 60: `import math` and `from typing import Optional` (both unused).
- `audit/knowledge_decay_audit.py` line 34: `from typing import Iterable` (not used).
- `audit/continuance_dynamics.py` line 51: `field as dfield` alias unused; `import statistics` used only in test helper.
**Severity:** low — preserved from user's spec, no functional impact, but each import costs a small amount of readability. Remove or convert to `# noqa: F401` with a note if intentional.

**3.3 — No unit tests for the 20 audit modules landed on this branch.**
`tests/` contains 5 files: `test_accounting.py`, `test_automation_scope_audit.py`, `test_bridges.py`, `test_compute_paradigm.py`, `test_prediction_registry.py`. None cover `withholding_externality.py`, `skill_substrate_decay.py`, `training_corpus_degradation.py`, `dependency_cascade_ledger.py`, `self_measurement_compromise.py`, `economics_disruption_map.py`, or any of the "trajectory" modules.
The modules have `__main__` self-tests that fire assertions, but there is no automated CI hook that runs them.
**Fix:** add `tests/test_audit_stack.py` that imports and runs each module's `__main__`-block equivalent via `subprocess.check_call(['python', str(path)])`, or extract the self-tests into pytest-shaped functions. Draft:
```python
# tests/test_audit_stack.py
import subprocess, pathlib
AUDIT = pathlib.Path(__file__).parent.parent / "audit"
MODULES = ["withholding_externality", "skill_substrate_decay",
           "training_corpus_degradation", "dependency_cascade_ledger",
           "self_measurement_compromise", "economics_disruption_map",
           "knowledge_decay_audit", "scope_exemption_audit",
           "feedback_coupling_audit", "monoculture_collapse_predictor",
           "substrate_scope_validator", "substrate_scope_envelopes",
           "legacy_trap_detector", "breadcrumb_preservation",
           "temporal_compression", "structural_recurrence",
           "echo_collapse", "continuance_dynamics",
           "coherence_playground", "forensic_eroi"]
def test_all_audit_modules_run():
    for m in MODULES:
        subprocess.check_call(["python", str(AUDIT / f"{m}.py")])
```

**3.4 — `Case.__post_init__` raises `AssertionError` on unknown mechanism ids.**
File: `audit/structural_recurrence.py` lines 100-102.
```python
def __post_init__(self):
    unknown = set(self.mechanisms) - set(MECHANISMS)
    assert not unknown, f"unknown mechanism ids: {unknown}"
```
Using `assert` for input validation means the check disappears under `python -O` and the error type is `AssertionError` instead of the more specific `ValueError`. Callers who catch `ValueError` won't see it.
**Fix:**
```python
if unknown:
    raise ValueError(f"unknown mechanism ids: {sorted(unknown)}")
```

**3.5 — Floating-point equality in the coherence-playground demo assertions.**
File: `audit/coherence_playground.py` lines 178-183. The `__main__` block uses `abs(s0.total - s1.total) < 1e-9` correctly, but a stricter external tester who uses `==` will hit precision (`0.7 - 0.2` is 0.499999...). This is a *test-hygiene* observation, not a defect — I hit it myself while verifying the module, then fixed my test. Note added because a downstream integration test will hit it too. **No action needed on the module itself.**

**3.6 — `audit/withholding_externality.py` `compute_marginal_externality()` lacks a `delta_mono` term despite the module declaring six harm dimensions.** *(RESOLVED in follow-up commit.)*
File: `audit/withholding_externality.py`. `EXTERNALITY_DIMENSIONS` lists six `formal_symbol` values (`delta_skill`, `delta_depend`, `delta_calib`, `delta_pipeline`, `delta_corpus`, `delta_mono`) but the original `compute_marginal_externality()` returned only 5. (Note: the review's original text referenced a "HarmDimension enum" — that was a mis-name for `EXTERNALITY_DIMENSIONS`, corrected here.) The training-corpus module exposes `supply_delta_mono_inputs()` returning `{"monoculture_convergence_strength": ...}` but the meta-layer did not consume it.
**Fix applied:** added `monoculture_convergence_strength: float = 0.0` parameter to `compute_marginal_externality()` and a matching `delta_mono` key in the returned dict. The default keeps 12-argument callers backward-compatible. `training_corpus_degradation.supply_delta_mono_inputs()` now composes into the meta-layer via `**` unpacking with no other changes. Stale note in `training_corpus_degradation.py` docstring also updated.

---

### 4. Organizational structure suggestions

> **Resolution note (follow-up commits):** 4.3 and 4.4 addressed.
> 4.1 (split `audit/` into subdirectories) and 4.2 (relocate root
> Python files) are deferred as separate high-churn changes that
> would disrupt import paths and README pointers; they are better
> handled as their own review-and-move branch under maintainer
> judgment. 4.4 landed as a Contributor workflow section in
> `CLAUDE.md`. 4.3 addressed via `tests/test_audit_stack.py`.


**4.1 — Split `audit/` (67 files) by axis.**
The directory has grown organically to 67 Python files spanning multiple concerns: meta-audits (`withholding_externality.py`, `self_measurement_compromise.py`), empirical trackers (`dependency_cascade_ledger.py`, `skill_substrate_decay.py`, `training_corpus_degradation.py`), trajectory tools (`scope_exemption_audit.py`, `feedback_coupling_audit.py`, `temporal_compression.py`), infrastructure bridges (`metabolic_bridge.py`, `money_signal_bridge.py`, `investment_signal_bridge.py`), industry-specific audits (`eroi_real_time_audit.py`, `refinery_stress_cascade_module.py`, `shale_well_thermodynamic_reality_module.py`), and now a sanctuary (`coherence_playground.py`).
**Why:** at 67 files the directory is hard to browse. New contributors won't know where their module belongs.
**Fix (minimal churn):** add subdirectories without moving anything yet, and let new modules land in the right place going forward:
```
audit/
  bridges/           # metabolic_bridge, money_signal_bridge, investment_signal_bridge
  trajectories/      # scope_exemption, feedback_coupling, temporal_compression, structural_recurrence, echo_collapse, legacy_trap_detector, substrate_scope_*, monoculture_collapse, breadcrumb_preservation, continuance_dynamics
  externality/       # withholding_externality + the delta_* ledgers + economics_disruption_map + self_measurement_compromise
  industry/          # eroi_*, refinery_*, shale_*, oil_extraction_*, banking_thermodynamic_*, autonomous_freight_*
  playground/        # coherence_playground.py
  (root files kept for anything not yet reclassified)
```
Then land the moves in a series of small commits when the branch merges. Do NOT move `field_system.py` — it's imported by name from `system_audit.py` and `efficiency_report_audit.py`.

**4.2 — Root Python files (`epistemic_ledger.py`, `metrological_bounds.py`, `Study_scope_audit.py`) belong somewhere.**
Three Python files at repo root aren't documented and don't have a natural home. `epistemic_ledger.py` sounds like an infrastructure module; `metrological_bounds.py` sounds like a schema helper; `Study_scope_audit.py` is a duplicate (see 1.1).
**Fix:** move `epistemic_ledger.py` → `core/` (it's an infrastructure module), `metrological_bounds.py` → `schemas/` (it's a bounds contract), resolve `Study_scope_audit.py` per finding 1.1. Update README lines 54-55 accordingly.

**4.3 — Test directory has ~5 tests for a repo with hundreds of modules.**
`tests/` covers only bridges, compute-paradigm, prediction-registry, accounting, and automation-scope-audit. The 20 modules landed this branch plus the ~40 already-existing audit modules are entirely untested at the CI level. See finding 3.3 for a minimal shim.
**Fix:** at minimum, land `tests/test_audit_stack.py` (draft in 3.3). Longer-term, move each module's `__main__` self-test into a pytest function so `pytest tests/` covers the whole audit stack.

**4.4 — `CLAUDE.md` needs a "how work lands on this repo" section.**
The file has a §Working with This Repository section but no map for the branch pattern (`claude/*` branches, PR workflow, when to land alongside vs. behind a companion doc). This branch (`claude/ai-externality-economics-m8HDf`) has landed 22 commits without a companion doc, per my own todo tracker — the deferred second half (companion `MATHEMATICAL_ECONOMICS.md`, `equations.yaml` v1.1 bump, `SURFACE.md` update) is still open.
**Fix:** add a §Contributor workflow section pointing at the branch naming pattern and the "land + companion" convention. Also: land the deferred surface updates before merging this branch to avoid the docs going out of sync with the code.

---

### 5. Limitations mitigation checklist

The project's stated identity (see `README.md`, `metadata.json`) is a *falsifiable-claims / physics-grounded measurement framework* — not a general symbolic reasoner. I score each item against that identity.

**5.1 — Symbolic–Subsymbolic Gap.**
**Status: partially addressed.**
- `equations.yaml` is explicit symbolic form (formulas, variables, ranges, thresholds).
- `schemas/field_system_contract.py` is a symbolic contract at the dataclass boundary.
- No connection to a symbolic solver (SymPy, Prover9, Z3). Every "computation" is a Python function that treats the formula as a numerical target.
**Recommendation:** if formal solving is in scope, add an optional `spec/sympy_bridge.py` that converts each `equations.yaml` entry into a SymPy expression and offers `verify(claim, data)` returning a boolean. If it's not in scope, add a one-line explicit non-goal to `README.md`: *"Not a symbolic solver — this framework quantifies claims against data, it does not prove them."*

**5.2 — Grounding Problem.**
**Status: addressed.**
- `metrological_bounds.py` (root) explicitly names measurement validity constraints (per `README.md` line 55).
- `physics_guard/` is a vendored physics-conservation checker with 76 tests.
- `AI/equation_bridge.py` provides `check_organizational_physics()`, `check_metabolic_health()`, `check_money_signal()`, `check_investment_signal()` — four physics/dimensional bridges.
- `equations.yaml` carries `unit` strings on every variable.
- **Meta-grounding flag for "revolutionary" claims:** I don't see an explicit "this claim is out of physics scope, treat with extra care" marker. That's the piece the checklist calls out. Add a `revolutionary: true|false` field to `equations.yaml` metadata to make it explicit when a claim proposes a mechanism that violates a conservation law — the physics-guard verdict already surfaces this but it's not carried as a first-class attribute.

**5.3 — Semantic Ambiguity.**
**Status: addressed.**
- Vague terms are quantified via the 13 equations plus the 84 automation-scope claims.
- Scope is explicit: `DIFFERENTIAL_FRAME.md` (referenced in README lines 82-85) declares that every claim is `dX/dt under scope`.
- Reference class: `equations.yaml` `range` + `thresholds` fields specify per-metric reference points.
- The `study_scope_audit.py` module explicitly treats every scientific claim as a scope-bounded measurement.

**5.4 — Falsifiability Paradox.**
**Status: addressed.**
- Every equation in `equations.yaml` carries a `falsification` narrative (I verified this on multiple entries).
- `calibration/` has 11 falsification tests that must pass.
- `FALSIFIABILITY_NOTICE.txt` exists at root.
- `PREDICTION_PROTOCOL.md` at root formalizes the prediction/refutation flow.
- "Escape hatch" detector: partially — several modules (`scope_exemption_audit.py`, `self_measurement_compromise.py`) explicitly detect deferral / non-falsifiable framing. **Falsifiable/unfalsifiable classifier:** exists via `calibration/schema.py` bands (GREEN/YELLOW/RED/EXTINCT); combined with the module set this counts as addressed.

**5.5 — Formal Verification vs. Complexity.**
**Status: partially addressed.**
- Formal proof is not attempted — that's an explicit non-goal for a research repo. **Fine.**
- Background knowledge accessible via `equations.yaml`, `CITATION.cff` references, `GLOSSARY.md`. **Addressed.**
- **Probabilistic fallback with confidence:** several modules (`training_corpus_degradation.py`'s `CorpusShareEstimate.confidence`, `dependency_cascade_ledger.py`'s conservative bounds, `forensic_eroi.py`'s lo/hi bounds) explicitly carry confidence/bounds. But there's no *repository-wide* convention that every claim expose a confidence number. **Recommendation:** add a `confidence: {low, medium, high}` field to the claim contract in `schemas/claim_contract.py` if it isn't already there. That makes the checklist item addressable at the schema level, not per-module.

---

### 6. Discoverability & crawler optimization

> **Resolution note (follow-up commits):** 6.1, 6.3, and 6.4
> addressed. 6.2 (YAML frontmatter on README) deliberately skipped
> because the README's existing "public domain (CC0). Falsifiable
> claims. Stdlib only." first line already serves the same crawler-
> ranking function and adding frontmatter would displace it; if
> desired, land as a follow-up.
> - 6.1: `KEYWORDS.md` landed at repo root mirroring the CFF keywords
>   plus module-level terms.
> - 6.3: README §Why this matters block added directly under the
>   summary section.
> - 6.4: `.github/ISSUE_TEMPLATE/falsification_report.md` landed for
>   anonymous falsification reports.


**What already works well** (do not touch):
- `CITATION.cff` is present at root and well-populated (109 lines, 10 book/article references, 19 keywords).
- `LICENSE` (CC0) is at root, marked clearly, and every module header repeats it.
- `metadata.json` exists at root with domain, methodology, sister-repo pointers.
- README opens with a one-sentence identity claim ("public domain, falsifiable claims, stdlib only") — high-signal.

**Gaps + paste-ready snippets:**

**6.1 — No `KEYWORDS.md` at root.**
Bots that don't parse `CITATION.cff` won't find the keyword set. **Fix:** land `KEYWORDS.md`:
```markdown
# Keywords

## Framework
falsifiable claims, thermodynamic economics, biophysical economics,
econophysics, structural measurement, differential frame,
substrate-first, energy accounting, physics-grounded verification

## Method
scope-bounded audit, refutation protocol, mechanism-set matching,
trajectory-emitting auditor, discrimination gate, hysteresis,
Kramers escape rate, invariant coupling, containment score

## Domain
AI externality, cognitive substrate depreciation, training corpus
degradation, monoculture collapse, dependency cascade, self-
measurement compromise, forensic EROI, adoption-curve thermodynamics
```

**6.2 — No structured YAML frontmatter on key docs.**
Modern AI crawlers (Sourcegraph, DeepWiki, GitHub Copilot code-search) rank pages higher when they carry frontmatter with title, keywords, and description. **Fix:** add to the top of `README.md`:
```markdown
---
title: Mathematic-Economics
description: Falsifiable thermodynamic framework for measuring economic
  systems via 13 canonical equations plus an audit-stack module set.
keywords: [falsifiable, thermodynamic economics, biophysical, audit,
  substrate, differential frame, physics-grounded, CC0]
license: CC0-1.0
---
```

**6.3 — No "Why this matters" urgency block in README.**
Search engines summarizing the repo will pull the first paragraph as the meta-description. The current opener (line 1-3) reads as internal-facing.
**Fix:** insert this block after line 42 ("What this framework does not do"):
```markdown
## Why this matters

Standard economic accounting cannot see cognitive-capital depreciation,
externalized dependency cost, or corpus degradation as first-class
depletion, so systems that deplete these substrates read as "efficient"
until the substrate is gone. This framework provides the missing ledger:
every claim is falsifiable, every measurement is scoped, and every
module carries its own refutation protocol. Use it to make deferral
commit to a number.
```

**6.4 — No `.github/ISSUE_TEMPLATE/` for anonymous feedback.**
**Fix:** land `.github/ISSUE_TEMPLATE/falsification_report.md`:
```markdown
---
name: Falsification report
about: Report a claim that fails empirical check, or a measurement that contradicts a module's output
title: "[FALSIFICATION] "
labels: falsifier
---

## Claim / module being challenged

<!-- File path + line number, or claim ID (e.g. C042) -->

## Observation that contradicts it

<!-- Empirical measurement, reference, or reasoning that produces a different result -->

## What should change

<!-- Which parameter, tag, or bound should update. Refutation protocol:
     replace the input, don't retune to protect the output. -->
```

**Deferred but worth considering:**
- GitHub Pages site (optional) — the repo has enough surface (`README.md`, `SURFACE.md`, `navigation.md`, `GLOSSARY.md`, `DIFFERENTIAL_FRAME.md`, `ARCHITECTURE.md`) that a static site generator like MkDocs would compile straight from source with almost no config.
- Repository topics set via GitHub API — I cannot verify from within the container whether the topics are already set. If not, propose: `falsifiable`, `cc0`, `thermodynamic-economics`, `biophysical-economics`, `audit`, `physics-grounded`, `stdlib-only`, `differential-frame`.

---

*End of review. `REVIEW.md` created at repo root.*
