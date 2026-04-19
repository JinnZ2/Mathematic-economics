# Failure Modes

Detailed specification of the five compounding measurement failures
that together produce the industrial workforce crisis narrative.

Each section follows the same structure:

```
MECHANISM      — what the failure IS, as an energy/information flow
OBSERVABLES    — what the organization sees from inside
DATA SIGNATURE — what the failure looks like in audit data
FALSIFIABILITY — how to test whether this mechanism is active
```

---

## L1: Attribution capture

### Mechanism

```
  POINT OF OBSERVATION         POINT OF REPORTING
  (floor, field, cab)          (office, exec)
  ────────────────             ──────────────────
  sees anomaly                 reframes in office vocabulary
  has tacit knowledge    →     strips attribution
  pattern-matches                adds "analysis"
  against direct contact        presents to decision authority
                                receives credit
                                receives conditioning subsidy
                                  (HVAC, salary-embodied energy,
                                   equipment)
```

The thermodynamic accounting:

```
  office role conditioning stack per quarter:
    HVAC + lighting + space:      ~5 × 10¹⁰ J
    salary + benefits (embodied): ~2 × 10¹² J
    equipment:                    ~1 × 10¹⁰ J
    TOTAL:                        ~2 × 10¹² J

  to break even on one "good decision per quarter," that
  decision must move >$40-60k of real downstream work.

  most quarterly strategic decisions don't clear this bar.
  the ones that do are usually laundered from floor.
```

### Observables

- "Hero" managers who always seem to be the ones with the good ideas
- Floor workers whose suggestions "don't make it" to leadership
- Strategic decisions attributed to executives that track back to
  customer-facing or shop-floor observation
- A reporting layer that rephrases, reframes, and re-owns insights
  before they reach decision authority

### Data signature

Under provenance audit, with timestamped records of where anomalies
were first detected vs. where they were "decided":

```
  sim baseline (50 floor / 15 office / 3 exec, 8 quarters)

  CURRENT SYSTEM (credit by reporting point)
    floor:     efficiency 0.25   (net loss)
    office:    efficiency 3.68   ("heroes")
    exec:      efficiency 0.18   (net loss)

  PROVENANCE AUDIT (credit by generation point)
    floor:     efficiency 3.21   (actual engine)
    office:    efficiency 0.37   (net loss)
    exec:      efficiency 0.003  (near-zero)

  CAPTURE MAGNITUDE
    floor:     -221 TJ (value reassigned AWAY)
    office:    +216 TJ (value reassigned TO)
    exec:      +5 TJ  (value reassigned TO)

  sign-stable across 30 seeds (30/30)
```

### Falsifiability

If L1 is NOT active at a given facility:

- Provenance tracking will show floor efficiency ≤ office efficiency
- Floor workers' insight attribution rate will match office's
- Credit retention rates will be within 0.1 of each other
  across all roles
- Time-to-decision after observation will not correlate with
  hierarchical distance from observer

If any of these fail, L1 is active. Magnitude is the distance
between observed and symmetric credit retention.

---

## L2: Competence-weighted trust decay

### Mechanism

```
  detection_rate(worker) = 0.02 + 0.28 × competence

  high competence → high insight rate
                 → high laundering exposure per unit time
                 → faster trust decay
                 → earlier disengagement
                 → earlier exit

  the filter runs continuously on every capture event:
    IF competence > threshold:
        worker detects → trust erodes → worker exits
    ELSE:
        worker stays → reproduces
```

The organization runs a competence-NEGATIVE selection process
on itself, continuously, while believing it is meritocratic.

### Observables

- Best workers leave first, often unexpectedly
- "Good attitude" and "team player" become code for low detection
  of attribution capture
- High performers get labeled "difficult" before leaving
- Retention bonuses don't work on the people leaving (trust, not price)
- Exit interviews report reasons management considers irrational
  or petty; the real reason is usually accurate but not legible
  to the interviewer

### Data signature

```
  trust trajectory by competence quintile (20 quarters)

  quarter   Q1 (low)  Q2    Q3    Q4    Q5 (high)
       0     0.97    0.93  0.90  0.93   0.87
       4     0.82    0.63  0.53  0.53   0.45
       8     0.68    0.47  0.39  0.36   0.30
      12     0.57    0.38  0.31  0.29   0.24
      16     0.50    0.33  0.25  0.25   0.21

  Q5 half-life ≈ 4 quarters
  Q1 half-life ≈ 18 quarters
  competent workers detect capture ~4.5x faster

  EXIT SELECTION at Q20:
    exited   (n=23): mean competence 0.78
    remained (n=27): mean competence 0.52
    gap: +0.26 (+50%)
    sign-stable across seeds (3/3)
```

