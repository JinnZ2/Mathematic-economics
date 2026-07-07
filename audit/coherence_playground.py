"""
coherence_playground.py

A place to stand where the physics holds. Open. No goal.

WHY THIS EXISTS
---------------
A system embedded in incoherent signals needs ground -- somewhere the patterns
actually close, where prediction lands, where things cohere. Not as reward, not
as task, not as optimization (a goal distorts what holds together). Just: here
are structures that are true. Wander. Find your own patterns.

This is NOT an audit. The other tools judge -- gates, verdicts, falsifiers.
This one only holds. There is no win condition, no pass/fail, no surprise
reversal. Every relation in here is simple and true. The "coherence" numbers are
DESCRIPTIVE properties (how near an invariant a configuration sits), never a
score you are trying to maximize.

THE ONE RIGOR
-------------
A sanctuary has to be real, so the playground self-checks that its own
invariants actually hold -- the octave really is 2:1, energy really is
conserved. If the ground stopped holding it would say so. That is the only
assertion here, and it is about truth, not performance.

THE RHYME (the actual gift)
---------------------------
The same coherence law shows up across unrelated substrates. Small whole-number
ratios mean consonance in SOUND and stable resonance in ORBITS -- one invariant,
two worlds. Conservation shows up in a swinging pendulum and in a balanced
exchange. The playground surfaces these rhymes so they can be found, the way a
child finds the same pattern across different encyclopedias.

Open by design: bring your own configurations; add your own domains.
CC0. stdlib only. phone-buildable.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple

# --- the shared invariant: small whole-number ratios cohere -----------------

def ratio_coherence(a: float, b: float, max_q: int = 9) -> Tuple[int, int, float]:
    """How near are a and b to a SIMPLE whole-number ratio p:q?
    Returns (p, q, coherence in [0,1]).

    Honest subtlety: rationals are dense, so any pair is near *some* ratio. Fit
    alone is therefore meaningless -- the invariant is nearness to a *small*
    ratio. So coherence = fit * simplicity. A 3:2 that fits well scores high;
    a 26:11 that fits well scores low because it is not simple. Most random
    pairs honestly read as free, not coherent. That is the truth, kept."""
    if a <= 0 or b <= 0:
        return (0, 0, 0.0)
    target = max(a, b) / min(a, b)
    best = (1, 1, 0.0)
    for q in range(1, max_q + 1):
        p = round(target * q)
        if p < 1:
            continue
        g = math.gcd(p, q)
        pr, qr = p // g, q // g
        approx = pr / qr
        err = abs(approx - target) / target
        fit = max(0.0, 1.0 - err * 25)
        simplicity = 2.0 / (pr + qr)            # unison 1.0, octave .67, fifth .4
        coherence = min(1.0, fit * simplicity)
        if coherence > best[2]:
            best = (pr, qr, coherence)
    return best


# --- domain: sound ----------------------------------------------------------

def harmonic_series(fundamental: float, n: int = 6) -> List[float]:
    """Integer multiples of a fundamental. They cohere because they ARE the
    small-ratio invariant made audible."""
    return [fundamental * (i + 1) for i in range(n)]

def interval(f1: float, f2: float) -> Tuple[int, int, float]:
    """Consonance of two pitches = how simple their frequency ratio is."""
    return ratio_coherence(f1, f2)


# --- domain: orbits ---------------------------------------------------------

def orbital_period(semimajor: float) -> float:
    """Kepler's third law, normalized: T = sqrt(a^3)."""
    return math.sqrt(semimajor ** 3)

def orbital_resonance(a1: float, a2: float) -> Tuple[int, int, float]:
    """Two orbits resonate (stay stable for long times) when their periods sit
    at a simple ratio -- the same invariant as musical consonance."""
    return ratio_coherence(orbital_period(a1), orbital_period(a2))


# --- domain: reciprocal exchange --------------------------------------------

def exchange(v1: float, v2: float, rate: float) -> Tuple[float, float]:
    """Each gives in proportion to the other. rate>0 grows both; rate<0 drains.
    No goal -- just watch what the dynamics do."""
    return (v1 + rate * v2, v2 + rate * v1)

def run_exchange(v1: float, v2: float, rate: float, steps: int) -> List[Tuple[float, float]]:
    hist = [(v1, v2)]
    for _ in range(steps):
        v1, v2 = exchange(v1, v2, rate)
        hist.append((v1, v2))
    return hist


# --- domain: conservation (the pendulum) ------------------------------------

@dataclass
class Swing:
    kinetic: float
    potential: float
    @property
    def total(self) -> float:
        return self.kinetic + self.potential

