# Economic Definition Paradoxes: Addendum 4 - Falsifiable Audit of Automation ROI Claims

## The Operating Question

What would have to be true for the "automation is more efficient at scale"
narrative — applied specifically to autonomous trucking, but generalizable
to any AI deployment — to hold under physics-grounded accounting?

This addendum extends the 13 canonical equations to **33 falsifiable
structural claims (C000-C032)** about autonomous-trucking ROI, organized
in `automation_scope_audit/`. Each claim:

- has a measurable threshold,
- publishes a single-sentence falsifier,
- conforms to the `DIFFERENTIAL_FRAME.md` ontology (`dX/dt under scope`),
- cross-references one or more of the 13 canonical equations where the
  measurement domain overlaps.

The claims are **not predictions**. They are the structural conditions
that must hold for the narrative to be falsifiable; a deployment that
satisfies every threshold is one whose proponents have done the
accounting honestly. A deployment that satisfies few is one whose claim
is not yet admissible to physics-grounded analysis.

-----

## Why structural claims, not predictions

The 13 canonical equations in this repository (`equations.yaml`) measure
**current state** of an economic system. They are the falsifiable
diagnostics for whether the labels we apply to that system (capitalism,
socialism, mixed economy) describe the measured reality.

The automation ROI narrative is a **forward-looking claim**: "deploying
AI / autonomous systems at scale will reduce energy / labor / cost per
unit of output." The claim is forward-looking, but its **structural
preconditions** are present-tense and measurable. The 33 claims in
`automation_scope_audit/` measure those preconditions.

If C001 (route variance < 5%) does not hold, the narrative's geometric
precondition fails. If C020 (honest eROI >= 1.5) does not hold, the
energy precondition fails. If C025 (Earth-system precondition stability
in a 10-year window) does not hold, the substrate precondition fails.
None of these is a prediction — each is a measurable structural test
that the narrative quietly assumes.

-----

## Cross-references to the canonical 13 equations

Several claims overlap measurement domain with the canonical equations.
The full cross-reference table lives in
`equations.yaml::automation_scope_audit_claims:`. Representative
mappings:

| automation claim                          | canonical equation overlap        |
|-------------------------------------------|-----------------------------------|
| **C002** wellsite labor not automated     | LWR (Labor Wealth Ratio), VE_VL, ER |
| **C003** infrastructure capex             | SID (Socialist Infrastructure Dep.), ISR |
| **C006/C007** scope collapse + wage suppression | SD (Semantic Drift), LWR, UFR  |
| **C011/C013** middleware + distributed labor | VE_VL, LWR                     |
| **C014/C015** refusal authority + liability void | RI (Risk Inequality), BSC    |
| **C017** legal framework premium          | UFR (Upward Flow Rate), ISR, BSC  |
| **C020** honest eROI                      | MSI (Money Signal), ER            |
| **C021-C024** scaling / institutional dynamics | HHI, MM, DI                  |
| **C025/C026** Earth-system + double-bind  | BSC, ISR, DI, MM                  |
| **C027-C032** epistemic / engineering-grade | MSI, SD, BSC                    |

The cross-references make explicit what the canonical equations already
imply: the autonomous-trucking ROI narrative is **structurally
identical** to the broader narrative that the canonical 13 equations
measure. Both extract value through institutional / infrastructure /
labor channels that the narrative does not count.

-----

## The seven framings

The 33 claims cluster into seven structural framings, each making one
unstated precondition of the narrative explicit:

1. **Scope collapse** (C006/C007) — the marketing pitch collapses
   distinct labor categories (haul / navigation / site work /
   monitoring / compliance / interface) into a single "automation"
   category, prices only the easiest piece (interstate haul), and
   carries the resulting "savings" forward as if the rest had been
   accomplished. Same pattern as Smith-era equivocation between
   "free markets" and "regulated, subsidized, bailed-out markets."

2. **Unpriced infrastructure** (C003/C008) — the road, the HD maps,
   the receiving pads, the comms towers, and the driver's ~60
   minutes/day of DOT inspection are externalized to the road
   authority, the operator's unpriced labor, or future maintenance
   budgets. Same pattern as `SID > 0.5`: the system is majority-
   dependent on collectively-funded infrastructure.

3. **Interface externalization** (C011/C012/C013) — driver-mediated
   touchpoints (fuel, customer, dispatch, maintenance, regulatory,
   roadside, payment) are not eliminated by automation; they are
   externalized onto middleware (remote diagnostic center),
   heterogeneity (third-party variant handling), and distributed
   labor (mobile techs, customer service, on-call specialists)
   billed at a higher fully-loaded rate than the driver.