### Falsifiability

If L2 is NOT active:

- Exit rates will be approximately uniform across competence bands
- Tenure-weighted competence of active staff will match or exceed
  tenure-weighted competence of departures
- "Best performers" (by actual output, not manager rating) will
  have longer-than-average tenure

If exit rates are elevated in the top competence quintile,
or "best performers" consistently leave before 5-year mark,
L2 is active.

---

## L3: Sector-level reputation filter

### Mechanism

```
  applicant.willingness_threshold = 0.10 + 0.65 × competence

  competent applicants can read the sector signal better,
  AND they have alternatives, so their minimum-reputation
  threshold is higher.

  facility.reputation = f(floor_trust,
                          floor_burnout,
                          recent_exit_stories)

  applicant accepts facility ONLY IF
    applicant.willingness_threshold ≤ facility.reputation

  result:
    captured facilities (reputation ~0.3) only successfully
    hire from the low-threshold tail of the pool
    (applicants with competence < 0.4)

    functional facilities (reputation ~0.6) successfully
    hire across the full distribution
```

### Observables

- "Can't find qualified workers"
- "The applicants we get can't pass a drug test"
- "New hires last two weeks then disappear"
- "Our training program produces good workers who immediately
  leave for [competitor]"
- Workforce average skill declining year-over-year despite
  stable or rising credential requirements

### Data signature

```
  sector sim, 5 captured + 2 functional facilities, 20 quarters
  shared labor pool of 1500 applicants

  REPUTATION FIELD AT Q20:
    captured:    avg reputation 0.36
    functional:  avg reputation 0.56

  NEW HIRE COMPETENCE (last 10 quarters):
    captured:    mean competence 0.30  ← "unskilled labor"
    functional:  mean competence 0.76  ← "great applicant pool"
    delta:       0.46 competence points

  OUTPUT (insights/quarter, last year):
    captured:    16.6
    functional:  64.6
    ratio:       3.9×

  LABOR POOL COMPOSITION:
    Q0:  1500 applicants, avg competence 0.571
    Q19: 1424 applicants, avg competence 0.579

    pool average is RISING over time because competent
    applicants stay in pool while low-competence ones
    are absorbed by captured facilities
```

### Falsifiability

If L3 is NOT active at sector scale:

- New hire competence distribution will match applicant pool
  competence distribution
- Reputation signal (measurable via turnover, Glassdoor-style
  ratings, referral rates) will not predict new hire quality
- Wage premiums will effectively lift new hire competence

If sector hiring disproportionately draws from low competence
regardless of wage, and if reputation correlates with new hire
quality across facilities, L3 is active.

---

## L4: Wage-lever ineffectiveness

### Mechanism

```
  effective_threshold(applicant, wage_boost) =
    applicant.willingness_threshold
    - (1 - 0.7 × applicant.competence) × (wage_boost/100)

  competent applicants discount wage more heavily because
  they have alternatives AND they know that wage compensates
  for reputation risk asymmetrically.

  wage boost dollars buy competence points at a DECREASING rate.
```

### Observables

- Pay increases that don't solve turnover
- "We raised pay 20% and it didn't help"
- Sign-on bonuses that attract people who leave during probation
- Wage inflation across the sector without corresponding
  workforce quality improvement
- Executives frustrated that "the market is broken"

### Data signature

```
  wage intervention experiment (captured facilities)

  wage boost    new hire competence    reputation
  ─────────    ───────────────────    ──────────
  0%            0.28                   0.35
  10%           0.36                   0.34
  25%           0.39                   0.33
  50%           0.53                   0.32
  100%          0.53                   0.36  ← asymptote

  at 100% boost (DOUBLE PAY):
    still can't match functional facility hiring (0.76)

  functional facility baseline:
    new hire competence 0.76 at STANDARD pay

  the functional facility is hiring better workers
  for less money because trust, not price, is the
  active signal.
```

### Falsifiability

If L4 is NOT active:

- Wage increases will produce linear improvement in new hire
  quality
- Sector-wide wage inflation will track workforce quality
  improvement
- Functional facilities will lose hires when captured
  competitors raise wages

If new hire quality plateaus under increasing wages, and if
functional facilities retain hiring advantage despite wage
parity or disadvantage, L4 is active.

---

## L5: Literacy-biased skill measurement

### Mechanism

Four orthogonal capacity dimensions collapsed into one scalar
measurement:

