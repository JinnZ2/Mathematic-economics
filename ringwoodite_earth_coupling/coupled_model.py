"""
coupled_model.py  -- CC0, stdlib-only

Ties the layers together and produces the testable observable:
a water-emergence / flood EVENT PROBABILITY time series over the last N kyr.

  P_event(t) = sigmoid( k * [ S_base * alpha + (1-alpha) ] * align(t) - theta )

  S_base : slow crustal sensitivity from the deep-water baseline (0..1)
  align  : fast forcing alignment (0..1)
  alpha  : how much the deep baseline matters. alpha=0 -> fast-forcing-only
           (the NULL model EVT-01 must beat). This is the load-bearing knob.

Hook: emits the same structured timeseries the earth-systems-physics cascade
engine ingests as a lithosphere/hydrosphere boundary forcing.
"""

import math
from claim_ledger import Quantity, gate
from ringwoodite_phase import deep_water_baseline
from mantle_crust_coupling import crustal_sensitivity
from forcing_functions import forcing_alignment, forcing_breakdown


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def event_probability(t_yr: float,
                      s_base: float,
                      alpha: float = 0.6,
                      k: float = 8.0,
                      theta: float = 2.5,
                      s_ref: float = 0.35,
                      gain: float = 1.2) -> float:
    """
    P of a surface water-emergence event in the window around t_yr.

    gain_factor swings ABOVE and BELOW 1 around a neutral baseline s_ref, so a
    primed base AMPLIFIES and a dry base DAMPS. alpha=0 pins gain_factor=1
    exactly -> the fast-forcing-only NULL model. This keeps the EVT-01 test
    FAIR: the baseline is free to help or hurt, the data decides.
    """
    align = forcing_alignment(t_yr)
    gain_factor = 1.0 + alpha * gain * (s_base - s_ref)
    gain_factor = max(0.1, gain_factor)
    drive = gain_factor * align
    p = _sigmoid(k * drive - theta)
    return gate(Quantity(p, "event_probability", 0.0, 1.0), "event_prob")


def run(t_start_bp: int = 150000,
        t_end_bp: int = 0,
        step_yr: int = 250,
        # slow boundary inputs (held quasi-constant; CPL-02):
        tz_temperature_k: float = 1850.0,
        downwelling_m_per_yr: float = 0.01,
        rw_water_wt: float = 1.4,
        alpha: float = 0.6) -> dict:
    """
    Returns {"t": [...BP...], "p": [...], "s_base": float, "peaks": [...]}.
    """
    base = deep_water_baseline(tz_temperature_k, downwelling_m_per_yr, rw_water_wt)
    s_base = crustal_sensitivity(base, rw_water_wt)

    ts, ps = [], []
    t = t_start_bp
    while t >= t_end_bp:
        ts.append(t)
        ps.append(event_probability(t, s_base, alpha=alpha))
        t -= step_yr

    peaks = _find_peaks(ts, ps, min_prob=0.5)
    return {"t": ts, "p": ps, "s_base": s_base, "alpha": alpha, "peaks": peaks}


def _find_peaks(ts, ps, min_prob=0.5):
    peaks = []
    for i in range(1, len(ps) - 1):
        if ps[i] >= min_prob and ps[i] >= ps[i-1] and ps[i] > ps[i+1]:
            peaks.append((ts[i], round(ps[i], 3)))
    return peaks


def to_earth_systems_forcing(result: dict) -> list:
    """
    Emit boundary-forcing records for the earth-systems-physics cascade engine.
    Each record carries units (metrological skin) for the hydrosphere layer.
    """
    out = []
    for t, p in zip(result["t"], result["p"]):
        out.append({
            "t_bp_yr": t,
            "hydrosphere_emergence_forcing": p,
            "unit": "event_probability",
            "layer": "hydrosphere",
        })
    return out


if __name__ == "__main__":
    res_full = run(alpha=0.6)
    res_null = run(alpha=0.0)   # fast-forcing-only NULL model (EVT-01)
    print(f"deep-water baseline -> S_base = {res_full['s_base']:.3f}")
    print(f"\nFULL model peaks (alpha=0.6), prob>=0.5:")
    for t, p in res_full["peaks"][:12]:
        print(f"  {t:6d} BP   P={p}")
    print(f"\nNULL model peaks (alpha=0.0):")
    for t, p in res_null["peaks"][:12]:
        print(f"  {t:6d} BP   P={p}")
    print(f"\nfull peaks: {len(res_full['peaks'])}  "
          f"null peaks: {len(res_null['peaks'])}")
