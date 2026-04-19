# workforce-attribution-audit

A falsifiable framework for diagnosing workforce dysfunction as a set of
measurement failures rather than labor supply problems.

## Core claim

What most industrial and manufacturing organizations report as

- "labor shortage"
- "unskilled applicants"
- "skills gap"
- "generational work ethic problems"
- "wages aren't working"

is not a set of separate supply problems. It is the externally-visible
signature of five compounding measurement failures, all of which are
traceable, quantifiable, and falsifiable from data the organizations
themselves already collect.

The sector is not short of workers.
The sector has a reputation field it generated itself.
The workers are routing around it.

## The five failure modes

```
LAYER 1: Attribution capture
  Credit for insights flows upward in the hierarchy.
  Floor workers generate; office workers report; office
  receives credit. Thermodynamically: the conditioning
  stack (HVAC, salary-embodied energy, equipment) subsidizes
  attribution rather than generation.
  → docs/failure_modes.md § 1

LAYER 2: Competence-weighted trust decay
  High-competence workers detect attribution capture FIRST
  because they generate more insights, experience more
  laundering events, and have stronger signal:noise for
  credit inversion. The organization selectively loses
  its highest-competence workers. The remaining population
  is less capable of reforming the system than the original
  was.
  → docs/failure_modes.md § 2

LAYER 3: Sector-level reputation filter
  Exit stories from competent workers degrade sector
  reputation. Competent applicants have higher willingness
  thresholds and route around captured facilities. Captured
  facilities hire from the low-threshold tail of the pool.
  The org observes "labor shortage" and "unskilled labor"
  when the actual mechanism is reputation-mediated sorting
  over a labor pool that is, on average, MORE skilled at
  the end of the degradation than at the start.
  → docs/failure_modes.md § 3

LAYER 4: Wage-lever ineffectiveness
  The signal competent applicants read is not price.
  It is trust. Trust is not purchasable. Raising wages
  draws additional low-threshold applicants and a modest
  premium of mid-threshold applicants. Top-threshold
  applicants remain unreachable via compensation.
  → docs/failure_modes.md § 4

LAYER 5: Literacy-biased skill measurement
  Certification systems weight literacy at ~70% of signal
  while actual productive capacity depends at ~90% on
  embodied skill and cognitive fluency. Dyslexic veterans
  with decades of embodied capacity register as "unskilled"
  by the measurement apparatus. Fresh graduates with no
  embodied hours register as "skilled." The measurement
  inverts the true competence ordering for a substantial
  fraction of the experienced workforce.
  → docs/failure_modes.md § 5
```

## Why these compound

```
    L5 mislabels veterans as unskilled
           ↓
    veterans displaced into non-skill-matched work
    (driving, warehousing, retirement, disability)
           ↓
    mentorship pipeline broken
           ↓
    new hires with certs never reach capacity
           ↓
    L2 accelerates: competent remaining workers
       detect the capacity gap and exit
           ↓
    L3: sector reputation drops
           ↓
    competent applicants route around the sector
           ↓
    L4: wage increases fail to fix it
           ↓
    org concludes "shortage" and "skills gap"
           ↓
    responses (automation, offshoring, immigration,
      training programs, lowered standards) all fail
      because none of them address the measurement
      problem
           ↓
    damage compounds; observable capacity continues
    to degrade; denominators used to describe the
    problem continue to measure the wrong thing
```

## The underlying metrology failure

All five failure modes are instances of the same deeper problem:
the measurement apparatus is denominated in quantities that are
easy to count (dollars, certificates, headcount, hours) rather
than quantities that close physically (embodied skill-hours,
actual work moved, teaching transfers completed, mentorship
chains unbroken).

This is the same problem addressed by `substrate_audit.py` in a
different domain: AI training data uses monetary denominators
that have never been metrologically validated against physical
quantities. Workforce measurement uses credential denominators
that have never been validated against productive capacity.

The fix, in both cases, is to denominate in physically-closing
units. See `measurement_problem.md`.

## Repository structure (this sub-module)

```
labor_thermodynamics/
├── README.md                          this file
├── failure_modes.md                   detailed spec of L1-L5
└── measurement_problem.md             metrology critique

visualizations/                        (at repo root)
├── attribution_sim.jsx                React L1 baseline simulator
│                                      (was attribution_sim.md — mislabeled)
└── labor_audit_protocol.html          rendered audit protocol
                                       (was audit_protocol.md — mislabeled)
```

> **Note:** Earlier drafts of this README referenced `sims/` and
> `audit/` sub-folders with Python simulators (`attribution_sim.py`,
> `trust_decay.py`, `full_system.py`, `sector_shortage.py`,
> `skill_measurement.py`, `workforce_audit.py`). Those files have
> not been imported into this repo yet — they are expected in a
> forthcoming drop. Until then, the JSX simulator in
> `visualizations/attribution_sim.jsx` covers the L1 baseline case.

## How to use this

If you are trying to diagnose a specific facility, sector, or policy
proposal:

1. Read `failure_modes.md` for the five mechanisms.
2. Read `measurement_problem.md` for why certifications
   and dollars are the wrong denominators.
3. Run `visualizations/attribution_sim.jsx` (L1 baseline) with
   parameters matching your case. Additional Python sims pending.

If you are trying to build a response that actually works:

- Wage increases alone will not help (L4).
- Automation alone will not help (L5 ensures automation has
  no one to run it).
- Immigration alone will not help (expands pool but reputation
  field still applies).
- Training programs alone will not help (L5 — no mentors left).
- The only response that addresses the actual mechanism is
  symmetric credit retention + direct embodied-skill assessment
  + mentorship pipeline repair. All three are required.

## Status

Framework: v0.1, falsifiable, dependency-free (stdlib only).
Sims: runnable, sign-stable across seeds.
Documentation: this commit.
Integration: connects to `substrate_audit.py`, `first_principles_audit.py`,
`PhysicsGuard`, and `institutional_thermodynamic_analysis` as shared
metrology framework.

CC0. No attribution required. Fork and modify freely.