```
  ACTUAL DIMENSIONS (roughly independent):
    embodied_skill      — hours of direct contact with the system
    cognitive_fluency   — pattern-match, systems thinking, improvisation
    literacy_score      — reading speed, test performance
    domain_specificity  — how tied to THIS plant/machine

  WHAT ACTUAL CAPACITY REQUIRES:
    productive_capacity ≈ 0.55 × embodied
                        + 0.35 × cognitive
                        + 0.10 × literacy

  WHAT CERTIFICATION MEASURES:
    cert_signal       ≈ 0.15 × embodied
                        + 0.15 × cognitive
                        + 0.70 × literacy

  THE INVERSION:
    a dyslexic 27-year veteran:
      embodied 0.95, cognitive 0.85, literacy 0.25
      → actual capacity = 0.84
      → cert signal = 0.33

    a fresh graduate with certification:
      embodied 0.10, cognitive 0.55, literacy 0.80
      → actual capacity = 0.29
      → cert signal = 0.66

    cert signal RANKS the fresh graduate HIGHER
    than the 27-year veteran, by 0.33 points.
    actual capacity is INVERSE: veteran outperforms
    fresh graduate by 0.55 points.

    the measurement does not just fail.
    it systematically inverts for the population
    whose cognition doesn't run on symbols.
```

### Observables

- Dyslexic, innumerate-on-paper, or ESL workers classified "unskilled"
  despite decades of embodied competence
- Certificate-heavy hires who can't actually do the work
- "Knowledge transfer" initiatives that fail because the people
  being asked to transfer the knowledge have no mentees who can
  absorb it (or vice versa)
- Plant closures where skilled workers disperse into unrelated
  low-skill work because the labor market cannot see their skill
- "Apprenticeship is making a comeback" articles that miss that
  apprenticeship was killed by the same measurement apparatus
  that now cannot replace it

### Data signature

```
  Diamond Match case (30 vets including salvage engineers
  with 15% dyslexia rate, competing with 30 fresh grads)

  HR HIRES TOP 15 BY CERTIFICATION SIGNAL:
    6 veterans + 9 fresh grads
    avg actual capacity of hires: 0.68
    avg teaching capacity of hires: 0.68

  COUNTERFACTUAL: HIRING BY ACTUAL CAPACITY:
    15 veterans (including all salvage engineers,
                  including the dyslexic ones)
    avg actual capacity: 0.92
    avg teaching capacity: 0.94

  CAPACITY FOREGONE BY CERTIFICATION-BASED HIRING:
    -0.24 per hire (35% below achievable)
    -0.26 in teaching capacity (breaks future pipeline)

  SPECIFIC WORKERS LOST TO THE MEASUREMENT:
    27-year veteran, dyslexic, salvage engineer:
      cert signal 0.53 (rank 24 of 60)
      actual capacity 0.92 (rank 8 of 60)
      hired? NO
```

### Falsifiability

If L5 is NOT active:

- Task-based trials on actual equipment will rank workers
  the same way certifications do
- Dyslexic veteran workforce will be hired at population rates
- Mentorship programs will successfully produce skilled workers
  at scale

If task-based evaluation ranks workers differently than
certification does, especially for dyslexic/embodied-skilled
populations, L5 is active.

---

## Compound signature

When all five are active simultaneously (the typical case for
deindustrialized manufacturing corridors, long-haul trucking
at captured carriers, and distressed industrial sectors):

```
  SYMPTOMS AT THE SECTOR LEVEL:

  • "labor shortage"          (L3)
  • "skills gap"              (L5)
  • "wages not working"       (L4)
  • "workers unreliable"      (L2+L3, new hires are low-comp)
  • "young people won't work" (L3 again, with generational framing)
  • "certificates worthless"  (L5, + broken mentorship)
  • "we need automation"      (avoidance of L1-L5)
  • "we need immigration"     (avoidance of L1-L5)
  • "we need training $$"     (avoidance of L5 specifically)

  UNDERLYING PROCESS:

  L1 establishes the attribution subsidy
    → L2 drains competent workers over ~3-4 years
      → L3 degrades sector reputation
        → L4 blocks the wage-based fix
  L5 mislabels remaining experienced workers as unskilled
    → displaces them out of sector
      → breaks mentorship pipeline
        → new hires never reach capacity
          → reinforces L3

  the system is LOCALLY STABLE in the captured regime.
  every individual actor is responding correctly to the
  signals they can see. the signals they can see are
  systematically wrong because the denominators they
  use (dollars, certificates, headcount, cert_signal)
  do not measure the physical quantities (embodied skill,
  mentorship transmission, actual work moved, trust).
```
