"""
knowledge_decay_audit.py

Poynard-style meta-audit, generalized.

Original Poynard (2002): sampled 474 papers in hepatology/cirrhosis,
fit exponential, reported "scientific truth half-life = 45 years."

Flaws fixed here:

  1. Single field              -> stratified across fields w/ different
                                  invariant coupling
  2. Binary valid/obsolete     -> gradient + mechanism tagging
  3. Same-community raters     -> multi-substrate rater panel
  4. No control field          -> includes low-decay controls
                                  (thermo, structural eng)
  5. No mechanism model        -> tags WHY a claim decayed
  6. No invariant coupling     -> the key predictor Poynard never measured

Hypothesis (falsifiable):
    decay_rate ~ 1 / invariant_coupling_score
    Fields tightly coupled to conserved quantities decay slowly.
    Fields coupled to instrument/funding/social layer decay fast.

If all fields show the same half-life: Poynard's universal claim survives.
If stratified by coupling: Poynard generalized from a high-decay outlier.

License: CC0
Dependencies: stdlib only (the exponential fit is pure stdlib;
              the original sketch mentioned scipy as optional but the
              fallback is the only path actually used here)
"""

from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


# ===================================================================
# SCHEMA -- what we're measuring
# ===================================================================

class Validity(Enum):
    """Gradient, not binary. Poynard's binary was a measurement failure."""
    LOAD_BEARING       = 1.00   # actively built upon, still cited as foundation
    REFINED            = 0.75   # core claim survives, edges updated
    NARROWED           = 0.50   # claim shrunk in scope but still valid
    CONTRADICTED       = 0.25   # partially overturned
    REFUTED            = 0.00   # dead


class DecayMechanism(Enum):
    """Tag WHY a claim decayed. Poynard never asked this."""
    BETTER_INSTRUMENT       = "instrument"   # new tool revealed prior was noise
    LARGER_SAMPLE           = "sample"       # underpowered original
    PARADIGM_SHIFT          = "paradigm"     # frame changed
    FRAUD_DETECTED          = "fraud"
    P_HACK_CORRECTION       = "p_hack"
    FUNDING_FLOW_CHANGE     = "funding"      # claim died with its grants
    SOCIAL_CONSENSUS_DRIFT  = "social"       # no new evidence, just fashion
    INVARIANT_VIOLATION     = "invariant"    # actually wrong physics
    STILL_VALID             = "none"         # did not decay


class RaterRole(Enum):
    """Fix Poynard's circular expert panel."""
    IN_FIELD               = "in_field"      # rates validity
    ADJACENT_FIELD         = "adjacent"      # rates dependency on field assumptions
    CONSTRAINT_CHECKER     = "constraint"    # physics/math/thermo
    PRACTITIONER           = "practitioner"  # still used or only cited?
    OUTSIDE_SUBSTRATE      = "outside"       # trades, indigenous, mechanics


# ===================================================================
# CORE RECORDS
# ===================================================================

@dataclass
class Paper:
    paper_id:           str
    field:              str
    year_published:     int
    citation_count:     int
    sample_tier:        str          # "top_cited" | "median_cited"


@dataclass
class Rating:
    paper_id:           str
    rater_role:         RaterRole
    validity:           Validity
    mechanism:          DecayMechanism
    notes:              str = ""


@dataclass
class FieldProfile:
    """The key Poynard-missing variable: where does this field's
    knowledge live?"""
    name:                       str
    invariant_coupling:         float  # 0.0 (pure social) -> 1.0 (pure conservation law)
    instrument_dependence:      float  # 0.0 -> 1.0
    funding_volatility:         float  # 0.0 -> 1.0
    replication_culture:        float  # 0.0 (none) -> 1.0 (strong)
    notes:                      str = ""


# ===================================================================
# FIELD CATALOG -- initial priors, refined by audit results
# ===================================================================

