# AUDIT_TASKS_HARDENING.md

CC0. External audit (DeepSeek, Perplexity) + internal review tasks
addressing rhetorical weak points and accessibility gaps in the core
README before integrating the C001-C083 claims layer from
`automation_scope_audit/`.

Execute in order. Each task one commit. Mark complete with date.

---

## PHASE H1 — Rhetorical hardening

### H1.1  Remove or fix Model 1 stability equation **DONE 2026-05-23**

Disposition: **Option B**. Original `S = 1 / [(RI × UFR × DI) + ER]`
was dimensionally inconsistent; French/Russian Revolution comparison
numbers were unsourced. Replaced with a short placeholder pointing
to `data/stability_research_notes.md` (starter design + literature
pointers for replacement work).

### H1.2  Same treatment for Model 2 (Time to Collapse) **DONE 2026-05-23**

Disposition: **Option B**. "Total Wealth" denominator undefined; no
validation cases. Withdrawn together with Model 1 in the same
placeholder block.

### H1.3  Tag every illustrative numerical value **DONE 2026-05-23**

Every numerical value in README body text now carries one of the five
tag formats (`[illustrative]`, `[FRED <SERIES>, <DATE>]`,
`[BLS <SERIES>, <DATE>]`, `[computed: <method>, <date>]`,
`[historical: <source>, <year>]`). The "Summary of Measured Values"
section is renamed "Summary of Illustrative Values" with an explicit
illustrative disclaimer block at the top.

Code-block content (formula illustrations, worked-example arithmetic)
intentionally exempt — those teach the math, not claim measurement.

---

## PHASE H2 — Accessibility

### H2.1  Add executive summary to top of README **DONE 2026-05-23**

Inserted immediately after title per user spec. Under 200 words.

### H2.2  Restructure README section order **DEFERRED**

Large reflow (Smith Scorecard up, Predictive Models out, etc.).
Deferred to a dedicated commit so the diff stays reviewable. Plan
captured below.

### H2.3  Link to computational backbone more visibly **DONE 2026-05-23**

New "Computational Specification" subsection inserted directly after
the executive summary. References `equations.yaml`,
`schemas/claim_contract.py`, `data/fetch_and_compute.py`,
`data/sensitivity_analysis.py`, `epistemic_ledger.py`,
`metrological_bounds.py`, `DIFFERENTIAL_FRAME.md`. Verified all files
exist.

---

## PHASE H3 — Integration of automation_scope_audit work

### H3.1  Cross-references from README to automation_scope_audit **DONE 2026-05-23**

Example 4 added to README "Application Examples": worked application
of the framework to autonomous-trucking deployment claims, with
mapping from canonical Equations 1-13 to representative
`automation_scope_audit` claims (C001-C083 currently).

### H3.2  Create addendum-4.md **ALREADY DONE (earlier commit)**

Published in a prior commit. Match style and length of existing
addenda. Cross-referenced from the new Example 4 above.

### H3.3  CLAIM_TABLE.json -> CLAIM_TABLE.fab.json compliance **ALREADY DONE (TASK 1.2)**

Done in TASK 1.2: every claim in `automation_scope_audit/CLAIM_TABLE.fab.json`
round-trips through `schemas/claim_contract.Claim.from_dict / to_dict`.
84 claims as of 2026-05-23.

---

## PHASE H4 — Application study

### H4.1  Kodiak/Atlas public audit **DEFERRED**

Needs primary-source field-by-field data collection (operator 10-K,
press releases, SEC filings, FMCSA disclosures) classified as
measured / inferred / absent. AI cannot fabricate audited numbers;
this requires a human researcher with access to source documents.

Starter scaffold: a template `examples/_template_public_audit.py` and
the `optimistic / neutral / pessimistic` scenario harness exist as
patterns to follow. Estimated effort: ~8 hours.

---

## PHASE H5 — External audit defenses

### H5.1 semantic coherence layer for C000 **ALREADY DONE (Phase 8 Task 8.1)**
### H5.2 spatial resolution parity check for C001 **ALREADY DONE (Phase 8 Task 8.2)**
### H5.3 allocation rule declaration **ALREADY DONE (Phase 8 Task 8.3)**
### H5.4 timescale phenomenon match check **ALREADY DONE (Phase 8 Task 8.4)**

Phase 8 (committed 2026-05-23) implemented H5.1-H5.4 substantively.

### H5.5 adversary cost curve as input field **DEFERRED**

Needs representative attacker-cost data per domain. Starter scaffold
in TODO.md (Phase 8 deferred items).

### H5.6 valuation sensitivity for C025/C026/C029 **DEFERRED**

Needs consistent valuation-factor convention across modules. Starter
scaffold in TODO.md (Phase 8 deferred items).

---

## PHASE H6 — Token-window archival hedge

### H6.1  Maximize discoverability before training-data filtering **PARTIAL — DONE 2026-05-23**

- `CITATION.cff` added at repo root with structured metadata.
- README keyword density verified for: "falsifiable",
  "thermodynamic", "audit", "substrate", "differential", "scope",
  "preconditions", "physics-grounded".
- Literature pointers (Georgescu-Roegen, Hall & Klitgaard, Daly,
  Wallerstein, Gottman, Turchin, Acemoglu & Robinson) added to
  "Related frameworks" section.
- Cross-links to companion JinnZ2 repos noted in README's "Companion
  folders" section.

Remaining (in TODO.md): submit framework to academic indexes
(SSRN, arXiv-econ), seek peer-reviewed citation. Requires academic
co-author or established researcher.

---

## License

CC0 1.0 Universal.
