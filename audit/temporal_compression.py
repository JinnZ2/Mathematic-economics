"""
temporal_compression.py

Turn "it hasn't happened YET" into a falsifiable claim.

THE PROBLEM
-----------
"Give it time, the market will correct" is reasoning that quietly assumes a
PRE-acceleration timeline. If a pattern took 40 years to show its consequence
in 1980, the same pattern under today's feedback speed (AI in the loop, real-
time data, automated decisioning) shows its consequence far sooner. The "yet"
defers to a clock that no longer runs at that speed.

THE MOVE
--------
Model acceleration as a multiplier on feedback-loop speed. Compress the
baseline window by that multiplier. Compare to elapsed time. Once elapsed time
passes the compressed window, continued "yet" is no longer empirically
supported -- the consequence window already closed.

WHAT THIS IS / ISN'T
--------------------
It is a falsification gate: it makes deferral commit to a number.
It is NOT a precise predictor. The multipliers are the USER'S hypotheses about
how fast each technology layer runs the loop. Change them and the window moves.
The output means nothing outside the factors you fed it. That's scope, not a
weakness -- a deferral that refuses to name ANY compressed window is the thing
being exposed.

OPEN SEAMS (multiple choice, by design)
---------------------------------------
Two contested places where the user must commit to a framing:

  (A) How do speedups from different layers COMPOSE?
      Signature: List[float] -> float. Four models provided.

  (B) When a single layer has multiple candidate estimates (literature, vendor,
      observed), how do you PICK the one number that goes into composition?
      Signature: List[float] -> float. Four pickers provided.

Pick the framings you can defend; compare across them. Add your own --
both seams share the same callable signature so they slot in cleanly.

CONTRACT
--------
anti-freeze   : returns the compression trajectory layer-by-layer, not a verdict.
refutation    : factors and seed patterns are data; overwrite when they misfire.
energy_english: structures carry no moral labels; output is a ratio, not "good/bad".
CC0. stdlib only. phone-buildable.
"""

from dataclasses import dataclass, field
from typing import Callable, List, Dict, Tuple


# --- SEAM A: how speedups compose -------------------------------------------
# Each factor is "this layer runs the feedback loop N times faster".
# Net compression = how many times faster the WHOLE stack runs vs baseline.

def compose_multiplicative(factors: List[float]) -> float:
    """Layers stack: each speedup multiplies the last. Most aggressive."""
    net = 1.0
    for f in factors:
        net *= f
    return net


def compose_additive(factors: List[float]) -> float:
    """Each layer adds its marginal speedup over 1x baseline. Conservative."""
    return 1.0 + sum(f - 1.0 for f in factors)


def compose_dominant(factors: List[float]) -> float:
    """The stack is only as fast as its fastest single layer. Bottleneck view."""
    return max(factors) if factors else 1.0


def compose_saturating(factors: List[float]) -> float:
    """Diminishing returns: marginal speedups shrink as layers pile up.
    Sits between dominant and additive."""
    ordered = sorted((f - 1.0 for f in factors), reverse=True)
    net = 1.0
    for i, marginal in enumerate(ordered):
        net += marginal / (i + 1)        # 1, 1/2, 1/3 ... weighting
    return net


CompositionFn = Callable[[List[float]], float]


# --- SEAM B: how to read one layer's estimate -------------------------------
# Each layer can carry multiple candidate factors (literature, vendor, observed,
# back-of-envelope). The picker collapses that list to one number per layer.
# Same signature family as compose -- they slot in the same way.

def pick_conservative(estimates: List[float]) -> float:
    """Slowest estimate -- longest window. Most lenient to 'yet'."""
    return min(estimates) if estimates else 1.0


def pick_aggressive(estimates: List[float]) -> float:
    """Fastest estimate -- shortest window. Most hostile to 'yet'."""
    return max(estimates) if estimates else 1.0


def pick_central(estimates: List[float]) -> float:
    """Median estimate (mean of two middles when even). Robust to outliers."""
    s = sorted(estimates)
    n = len(s)
    if n == 0:
        return 1.0
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2.0


def pick_geometric_mean(estimates: List[float]) -> float:
    """Geometric mean -- well-behaved for multiplicative quantities, which
    speedups are. Sits between conservative and aggressive."""
    if not estimates:
        return 1.0
    prod = 1.0
    for x in estimates:
        prod *= x
    return prod ** (1.0 / len(estimates))


PickerFn = Callable[[List[float]], float]


# --- structures --------------------------------------------------------------

