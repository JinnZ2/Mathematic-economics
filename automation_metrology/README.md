# automation-metrology-audit  (CC0, stdlib-only)

The claim "automation beats human labor" rests on an invalid measurement. This
audit makes the rig explicit and reduces the whole question to numbers you can
clock in a real yard.

## THE RIG

```
What industry measures:   BOTTLENECKED human   vs   UNENCUMBERED automation
                          (mandatory tiny-screen           (logs straight
                           data entry, GPS gates,            from sensors,
                           manual address fixes)             no data-entry tax)

What a valid test needs:  UNENCUMBERED human   vs   automation
                          (paper folder, parallel
                           cognition, no tax)

The data-entry + GPS tax has NO automation analog. It is an ARTIFICIAL handicap
applied to one side of the scale.
```

## MODULES

```
decision_tree_energy.py        nodes + dependencies + energy/time per node.
                               automation traverses SERIAL with retries on
                               violation; human handles the tree in PARALLEL
                               at flat marginal cost.

automation_step_ledger.py      Kavik's enumeration, executable. 31 atomic
                               perceive/decide/validate/act steps for one
                               yard-pickup+fuel cycle (16 verbatim + 15
                               continuation). 12 re-run on constraint violation.
                               -> the COUNT is the argument.

automation_metrology_audit.py  three configs (baseline human / bottlenecked
                               human / automation), continuous compute draw,
                               crossover sweep, and a self-detecting verdict:
                               METROLOGY_INVALID / HUMAN_WINS_OUTRIGHT /
                               CLAIM_FALSIFIED.
```

## THE TWO HONEST FINDINGS

```
1. TIME reduces to ONE measurable unknown: seconds per validate-decide cycle.
   With placeholder step-times the 31-step cycle sums to ~650 s (faster than
   the ~1050 s human). Crossover k = 1.62: if real per-step times average just
   1.62x the guesses, automation is already slower. The 'speed' is an
   assumption, not a physics result. MEASURE THE PER-STEP SECONDS.

2. ENERGY favors the human regardless of the time outcome, once you count the
   perception/planning stack drawing ~1 kW CONTINUOUSLY (not just per decision).
   Human:      ~365 kJ/unit
   Automation: ~920 kJ/unit (guessed time) ... ~2760 kJ/unit (observed time)
```

## THE METROLOGY IS THE POINT (claims)

```
MET-01  the benchmark compares unequal encumbrance. FALSIFIER: show the mandated
        human inputs are also required of and timed against the automation.
MET-02  removing the handicap inverts the time result. FALSIFIER: fair advantage
        stays >= 1 after the tax is removed.
MET-03  automation decision-energy scales with violation_rate x backtrack; human
        absorbs violations in parallel. FALSIFIER: no crossover across plausible
        violation rates.
```

## RUN

```
python3 decision_tree_energy.py        # the asymmetry, minimal
python3 automation_step_ledger.py      # the 31-step enumeration + crossover k
python3 automation_metrology_audit.py  # three configs + verdict (guessed & observed)
```

## TO MAKE IT BITE

Clock a real yard. Replace the ARCH per-step durations in
automation_step_ledger.py with measured seconds, and pass your observed
automation cycle time into metrology_verdict(observed_automation_cycle_s=...).
The model already says the answer hinges on exactly those numbers – the ones
nobody publishes head-to-head. Demand the measurement.

stdlib only. no numpy. no network. runs from a phone.
