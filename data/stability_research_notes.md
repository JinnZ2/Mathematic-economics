# Stability / Time-to-Collapse Research Notes

CC0. Starter notes for the predictive-modeling work withdrawn from
`README.md` per `AUDIT_TASKS_HARDENING.md` H1.1 + H1.2.

The descriptive equations (1-13) in `README.md` + `equations.yaml`
measure *current* structural state. They are silent on *when* a
system in a given state transitions to instability. Closing that gap
requires empirical work that is not yet done here.

---

## What the withdrawn equations claimed

Two composite equations were withdrawn in 2026-05:

1. `S = 1 / [(RI × UFR × DI) + ER]` — purported "stability" scalar.
2. `T = W / (ER × UFR × DI)` — purported "time to collapse".

Both failed the H1.1 / H1.2 audit gate:

- **Dimensional inconsistency**. RI is a per-capita risk ratio, UFR
  is a wealth-growth-rate ratio, DI is a power-concentration count,
  ER is a fractional rate. Multiplying them produces a number with no
  physical interpretation.
- **Unsourced historical comparison**. The S values reported for
  1789 France and 1917 Russia were not derived from documented
  pre-revolution data; they appeared to be back-fit illustrative
  numbers chosen to bracket the contemporary-US estimate.
- **No falsifier**. The formulas could not be wrong; any new value
  of S could be declared "within the historical instability range"
  by adjusting which historical points define the range.

The structural critique (high concentration + extraction + risk
inequality → unstable systems) is well-supported in the literature.
The *specific composite formula* was not. The literature pointer is
the right citation; a back-of-envelope multiplication is not.

## Starter design for replacement work

If a future contributor wants to attempt Option A from H1.1:

1. **Pick the documented historical instability events.** Minimum
   set: France 1789, Russia 1917, Germany 1933, US 1929, Iran 1979,
   USSR 1989, global financial 2008. Plus stable controls: US
   1955-65, Switzerland 1980-2020, Japan 1990-2020.

2. **For each event, find the measured pre-instability values** of
   each canonical equation (VE/VL, SID, RI, DI, LWR, MSI, BSC, MM,
   ISR, UFR, ER, HHI, SD) in the 5-year window before the event.
   Sources: Piketty & Saez wealth share series, Bank of England
   1700+ rate series, Maddison Project GDP series, Bardhan inequality
   data for India, Atkinson historical Gini estimates.

3. **Fit a regression** (logit on `unstable_within_5yr` or Cox
   proportional-hazards on `years_until_unstable`) against the
   pre-instability values. Report the coefficients with confidence
   intervals.

4. **Validate** on held-out events not used in fitting.

5. **Document the falsifier**: e.g., "if observed event-onset
   probability for high-concentration states (HHI > 4000, UFR > 25)
   falls below 0.30 in 5-year window across 5+ historical cohorts,
   the model is refuted."

## Literature pointers

- Acemoglu & Robinson, *Why Nations Fail* (2012) — institutional
  preconditions for collapse.
- Turchin, *Secular Cycles* (2009) — cliometric model of elite
  overproduction + instability cycle.
- Piketty, *Capital in the Twenty-First Century* (2014) — wealth
  share time series across countries.
- Tainter, *Collapse of Complex Societies* (1988) — diminishing-
  returns / complexity-collapse framing.
- Diamond, *Collapse* (2005) — environmental + governance pre-
  collapse case studies.
- Wright, *Class, Crisis and the State* (1978) — Marxist structural
  analysis of capitalist instability.
- Goldstone, *Revolution and Rebellion in the Early Modern World*
  (1991) — comparative analysis of 1640-1840 instability events.

## Status

Open research area. No equations should be added to README.md without
satisfying the H1.1 acceptance criteria.

License: CC0 1.0 Universal.