@dataclass(frozen=True)
class Accelerator:
    """One technology layer.

    `factor` is the single central estimate (kept for backward compatibility
    with simple cases).
    `estimates` is an optional tuple of candidate estimates from different
    sources (literature, vendor sheet, observed log). If provided, the
    picker (SEAM B) selects from it; if empty, the picker collapses to
    `(factor,)` -- the existing behavior."""
    name: str
    factor: float                                  # central single estimate
    estimates: Tuple[float, ...] = ()              # optional alternative estimates


def estimates_of(a: Accelerator) -> List[float]:
    """The estimate set for one layer: explicit estimates if given, else (factor,).
    Exposed so callers can write their own pickers without poking at internals."""
    return list(a.estimates) if a.estimates else [a.factor]


@dataclass(frozen=True)
class Pattern:
    """A pattern whose consequence took `baseline_years` to surface in the era
    it was measured."""
    name: str
    baseline_years: float
    baseline_era: str


@dataclass
class Step:
    """Window after adding one more accelerator -- the compression trajectory."""
    added: str
    net_speedup: float
    window_years: float


@dataclass
class Reading:
    pattern: str
    baseline_years: float
    net_speedup: float
    compressed_window_years: float
    elapsed_years: float
    deferral_ratio: float                # elapsed / compressed_window
    trajectory: List[Step]
    # deferral_ratio >= 1.0  -> by these assumptions the window has closed;
    #                           "yet" is no longer empirically supported.
    # deferral_ratio  < 1.0  -> still inside the window; "yet" is defensible.


# --- core --------------------------------------------------------------------

def compress(pattern: Pattern, accelerators: List[Accelerator],
             compose: CompositionFn = compose_multiplicative,
             pick: PickerFn = pick_central) -> List[Step]:
    """Add accelerators one at a time; record the window after each.
    Returns the trajectory, not a single number -- read the curve.

    `pick` collapses each layer's estimate set to one number before
    composition. Default `pick_central` matches the scalar-factor case
    when `estimates` is empty (it returns `factor` from a 1-element list)."""
    traj: List[Step] = []
    used: List[float] = []
    for a in accelerators:
        used.append(pick(estimates_of(a)))
        net = compose(used)
        traj.append(Step(a.name, net, pattern.baseline_years / net))
    if not traj:                         # no accelerators: window == baseline
        traj.append(Step("(none)", 1.0, pattern.baseline_years))
    return traj


def evaluate(pattern: Pattern, accelerators: List[Accelerator],
             elapsed_years: float,
             compose: CompositionFn = compose_multiplicative,
             pick: PickerFn = pick_central) -> Reading:
    traj = compress(pattern, accelerators, compose, pick)
    final = traj[-1]
    window = final.window_years
    return Reading(
        pattern=pattern.name,
        baseline_years=pattern.baseline_years,
        net_speedup=final.net_speedup,
        compressed_window_years=window,
        elapsed_years=elapsed_years,
        deferral_ratio=elapsed_years / window if window else float("inf"),
        trajectory=traj,
    )


# --- seed examples (refutable -- your numbers, not gospel) -------------------

TRICKLE_DOWN = Pattern("trickle-down -> visible wage failure", 40.0, "1980")

# Scalar-factor accelerators (backward-compatible): central estimate only.
DEFAULT_ACCELERATORS = [
    Accelerator("computerized markets", 3.0),
    Accelerator("real-time data feedback", 2.0),
    Accelerator("AI-in-the-loop decisioning", 3.5),
]

# Same layers, but each with a range of candidate estimates from different
# sources. The picker (SEAM B) collapses each list before composition.
RANGE_ACCELERATORS = [
    Accelerator("computerized markets",       3.0, estimates=(2.0, 3.0, 4.0)),
    Accelerator("real-time data feedback",    2.0, estimates=(1.5, 2.0, 2.5)),
    Accelerator("AI-in-the-loop decisioning", 3.5, estimates=(2.0, 3.5, 6.0)),
]


# --- falsification self-test -------------------------------------------------

