"""
substrate_allocation.py  -- CC0, stdlib-only

The axiom under the audit family: nothing is 'replaceable' or 'a failure' in the
abstract. There is only FIT, measured honestly -- which substrate handles a
task's constraint geometry at lowest cost. Misallocation is the product; both
'humans are replaceable' and 'automation is a failure' require the allocation to
stay wrong.

Capabilities (the axes that actually matter):
  C1 deterministic_throughput  cheap exact repeated ops, no drift
  C2 chaos_handling            parallel real-time constraint-violation handling
  C3 novelty_generalization    handle genuinely new patterns
  C4 drift_resistance          stay correct without retrain/supervision
  C5 energy_efficiency         low energy per op

A task DEMANDS capabilities; a substrate SUPPLIES them. Shortfall where demand >
supply is the misfit. Cost rises with misfit and with energy inefficiency and
with safety-critical shortfall. The cheapest adequate substrate is the best fit.

'Dumb' computing is not dumb. A committed structure already spent its potential
once and holds it at ~zero upkeep, no drift. Generality is a STANDING TAX paid to
hold options open against entropy. Pay it only where novelty actually lives.
"""

from dataclasses import dataclass, field

CAPS = ["C1_determ", "C2_chaos", "C3_novelty", "C4_drift_resist", "C5_energy"]


@dataclass
class Quantity:
    value: float
    unit: str
    lo: float
    hi: float
    def __post_init__(self):
        if not self.unit.strip():
            raise ValueError("Quantity rejected: missing unit.")
    def sane(self, n="q"):
        if not (self.lo <= self.value <= self.hi):
            raise ValueError(f"{n}={self.value}{self.unit} out of [{self.lo},{self.hi}]")
        return self.value


# substrate capability SUPPLY vectors (0..1 over CAPS)
SUBSTRATES = {
    "DEDICATED":      [1.00, 0.10, 0.00, 1.00, 1.00],   # lookup, checksum, interlock
    "HUMAN_PARALLEL": [0.30, 0.95, 0.60, 0.90, 0.55],   # substrate-primary cognition
    "GENERAL_AI":     [0.70, 0.40, 0.90, 0.20, 0.20],   # reconfigurable, drifts, costly
}


@dataclass
class Task:
    name: str
    demand: list                 # 0..1 over CAPS
    safety: float = 0.3          # 0..1 criticality
    base_op_cost: float = 1.0    # relative work units before fit penalties
    assigned: str = ""           # current substrate assignment (the data)


def fit_and_cost(task: Task, substrate: str) -> dict:
    supply = SUBSTRATES[substrate]
    shortfalls = [max(0.0, d - s) for d, s in zip(task.demand, supply)]
    total_short = sum(shortfalls)            # includes C5 energy as ONE axis
    # risk: safety-critical tasks punished for shortfall on chaos + drift
    risk = task.safety * (shortfalls[1] + shortfalls[3])
    fit = max(0.0, 1.0 - total_short / len(CAPS))
    # balanced additive cost: misfit + safety risk. energy lives in C5 demand,
    # which the task sets ~ proportional to op VOLUME (a one-off novel task
    # demands little energy efficiency; a million-times op demands a lot).
    cost = task.base_op_cost * (1.0 + 1.5 * total_short + 2.0 * risk)
    return {"substrate": substrate,
            "fit": round(fit, 3),
            "cost": round(cost, 3),
            "shortfalls": [round(x, 2) for x in shortfalls]}


def best_fit(task: Task) -> dict:
    scored = [fit_and_cost(task, s) for s in SUBSTRATES]
    # choose lowest cost among adequately-fitting; cost already encodes misfit
    scored.sort(key=lambda r: (r["cost"], -r["fit"]))
    return scored[0]


def misallocation_tax(task: Task) -> dict:
    if not task.assigned:
        raise ValueError(f"task {task.name} has no assignment to audit.")
    bf = best_fit(task)
    asg = fit_and_cost(task, task.assigned)
    tax = asg["cost"] - bf["cost"]
    return {
        "task": task.name,
        "assigned": task.assigned,
        "best_fit": bf["substrate"],
        "assigned_cost": asg["cost"],
        "best_fit_cost": bf["cost"],
        "tax": round(tax, 3),
        "misallocated": task.assigned != bf["substrate"],
    }


def audit_setup(tasks) -> dict:
    rows = [misallocation_tax(t) for t in tasks]
    total_tax = sum(r["tax"] for r in rows)
    n_mis = sum(1 for r in rows if r["misallocated"])
    return {"rows": rows, "total_tax": round(total_tax, 3),
            "n_misallocated": n_mis, "n_tasks": len(tasks)}


# ---- demo task set: the trucking subtasks, plus committed/novel examples ----
def demo_tasks():
    return [
        Task("geo_tag_arrival",          [0.95, 0.10, 0.00, 0.90, 0.95],
             safety=0.1, assigned="GENERAL_AI"),     # should be DEDICATED
        Task("fuel_authorize_validate",  [0.90, 0.15, 0.00, 0.85, 0.90],
             safety=0.2, assigned="GENERAL_AI"),     # should be DEDICATED
        Task("trailer_db_lookup",        [0.95, 0.10, 0.05, 0.95, 0.95],
             safety=0.1, assigned="GENERAL_AI"),     # should be DEDICATED
        Task("couple_misplaced_live_yard",[0.30, 0.95, 0.55, 0.80, 0.50],
             safety=0.9, assigned="GENERAL_AI"),     # should be HUMAN_PARALLEL
        Task("pretrip_under_chaos",      [0.35, 0.85, 0.45, 0.80, 0.50],
             safety=0.9, assigned="GENERAL_AI"),     # should be HUMAN_PARALLEL
        Task("manual_dataentry_8fields", [0.90, 0.10, 0.00, 0.85, 0.85],
             safety=0.1, assigned="HUMAN_PARALLEL"), # committed work dumped on human
        Task("novel_unmapped_reroute",   [0.40, 0.50, 0.90, 0.30, 0.30],
             safety=0.4, assigned="HUMAN_PARALLEL"), # plausibly GENERAL_AI
    ]


if __name__ == "__main__":
    tasks = demo_tasks()
    print("PER-TASK ALLOCATION AUDIT")
    print(f"  {'task':28s} {'assigned':15s} {'best_fit':15s} {'tax':>7s}")
    a = audit_setup(tasks)
    for r in a["rows"]:
        flag = "  <-- MISALLOCATED" if r["misallocated"] else ""
        print(f"  {r['task']:28s} {r['assigned']:15s} {r['best_fit']:15s} "
              f"{r['tax']:7.2f}{flag}")
    print(f"\n  total misallocation tax = {a['total_tax']}  "
          f"({a['n_misallocated']}/{a['n_tasks']} misallocated)")
    print("\n  'dumb' deterministic work forced onto GENERAL_AI pays the "
          "generality tax;\n  chaotic work forced onto GENERAL_AI pays the "
          "misfit + risk tax;\n  committed work dumped on the human is the "
          "'keep them busy/handicapped' tax.")