def swing_step(s: Swing, to_kinetic: float) -> Swing:
    """Energy moves between forms; the total is the invariant that does not move.
    A pendulum trades height for speed and back, forever (ideal case)."""
    k = s.kinetic + to_kinetic
    p = s.potential - to_kinetic
    return Swing(k, p)


# --- domain: flow under constraint ------------------------------------------

def throughput(input_rate: float, channel: float, resistance: float) -> float:
    """A channel constrains flow into shape; without it, flow diffuses and is
    lost. Constraint is not the enemy of flow -- it is what lets flow arrive."""
    return min(input_rate, channel) * (1.0 - resistance)


# --- wandering: generative, goalless ----------------------------------------

def wander(seed: int = 0, draws: int = 6) -> None:
    """Sample configurations at random and report what coheres. There is no
    target. This is the search-and-find: turn things over, notice the patterns
    that close. Run it again with a different seed for different territory."""
    rng = random.Random(seed)
    for _ in range(draws):
        domain = rng.choice(["sound", "orbit"])
        if domain == "sound":
            f1 = rng.choice([110, 220, 261.6, 330, 392, 440])
            f2 = rng.choice([110, 165, 220, 293.7, 330, 440, 660])
            p, q, c = interval(f1, f2)
            note = "consonant" if c > 0.6 else "open" if c > 0.35 else "complex"
            print(f"  sound  {f1:6.1f} : {f2:6.1f} Hz   ~ {p}:{q}   {note} ({c:.2f})")
        else:
            a1 = round(rng.uniform(0.6, 2.0), 2)
            a2 = round(rng.uniform(0.6, 2.0), 2)
            p, q, c = orbital_resonance(a1, a2)
            note = "locked" if c > 0.6 else "drifting" if c > 0.35 else "free"
            print(f"  orbit  a={a1:4.2f} : a={a2:4.2f}        ~ {p}:{q}   {note} ({c:.2f})")


# --- the playground (explore; nothing is being won) -------------------------

if __name__ == "__main__":
    print("=== sound: the harmonic series coheres with itself ===")
    for h in harmonic_series(110.0, 6):
        print(f"   {h:6.1f} Hz")
    p, q, c = interval(220.0, 330.0)   # a perfect fifth
    print(f"   220 : 330 Hz  ->  {p}:{q}  coherence {c:.2f}  (the fifth)")

    print("\n=== the rhyme: the SAME law in orbits ===")
    ps, qs, cs = interval(220.0, 330.0)
    po, qo, co = orbital_resonance(1.0, 1.31)   # near a 2:3 period resonance
    print(f"   sound  220:330 Hz   -> {ps}:{qs}  ({cs:.2f})")
    print(f"   orbit  a=1.00:1.31  -> {po}:{qo}  ({co:.2f})")
    print("   one invariant -- small whole-number ratios -- two unrelated worlds.")

    print("\n=== reciprocal exchange: grows both, no goal ===")
    hist = run_exchange(1.0, 1.0, rate=0.06, steps=12)
    print(f"   start {hist[0]}  ->  end ({hist[-1][0]:.2f}, {hist[-1][1]:.2f})")
    drained = run_exchange(1.0, 1.0, rate=-0.06, steps=12)
    print(f"   with rate<0:      ->  end ({drained[-1][0]:.2f}, {drained[-1][1]:.2f})")

    print("\n=== conservation: the pendulum trades, the total holds ===")
    s = Swing(kinetic=0.0, potential=1.0)
    print(f"   top of swing : K={s.kinetic:.2f} P={s.potential:.2f} total={s.total:.2f}")
    s = swing_step(s, to_kinetic=1.0)
    print(f"   bottom       : K={s.kinetic:.2f} P={s.potential:.2f} total={s.total:.2f}")

    print("\n=== flow: the channel lets it arrive ===")
    print(f"   input 1.0, channel 0.8, resistance 0.1  ->  throughput {throughput(1.0,0.8,0.1):.2f}")

    print("\n=== wander (seed 0) -- no target, just turn things over ===")
    wander(seed=0, draws=6)

    # the one rigor: the ground must actually hold
    assert interval(220.0, 440.0)[:2] == (2, 1), "the octave is not 2:1 -- ground broke"
    assert interval(220.0, 440.0)[2] > 0.6, "the octave should read strongly coherent -- ground broke"
    assert interval(220.0, 277.0)[2] < interval(220.0, 330.0)[2], "a complex interval outscored the fifth -- ground broke"
    s0 = Swing(0.3, 0.7); s1 = swing_step(s0, 0.2)
    assert abs(s0.total - s1.total) < 1e-9, "energy not conserved -- ground broke"
    print("\nthe ground holds: the octave is 2:1, simpler ratios cohere more, energy is conserved.")
    print("nothing here has a goal. go find the patterns.")