FIELD_CATALOG: dict[str, FieldProfile] = {
    # high-decay expected
    "clinical_medicine":        FieldProfile("clinical_medicine",       0.20, 0.85, 0.70, 0.40),
    "experimental_psychology":  FieldProfile("experimental_psychology", 0.10, 0.50, 0.60, 0.30),
    "nutrition_science":        FieldProfile("nutrition_science",       0.15, 0.70, 0.80, 0.20),
    "macroeconomics":           FieldProfile("macroeconomics",          0.05, 0.30, 0.90, 0.10),

    # mid-decay expected
    "molecular_biology":        FieldProfile("molecular_biology",       0.50, 0.80, 0.50, 0.60),
    "climate_modeling":         FieldProfile("climate_modeling",        0.60, 0.70, 0.60, 0.50),
    "materials_science":        FieldProfile("materials_science",       0.65, 0.60, 0.40, 0.70),

    # low-decay controls
    "classical_thermodynamics": FieldProfile("classical_thermodynamics", 0.95, 0.20, 0.10, 0.90),
    "structural_engineering":   FieldProfile("structural_engineering",   0.90, 0.30, 0.20, 0.95),
    "organic_chem_mechanisms":  FieldProfile("organic_chem_mechanisms",  0.80, 0.50, 0.20, 0.85),
    "celestial_mechanics":      FieldProfile("celestial_mechanics",      0.98, 0.40, 0.10, 0.95),

    # non-academic substrate -- the real control
    "indigenous_landscape":     FieldProfile("indigenous_landscape",     0.85, 0.05, 0.00, 0.95,
                                             notes="multi-generational validation, "
                                                   "landscape-encoded, self-updating"),
    "traditional_navigation":   FieldProfile("traditional_navigation",   0.95, 0.10, 0.00, 0.95),
    "diesel_failure_modes":     FieldProfile("diesel_failure_modes",     0.80, 0.30, 0.10, 0.90),
}


# ===================================================================
# AGGREGATION -- turn multiple ratings into a single survival signal
# ===================================================================

def aggregate_validity(ratings: list[Rating]) -> float:
    """Average across rater roles. Returns 0.0 (refuted) to 1.0 (load-bearing)."""
    if not ratings:
        return float("nan")
    return sum(r.validity.value for r in ratings) / len(ratings)


def dominant_mechanism(ratings: list[Rating]) -> DecayMechanism:
    """Most-cited decay mechanism across raters."""
    counts: dict[DecayMechanism, int] = {}
    for r in ratings:
        counts[r.mechanism] = counts.get(r.mechanism, 0) + 1
    return max(counts.items(), key=lambda kv: kv[1])[0]


# ===================================================================
# SURVIVAL CURVE -- exponential fit, but report goodness so we can
# detect when it ISN'T exponential (Poynard never checked this either)
# ===================================================================

def fit_exponential_decay(ages: list[float], validities: list[float]
                          ) -> tuple[float, float, float]:
    """
    Fit V(t) = exp(-lambda * t) via log-linear regression.
    Returns (lambda, half_life_years, r_squared).
    Pure stdlib -- no scipy required.
    """
    pairs = [(a, v) for a, v in zip(ages, validities)
             if v is not None and v > 0.01 and not math.isnan(v)]
    if len(pairs) < 3:
        return float("nan"), float("nan"), float("nan")

    xs = [p[0] for p in pairs]
    ys = [math.log(p[1]) for p in pairs]

    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return float("nan"), float("nan"), float("nan")

    slope = num / den                       # = -lambda
    intercept = my - slope * mx
    lam = -slope
    half_life = math.log(2) / lam if lam > 0 else float("inf")

    # R^2
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    return lam, half_life, r2


# ===================================================================
# AUDIT PIPELINE
# ===================================================================

@dataclass
class FieldResult:
    field:               str
    n_papers:            int
    half_life_years:     float
    decay_lambda:        float
    fit_r_squared:       float
    mechanism_breakdown: dict[str, float]
    invariant_coupling:  float

    def to_dict(self) -> dict:
        return asdict(self)


def audit_field(field_name: str,
                papers: list[Paper],
                ratings_by_paper: dict[str, list[Rating]],
                current_year: int = 2026) -> FieldResult:

    profile = FIELD_CATALOG[field_name]
    ages, validities, mechs = [], [], []

    for p in papers:
        if p.field != field_name:
            continue
        rs = ratings_by_paper.get(p.paper_id, [])
        if not rs:
            continue
        ages.append(current_year - p.year_published)
        validities.append(aggregate_validity(rs))
        mechs.append(dominant_mechanism(rs))

    lam, hl, r2 = fit_exponential_decay(ages, validities)

    mech_breakdown: dict[str, float] = {}
    if mechs:
        for m in mechs:
            mech_breakdown[m.value] = mech_breakdown.get(m.value, 0) + 1
        n = len(mechs)
        mech_breakdown = {k: v / n for k, v in mech_breakdown.items()}

    return FieldResult(
        field               = field_name,
        n_papers            = len(ages),
        half_life_years     = hl,
        decay_lambda        = lam,
        fit_r_squared       = r2,
        mechanism_breakdown = mech_breakdown,
        invariant_coupling  = profile.invariant_coupling,
    )


