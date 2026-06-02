"""
narrative_crossval.py  -- CC0, stdlib-only

The falsifier engine for EVT-01 / NAR-01.

Tests whether dated flood / island-subsidence narratives overlap predicted
high-probability windows MORE than a random-shuffle null. Also tests whether
the FULL model (alpha>0, deep-water baseline on) beats the NULL model
(alpha=0, fast-forcing only). If it does not, EVT-01 says: drop the baseline.

SHIPPED DATASET IS A PLACEHOLDER. Replace `NARRATIVES` with real, independently
dated entries (sediment cores, drowned-shoreline dates, oral-tradition
chronologies). Until then this proves the PIPELINE, not the CLAIM.
"""

import random
from coupled_model import run, event_probability


# placeholder: (label, central_date_BP, +/- uncertainty_yr)
# dates here are illustrative anchors near known deglacial water events.
NARRATIVES = [
    ("meltwater-pulse-1A horizon",       14600, 500),
    ("early-Holocene transgression",      9500, 600),
    ("Black-Sea / Doggerland type",       8200, 400),
    ("mid-Holocene high-stand",           6000, 700),
    ("late-Holocene subsidence cluster",  4200, 500),
]


def _prob_at(t_bp, s_base, alpha):
    return event_probability(t_bp, s_base, alpha=alpha)


def overlap_score(narratives, s_base, alpha, prob_floor=0.5):
    """Fraction of narratives whose window contains a high-prob model year."""
    hits = 0
    for _label, t0, dt in narratives:
        window = range(int(t0 - dt), int(t0 + dt) + 1, 100)
        if any(_prob_at(t, s_base, alpha) >= prob_floor for t in window):
            hits += 1
    return hits / len(narratives)


def monte_carlo_null(s_base, alpha, n_trials=2000, seed=12345,
                     t_min=2000, t_max=150000, prob_floor=0.5):
    """
    Null: scatter the SAME number of fake narratives at random dates with the
    same uncertainty distribution; measure expected overlap by chance.
    """
    rng = random.Random(seed)
    durs = [dt for _l, _t, dt in NARRATIVES]
    n = len(NARRATIVES)
    scores = []
    for _ in range(n_trials):
        fake = []
        for i in range(n):
            t0 = rng.randint(t_min, t_max)
            fake.append((f"rand{i}", t0, durs[i]))
        scores.append(overlap_score(fake, s_base, alpha, prob_floor))
    scores.sort()
    mean = sum(scores) / len(scores)
    p95 = scores[int(0.95 * len(scores)) - 1]
    return {"null_mean": mean, "null_p95": p95}


def evaluate(prob_floor=0.5):
    full = run(alpha=0.6)
    null = run(alpha=0.0)
    s_base = full["s_base"]

    obs_full = overlap_score(NARRATIVES, s_base, 0.6, prob_floor)
    obs_null = overlap_score(NARRATIVES, s_base, 0.0, prob_floor)
    mc = monte_carlo_null(s_base, 0.6, prob_floor=prob_floor)

    beats_chance = obs_full > mc["null_p95"]
    baseline_helps = obs_full > obs_null

    return {
        "observed_overlap_full": round(obs_full, 3),
        "observed_overlap_null": round(obs_null, 3),
        "chance_mean": round(mc["null_mean"], 3),
        "chance_p95": round(mc["null_p95"], 3),
        "beats_chance_p95": beats_chance,
        "deep_baseline_helps": baseline_helps,
        "verdict_EVT01": ("SUPPORTED (provisional, placeholder data)"
                          if (beats_chance and baseline_helps)
                          else "NOT SUPPORTED on current data -> "
                               "drop deep baseline per EVT-01 falsifier"),
    }


if __name__ == "__main__":
    r = evaluate()
    for k, v in r.items():
        print(f"{k:24s}: {v}")
    print("\nNOTE: NARRATIVES is a placeholder. Verdict is about the PIPELINE, "
          "not the world, until real dated entries replace it.")
