"""
paleoseismic_crossval.py  -- CC0, stdlib-only

The tighter falsifier. Two SEPARATE tests, because they are different claims:

  SYN-01  CO-DATING: do emergence narratives co-date with REGIONAL paleoseismic
          markers (turbidites, liquefaction features, tsunami deposits) better
          than a shuffle null?  This is the defensible, local claim.

  SYN-02  SYNCHRONY: is cross-continental temporal clustering of emergence
          events real, or just what independent regional seismicity produces by
          chance once dating uncertainty is smeared in?  This is the seductive
          claim, built to be KILLED unless the data is overwhelming.

ALL DATA HERE IS PLACEHOLDER. Replace with provenanced entries:
  - paleoseismic markers: dated turbidite/liquefaction/tsunami horizons + Mw est
  - emergence narratives: independently dated oral/written 'water-from-ground'
Until then this proves the PIPELINE, not the world.
"""

import random
from aquifer_pressure_head import emergence_response

# (region, date_BP, +/- dt_yr, est_magnitude, site_distance_km_to_source)
PALEOSEISMIC = [
    ("Cascadia",      9000, 400, 9.0, 120),
    ("Cascadia",      4800, 300, 8.8, 150),
    ("Aegean",        8200, 500, 7.6, 60),
    ("Aegean",        3600, 350, 7.4, 80),
    ("Sunda",         7400, 600, 8.5, 200),
    ("Andes",         6000, 450, 8.7, 100),
    ("Japan",         5200, 300, 8.4, 90),
]

# (culture/region, date_BP, +/- dt_yr)
EMERGENCE_NARRATIVES = [
    ("PacificNW",  8800, 500),
    ("Mediterranean", 8100, 600),
    ("SE_Asia",    7500, 700),
    ("Andean",     6100, 500),
    ("Japanese",   5300, 400),
    ("Mesopotamian", 4500, 700),
]

# crude region adjacency: which paleoseismic regions a narrative could reflect
REGION_LINK = {
    "PacificNW": {"Cascadia"},
    "Mediterranean": {"Aegean"},
    "SE_Asia": {"Sunda"},
    "Andean": {"Andes"},
    "Japanese": {"Japan"},
    "Mesopotamian": set(),     # no linked marker in placeholder -> should miss
}


def _overlap(a0, da, b0, db):
    return abs(a0 - b0) <= (da + db)


def codating_hits(narratives, markers, s_base=0.0):
    """SYN-01: narrative counts as a hit if a LINKED marker overlaps in time
    AND that marker would actually force emergence at the site."""
    hits = 0
    for region, t0, dt in narratives:
        linked = REGION_LINK.get(region, set())
        hit = False
        for mr, mt, mdt, mM, mr_km in markers:
            if mr in linked and _overlap(t0, dt, mt, mdt):
                resp = emergence_response(mM, mr_km, s_base=s_base)
                if resp["class"] != "NONE":
                    hit = True
                    break
        hits += 1 if hit else 0
    return hits / len(narratives)


def codating_null(narratives, markers, n=3000, seed=7, s_base=0.0,
                  t_min=2000, t_max=12000):
    """Shuffle narrative dates uniformly; measure chance co-dating."""
    rng = random.Random(seed)
    scores = []
    for _ in range(n):
        shuffled = [(r, rng.randint(t_min, t_max), dt) for r, _t, dt in narratives]
        scores.append(codating_hits(shuffled, markers, s_base))
    scores.sort()
    return {"mean": sum(scores)/len(scores),
            "p95": scores[int(0.95*len(scores))-1]}


def synchrony_observed(markers, window_yr=600):
    """SYN-02: count cross-REGION marker pairs whose dates fall within window."""
    coincidences = 0
    for i in range(len(markers)):
        for j in range(i+1, len(markers)):
            if markers[i][0] != markers[j][0]:                  # different region
                if abs(markers[i][1] - markers[j][1]) <= window_yr:
                    coincidences += 1
    return coincidences


def synchrony_poisson_null(markers, window_yr=600, n=5000, seed=11,
                           t_min=2000, t_max=12000):
    """
    Independent Poisson null: keep each region's event COUNT, but redraw event
    dates uniformly+jitter per region independently. If observed cross-region
    coincidence is within this null, synchrony is an ARTIFACT (SYN-02 falsified).
    """
    rng = random.Random(seed)
    # group counts and dating jitter by region
    regions = {}
    for r, t, dt, M, rk in markers:
        regions.setdefault(r, []).append(dt)
    counts = {r: len(v) for r, v in regions.items()}
    jit = {r: (sum(v)/len(v)) for r, v in regions.items()}

    obs = synchrony_observed(markers, window_yr)
    sims = []
    for _ in range(n):
        fake = []
        for r, c in counts.items():
            for _k in range(c):
                t = rng.randint(t_min, t_max)
                t += int(rng.uniform(-jit[r], jit[r]))           # dating smear
                fake.append((r, t, jit[r], 8.0, 100))
        sims.append(synchrony_observed(fake, window_yr))
    sims.sort()
    return {"observed": obs,
            "null_mean": round(sum(sims)/len(sims), 2),
            "null_p95": sims[int(0.95*len(sims))-1]}


def evaluate():
    obs = codating_hits(EMERGENCE_NARRATIVES, PALEOSEISMIC, s_base=0.0)
    obs_primed = codating_hits(EMERGENCE_NARRATIVES, PALEOSEISMIC, s_base=1.0)
    nul = codating_null(EMERGENCE_NARRATIVES, PALEOSEISMIC)
    syn = synchrony_poisson_null(PALEOSEISMIC)

    syn01_supported = obs > nul["p95"]
    syn02_supported = syn["observed"] > syn["null_p95"]

    return {
        "SYN01_codating_obs": round(obs, 3),
        "SYN01_codating_obs_primed": round(obs_primed, 3),
        "SYN01_chance_mean": round(nul["mean"], 3),
        "SYN01_chance_p95": round(nul["p95"], 3),
        "SYN01_verdict": ("SUPPORTED (provisional)" if syn01_supported
                          else "NOT SUPPORTED on current data"),
        "SYN02_synchrony_obs_pairs": syn["observed"],
        "SYN02_poisson_null_mean": syn["null_mean"],
        "SYN02_poisson_null_p95": syn["null_p95"],
        "SYN02_verdict": ("SUPPORTED -> real common pacing" if syn02_supported
                          else "NOT SUPPORTED -> synchrony is a dating/Poisson "
                               "artifact, DROP it (SYN-02 falsifier)"),
    }


if __name__ == "__main__":
    for k, v in evaluate().items():
        print(f"{k:30s}: {v}")
    print("\nNOTE: placeholder data. SYN-01 is the defensible local test; "
          "SYN-02 is meant to stay dead unless real dates overwhelm the null.")