def cross_field_signature(results: list[FieldResult]) -> dict:
    """
    The actual Poynard-killer (or confirmer).
    Correlate invariant_coupling vs half_life across fields.
    """
    pts = [(r.invariant_coupling, r.half_life_years)
           for r in results
           if not math.isnan(r.half_life_years)
           and not math.isinf(r.half_life_years)]
    if len(pts) < 3:
        return {"correlation": float("nan"), "n": len(pts)}

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx  = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy  = math.sqrt(sum((y - my) ** 2 for y in ys))
    rho = num / (dx * dy) if dx * dy > 0 else float("nan")

    return {
        "correlation_coupling_vs_halflife": rho,
        "interpretation": (
            "rho > 0.5  -> Poynard generalized from outlier; "
            "decay is field-specific, predicted by invariant coupling"
            if rho > 0.5 else
            "rho ~ 0    -> Poynard's universal half-life survives; "
            "coupling does not predict decay"
            if abs(rho) < 0.2 else
            "rho < -0.5 -> inverse: tighter coupling correlates with FASTER decay "
            "(unexpected; investigate)"
        ),
        "n_fields": n,
        "points": pts,
    }


# ===================================================================
# I/O -- minimal CSV in, JSON out (mobile-friendly, no deps)
# ===================================================================

def load_papers(path: Path) -> list[Paper]:
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out.append(Paper(
                paper_id       = row["paper_id"],
                field          = row["field"],
                year_published = int(row["year_published"]),
                citation_count = int(row["citation_count"]),
                sample_tier    = row["sample_tier"],
            ))
    return out


def load_ratings(path: Path) -> dict[str, list[Rating]]:
    out: dict[str, list[Rating]] = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            r = Rating(
                paper_id   = row["paper_id"],
                rater_role = RaterRole(row["rater_role"]),
                validity   = Validity[row["validity"]],
                mechanism  = DecayMechanism(row["mechanism"]),
                notes      = row.get("notes", ""),
            )
            out.setdefault(r.paper_id, []).append(r)
    return out


def run_audit(papers_csv: Path, ratings_csv: Path,
              out_json: Path, current_year: int = 2026) -> dict:
    papers  = load_papers(papers_csv)
    ratings = load_ratings(ratings_csv)
    fields  = sorted({p.field for p in papers})

    results = [audit_field(f, papers, ratings, current_year) for f in fields]
    signature = cross_field_signature(results)

    payload = {
        "current_year":   current_year,
        "n_papers_total": len(papers),
        "field_results":  [r.to_dict() for r in results],
        "cross_field":    signature,
    }
    out_json.write_text(json.dumps(payload, indent=2))
    return payload


# ===================================================================
# SELF-TEST -- synthetic data with known decay rates, verify recovery
# ===================================================================

def _synthesize(seed: int = 42) -> tuple[list[Paper], dict[str, list[Rating]]]:
    """Generate fake papers w/ known half-lives so we can check the fit."""
    rng = random.Random(seed)
    true_half_lives = {
        "clinical_medicine":        45,
        "classical_thermodynamics": 200,
        "indigenous_landscape":     400,
    }
    papers: list[Paper] = []
    ratings: dict[str, list[Rating]] = {}

    pid = 0
    for fname, hl in true_half_lives.items():
        lam = math.log(2) / hl
        for _ in range(60):
            year = rng.randint(1950, 2020)
            age  = 2026 - year
            v_true = math.exp(-lam * age)
            v_obs  = max(0.01, min(1.0, v_true + rng.gauss(0, 0.05)))

            # snap to nearest Validity bucket
            buckets = sorted(Validity, key=lambda b: abs(b.value - v_obs))
            v_enum  = buckets[0]
            mech    = (DecayMechanism.STILL_VALID if v_obs > 0.6
                       else DecayMechanism.BETTER_INSTRUMENT)

            pid += 1
            pid_s = f"P{pid:05d}"
            papers.append(Paper(pid_s, fname, year, rng.randint(10, 5000), "top_cited"))
            ratings[pid_s] = [Rating(pid_s, RaterRole.IN_FIELD, v_enum, mech)]

    return papers, ratings


def _self_test() -> None:
    papers, ratings = _synthesize()
    fields = sorted({p.field for p in papers})
    print(f"{'field':30s}  {'n':>4s}  {'half_life':>10s}  {'R^2':>6s}  coupling")
    print("-" * 70)
    results = []
    for f in fields:
        r = audit_field(f, papers, ratings)
        results.append(r)
        print(f"{f:30s}  {r.n_papers:4d}  "
              f"{r.half_life_years:10.1f}  {r.fit_r_squared:6.3f}  "
              f"{r.invariant_coupling:.2f}")
    print()
    sig = cross_field_signature(results)
    print(f"cross-field rho(coupling, half_life) = "
          f"{sig['correlation_coupling_vs_halflife']:.3f}")
    print(sig["interpretation"])


if __name__ == "__main__":
    _self_test()
