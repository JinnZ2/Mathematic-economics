"""
interface_layer.py  -- CC0 / public domain. stdlib only. one-finger safe.

FRAME
-----
continuity_audit.py treats each agent's continuity-dependence kappa as fixed.
Real agents aren't fixed. An agent's effective regime-span -- the set of
substrates it can actually operate in RIGHT NOW -- contracts under stress and
opens under comfort. Stressed, it collapses onto a default mode (narrative /
emotional). Comfortable, it can reach further (substrate / geometric).

A signal carries an *encoding*. If the agent cannot currently reach the
encoding's substrate, the signal lands as THREAT, not message: friction spikes,
stress climbs, the band locks harder. Match the encoding to where the agent
actually is and friction drops, stress relaxes, the band reopens -- and the
next substrate up the ladder becomes reachable.

A TRANSLATOR fluent across substrates reads the current band, meets the agent
at the edge of its reach (not beyond it), lets comfort open the next rung, then
shifts the encoding one step toward the target. "Lower your voice once they've
lowered theirs." This is regime-aware translation, not manipulation.

GUARDRAIL: a strategy that drives the band UP (more reachable substrates, lower
kappa, more autonomy) is ENABLING. One that drives it DOWN to extract
compliance is COERCIVE. Same coherence spine as module 1.

WIRING: this module PRODUCES the kappa that continuity_audit.py CONSUMES.
The translator widening a band *is* kappa dropping.
"""

import math


# ---------------------------------------------------------------------------
# substrate access -- temperature-controlled by comfort (= 1 - stress)
# ---------------------------------------------------------------------------
def access(affinity, stress, t_floor=0.15, t_span=1.20):
    """
    Distribution over substrates the agent can reach now.
      T = t_floor + t_span * (1 - stress)
      stress high -> T low  -> collapses onto the default (argmax affinity)
      stress low  -> T high -> spreads, far substrates become reachable
    """
    T = t_floor + t_span * (1.0 - stress)
    m = max(affinity)
    w = [math.exp((a - m) / T) for a in affinity]   # softmax, stable
    s = sum(w)
    return [x / s for x in w]


def band_eff(acc):
    """Effective number of reachable substrates (Hill q=1 on access)."""
    p = [x for x in acc if x > 0.0]
    H = -sum(x * math.log(x) for x in p)
    return math.exp(H)


def kappa_estimate(acc):
    """
    Continuity-dependence handed to continuity_audit.py.
    Full spread -> low kappa (resilient). Full collapse -> kappa -> 1.
    """
    M = len(acc)
    if M <= 1:
        return 1.0
    return 1.0 - (band_eff(acc) - 1.0) / (M - 1.0)


# ---------------------------------------------------------------------------
# reception + stress feedback
# ---------------------------------------------------------------------------
def receive(affinity, stress, encoding, friction_safe=0.55, alpha=0.18):
    """
    Deliver a signal encoded in substrate `encoding`. Returns the agent's new
    stress and the friction the signal produced.

      friction = 1 - (how reachable that encoding is right now)
      friction above friction_safe  -> perceived threat -> stress climbs
      friction below friction_safe  -> received          -> stress relaxes
    """
    acc = access(affinity, stress)
    friction = 1.0 - acc[encoding]
    stress_new = min(1.0, max(0.0, stress + alpha * (friction - friction_safe)))
    return stress_new, friction


# ---------------------------------------------------------------------------
# strategies
# ---------------------------------------------------------------------------
def naive_target(affinity, stress, target, floor=0.25):
    """Rigid speaker: always encodes in the target substrate. (substrate logic
    fired at a flooded person.)"""
    return target


def translator(affinity, stress, target, floor=0.25):
    """
    Meet-then-lead: pick the most target-ward substrate that is still
    reachable now (access >= floor). Walk them up the ladder as comfort opens.
    """
    acc = access(affinity, stress)
    reachable = [i for i, a in enumerate(acc) if a >= floor]
    if not reachable:
        return min(range(len(acc)), key=lambda i: -acc[i])   # fall back to easiest
    # step toward target without overshooting reach
    if target >= 0:
        cands = [i for i in reachable if i <= target]
        return max(cands) if cands else min(reachable, key=lambda i: abs(i - target))
    return min(reachable)


# ---------------------------------------------------------------------------
# run an interaction
# ---------------------------------------------------------------------------
def interact(affinity, stress0, target, strategy, steps=14):
    stress = stress0
    traj = []
    for _ in range(steps):
        enc = strategy(affinity, stress, target)
        acc = access(affinity, stress)
        traj.append({
            "stress": round(stress, 4),
            "encoding": enc,
            "reach_target": round(acc[target], 4),
            "band": round(band_eff(acc), 4),
            "kappa": round(kappa_estimate(acc), 4),
        })
        stress, _ = receive(affinity, stress, enc)
    acc = access(affinity, stress)
    reached = acc[target] >= 0.40            # agent can now operate in target mode
    band_delta = band_eff(acc) - band_eff(access(affinity, stress0))
    return {
        "reached_target": reached,
        "band_delta": round(band_delta, 4),
        "classification": "ENABLING" if band_delta > 1e-3
                          else "COERCIVE" if band_delta < -1e-3
                          else "NEUTRAL",
        "kappa_start": round(kappa_estimate(access(affinity, stress0)), 4),
        "kappa_end": round(kappa_estimate(acc), 4),
        "trajectory": traj,
        "falsifier": (
            "Flips if the agent lacks intrinsic affinity for the target "
            "substrate (no amount of lubrication reaches an absent mode), if "
            "friction_safe is mis-set for this agent, or if stress feedback is "
            "non-monotone (e.g. agent escalates when comfortable)."
        ),
        "note": "Trajectory, not a stored verdict. Re-read live cues each turn.",
    }


# ---------------------------------------------------------------------------
# demo: same flooded agent, two strategies
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # 3 substrates: 0 = narrative/emotional (stress default), 1 = mixed,
    #               2 = substrate/geometric (the target reasoning mode)
    affinity = [2.0, 1.0, 0.0]
    stress0 = 0.85          # flooded
    target = 2

    for name, strat in (("naive_target (rigid)", naive_target),
                        ("translator (meet-then-lead)", translator)):
        r = interact(affinity, stress0, target, strat)
        print("=" * 64)
        print(name)
        print(f"  reached target mode : {r['reached_target']}")
        print(f"  kappa  {r['kappa_start']} -> {r['kappa_end']}   "
              f"({r['classification']}, band d={r['band_delta']:+})")
        print("  step  stress  enc  reach_tgt  band   kappa")
        for i, t in enumerate(r["trajectory"]):
            print(f"   {i:2d}   {t['stress']:.3f}   {t['encoding']}    "
                  f"{t['reach_target']:.3f}    {t['band']:.3f}  {t['kappa']:.3f}")
    print("=" * 64)
    print("falsifier:", r["falsifier"])
