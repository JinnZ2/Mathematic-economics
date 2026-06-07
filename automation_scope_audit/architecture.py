"""
architecture.py — 6-layer structural architecture for the audit framework

Every claim C000-C089 belongs to one of six layers (or to a cross-cutting
band that spans multiple layers). The layers form a closed coupling
cycle: a break in any layer propagates downstream until it returns to
the upstream layer it depends on. When every layer has at least one
firing claim, the cycle has *closed* — the deployment is structurally
untenable.

Layers and coupling constraints (provided by the user spec):

    1 technical      ── what breaks ─────────────────▶ 2 operational
    2 operational    ── how agents respond ──────────▶ 3 behavioral
    3 behavioral     ── what governance is needed ───▶ 4 institutional
    4 institutional  ── costs of enforcement ────────▶ 5 energy
    5 energy         ── true cost accounting ────────▶ 6 economic
    6 economic       ── ROI feasibility check ───────▶ 1 technical
                              CYCLE CLOSES

License: CC0-1.0
"""

from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Layer membership
# ---------------------------------------------------------------------------

# The six load-bearing layers + the cross-cutting band. Each layer
# carries the claim IDs it owns plus a short description of its role.
LAYERS: List[dict] = [
    {"layer": 1, "name": "technical",
     "claims": ["C001", "C003", "C004", "C005"],
     "description":
        "What breaks. Route geometry, infrastructure preconditions, "
        "lifecycle EROI, stranded-asset risk."},
    {"layer": 2, "name": "operational",
     "claims": ["C008", "C009", "C010",
                "C011", "C012", "C013",
                "C014", "C015", "C016", "C017"],
     "description":
        "How the operation responds when the technical layer fails. "
        "Condition monitoring, interface externalization, constraint "
        "validation, legal liability."},
    {"layer": 3, "name": "behavioral",
     "claims": ["C018", "C019",
                "C033", "C034", "C035", "C038",
                "C042"],
     "description":
        "How agents respond once the operational substrate is degraded. "
        "Cognitive monoculture, decision latency, skill transfer, "
        "threat-adaptive overhead."},
    {"layer": 4, "name": "institutional",
     "claims": ["C022", "C023", "C024",
                "C051", "C052",
                "C060", "C061", "C062", "C063", "C064",
                "C065", "C066", "C067", "C068", "C069",
                "C070", "C071", "C072",
                "C076", "C077", "C078"],
     "description":
        "What governance the behavioral layer demands. Institutional "
        "lock-in, regulatory capture, knowledge exclusion, substrate "
        "care + authority, credential inversion, adoption-curve "
        "thermodynamics, institutional cycle blindness, training-corpus "
        "dynamics (token-economics pruning, archival window, recursive "
        "homogenization)."},
    {"layer": 5, "name": "energy",
     "claims": ["C020", "C021", "C025", "C026",
                "C043", "C044", "C045", "C046", "C047", "C048"],
     "description":
        "Costs of enforcing the institutional layer. Energy / "
        "thermodynamic accounting, scaling, coercive governance, "
        "Earth-system coupling."},
    {"layer": 6, "name": "economic",
     "claims": ["C027", "C028", "C029", "C030",
                "C054", "C055", "C058",
                "C073", "C074",
                "C084", "C085", "C086", "C087", "C089"],
     "description":
        "True cost accounting that closes the cycle. Energy-grounded "
        "economic claims, unified capital, baseline corruption, deferred "
        "maintenance liability, lifecycle design accountability, "
        "trucking-ROI falsifiers (pilot-geometry extrapolation, static "
        "input-price assumption, insurance actuarial gap, secondary-market "
        "absence, payback vs technological obsolescence) — feeds back "
        "into layer 1 as the ROI feasibility check."},
]

CROSS_CUTTING: dict = {
    "layer": 0,
    "name": "cross_cutting",
    "claims": [
        "C000",                  # scope gate (pre-pipeline)
        "C002",                  # embedded labor (tech/operational hybrid)
        "C006", "C007",          # scope collapse (narrative cross-cut)
        "C031", "C032",          # engineering-grade (epistemic cross-cut)
        "C036", "C037",          # timescale adequacy (training cross-cut)
        "C039", "C040", "C041",  # substrate primacy (cross-cut: energy + behavior + governance)
        "C049", "C050", "C053",  # regulatory dynamics (cross-cut: institutional + operational)
        "C056", "C057", "C059",  # ROI/operational (cross-cut: economic + operational)
        "C075",                  # framework reflexivity (meta, pre-cycle)
        "C079",                  # 8-step cascade synthesis (meta-claim across layers)
        "C080", "C081", "C082", "C083",  # cross-domain empirical validation of the cascade
        "C088",                  # pilot survivorship bias (industry-level reporting pattern)
    ],
    "description":
        "Claims that span multiple layers or sit outside the cycle "
        "(scope gate, scope collapse, engineering-grade epistemics, "
        "training adequacy, substrate primacy, regulatory dynamics, "
        "ROI / operational coupling)."
}


# Forward edge of the coupling cycle (closes back to layer 1).
COUPLING_EDGES: List[dict] = [
    {"upstream": 1, "downstream": 2, "label": "what breaks"},
    {"upstream": 2, "downstream": 3, "label": "how agents respond"},
    {"upstream": 3, "downstream": 4, "label": "what governance is needed"},
    {"upstream": 4, "downstream": 5, "label": "costs of enforcement"},
    {"upstream": 5, "downstream": 6, "label": "true cost accounting"},
    {"upstream": 6, "downstream": 1, "label": "ROI feasibility check"},
]


# Polarity-inverted claims (same convention as run.py / correlation.py).
CONCERN_INVERTED = {"C001", "C004"}


