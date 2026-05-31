"""
automation_metrology_audit.py  -- CC0, stdlib-only

AUDIT: "automation beats human labor" claims rest on an invalid measurement.
The industry benchmarks a BOTTLENECKED human (mandatory tiny-screen data entry,
GPS validation gates, manual address correction) against an UNENCUMBERED
automation (logs straight from sensors, no data-entry tax). That is not a
head-to-head test. It is a rigged measurement. This module quantifies the rig
and lets the numbers decide.

Three configurations, same task, same constraint environment:
  BASELINE_HUMAN     paper folder, parallel cognition, NO digital data-entry tax
  BOTTLENECKED_HUMAN baseline + the mandatory input/validation tax (current reality)
  AUTOMATION         serial perceive-plan-validate-log, retries on violation

Outputs: time, decision-energy, physical-energy, throughput (units/shift),
energy-per-unit; a violation-rate crossover sweep; and a METROLOGY VERDICT that
detects the rig and reports what the FAIR comparison says.

PARAMETERS ARE EXPLICIT AT TOP. Tune to your yard. Everything carries units.
"""

from dataclasses import dataclass, field
from decision_tree_energy import (DNode, traverse_automation, traverse_human,
                                  Quantity, gate)

# ---- ENERGY / TIME PARAMETERS (documented, tunable) --------------------
SHIFT_HOURS = 11.0                 # legal driving/work window
HUMAN_PHYSICAL_W = 350.0           # active yard work metabolic draw [W]
AUTO_PHYSICAL_W = 350.0            # SAME physical work (mass x distance) [W]
                                   # honesty: moving a trailer costs ~the same
                                   # regardless of who decides. asymmetry is in
                                   # the DECISION layer, not the muscle.
# CONTINUOUS automation intelligence draw -- ON for the whole cycle, not just
# per-node. This was omitted in v1 and unfairly favored automation on energy.
AUTO_COMPUTE_W = 800.0             # perception + planning stack (GPU/CPU) [W]
AUTO_SENSOR_W = 200.0              # LiDAR + cameras + force/pressure sensors [W]

DATAENTRY_FIELDS_PER_STOP = 8      # temp, miles, arrival, trailer#, seal, ...
DATAENTRY_S_PER_FIELD = 28.0       # seconds per field on a tiny screen
GPS_FAILURE_PENALTY_S = 180.0      # manual address/reroute when GPS rejects truth
GPS_FAILURE_RATE = 0.25            # fraction of stops GPS db is stale/wrong

#   NOTE: DATAENTRY tax + GPS penalty have NO automation analog (sensors log
#   directly). They are the ARTIFICIAL human handicap. That is the whole point.
#
#   HONESTY ON AUTOMATION TIME: the per-node durations in trailer_cycle() are
#   ILLUSTRATIVE GUESSES, not measured. They are the weakest numbers here. Pass
#   observed_automation_cycle_s (e.g. from watching a real yard) to override the
#   tree and benchmark against GROUND TRUTH instead of a guess. Kavik's yard
#   observation -- automation completes ~1 cycle per ~2 of his -- goes here.


@dataclass
class Operation:
    name: str
    human_unencumbered_s: float    # Kavik's measured reality (fast, parallel)
    tree: list                     # automation decision/validation tree
    has_dataentry: bool = False    # does the system force input here?


# ---- THE WORKFLOW: one trailer cycle in a DC yard ----------------------
def trailer_cycle():
    return [
        Operation("locate_trailer", 90.0, [
            DNode("query_or_recall", 5, 100, 20, network_j=400,
                  retries_on_violation=True),
            DNode("drive_to_slot", 40, 80, 60),
            DNode("perceive_present", 10, 300, 150, retries_on_violation=True),
        ]),
        Operation("drop_current", 120.0, [
            DNode("align_drop", 25, 250, 120),
            DNode("dolly_down", 30, 60, 40),
            DNode("disconnect_glad_hands", 15, 90, 70),
            DNode("validate_clear", 8, 120, 90),
        ]),
        Operation("couple_next", 150.0, [
            DNode("back_under", 35, 400, 200, retries_on_violation=True),
            DNode("validate_kingpin_lock", 10, 150, 110),
            DNode("connect_glad_hands", 18, 100, 80),
            DNode("dolly_up", 28, 60, 40),
        ]),
        Operation("pretrip", 300.0, [
            DNode("inspect_lights", 20, 120, 100),
            DNode("inspect_tires", 30, 140, 120),
            DNode("check_seal", 10, 90, 70),
            DNode("apply_lock", 12, 60, 40),
            DNode("log_inspection", 8, 40, 0, network_j=200),
        ]),
        Operation("fuel", 300.0, [
            DNode("authorize_pump", 20, 80, 30, network_j=600,
                  retries_on_violation=True),
            DNode("calibrate_nozzle_sensor", 25, 120, 150),
            DNode("monitor_flow", 240, 200, 180),
            DNode("validate_fill", 10, 90, 70),
        ], has_dataentry=True),
        Operation("log_arrival_depart", 60.0, [
            DNode("geo_confirm", 8, 60, 40, network_j=300,
                  retries_on_violation=True),
            DNode("write_record", 10, 40, 0, network_j=200),
        ], has_dataentry=True),
    ]


