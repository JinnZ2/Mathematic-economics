WORK ORDER — Mathematic-economics, branch biological-load-accounting
File as v4. Keep v1–v3 untouched; keep records_v3.json beside new records.

CHANGE 1 — Decision-Exposure Coupling, PROVENANCE block, line after the closing brace
Replace:  # office seat writing about the floor = DERIVED at best, never OBSERVED
With:     # office, media or academic seat writing about the floor / cab = DERIVED at best, never OBSERVED
(restores v1 "media seat"; adds academic, matching current_seat options)

README: the 5 other v1->v3 wording changes are intentional (generalized across roles). Mark accepted.

NEW DOC — file as third document in same delivery, verbatim below.
Title: Engineered Stability: Overshoot, Coupling and Buffer Visibility

CC0. Co-authored. Status tags: OBSERVED / DERIVED / PROPOSED. Long-running research program. Companions: Decision-Exposure Coupling (canonical PROVENANCE, FALSE_DENOMINATOR, SENSOR_VALIDITY); Biological Load Accounting for Truck Drivers.

Stability can no longer be assumed; it has to be engineered. Overshoot is driven by delayed feedback, and delay is the one part of it that can be engineered. Direct sensor coupling and data hygiene shrink that delay. Buffers are the stability margin, and they are invisible by design, so they have to be inventoried before they run out.

## Core model (DERIVED from systems dynamics and control theory)

OVERSHOOT = {
  "requires": ["growth", "a limit", "delayed feedback"],   # Meadows et al. framing
  "limit": "physical, not negotiable (energy, materials, biology)",
  "engineerable": "feedback delay and noise",
  "outcomes": {
    "long delay / noisy sensors": "overshoot and collapse",
    "short delay / clean sensors": "damped oscillation or controlled descent",
  },
  "goal": "buy time for better solutions, technologies, energy pathways",
}

CONTROL = {
  "stability_margin": "shrinks with sensor latency and noise",
  "decoupled_decisions": "= added sensor delay -> late corrections -> amplified swings",
  "lever": "direct coupling: those who live the conditions report them, fast and clean",
}

## Efficiency vs. stability (DERIVED)

EFFICIENCY_TRAP = {
  "move": "cut what looks unused or redundant",
  "what is cut": "buffers, redundancy, slack = stability margin",
  "complexity_cost": "each added layer costs more energy to maintain (Tainter, diminishing returns)",
  "result": "brittleness without removing the energy burden",
  "check_first": "efficient toward whose goal? (name it before cutting)",
}

## Buffer visibility (OBSERVED principle, PROPOSED method)

A buffer works by not being noticed. That makes it the first thing cut and the last thing measured. A buffer only protects you while you know it's there.

BUFFER_RECORD = {
  "name": None,
  "domain": None,           # energy, food, water, labor, biology, materials, social, time
  "function": None,         # what failure it absorbs
  "visible_to": None,       # who knows it exists
  "size_now": None,
  "size_then": None,        # trend: shrinking / stable / growing
  "refill_rate": None,
  "draw_rate": None,
  "sensor": None,           # who or what measures it; validity per SENSOR_VALIDITY
  "failure_mode_if_gone": None,
  "status": None,           # OBSERVED / DERIVED / PROPOSED
}
# None = void (unassessed), never treated as zero or as safe

BUFFER_EXAMPLES = [
  "driver following distance (3 s+) — erased ~300x/day",
  "worker homeostasis reserves across a shift or run",
  "dock crew goodwill (carryover between drivers)",
  "time slack in schedules (HOS, delivery windows)",
  "unpaid community repair and volunteer capacity",
  "forest, soil, water reserves",
]

## Research program (open)
- Common denominators across domains: energy (joules), time (hours), biological need-states
- Measured feedback delay per decision chain: event -> sensor -> decision -> action
- Buffer inventory per domain, with trend
- Historical cases: civilizations and technologies where efficiency cuts removed buffers before collapse
- Experiments: sensor latency vs. overshoot magnitude in small systems (stdlib sims, phone-buildable)
- Thresholds: when a shrinking buffer becomes a forcing event

CHECKER
- Rerun all checks; add new doc to hash set and records.
- New doc: BUFFER_RECORD voids counted as void, never zero/safe.
- Flag Meadows and Tainter as outside figures NOT OPENED.
- Report pass/fail, void count, strings not found in source.
Commit + push, no PR. Observer slots: null.
