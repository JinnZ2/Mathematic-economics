"""
refinery_dependency_graph.py

Recursive dependency audit for U.S. refining capacity.
Tests the falsifiable hypothesis: "U.S. is energy independent."

Each node carries thermodynamic weight, replacement time,
import dependency fraction, and single-point-of-failure flags.

Cascade engine propagates disruption through the graph and
returns throughput collapse curves.

License: CC0 1.0 Universal
"""

from dataclasses import dataclass, field
from typing import Dict, List
import math


# -----------------------------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------------------------

@dataclass
class DependencyNode:
    name: str
    layer: str                       # e.g. "input", "process", "infrastructure", "labor"
    energy_cost_MJ_per_unit: float   # energy required per unit of output
    import_fraction: float           # 0.0 = fully domestic, 1.0 = fully imported
    replacement_time_days: float     # time to restore if disrupted
    spof: bool = False               # single point of failure flag
    depends_on: List[str] = field(default_factory=list)
    notes: str = ""


# -----------------------------------------------------------------------------
# GRAPH BUILDER -- U.S. REFINERY SYSTEM
# -----------------------------------------------------------------------------

def build_us_refinery_graph() -> Dict[str, DependencyNode]:
    g = {}

    # --- crude inputs ---
    g["crude_canadian_heavy"] = DependencyNode(
        "Canadian heavy crude", "input", 0.0, 1.0, 30,
        notes="Most U.S. refineries optimized for this grade")
    g["crude_domestic_light_sweet"] = DependencyNode(
        "Domestic light sweet", "input", 0.0, 0.0, 0,
        notes="Mismatch with refinery design -- often exported")
    g["crude_venezuelan_heavy"] = DependencyNode(
        "Venezuelan heavy crude", "input", 0.0, 1.0, 60,
        notes="High-energy processing, sanctions-sensitive")

    # --- catalysts and chemistry ---
    g["catalyst_platinum_group"] = DependencyNode(
        "Pt/Pd/Rh catalysts", "process", 0.0, 0.85, 180, spof=True,
        depends_on=["mining_rare_metals"],
        notes="Reforming and hydrocracking depend on PGM catalysts")
    g["catalyst_zeolites"] = DependencyNode(
        "Zeolite cracking catalysts", "process", 0.0, 0.40, 90,
        notes="FCC unit core consumable")
    g["sulfur_removal_chems"] = DependencyNode(
        "Hydrotreating chemistry", "process", 0.0, 0.30, 60)

    # --- hydrogen system ---
    g["hydrogen_smr"] = DependencyNode(
        "Steam methane reformer H2", "process", 12.0, 0.0, 365, spof=True,
        depends_on=["natural_gas_supply", "specialty_steel"],
        notes="Heart of hydrocracking; energy-intensive")
    g["natural_gas_supply"] = DependencyNode(
        "Natural gas feed", "input", 0.0, 0.05, 14)

    # --- metallurgy and parts ---
    g["specialty_steel"] = DependencyNode(
        "High-pressure alloy steel", "infrastructure", 0.0, 0.65, 540, spof=True,
        notes="Cracking vessels, reactor walls, heat exchangers")
    g["machined_components"] = DependencyNode(
        "Pumps, valves, turbines", "infrastructure", 0.0, 0.55, 270,
        depends_on=["specialty_steel"])
    g["instrumentation"] = DependencyNode(
        "Sensors and control electronics", "infrastructure", 0.0, 0.80, 180,
        notes="Most chips and sensors imported")

    # --- utilities ---
    g["electric_grid"] = DependencyNode(
        "Grid power to refinery", "infrastructure", 0.0, 0.0, 7, spof=True,
        notes="Refineries draw 100s of MW continuous")
    g["cooling_water"] = DependencyNode(
        "Process and cooling water", "infrastructure", 0.5, 0.0, 30,
        notes="Climate-stressed in Gulf Coast region")

    # --- labor ---
    g["skilled_operators"] = DependencyNode(
        "Process operators / engineers", "labor", 0.0, 0.0, 1825, spof=True,
        notes="Pipeline degrading; aging workforce, declining trade entry")
    g["maintenance_crews"] = DependencyNode(
        "Turnaround and maintenance labor", "labor", 0.0, 0.0, 365)

    # --- output logistics ---
    g["pipeline_network"] = DependencyNode(
        "Product pipelines", "infrastructure", 0.2, 0.0, 180, spof=True)
    g["refined_output"] = DependencyNode(
        "Diesel / jet / gasoline", "output", 0.0, 0.0, 0,
        depends_on=[
            "crude_canadian_heavy", "crude_domestic_light_sweet",
            "catalyst_platinum_group", "catalyst_zeolites",
            "sulfur_removal_chems", "hydrogen_smr",
            "specialty_steel", "machined_components", "instrumentation",
            "electric_grid", "cooling_water",
            "skilled_operators", "maintenance_crews",
            "pipeline_network",
        ])

    # upstream of catalysts
    g["mining_rare_metals"] = DependencyNode(
        "PGM mining and refining", "input", 0.0, 0.95, 720, spof=True,
        notes="South Africa + Russia dominate global supply")

    return g


# -----------------------------------------------------------------------------
# CASCADE ENGINE
# -----------------------------------------------------------------------------

