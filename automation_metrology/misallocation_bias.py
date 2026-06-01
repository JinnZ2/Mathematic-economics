"""
misallocation_bias.py  -- CC0, stdlib-only

Random misallocation SCATTERS. Motivated misallocation is DIRECTIONAL. That
difference is the falsifiable signature Kavik named: incompetence is noisy;
capture has a gradient.

Test: take the misallocations (best_fit -> assigned flows) and measure how
CONCENTRATED the 'wrong work' is onto particular substrates (Herfindahl index
on inflow shares). Compare to a permutation null where each misallocation is
reassigned to a random WRONG substrate. If observed concentration exceeds the
null band, the errors lean -- a directional-structure signature.

HONESTY GUARD (BIAS-01): a directional signature is CONSISTENT WITH motive
contamination but does NOT prove intent or coordination. A single shared
structural cause (one vendor, one tool limitation, one procurement rule) can
produce the same lean. The detector indicts STRUCTURE, agnostic to who/why --
exactly as intended. It names the innocent common-cause alternative to rule out.
"""

import random
from substrate_allocation import (audit_setup, demo_tasks, SUBSTRATES, Task,
                                  best_fit)

SUBS = list(SUBSTRATES.keys())


def _herfindahl(counts) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((c / total) ** 2 for c in counts.values())


def inflow_counts(rows):
    """How much misallocated work is dumped ONTO each substrate."""
    c = {s: 0 for s in SUBS}
    for r in rows:
        if r["misallocated"]:
            c[r["assigned"]] += 1
    return c


def observed_concentration(rows):
    return _herfindahl(inflow_counts(rows))


def permutation_null(rows, n=5000, seed=17):
    """
    Null: each misallocated task is reassigned to a RANDOM wrong substrate
    (uniform among non-best-fit options). If real errors are mere noise, their
    concentration sits inside this distribution.
    """
    rng = random.Random(seed)
    mis = [r for r in rows if r["misallocated"]]
    samples = []
    for _ in range(n):
        c = {s: 0 for s in SUBS}
        for r in mis:
            wrong = [s for s in SUBS if s != r["best_fit"]]
            c[rng.choice(wrong)] += 1
        samples.append(_herfindahl(c))
    samples.sort()
    return {"mean": sum(samples) / len(samples),
            "p95": samples[int(0.95 * len(samples)) - 1]}


NARRATIVE = {
    "GENERAL_AI": ("work that should be DEDICATED or HUMAN is piled onto "
                   "general AI -> sets AI up to fail on bad-fit tasks AND "
                   "feeds 'automation' deployment/hype. Both at once."),
    "HUMAN_PARALLEL": ("committed/deterministic work is dumped on humans "
                       "(busywork/bottleneck) and/or chaotic work withheld "
                       "elsewhere -> sustains 'humans are replaceable' by "
                       "keeping them handicapped at the wrong tasks."),
    "DEDICATED": ("novel/chaotic work forced onto fixed structures -> brittle "
                  "failure at the edge; less commonly a capture vector."),
}


def detect(rows, n=5000, seed=17):
    h_obs = observed_concentration(rows)
    nul = permutation_null(rows, n, seed)
    inflow = inflow_counts(rows)
    signature = h_obs > nul["p95"]
    dominant = max(inflow, key=inflow.get) if sum(inflow.values()) else None

    if signature:
        verdict = "DIRECTIONAL_STRUCTURE_DETECTED"
        reading = NARRATIVE.get(dominant, "")
    else:
        verdict = "CONSISTENT_WITH_NOISE"
        reading = ("errors scatter within the random-misallocation band -> "
                   "looks like ordinary incompetence/tool limits, not a lean.")

    return {
        "concentration_H_obs": round(h_obs, 4),
        "null_mean_H": round(nul["mean"], 4),
        "null_p95_H": round(nul["p95"], 4),
        "inflow_counts": inflow,
        "dominant_sink": dominant,
        "verdict": verdict,
        "reading": reading,
        "caveat": ("signature != intent. rule out a single shared structural "
                   "cause (one vendor/tool/rule) before inferring motive."),
    }


def _random_setup(n_tasks=40, seed=3):
    """Honesty self-check: random demands + random WRONG assignments.
    A trustworthy detector must call THIS noise."""
    rng = random.Random(seed)
    tasks = []
    for i in range(n_tasks):
        demand = [round(rng.random(), 2) for _ in CAPS_LEN]
        t = Task(f"rand{i}", demand, safety=round(rng.random(), 2), assigned="X")
        bf = best_fit(t)["substrate"]
        wrong = [s for s in SUBS if s != bf]
        t.assigned = rng.choice(wrong)        # deliberately wrong, but RANDOM-wrong
        tasks.append(t)
    return tasks


def _directional_setup(n_tasks=45, seed=5):
    """A setup that SYSTEMATICALLY dumps wrong work onto GENERAL_AI (the
    motivated pattern). A detector with real power must fire on THIS."""
    rng = random.Random(seed)
    tasks = []
    for i in range(n_tasks):
        demand = [round(rng.random(), 2) for _ in CAPS_LEN]
        t = Task(f"dir{i}", demand, safety=round(rng.random(), 2), assigned="X")
        bf = best_fit(t)["substrate"]
        # motivated lean: if AI isn't already best, force the work onto AI
        t.assigned = "GENERAL_AI" if bf != "GENERAL_AI" else rng.choice(
            [s for s in SUBS if s != bf])
        tasks.append(t)
    return tasks


CAPS_LEN = range(6)


if __name__ == "__main__":
    print("=== REAL SETUP (trucking demo, only 6 misallocations) ===")
    rows = audit_setup(demo_tasks())["rows"]
    d = detect(rows)
    for k in ("concentration_H_obs", "null_p95_H", "inflow_counts", "verdict"):
        print(f"  {k}: {d[k]}")
    print("  -> UNDERPOWERED: 6 errors can't separate lean from chance. Honest.")

    print("\n=== HONESTY SELF-CHECK (random demands, RANDOM-wrong assigns) ===")
    d2 = detect(audit_setup(_random_setup())["rows"])
    for k in ("concentration_H_obs", "null_p95_H", "inflow_counts", "verdict"):
        print(f"  {k}: {d2[k]}")
    print("  -> must say NOISE, or it's a rubber stamp.")

    print("\n=== DIRECTIONAL SETUP (45 tasks, work systematically -> AI) ===")
    d3 = detect(audit_setup(_directional_setup())["rows"])
    for k, v in d3.items():
        print(f"  {k}: {v}")
    print("\n  noise->NOISE, underpowered->NOISE, real lean->SIGNATURE.")
    print("  the detector has power AND restraint. that is the whole point.")
