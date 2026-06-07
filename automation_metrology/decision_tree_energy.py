"""
decision_tree_energy.py  -- CC0, stdlib-only

The decision/validation layer is where human and automation diverge. This
module makes the tree EXPLICIT: nodes, dependencies, and the energy + time each
node costs. Physical relocation of mass is ~equal for both (work = force x
distance) and is accounted separately. The ASYMMETRY lives here, in the cost of
DECIDING and VALIDATING under constraint violations.

Thesis (KAVIK): a human handles a misplaced-trailer / stale-GPS violation in
PARALLEL at ~flat metabolic cost. Automation must re-traverse the tree:
re-perceive, re-plan, re-validate, sometimes round-trip a fleet server. Each
retry is a full cycle. Energy scales with violation_rate x backtrack_depth.

Metrological skin: nothing crosses a boundary without a unit + sanity range.
"""

from dataclasses import dataclass, field


@dataclass
class Quantity:
    value: float
    unit: str
    lo: float
    hi: float

    def __post_init__(self):
        if not self.unit.strip():
            raise ValueError("Quantity rejected: missing unit.")
        if self.lo > self.hi:
            raise ValueError("Quantity rejected: bad range.")

    def assert_sane(self, name="q"):
        if not (self.lo <= self.value <= self.hi):
            raise ValueError(f"{name}={self.value} {self.unit} outside "
                             f"[{self.lo},{self.hi}]")
        return self.value


def gate(q: Quantity, name="q"):
    return q.assert_sane(name)


@dataclass
class DNode:
    """One node in a decision/validation tree."""
    nid: str
    duration_s: float            # wall-clock to execute the node once
    compute_j: float             # inference / planning energy per execution
    sensor_j: float              # sensor read + fusion energy per execution
    network_j: float = 0.0       # remote (fleet/datacenter) query energy
    depends_on: list = field(default_factory=list)
    retries_on_violation: bool = False   # re-executes when constraint violated


def _exec_count(node: DNode, violation_rate: float, backtrack: float) -> float:
    """Expected number of executions of a node given the constraint env."""
    if not node.retries_on_violation:
        return 1.0
    # baseline once + expected extra traversals when the world is wrong
    return 1.0 + violation_rate * backtrack


def traverse_automation(tree, violation_rate=0.0, backtrack=1.0) -> dict:
    """
    Automation is SERIAL: total time = sum of node durations along execution
    (it cannot physically couple while still perceiving). Energy sums over all
    executions including violation-driven retries.
    """
    t_total = 0.0
    e_total = 0.0
    for node in tree:
        n = _exec_count(node, violation_rate, backtrack)
        t_total += node.duration_s * n
        e_total += (node.compute_j + node.sensor_j + node.network_j) * n
    t = gate(Quantity(t_total, "s", 0.0, 1.0e5), "auto_time")
    e = gate(Quantity(e_total, "J", 0.0, 1.0e9), "auto_energy")
    return {"time_s": t, "energy_j": e}


def traverse_human(tree, violation_rate=0.0,
                   parallelism=0.55,
                   violation_penalty_s=30.0,
                   cognitive_w=20.0) -> dict:
    """
    Human handles the same tree but in PARALLEL (substrate-primary spatial
    cognition): effective time = serial sum x parallelism factor (<1 means
    overlap). Violations cost a FLAT penalty, not a multiplicative retry.
    Cognitive energy is the small marginal brain draw over the duration.
    """
    serial = sum(node.duration_s for node in tree)
    t_total = serial * parallelism + violation_rate * violation_penalty_s
    e_total = cognitive_w * t_total            # marginal cognitive energy only
    t = gate(Quantity(t_total, "s", 0.0, 1.0e5), "human_time")
    e = gate(Quantity(e_total, "J", 0.0, 1.0e9), "human_energy")
    return {"time_s": t, "energy_j": e}


if __name__ == "__main__":
    # toy tree: locate trailer -> perceive -> validate kingpin -> validate seal
    tree = [
        DNode("locate", 8, 150, 40, network_j=500, retries_on_violation=True),
        DNode("perceive_align", 12, 300, 120, retries_on_violation=True),
        DNode("validate_kingpin", 6, 120, 80),
        DNode("validate_seal", 5, 90, 60),
        DNode("log_state", 3, 30, 0, network_j=200),
    ]
    for vr in (0.0, 0.3, 0.6):
        a = traverse_automation(tree, vr, backtrack=2.5)
        h = traverse_human(tree, vr)
        print(f"violation_rate={vr:.1f}  "
              f"AUTO {a['time_s']:.0f}s/{a['energy_j']:.0f}J   "
              f"HUMAN {h['time_s']:.0f}s/{h['energy_j']:.0f}J")
