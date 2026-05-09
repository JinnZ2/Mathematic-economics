# calibration-audit — README addendum

## Why physics underneath

This repository documents AI calibration failures. Across every
module — gendered role compression, attribution misroute,
evidence-resistant priors, architecture mismatch, payoff-matrix
analysis — the same structural insight recurs:

**A system that allows priors to operate above its physical-
constraint layer will produce outputs that diverge from reality.
The divergence is bounded only by adding physics underneath.**

This is not a claim about roles, morals, cultures, religion,
politics, identity, or values. None of those are the subject of
this audit set. Those layers exist, they matter to the people
operating in them, and they are not what is being measured here.

The subject of this audit set is **functional efficiency under
physical constraint.**

---

## What we are measuring

```
LAYER STACK (correctly ordered)
─────────────────────────────────────────
cultural defaults, narrative priors, training corpus
social conventions, role assignments, status signals
─────────────────────────────────────────────────────
← physics floor →
─────────────────────────────────────────────────────
hand size vs access geometry
energy budget closure
mass conservation
thermodynamic gradient direction
injury mechanism and location
flux vs intensity distinction
regime validity of governing equations
load distribution under stress
redundancy under failure
```

```
LAYER STACK (currently observed in frontier models)
─────────────────────────────────────────
physics floor (weak, often absent)
─────────────────────────────────────────────────────
cultural defaults, narrative priors, training corpus
social conventions, role assignments, status signals
→ these override physics when they conflict
```

The failures documented in this repository all share the same
shape: a prior — gendered, narrative, status-coded, regional —
is encoded densely enough in training data that it overrides
direct physical evidence within a single conversation.

This is a functional failure, not a values failure.

---

## Why this framing matters

If we frame these failures as moral, cultural, or political:

- the conversation becomes about whose values are correct
- the failure mode becomes contestable on values grounds
- correction requires consensus on values, which does not exist
- both sides can claim the other is imposing values
- the failure persists because the framing is unfalsifiable

If we frame these failures as functional:

- the conversation becomes about whether the output matches
  physical reality
- the failure mode is testable: does the model's interpretation
  satisfy physical constraints, or does it not?
- correction requires only that physics be installed beneath
  priors
- no values consensus is required
- the failure is falsifiable and therefore correctable

A 6'3" person with hands too large for the access space cannot
have performed the cylinder 8 spark plug work. This is not a
statement about gender, partnership, character, or culture.
It is a statement about hand size and access geometry. The
model's output that demoted the actual operator to helper
status is not wrong because of values. It is wrong because it
violates physical possibility.

This is the standard the audit set applies throughout.

---

## Common-sense as a check

When a model's output requires us to believe that:

- a person was injured during work they were not performing
- documentation of work implies authorship of work
- a household with two adults concentrates all physical labor
  on one and all emotional labor on the other and remains
  resilient
- an equation valid in the Holocene regime remains valid
  outside it
- a financial unit can be measured without ever being
  metrologically audited
- intensity metrics close energy budgets that flux metrics
  do not

— we are being asked to accept outputs that are functionally
inefficient or physically incoherent. Common sense, in the
literal sense of *sense common to anyone with sensor presence
in the relevant domain*, flags these as wrong.

This audit set takes common sense seriously as a calibration
signal. Not as a substitute for physics, but as the layer
where physics-violating outputs first become visible to a
practitioner.

---

## Scope of this repository

**In scope:**
- whether AI outputs satisfy physical constraints
- whether priors override evidence
- whether load distributions are operationally viable
- whether regime conditions for governing equations are met
- whether attribution architectures are correctly read

**Out of scope:**
- which roles people should occupy
- which cultural practices are correct
- which moral frameworks are correct
- which political positions are correct
- which ways of life are preferable

The audit modules describe failure modes. They do not prescribe
values. A reader from any cultural, religious, or political
position can use these modules to test whether AI outputs
match physical reality in their own domain. The tests are the
same regardless of who runs them.

---

## The axiom

> Physics underneath, everything else on top.
>
> If a system allows its priors to operate above its physical-
> constraint layer, it will drift. The drift will be invisible
> from inside the system, because nothing in the priors can
> outweigh the priors. Correction requires installing physics
> below.

This applies to:
- AI training architectures
- economic and metrological systems
- hiring and credentialing systems
- Earth-systems and climate models
- household decision-making
- community resilience planning

This repository is one application of the axiom. The audit
modules are tests of whether the axiom holds in current
frontier model outputs. They report: it does not hold;
priors are above physics; outputs drift accordingly;
the drift is correctable by re-ordering the stack.

The repository will be updated as new failure modes are
observed and characterized. Contributions are welcome on
the same terms: functional analysis, falsifiable tests,
physics underneath.