4. **Lifecycle mismatch** (C004/C005) — equipment depreciates over
   7 years against shale wells losing 70-80% of flow in year one.
   Same pattern as `ER` (Extraction Rate): the system is structurally
   short of the resource it depends on.

5. **Missing constraint-validation authority** (C014/C015/C016) —
   drivers carry legally-recognized refusal authority, override
   authority, and a settled liability chain. Autonomous stacks do not.
   The liability void across the 7-participant chain (OEM, software,
   sensor, map, fleet operator, remote operator, insurer) creates a
   residual unrecovered share that no insurance market can price.

6. **Institutional dynamics** (C022/C023/C024) — at scale,
   institutions develop lock-in that blocks optimization, exclude
   alternatives as "not scalable," and enter an accelerated collapse
   cycle when external variation arrives. Same pattern as `HHI > 2500`:
   high concentration creates brittleness.

7. **Energy / substrate accounting** (C020/C025/C026/C029/C030) —
   apparent eROI counts fuel saved against truck operations. Honest
   eROI must include server farm electricity, sensor manufacturing,
   rare-earth extraction, network transmission, and software / CI-CD
   energy. Under unified capital accounting with joules-equivalent
   denominators, large-scale deployments routinely show
   `non_financial_loss > financial_gain`: scaling is then *capital
   reallocation* from environmental / biological / temporal reserves
   into financial accounts, not capital *creation*.

-----

## Engineering-grade falsifiability

C031 / C032 generalize the framework: any economic model used for
billion-dollar deployment decisions must pass the four engineering-grade
preconditions (assumptions stated, validated across multiple market
regimes, design margin + failure modes enumerated, falsifiability
criteria published) — the same preconditions NASA / DNV / NRC require
before launching aerospace / offshore / nuclear systems. Most current
AI economic models satisfy zero of the four.

The cascade pattern is well-documented: LTCM 1998, 2008 quant collapse,
2010 flash crash, March 2020 treasury dislocation. Each was an AI
deployment on an economic model trained on a stable-period regime and
deployed into a volatile / supply-constrained / demand-shocked regime
the model had no mechanism to detect.

`C032` is the **structural prefix** to every historical cascade in the
financial-AI literature. Its registering against an automation
deployment is not a prediction; it is the observation that the
deployment is operating inside the same prefix.

-----

## What this addendum claims, and what it does not

- **Claims**: that the 33 structural conditions encoded in
  `automation_scope_audit/` are necessary preconditions for the
  autonomous-trucking ROI narrative to be honest; that the narrative
  systematically omits accounting for many of them; that the
  cross-references to the canonical 13 equations show this is the
  *same* structural pattern measured elsewhere in this repo.

- **Does not claim**: that automation is bad, that no autonomous
  deployment can succeed, or that the threshold lines are immutable.
  The works case (`kodiak_atlas_permian`) deliberately satisfies
  several thresholds; the framework is biased toward *honest
  accounting*, not refusal. Threshold values are 2025-era calibrations
  and should be re-checked as data evolves.

-----

## How to use this addendum

For each public automation ROI claim:

1. Run the claim text through
   `automation_scope_audit/modules/meta_scope_guard.c000_verdict`.
   If it fails to declare the seven scope dimensions (beneficiary,
   conditions, time period, resource, externalization, profit
   allocation, falsifier), it is structurally unfalsifiable and not
   admissible.
2. Pass the deployment spec through
   `automation_scope_audit/modules/scope_gate.scope_gate_verdict`. If
   the spec is incomplete, the audit refuses to run.
3. If admitted, run the full 33-claim audit
   (`automation_scope_audit/run.py`). Examine the cluster report
   (`--clusters`) for triggered cluster signatures.
4. Cross-reference the triggered claims against the 13 canonical
   equations to see which structural patterns are reinforced.

The output is not a prediction. It is a published, verifiable,
contract-validated record of which structural preconditions a
particular deployment claim has satisfied and which it has not. The
ledger (`epistemic_ledger.jsonl`) preserves every audit run with HMAC
chaining; tampering is detectable.

-----

## License

CC0 1.0 Universal (public domain).

*Companion documents: `addendum-1.md`, `addendum-2.md`, `addendum-3.md`
(definition paradoxes); `automation_scope_audit/README.md` (full
package documentation); `equations.yaml` (canonical 13 + 33
automation claims); `DIFFERENTIAL_FRAME.md` (ontology).*