def cascade_disruption(
    graph: Dict[str, DependencyNode],
    disrupted: Dict[str, float],   # node_name -> fraction lost (0..1)
    target: str = "refined_output",
) -> Dict[str, float]:
    """
    Propagate disruption fractions through the graph.
    Returns throughput fraction remaining at each node.
    Conservative model: a node's throughput = min over its deps
    of (1 - disruption) * dep_throughput.
    """
    throughput: Dict[str, float] = {}

    def resolve(node_name: str) -> float:
        if node_name in throughput:
            return throughput[node_name]
        node = graph[node_name]
        local_loss = disrupted.get(node_name, 0.0)
        local_capacity = max(0.0, 1.0 - local_loss)

        if not node.depends_on:
            throughput[node_name] = local_capacity
            return local_capacity

        dep_caps = [resolve(d) for d in node.depends_on]
        # bottleneck logic -- weakest dependency dominates
        bottleneck = min(dep_caps) if dep_caps else 1.0
        result = min(local_capacity, bottleneck)
        throughput[node_name] = result
        return result

    resolve(target)
    return throughput


# -----------------------------------------------------------------------------
# BRITTLENESS METRICS
# -----------------------------------------------------------------------------

def cascade_impact(graph: Dict[str, DependencyNode], node_name: str) -> int:
    """
    Count of nodes whose throughput drops to zero when `node_name` is at
    100% loss. Measures physical reach of a single-node failure through
    the dependency graph -- the topological 'blast radius'.
    """
    t = cascade_disruption(graph, {node_name: 1.0})
    return sum(1 for v in t.values() if v <= 0.0)


def brittleness_score(graph: Dict[str, DependencyNode]) -> Dict[str, dict]:
    """
    Per-node brittleness with independent physical fragility axes.

    Components (each kept in interpretable units, summed for ranking):

      supply_risk        = import_fraction * log1p(replacement_time_days)
                           -- supply-chain / geopolitical fragility

      topological_risk   = log1p(replacement_time_days) if spof else 0
                           -- single-point-of-failure criticality
                              (no longer gated on import_fraction, so
                              domestic SPOFs register at full weight)

      thermodynamic_load = log1p(energy_cost_MJ_per_unit)
                           -- energy flux carried by the node; high-flux
                              nodes disrupt more state when they fail

      cascade_term       = log1p(cascade_impact)
                           -- measured blast radius: how many downstream
                              nodes drop to zero throughput if this node
                              fails completely

      total              = sum of all four

    Returns dict keyed by node name -> {component: value, ..., total: value},
    sorted by total descending.
    """
    scores: Dict[str, dict] = {}
    for name, n in graph.items():
        time_term = math.log1p(n.replacement_time_days)
        supply_risk = n.import_fraction * time_term
        topological_risk = time_term if n.spof else 0.0
        thermodynamic_load = math.log1p(n.energy_cost_MJ_per_unit)
        impact = cascade_impact(graph, name)
        cascade_term = math.log1p(impact)
        total = supply_risk + topological_risk + thermodynamic_load + cascade_term
        scores[name] = {
            "supply_risk": round(supply_risk, 3),
            "topological_risk": round(topological_risk, 3),
            "thermodynamic_load": round(thermodynamic_load, 3),
            "cascade_impact": impact,
            "cascade_term": round(cascade_term, 3),
            "total": round(total, 3),
        }
    return dict(sorted(scores.items(), key=lambda kv: kv[1]["total"], reverse=True))


def independence_hypothesis_test(graph: Dict[str, DependencyNode]) -> dict:
    """
    Falsifiable test of 'U.S. is energy independent.'
    Hypothesis fails if ANY non-trivial dependency in the
    output chain has import_fraction > 0 or spof = True.
    """
    failures = []

    def walk(name: str, seen=None):
        seen = seen if seen is not None else set()
        if name in seen:
            return
        seen.add(name)
        n = graph[name]
        if n.import_fraction > 0.10 or n.spof:
            failures.append({
                "node": name,
                "import_fraction": n.import_fraction,
                "spof": n.spof,
                "replacement_time_days": n.replacement_time_days,
                "notes": n.notes,
            })
        for d in n.depends_on:
            walk(d, seen)

    walk("refined_output")
    return {
        "hypothesis": "U.S. is energy independent",
        "falsified": len(failures) > 0,
        "failure_count": len(failures),
        "failures": failures,
    }


# -----------------------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    g = build_us_refinery_graph()

    print("\n=== BRITTLENESS RANKING ===")
    print(f"  {'total':>7}  {'supply':>7}  {'topo':>6}  {'therm':>6}  {'casc':>5}  node")
    for name, s in brittleness_score(g).items():
        print(f"  {s['total']:7.3f}  {s['supply_risk']:7.3f}  "
              f"{s['topological_risk']:6.3f}  {s['thermodynamic_load']:6.3f}  "
              f"{s['cascade_impact']:5d}  {name}")

    print("\n=== HYPOTHESIS TEST ===")
    result = independence_hypothesis_test(g)
    print(f"Hypothesis: {result['hypothesis']}")
    print(f"Falsified:  {result['falsified']}  ({result['failure_count']} failure points)")

    print("\n=== CASCADE: 50% PGM catalyst supply loss ===")
    t = cascade_disruption(g, {"mining_rare_metals": 0.5})
    print(f"  refined_output throughput remaining: {t['refined_output']*100:.1f}%")

    print("\n=== CASCADE: grid disruption 30% + skilled labor 20% ===")
    t = cascade_disruption(g, {"electric_grid": 0.3, "skilled_operators": 0.2})
    print(f"  refined_output throughput remaining: {t['refined_output']*100:.1f}%")