def dataentry_tax_s(ops) -> float:
    stops = sum(1 for o in ops if o.has_dataentry)
    tax = stops * DATAENTRY_FIELDS_PER_STOP * DATAENTRY_S_PER_FIELD
    tax += GPS_FAILURE_RATE * GPS_FAILURE_PENALTY_S
    return tax


def run_config(config: str, violation_rate: float, backtrack: float = 2.5,
               observed_automation_cycle_s: float = 0.0):
    ops = trailer_cycle()
    t_total = 0.0
    e_node = 0.0       # per-node decision spikes (automation) / cognition (human)

    for o in ops:
        if config == "AUTOMATION":
            r = traverse_automation(o.tree, violation_rate, backtrack)
            t_total += r["time_s"]
            e_node += r["energy_j"]      # incremental planning spikes per node
        else:
            r = traverse_human(o.tree, violation_rate)
            t_total += o.human_unencumbered_s
            e_node += HUMAN_PHYSICAL_W * o.human_unencumbered_s + r["energy_j"]
            if any(n.retries_on_violation for n in o.tree):
                t_total += violation_rate * 25.0   # flat parallel penalty

    if config == "BOTTLENECKED_HUMAN":
        tax = dataentry_tax_s(ops)
        t_total += tax
        e_node += HUMAN_PHYSICAL_W * tax

    if config == "AUTOMATION":
        # observed override: trust ground truth over the guessed tree
        if observed_automation_cycle_s > 0.0:
            t_total = observed_automation_cycle_s
        # CONTINUOUS draw: physical move + perception/planning stack + sensors,
        # powered the ENTIRE cycle (this is the v1 omission, now corrected)
        continuous_w = AUTO_PHYSICAL_W + AUTO_COMPUTE_W + AUTO_SENSOR_W
        e_total = e_node + continuous_w * t_total
    else:
        e_total = e_node   # human physical already folded in per-op

    cycle_time_s = gate(Quantity(t_total, "s", 1.0, 1.0e5), "cycle_time")
    cycle_energy_j = gate(Quantity(e_total, "J", 1.0, 1.0e9), "cycle_energy")
    units_per_shift = (SHIFT_HOURS * 3600.0) / cycle_time_s
    return {
        "config": config,
        "cycle_time_s": round(cycle_time_s, 1),
        "cycle_energy_j": round(cycle_energy_j, 0),
        "units_per_shift": round(units_per_shift, 1),
        "energy_per_unit_kj": round(cycle_energy_j / 1000.0, 1),
    }


def crossover_sweep(rates=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)):
    rows = []
    for vr in rates:
        h = run_config("BASELINE_HUMAN", vr)
        b = run_config("BOTTLENECKED_HUMAN", vr)
        a = run_config("AUTOMATION", vr)
        rows.append({
            "violation_rate": vr,
            "baseline_human_units": h["units_per_shift"],
            "bottlenecked_human_units": b["units_per_shift"],
            "automation_units": a["units_per_shift"],
            "auto_vs_baseline_time": round(a["cycle_time_s"]
                                           / run_config("BASELINE_HUMAN", vr)["cycle_time_s"], 2),
        })
    return rows


