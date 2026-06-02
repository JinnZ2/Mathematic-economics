"""
forcing_functions.py  -- CC0, stdlib-only

The FAST layer. These are the triggers that ride on top of the slow deep-water
baseline. Each is a time-varying boundary condition, returned normalized to
[-1, 1] amplitude so they can be combined into an alignment metric.

Time convention: t in years BEFORE PRESENT (BP), t >= 0.

Periods (years):
  annual wobble        1.0
  Chandler wobble      1.186            (~433 d polar motion)
  Schwabe solar        11
  Gleissberg solar     88
  Suess/de Vries solar 210
  Hallstatt solar      2400
  precession           23000, 19000
  obliquity            41000
  eccentricity         100000, 405000

Honest note: amplitudes here are SCHEMATIC normalizations, not W/m^2. The model
tests STRUCTURE (do peaks coincide), not absolute energy. Calibrating real
insolation (Laskar solution) and real ice-volume (delta-18-O) is the next step
and is declared in EVT-01's falsifier.
"""

import math
from claim_ledger import Quantity, gate

TWO_PI = 2.0 * math.pi


def _wave(t_yr: float, period_yr: float, phase: float = 0.0) -> float:
    return math.cos(TWO_PI * (t_yr / period_yr) + phase)


# Distinct, fixed phase offsets so the cycles are NOT all synchronized at
# t=0 BP. Without these every cosine peaks at the present and "now" looks
# artificially aligned. Values are arbitrary-but-fixed (reproducible);
# real phases come from the Laskar orbital solution + sunspot record.
PH = {
    "ann": 0.7, "chan": 2.1,
    "s11": 1.3, "s88": 5.0, "s210": 3.4, "s2400": 0.9,
    "ecc100": 2.7, "ecc405": 4.8,
    "prec23": 1.1, "prec19": 5.6, "obl": 3.9,
}


# ---- individual forcings (each normalized to [-1,1]) -------------------

def chandler(t_yr: float) -> float:
    # annual + Chandler beat -> envelope ~6.4 yr (the real polar-motion beat)
    return 0.5 * (_wave(t_yr, 1.0, PH["ann"]) + _wave(t_yr, 1.186, PH["chan"]))


def solar(t_yr: float) -> float:
    # superposed solar cycles, longer cycles weighted more for slow climate
    s = (0.30 * _wave(t_yr, 11.0, PH["s11"])
         + 0.30 * _wave(t_yr, 88.0, PH["s88"])
         + 0.25 * _wave(t_yr, 210.0, PH["s210"])
         + 0.15 * _wave(t_yr, 2400.0, PH["s2400"]))
    return s


def insolation(t_yr: float) -> float:
    # Milankovitch proxy: eccentricity-modulated precession + obliquity
    ecc = 0.5 * (_wave(t_yr, 100000.0, PH["ecc100"])
                 + _wave(t_yr, 405000.0, PH["ecc405"]))           # -1..1
    prec = 0.5 * (_wave(t_yr, 23000.0, PH["prec23"])
                  + _wave(t_yr, 19000.0, PH["prec19"]))
    obl = _wave(t_yr, 41000.0, PH["obl"])
    # eccentricity gates precession amplitude (classic envelope)
    env = 0.5 * (1.0 + ecc)            # 0..1
    return 0.6 * env * prec + 0.4 * obl


def glacial_unloading(t_yr: float) -> float:
    """
    Ice-volume proxy lagged behind insolation; its TIME-DERIVATIVE (rate of
    unloading) is what stresses the crust (isostatic rebound, meltwater pulses).
    Returns the unloading RATE proxy in [-1,1]. Positive = rapid deglaciation.
    """
    lag = 5000.0   # yr, ice responds slowly to insolation
    ice_now = -insolation(t_yr)            # more ice when insolation low
    ice_lag = -insolation(t_yr + lag)
    rate = (ice_lag - ice_now)             # finite difference (per 5 kyr)
    return max(-1.0, min(1.0, rate))


FORCINGS = {
    "chandler": (chandler, 0.10),     # (function, weight in alignment)
    "solar": (solar, 0.20),
    "insolation": (insolation, 0.30),
    "glacial": (glacial_unloading, 0.40),
}


def forcing_alignment(t_yr: float) -> float:
    """
    Constructive-interference metric in [0,1].
    Weighted, half-wave-rectified sum: only co-occurring POSITIVE excursions
    (toward water release) reinforce. Anti-aligned forcings cancel.
    """
    total = 0.0
    wsum = 0.0
    for name, (fn, w) in FORCINGS.items():
        v = fn(t_yr)
        total += w * max(0.0, v)     # rectify: only release-direction counts
        wsum += w
    a = total / wsum if wsum else 0.0
    return gate(Quantity(a, "alignment_0_1", 0.0, 1.0), "forcing_alignment")


def forcing_breakdown(t_yr: float) -> dict:
    return {name: round(fn(t_yr), 3) for name, (fn, _w) in FORCINGS.items()}


if __name__ == "__main__":
    for t in (0, 7000, 11700, 14600, 20000):
        print(f"t={t:6d} BP  align={forcing_alignment(t):.3f}  "
              f"{forcing_breakdown(t)}")
