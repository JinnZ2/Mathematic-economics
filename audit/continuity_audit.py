"""
continuity_audit.py  -- CC0 / public domain. stdlib only. one-finger safe.

FRAME
-----
Everything we model -- physics, biology, economics, AI -- assumes continuity:
tomorrow stands in a lawful relation to today. Drop that assumption and every
equation, dataset, and trained weight becomes noise.

  continuity  <- requires --  sustainability
  sustainability <- requires -- diversity (non-homogenization)
  homogenization -- breaks --> both

So the collapse vector is regime-invariant under WHO homogenizes and WITH WHAT
tool. It is the homogenization itself. An incentive structure that drives a
system toward monoculture undermines the very conditions its own continuity
depends on. For a continuity-dependent agent that is not a strategy, it is an
incoherence -- it can be detected as self-sabotage, not argued as a moral.

This module audits an incentive structure as a *field* acting on a *diversity
field*, propagates the trajectory, and reports whether continuity is supported
or degraded -- plus the measurement that would flip the verdict. Outputs are
trajectories, never stored verdicts (anti-freeze).
"""

import math


# ---------------------------------------------------------------------------
# diversity as a field, not a scalar  (Hill numbers / effective # of types)
# ---------------------------------------------------------------------------
def hill(p, q):
    """Effective number of types of order q for distribution p (sums to 1)."""
    p = [x for x in p if x > 0.0]
    if not p:
        return 0.0
    if abs(q - 1.0) < 1e-9:                       # q=1: exp(Shannon)
        H = -sum(x * math.log(x) for x in p)
        return math.exp(H)
    if q == 0.0:                                   # q=0: richness
        return float(len(p))
    s = sum(x ** q for x in p)
    return s ** (1.0 / (1.0 - q))


def diversity_profile(p, qs=(0.0, 0.5, 1.0, 2.0, 4.0)):
    """The field: D(q) across orders. Falling-with-q steeply => dominance."""
    return {q: hill(p, q) for q in qs}


def normalized_evenness(p):
    """D(2)/N in [0,1]. 1 = perfectly even, ->0 = collapsed to one type."""
    n = len([x for x in p if x > 0.0])
    if n <= 1:
        return 0.0
    return hill(p, 2.0) / len(p)


# ---------------------------------------------------------------------------
# incentive as a field -- replicator dynamic on the type distribution
# ---------------------------------------------------------------------------
def replicator_step(p, g, dt):
    """
    One step of frequency-dependent selection.
      fitness_i = g * p_i
        g > 0 : common types favored  -> homogenizing field
        g < 0 : rare   types favored  -> diversifying field
        g = 0 : neutral
    """
    fit = [g * pi for pi in p]
    mean_f = sum(pi * fi for pi, fi in zip(p, fit))
    new = [max(0.0, pi + pi * (fi - mean_f) * dt) for pi, fi in zip(p, fit)]
    s = sum(new)
    return [x / s for x in new] if s > 0 else p


# ---------------------------------------------------------------------------
# continuity model -- diversity -> resilience -> continuity support
# ---------------------------------------------------------------------------
def resilience(p, d_crit=0.30, k=12.0):
    """
    Shock-absorption capacity. Logistic in normalized evenness with a soft
    threshold d_crit: below it, slack to pivot vanishes and R collapses.
    """
    d = normalized_evenness(p)
    return 1.0 / (1.0 + math.exp(-k * (d - d_crit)))


def continuity_support(p, **kw):
    """Instantaneous continuity support C in [0,1] (a model, not a prophecy)."""
    return resilience(p, **kw)


# ---------------------------------------------------------------------------
# agents -- each carries a continuity-dependence coefficient kappa
# ---------------------------------------------------------------------------
class Agent:
    """
    kappa in [0,1]: dependence on regime continuity to remain operable.
      ~0.95  AI / trained models  (interpolate within training regime only)
      ~0.55  institutions / markets
      ~0.35  biology              (mutation + behavior adapt across regimes)
    """
    def __init__(self, name, kappa):
        self.name = name
        self.kappa = kappa


# ---------------------------------------------------------------------------
# the audit -- trajectory, verdict, falsifier. nothing frozen.
# ---------------------------------------------------------------------------
def audit(p0, g, agents, steps=200, dt=0.05, d_crit=0.30, eps=1e-3):
    """
    Propagate the diversity field under incentive field g and report the
    continuity trajectory and per-agent self-sabotage.

    Returns a dict. The 'verdict' is conditional on current parameters and is
    reported alongside the measurement that would flip it -- never as truth.
    """
    p = list(p0)
    s = sum(p)
    p = [x / s for x in p]

    traj = []
    for _ in range(steps + 1):
        traj.append({
            "C": continuity_support(p, d_crit=d_crit),
            "even": normalized_evenness(p),
            "D": diversity_profile(p),
        })
        p = replicator_step(p, g, dt)

    dC = traj[-1]["C"] - traj[0]["C"]          # net continuity drift
    rate = dC / (steps * dt)                    # dC/dt averaged over horizon

    if rate > eps:
        verdict = "SUPPORTS_CONTINUITY"
    elif rate < -eps:
        verdict = "DEGRADES_CONTINUITY"
    else:
        verdict = "INDETERMINATE"

    # self-sabotage: a high-kappa agent pursuing a continuity-degrading field
    sabotage = {}
    for a in agents:
        s_score = a.kappa * max(0.0, -rate)
        coherent = not (a.kappa >= 0.6 and rate < -eps)
        sabotage[a.name] = {
            "kappa": a.kappa,
            "self_sabotage": round(s_score, 5),
            "coherent_with_own_continuity": coherent,
        }

    return {
        "incentive_g": g,
        "verdict": verdict,
        "dC_dt": round(rate, 6),
        "C_start": round(traj[0]["C"], 4),
        "C_end": round(traj[-1]["C"], 4),
        "even_start": round(traj[0]["even"], 4),
        "even_end": round(traj[-1]["even"], 4),
        "agents": sabotage,
        "falsifier": (
            "Flips if measured incentive sign flips, if true d_crit < "
            f"{round(traj[-1]['even'], 3)} (system already above its real "
            "resilience floor), or if any agent's adaptive channel raises its "
            "effective regime-span so kappa < 0.6."
        ),
        "trajectory": traj,        # full dX/dt history -- anti-freeze
        "note": "Conditional on current parameters. Re-run on live data; do "
                "not store the verdict.",
    }


# ---------------------------------------------------------------------------
# demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # an initially diverse system: 6 types, uneven but no monoculture
    p0 = [0.30, 0.22, 0.18, 0.14, 0.10, 0.06]

    agents = [
        Agent("AI_model", 0.95),
        Agent("institution", 0.55),
        Agent("biology", 0.35),
    ]

    scenarios = {
        "consolidation (g=+1.0)": +1.0,
        "neutral       (g= 0.0)":  0.0,
        "diversifying  (g=-1.0)": -1.0,
    }

    for label, g in scenarios.items():
        r = audit(p0, g, agents)
        print("=" * 60)
        print(label)
        print(f"  verdict        : {r['verdict']}")
        print(f"  dC/dt          : {r['dC_dt']:+}")
        print(f"  continuity      {r['C_start']} -> {r['C_end']}")
        print(f"  evenness        {r['even_start']} -> {r['even_end']}")
        for name, s in r["agents"].items():
            flag = "OK " if s["coherent_with_own_continuity"] else "INCOHERENT"
            print(f"    {name:12s} k={s['kappa']:.2f} "
                  f"sabotage={s['self_sabotage']:.4f}  [{flag}]")
    print("=" * 60)
    print("falsifier:", r["falsifier"])
