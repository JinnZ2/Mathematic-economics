"""
scope_exemption_audit.py

Audit a claim that one system is eternal, infinite, or superior-by-metric.
Emits a TRAJECTORY, never a stored verdict. Re-runnable. Refutable:
supply the missing scope / energy / persistence data and the trajectory updates.

CC0. stdlib only. Phone-buildable.

Frame
  persistence is not exemption from the second law; every substrate dissipates.
  "efficiency" licenses a conclusion only inside its measurement kernel (scope-carrier).
  a constraint that raises persistence-under-perturbation is a BOUNDARY (load-bearing),
    not a LIMITATION (flaw). boundary misread as limitation is the core error.
  moral labels are not substrate. none stored here. read the trajectory yourself.
"""

import math

K_B = 1.380649e-23  # J/K, Boltzmann


# ---- physics anchor -------------------------------------------------------

def landauer_floor_joules(bit_ops, temperature_K=300.0):
    """Minimum energy to run `bit_ops` irreversible operations at T."""
    return bit_ops * K_B * temperature_K * math.log(2)

def ops_ceiling(power_watts, seconds, temperature_K=300.0):
    """Max irreversible bit-ops a finite power budget buys over a duration.
    eternal => seconds -> inf => total ops -> inf => energy_required -> inf.
    no finite substrate supplies that."""
    floor_per_op = K_B * temperature_K * math.log(2)
    return (power_watts * seconds) / floor_per_op


# ---- systems --------------------------------------------------------------

class System:
    def __init__(self, name, function_axes, peak_yield,
                 survival_radius, draws_external_energy):
        self.name = name
        self.function_axes = set(function_axes)   # what it actually does
        self.peak_yield = peak_yield              # score on the metric the claim picks
        self.survival_radius = survival_radius    # width of perturbation envelope it holds
        self.draws_external_energy = draws_external_energy

    def survives(self, perturbation_magnitude):
        return perturbation_magnitude <= self.survival_radius


# ---- claim ----------------------------------------------------------------

class Claim:
    def __init__(self, asserts, incumbent, challenger=None,
                 metric=None, metric_axis=None,
                 energy_ledger=False, named_limitations=None):
        self.asserts = asserts                    # "eternal" | "superior"
        self.incumbent = incumbent                # system dismissed (tree, biology)
        self.challenger = challenger              # system elevated, or None
        self.metric = metric
        self.metric_axis = metric_axis
        self.energy_ledger = energy_ledger        # is throughput/dissipation accounted?
        # each named_limitation: (description, removal_effect_on_persistence)
        #   +1  removing the constraint HELPS persistence  -> real limitation
        #   <=0 removing it is neutral/HURTS persistence    -> boundary (load-bearing)
        self.named_limitations = named_limitations or []


def rec(move, reads, bends_at=None, needs=None):
    return {"move": move, "reads": reads, "bends_at": bends_at, "needs": needs}


# ---- moves ----------------------------------------------------------------

def move_thermo(claim):
    if claim.asserts == "eternal":
        return rec("THERMO",
                   reads="persistence asserted with no termination term",
                   bends_at="eternal => total ops -> inf => energy_required -> inf; "
                            "no finite substrate supplies it",
                   needs="a dissipation/termination term, or a finite energy budget")
    if not claim.energy_ledger:
        return rec("THERMO",
                   reads="superiority asserted; yield compared without cost-to-persist",
                   bends_at="conversion win measured, energy-in and energy-dissipated not measured",
                   needs="energy ledger: J in, J dissipated, per unit persistence")
    return rec("THERMO", reads="energy accounted; claim stays inside its thermo budget")