def metrology_verdict(violation_rate=0.3, observed_automation_cycle_s=0.0):
    base = run_config("BASELINE_HUMAN", violation_rate)
    bott = run_config("BOTTLENECKED_HUMAN", violation_rate)
    auto = run_config("AUTOMATION", violation_rate,
                      observed_automation_cycle_s=observed_automation_cycle_s)

    advertised = bott["cycle_time_s"] / auto["cycle_time_s"]   # what industry shows
    fair = base["cycle_time_s"] / auto["cycle_time_s"]         # head-to-head
    handicap_s = bott["cycle_time_s"] - base["cycle_time_s"]

    # advertised>1 => automation looks faster than the bottlenecked human
    # fair<1       => the UNENCUMBERED human is actually faster
    invalid = (advertised > 1.0) and (fair < 1.0)

    if invalid:
        verdict = ("METROLOGY_INVALID: automation 'wins' only against the "
                   "handicapped human. Remove the data-entry/GPS tax and the "
                   "unencumbered human is faster. The benchmark is rigged.")
    elif fair < 1.0 and advertised <= 1.0:
        verdict = ("HUMAN_WINS_OUTRIGHT: observed automation is slower than "
                   "even the HANDICAPPED human. The 'automation is faster' "
                   "claim is not just rigged, it is false at these params.")
    elif fair >= 1.0:
        verdict = ("CLAIM_FALSIFIED (this audit's claim): automation is faster "
                   "head-to-head even without the human handicap. The bottleneck "
                   "was NOT the cause; automation genuinely wins on time here.")
    else:
        verdict = ("INCONCLUSIVE at this violation_rate; sweep to find the flip.")

    energy_winner = ("human" if base["energy_per_unit_kj"]
                     < auto["energy_per_unit_kj"] else "automation")

    return {
        "violation_rate": violation_rate,
        "automation_time_source": ("OBSERVED" if observed_automation_cycle_s > 0
                                   else "GUESSED_TREE (weak - measure this)"),
        "baseline_human_cycle_s": base["cycle_time_s"],
        "bottlenecked_human_cycle_s": bott["cycle_time_s"],
        "automation_cycle_s": auto["cycle_time_s"],
        "artificial_handicap_s": round(handicap_s, 1),
        "advertised_automation_advantage_x": round(advertised, 2),
        "fair_automation_advantage_x": round(fair, 2),
        "energy_per_unit_kj": {
            "baseline_human": base["energy_per_unit_kj"],
            "automation": auto["energy_per_unit_kj"],
        },
        "energy_winner": energy_winner,
        "verdict": verdict,
    }


CLAIMS = [
    {"cid": "MET-01", "evidence": "DERIVED", "unit": "advantage_ratio",
     "statement": "Industry benchmarks bottlenecked-human vs unencumbered-"
                  "automation; the data-entry/GPS tax has no automation analog.",
     "falsifier": "Show the mandated human inputs are also required of and "
                  "timed against the automated system. Then the tax is symmetric "
                  "and the comparison is valid."},
    {"cid": "MET-02", "evidence": "SPECULATIVE", "unit": "advantage_ratio",
     "statement": "Removing the artificial handicap inverts the result: the "
                  "unencumbered human is faster per cycle.",
     "falsifier": "fair_automation_advantage_x >= 1 after the tax is removed."},
    {"cid": "MET-03", "evidence": "DERIVED", "unit": "J_per_unit",
     "statement": "Automation decision-energy scales with violation_rate x "
                  "backtrack depth; human handles violations in parallel at flat "
                  "marginal cost, so energy-per-unit crosses over above some "
                  "violation rate.",
     "falsifier": "Energy-per-unit shows no crossover across plausible "
                  "violation rates (automation always lower or always higher)."},
]


if __name__ == "__main__":
    print("=== SINGLE-CYCLE (violation_rate=0.3, GUESSED automation tree) ===")
    for cfg in ("BASELINE_HUMAN", "BOTTLENECKED_HUMAN", "AUTOMATION"):
        r = run_config(cfg, 0.3)
        print(f"  {cfg:20s} {r['cycle_time_s']:7.0f}s  "
              f"{r['energy_per_unit_kj']:8.1f} kJ/unit  "
              f"{r['units_per_shift']:5.1f} units/shift")

    print("\n=== METROLOGY VERDICT (A) automation time = GUESSED tree ===")
    v1 = metrology_verdict(0.3)
    for k, val in v1.items():
        if k != "verdict":
            print(f"  {k}: {val}")
    print(f"  >> {v1['verdict']}")

    # Kavik's yard observation: automation completes ~1 cycle per ~2 of his.
    # baseline human unencumbered cycle ~1020 s -> observed automation ~2040 s.
    obs = 2040.0
    print(f"\n=== METROLOGY VERDICT (B) automation time = OBSERVED {obs:.0f}s ===")
    print("    (your yard: automation finishes 1 cycle per ~2 of yours)")
    v2 = metrology_verdict(0.3, observed_automation_cycle_s=obs)
    for k, val in v2.items():
        if k != "verdict":
            print(f"  {k}: {val}")
    print(f"  >> {v2['verdict']}")

    print("\n  The point: the verdict HINGES on automation cycle time, which is")
    print("  the one number nobody publishes head-to-head. Guess -> automation")
    print("  wins. Your measurement -> it does not. Demand the measurement.")
