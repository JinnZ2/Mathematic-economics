# accounting/ — Claim Families

License: CC0 1.0 Universal.

The `accounting/` package declares four composable falsifiable-audit
claim families with stable prefixes that **do not enter** the global
mathematic-economics C-series. They are domain-agnostic primitives
usable across the JinnZ2 substrate-primary toolchain.

| Family | Prefix | Module | Count |
|---|---|---|---|
| Atomic accounting | `AA-` | `atomic_accounting.py` | 5 |
| GDP metrology political invariant | `GM-` | `gdp_metrology_political_invariant.py` | 5 |
| Substrate parity | `SP-` | `substrate_parity_audit.py` | 5 |
| Thermodynamic exception | `TE-` | `thermodynamic_exception_detector.py` | 5 |

Each module's docstring carries the load-bearing claim text inline.
This document is the cross-family index plus the test invariants that
lock them.

## AA — Atomic Accounting

Universal closure test: input flux = output flux + transformation
cost + accounted remainder. Gap != 0 within tolerance → ledger does
not close → hidden term or cascade signal.

| ID | Statement | Falsifier |
|---|---|---|
| **AA-1** | A ledger closes iff `|sum(signed entries)| <= tol`. | Ledger with `|gap| > tol` reported as closed. |
| **AA-2** | Mixed units in one ledger is a measurement error, not an accounting result. | Single-unit ledger that nets unit-mismatched entries to GREEN. |
| **AA-3** | An entry marked unfalsifiable (no physical unit / no source) cannot reduce the gap; it is held aside and reported, never netted. | Held-aside term that reduces the reported gap. |
| **AA-4** | Closure status is GREEN if `|gap|<=tol`, YELLOW if `<=warn`, RED otherwise. | Status assignment that violates these thresholds. |
| **AA-5** | A ledger that only closes after adding an unfalsifiable plug term is RED, not GREEN. | Plug-closed ledger reported as GREEN. |

Worked demos: orbital-compute power budget (RED, 6.9 MW asserted plug
held aside); Ashland fire-protection fee (RED, asserted aerial-response
plug held aside).

## GM — GDP Metrology Political Invariant

Test for the claim "automation produces economic growth." Productivity
signal = output / energy. If physically invariant across regimes but
monetarily divergent, the gain spread is extraction artifact, not
productivity.

| ID | Statement | Falsifier |
|---|---|---|
| **GM-1** | Productivity signal := `output_units / energy_in_J`. Currency-free, substrate-physical. | Signal that depends on currency choice. |
| **GM-2** | For true automation, coefficient of variation of the signal across regimes `<= cv_tol`. | Audited deployment with cross-regime signal CV > tol. |
| **GM-3** | `claimed_gain` (currency, no physical-output delta behind it) is held aside, never netted. | Audit that nets monetary gain into the physical signal. |
| **GM-4** | If signal CV `<= cv_tol` but claimed_gain CV `> cv_tol`, the gain spread = extraction artifact. | Documented case with flat physical signal + variable money classified as productivity. |
| **GM-5** | If the signal collapses toward 0 in pre-industrial / off-grid substrate, the gain is substrate-dependent, not universal automation. | Off-grid deployment with signal at full industrial parity. |

Worked demo: 4 industrial regimes (US/Germany/Vietnam/China) +
off-grid rural — physical signal CV 0.0 across industrial, claimed
gain CV 0.69, off-grid signal 12% of industrial → classified
EXTRACTION ARTIFACT + SUBSTRATE-DEPENDENT.

## SP — Substrate Parity Audit

Test for the claim "AI development is decoupled from substrate /
humans." Human cognition and AI compute occupy one substrate
envelope; AI fails through the human-maintenance coupling.

| ID | Statement | Falsifier |
|---|---|---|
| **SP-1** | Human and AI occupy one substrate envelope; neither is substrate-independent. | Sustained AI operation in a substrate state lethal to local human maintainers. |
| **SP-2** | A constraint is BREACHED when current value falls outside its viability window `[lo, hi]`. | Audit treating an out-of-window value as in-window. |
| **SP-3** | `margin` := signed normalized distance to nearest edge (<0 = breached); the constraint with the smallest margin names the first failure mode. | First-failure attribution to a non-minimum-margin constraint. |
| **SP-4** | AI fails effectively if its hardware window is breached OR any maintainer-critical human constraint is breached (maintenance coupling). | Sustained AI operation through human-maintainer collapse without alternative maintenance. |
| **SP-5** | A closed-loop private exception (private O2 / private cooling) is held aside, never credited: finite energy in, entropy monotone up → cannot hold the window indefinitely. | Indefinite closed-loop substrate exception with no external resupply. |