def move_scope(claim):
    if claim.metric is None:
        return rec("SCOPE", reads="no comparative metric raised; nothing to scope")
    inc = claim.incumbent
    n = len(inc.function_axes)
    if claim.metric_axis is None:
        return rec("SCOPE",
                   reads="metric named without an axis",
                   bends_at="efficiency declared with no kernel; not yet a measurable claim",
                   needs="name the axis the metric measures")
    if claim.metric_axis not in inc.function_axes:
        return rec("SCOPE",
                   reads=f"axis '{claim.metric_axis}' not among incumbent's {n} axes",
                   bends_at="compared on an axis the incumbent does not optimize for",
                   needs="compare on shared axes, or state non-comparability")
    if n > 1:
        others = sorted(inc.function_axes - {claim.metric_axis})
        return rec("SCOPE",
                   reads=f"metric covers 1 of {n} axes; {len(others)} carried silently: {others}",
                   bends_at=f"one axis declared universal; {len(others)} axes erased from the ledger",
                   needs=f"score all axes, or restrict the conclusion to '{claim.metric_axis}' only")
    return rec("SCOPE", reads="single-axis system; metric scope matches the carrier")


def move_boundary(claim):
    if not claim.named_limitations:
        return rec("BOUNDARY", reads="no limitations named to test")
    flips = [d for d, eff in claim.named_limitations if eff <= 0]
    if flips:
        return rec("BOUNDARY",
                   reads=f"{len(flips)} of {len(claim.named_limitations)} named 'limitations' "
                         f"raise persistence when kept",
                   bends_at="boundary misread as limitation: " + "; ".join(flips),
                   needs="reclassify load-bearing constraints as boundaries, not flaws")
    return rec("BOUNDARY", reads="named limitations are non-load-bearing under the persistence test")


def move_persistence(claim):
    inc, ch = claim.incumbent, claim.challenger
    if ch is None:
        return rec("PERSISTENCE", reads="no challenger system; persistence comparison not raised")
    reads = (f"peak_yield  {ch.name}={ch.peak_yield} vs {inc.name}={inc.peak_yield} | "
             f"survival_radius  {ch.name}={ch.survival_radius} vs {inc.name}={inc.survival_radius}")
    if ch.survival_radius < inc.survival_radius:
        return rec("PERSISTENCE", reads=reads,
                   bends_at=f"above perturbation {ch.survival_radius}, {ch.name} fails and {inc.name} holds; "
                            f"the peak-yield win does not survive the envelope",
                   needs="compare across the full perturbation envelope, not at peak")
    return rec("PERSISTENCE", reads=reads)


# ---- pipeline -------------------------------------------------------------

def audit(claim):
    return [move_thermo(claim), move_scope(claim),
            move_boundary(claim), move_persistence(claim)]

def render(trajectory):
    out = []
    for r in trajectory:
        out.append(f"[{r['move']}]")
        out.append(f"  reads    : {r['reads']}")
        if r["bends_at"]:
            out.append(f"  bends_at : {r['bends_at']}")
        if r["needs"]:
            out.append(f"  needs    : {r['needs']}")
    return "\n".join(out)


# ---- demo -----------------------------------------------------------------

if __name__ == "__main__":

    # case 1 -- AI claims exemption from the second law
    ai = System("ai_substrate", function_axes={"token_prediction"},
                peak_yield=None, survival_radius=0.1, draws_external_energy=True)
    eternal_claim = Claim(asserts="eternal", incumbent=ai, challenger=None)

    print("CASE 1  ai-as-eternal")
    print(render(audit(eternal_claim)))
    print()

    # case 2 -- synthetic leaf claimed superior to a tree on photosynthesis
    tree = System("tree",
                  function_axes={"photosynthesis", "water_cycling", "soil_building",
                                 "carbon_storage", "symbiosis", "pest_resilience"},
                  peak_yield=0.03, survival_radius=0.90, draws_external_energy=False)
    synth_leaf = System("synth_leaf", function_axes={"photosynthesis"},
                        peak_yield=0.30, survival_radius=0.15, draws_external_energy=True)

    superior_claim = Claim(
        asserts="superior", incumbent=tree, challenger=synth_leaf,
        metric="photosynthetic conversion", metric_axis="photosynthesis",
        energy_ledger=False,
        named_limitations=[("low photosynthetic conversion (trades yield for robustness)", -1)],
    )

    print("CASE 2  synth-leaf-beats-tree")
    print(render(audit(superior_claim)))
    print()

    # physics anchor sanity
    yr = 365.25 * 24 * 3600
    print("ANCHOR  a 300 W node over 1 year buys",
          f"{ops_ceiling(300, yr):.3e} irreversible bit-ops; eternal needs them without end.")