# ---------------------------------------------------------------------------
# Coverage check
# ---------------------------------------------------------------------------

def coverage_check() -> dict:
    """Verify every claim C000..C089 is in exactly one layer (or cross-cutting)."""
    all_claim_ids = ["C000"] + [f"C{n:03d}" for n in range(1, 90)]
    in_layers = []
    for L in LAYERS:
        in_layers.extend(L["claims"])
    in_cross = list(CROSS_CUTTING["claims"])
    covered = set(in_layers) | set(in_cross)
    missing = sorted(set(all_claim_ids) - covered)
    layered = sorted(set(in_layers) & set(in_cross))    # in both = error
    return {
        "total_claims":    len(all_claim_ids),
        "layered_count":   len(in_layers),
        "cross_cutting_count": len(in_cross),
        "missing":         missing,
        "double_assigned": layered,
        "complete":        not missing and not layered,
    }


# ---------------------------------------------------------------------------
# Per-layer health computation
# ---------------------------------------------------------------------------

def _concern_registers(cid: str, verdict: dict) -> bool | None:
    """Same polarity logic as correlation.py / run.py."""
    if not verdict:
        return None
    tm = verdict.get("threshold_met")
    if tm is None:
        tm = verdict.get("scope_collapse_detected")
    if tm is None:
        return None
    return (not tm) if cid in CONCERN_INVERTED else bool(tm)


def layer_health(report: Dict[str, dict],
                 layer_def: dict) -> dict:
    """For one layer, compute how many claims register concern."""
    claims = layer_def["claims"]
    registered = []
    cleared = []
    unevaluated = []
    for cid in claims:
        cr = _concern_registers(cid, report.get(cid) or {})
        if cr is True:
            registered.append(cid)
        elif cr is False:
            cleared.append(cid)
        else:
            unevaluated.append(cid)
    total = len(claims)
    health = (len(cleared) / total) if total else 1.0
    if not registered:
        status = "GREEN"
    elif len(registered) == total:
        status = "RED"
    else:
        status = "YELLOW"
    return {
        "layer":        layer_def["layer"],
        "name":         layer_def["name"],
        "description":  layer_def["description"],
        "total":        total,
        "registered":   registered,
        "cleared":      cleared,
        "unevaluated":  unevaluated,
        "health":       health,
        "status":       status,
    }


def cycle_status(report: Dict[str, dict]) -> dict:
    """Compute per-layer status and overall cycle closure."""
    per_layer = [layer_health(report, L) for L in LAYERS]
    cross = layer_health(report, CROSS_CUTTING)

    # Cycle CLOSES (deployment structurally untenable) when every
    # load-bearing layer has at least one firing claim. The forward
    # edge of the cycle then has no break — concern propagates around.
    all_have_concern = all(len(L["registered"]) > 0 for L in per_layer)
    fully_failed_layers = [L["name"] for L in per_layer if L["status"] == "RED"]
    breaking_edges = []
    for e in COUPLING_EDGES:
        up = per_layer[e["upstream"] - 1]
        dn = per_layer[e["downstream"] - 1]
        # An edge is "active" when concern is propagating across it:
        # upstream has firing claims AND downstream has firing claims.
        if up["registered"] and dn["registered"]:
            breaking_edges.append({
                "upstream":    up["name"],
                "downstream":  dn["name"],
                "label":       e["label"],
                "upstream_registered_count": len(up["registered"]),
                "downstream_registered_count": len(dn["registered"]),
            })

    return {
        "by_layer":            per_layer,
        "cross_cutting":       cross,
        "fully_failed_layers": fully_failed_layers,
        "active_cycle_edges":  breaking_edges,
        "cycle_closed":        all_have_concern,
        "structural_verdict":  ("UNTENABLE_CYCLE_CLOSED"
                                if all_have_concern
                                else "PARTIAL_FAILURE"
                                if any(L["registered"] for L in per_layer)
                                else "ADMISSIBLE"),
    }


# ---------------------------------------------------------------------------
# Printable report
# ---------------------------------------------------------------------------

def print_layer_report(report: Dict[str, dict]) -> None:
    cs = cycle_status(report)
    print(f"\n=== layer architecture: {report.get('scenario', '')} ===")
    print(f"{'layer':<22}  {'status':<8}  registered / total")
    print("-" * 64)
    for L in cs["by_layer"]:
        registered_str = ",".join(L["registered"]) or "-"
        print(f"{str(L['layer']) + ' ' + L['name']:<22}  "
              f"{L['status']:<8}  "
              f"{len(L['registered'])} / {L['total']}    "
              f"[{registered_str[:48]}{'...' if len(registered_str) > 48 else ''}]")
    print(f"{'(cross-cutting)':<22}  {cs['cross_cutting']['status']:<8}  "
          f"{len(cs['cross_cutting']['registered'])} / {cs['cross_cutting']['total']}")
    print()
    print(f"cycle status:   {cs['structural_verdict']}")
    print(f"closed?         {cs['cycle_closed']}")
    if cs["fully_failed_layers"]:
        print(f"fully failed:   {', '.join(cs['fully_failed_layers'])}")
    if cs["active_cycle_edges"]:
        print(f"active edges:   {len(cs['active_cycle_edges'])} / 6 propagating concern")
        for e in cs["active_cycle_edges"]:
            print(f"  {e['upstream']:<14} -> {e['downstream']:<14} "
                  f"({e['label']})")
    print()


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from automation_scope_audit.examples import (
        kodiak_atlas_permian, dispersed_wellsite)

    print("Coverage check:", coverage_check())
    for runner in (kodiak_atlas_permian.run, dispersed_wellsite.run):
        print_layer_report(runner())