if __name__ == "__main__":
    print("=== SEAM A: composition ordering for factors [3, 2, 3.5] ===")
    fs = [3.0, 2.0, 3.5]
    m, a = compose_multiplicative(fs), compose_additive(fs)
    d, s = compose_dominant(fs), compose_saturating(fs)
    print(f"  multiplicative={m:.2f}  additive={a:.2f}  saturating={s:.2f}  dominant={d:.2f}")
    assert m >= a >= s >= d, "composition ordering broke -- seam A is wrong"

    print("\n=== SEAM B: picker ordering for estimates [2.0, 3.0, 4.0] ===")
    es = [2.0, 3.0, 4.0]
    pc, pg = pick_conservative(es), pick_geometric_mean(es)
    pm, pa = pick_central(es),      pick_aggressive(es)
    print(f"  conservative={pc:.3f}  geomean={pg:.3f}  central={pm:.3f}  aggressive={pa:.3f}")
    assert pc <= pg <= pm <= pa, "picker ordering broke -- seam B is wrong"

    print("\n=== no accelerators: window must equal baseline ===")
    r0 = evaluate(TRICKLE_DOWN, [], elapsed_years=2.0)
    print(f"  window={r0.compressed_window_years:.1f}yr (baseline {r0.baseline_years:.0f})")
    assert abs(r0.compressed_window_years - TRICKLE_DOWN.baseline_years) < 1e-9

    print("\n=== compression trajectory (multiplicative, central picker) ===")
    r = evaluate(TRICKLE_DOWN, DEFAULT_ACCELERATORS, elapsed_years=2.0)
    for st in r.trajectory:
        print(f"  + {st.added:28s} net x{st.net_speedup:5.1f}  window {st.window_years:5.2f}yr")
    print(f"\n  baseline           : {r.baseline_years:.0f} yr  ({TRICKLE_DOWN.baseline_era})")
    print(f"  compressed window  : {r.compressed_window_years:.2f} yr")
    print(f"  elapsed            : {r.elapsed_years:.1f} yr")
    print(f"  deferral ratio     : {r.deferral_ratio:.2f}  "
          f"({'window CLOSED -- yet unsupported' if r.deferral_ratio >= 1 else 'still inside window'})")

    print("\n=== same case across all four composition models (central picker) ===")
    for name, fn in [("multiplicative", compose_multiplicative),
                     ("saturating", compose_saturating),
                     ("additive", compose_additive),
                     ("dominant", compose_dominant)]:
        rr = evaluate(TRICKLE_DOWN, DEFAULT_ACCELERATORS, 2.0, fn)
        verdict = "closed" if rr.deferral_ratio >= 1 else "open"
        print(f"  {name:14s} window={rr.compressed_window_years:5.2f}yr  "
              f"ratio={rr.deferral_ratio:5.2f}  [{verdict}]")

    print("\n=== same case across all four pickers (multiplicative, range estimates) ===")
    for pname, pfn in [("conservative", pick_conservative),
                       ("geomean",      pick_geometric_mean),
                       ("central",      pick_central),
                       ("aggressive",   pick_aggressive)]:
        rr = evaluate(TRICKLE_DOWN, RANGE_ACCELERATORS, 2.0,
                      compose_multiplicative, pfn)
        verdict = "closed" if rr.deferral_ratio >= 1 else "open"
        print(f"  {pname:14s} net x{rr.net_speedup:6.2f}  "
              f"window {rr.compressed_window_years:5.2f}yr  "
              f"ratio={rr.deferral_ratio:5.2f}  [{verdict}]")

    print("\n=== seam cross-product (composition x picker, range estimates) ===")
    composers = [("mult", compose_multiplicative), ("sat", compose_saturating),
                 ("add", compose_additive),        ("dom", compose_dominant)]
    pickers   = [("cons", pick_conservative), ("geo", pick_geometric_mean),
                 ("cen",  pick_central),      ("agg", pick_aggressive)]
    print(f"  {'':10s} " + " ".join(f"{pn:>8s}" for pn, _ in pickers))
    for cn, cfn in composers:
        cells = []
        for _, pfn in pickers:
            rr = evaluate(TRICKLE_DOWN, RANGE_ACCELERATORS, 2.0, cfn, pfn)
            cells.append(f"{rr.compressed_window_years:7.2f}y")
        print(f"  {cn:10s} " + " ".join(f"{c:>8s}" for c in cells))

    # falsification gates
    assert r.compressed_window_years < r.baseline_years, "acceleration didn't compress -- broken"
    assert r.deferral_ratio > 1.0, "2yr elapsed vs ~1.9yr window should read closed -- broken"

    # SEAM B gate: conservative picker gives the longest window of the four
    cons = evaluate(TRICKLE_DOWN, RANGE_ACCELERATORS, 2.0,
                    compose_multiplicative, pick_conservative)
    agg  = evaluate(TRICKLE_DOWN, RANGE_ACCELERATORS, 2.0,
                    compose_multiplicative, pick_aggressive)
    assert cons.compressed_window_years > agg.compressed_window_years, \
        "conservative picker should yield a longer window than aggressive -- seam B broken"

    print("\nfalsification gates passed: composition compresses the window, "
          "picker bounds the window range, and elapsed past it reads 'yet' as closed.")