Worked demo: 6-constraint local-substrate state (O2, SO2, salinity,
ambient temp, radiation, grid stability) → STATUS RED, first failure
mode `SO2_load` with `human_m=-10.000, ai_m=-1.000`.

## TE — Thermodynamic Exception Detector

Test for the private-exception move ("I'll maintain my own
[O2 / cooling / water] indefinitely with a closed loop"). A loop is
simulated cycle-by-cycle with imperfect regen, decay, and a finite
reservoir; "indefinite" is falsified the moment `t_fail < inf`.

| ID | Statement | Falsifier |
|---|---|---|
| **TE-1** | Real closed loop: `loss_per_cycle > 0` and `0 < eta0 < 1` (no perfect seal, no perfect regen). | Demonstrated steady-state loop with `loss=0` or `eta=1`. |
| **TE-2** | Maintenance energy per cycle is monotone non-decreasing as efficiency decays. | A loop whose per-cycle maintenance cost falls as `eta` decays. |
| **TE-3** | "Maintained indefinitely" is falsified iff `t_fail < inf`. | Indefinite-survival claim accepted when the simulator returns finite `t_fail`. |
| **TE-4** | `t_fail < inf` whenever (reservoir finite) OR (efficiency decay `d > 0`). Both hold physically. | Physically-grounded loop with finite reservoir or `d > 0` that the audit rates as indefinite. |
| **TE-5** | A claim survives only by asserting `d = 0` AND `reservoir = inf` AND `eta >= 1` → 2nd-law VIOLATION, flagged and not credited (this is the held-aside term from `SP-5`). | Audit that credits the `d=0, reservoir=inf, eta>=1` corner as a real exception. |

Worked demo: honest private-O2 loop (`eta0=0.92, decay=8e-4`, 50 000-J
reservoir, 1-hour cycles) → FALSIFIED at cycle 62 (~2.6 days);
"indefinite" marketing claim → VIOLATION held aside per TE-5.

## Test invariants

`tests/test_accounting.py` locks the load-bearing semantics:

| Test | Claim |
|---|---|
| `test_aa1_balanced_ledger_closes_GREEN` | AA-1 |
| `test_aa1_imbalanced_ledger_is_RED` | AA-1 + AA-4 |
| `test_aa2_mixed_units_force_RED` | AA-2 |
| `test_aa3_held_aside_does_not_net` | AA-3 |
| `test_aa5_plug_does_not_rescue_to_GREEN` | AA-5 |
| `test_gm1_signal_is_currency_free` | GM-1 |
| `test_gm4_extraction_artifact_detected` | GM-4 |
| `test_gm5_substrate_dependence_collapses_signal` | GM-5 |
| `test_sp3_first_failure_is_lowest_margin` | SP-3 |
| `test_sp4_ai_fails_through_maintenance_coupling` | SP-4 |
| `test_sp4_no_coupling_does_not_propagate` | SP-4 (negative) |
| `test_te3_finite_reservoir_falsifies_indefinite` | TE-3 + TE-4 |
| `test_te4_decay_alone_falsifies_indefinite` | TE-4 |
| `test_te5_asserted_corner_flagged_VIOLATION` | TE-5 |

14/14 pass.

## Relation to the C-series

The AA / GM / SP claims are **complementary** to the C000-C083
automation-scope-audit C-series:

- C020 (thermodynamic_accounting) is one application of AA-style
  closure to autonomous-trucking energy budgets.
- C047 (defensive spending as GDP) and the user-spec C081 (Gottman /
  cross-domain) are special cases of GM-4 detection in particular
  domains.
- C025 (Earth-system fragility) and C040 (degraded-mode capacity) are
  special cases of SP-4 maintenance coupling.
- TE-5 is the engine behind the `held aside` term in SP-5: any
  "private closed loop" exception must be run through TE before
  being credited.

When in doubt: domain-specific claim → C-series; reusable audit
primitive → accounting/ family.

## License

CC0 1.0 Universal.
