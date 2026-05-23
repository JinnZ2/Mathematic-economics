"""
correlation.py — cross-claim cluster detector

Given a report dict from `run.py` (the C000..C032 verdict map for one
scenario), surface clusters of claims that triggered together. Curated
cluster signatures:

  infrastructure_inadequacy_cluster: C001 + C003 + C014
    fixed geometry absent, infrastructure capex > vehicle, refusal
    authority not transferable -> deployment is geometrically and
    contractually unbacked.

  institutional_blindness_cluster: C022 + C023 + C027 + C028 + C031
    lock-in + knowledge exclusion + ungrounded economic model +
    institutional blindness + engineering-grade falsifiability gap.

  earth_system_fragility_cluster: C025 + C026 + C019
    Earth-system precondition fragility, economic-model double-bind,
    monoculture recovery cost > apparent savings.

  scope_collapse_cluster: C006 + C007 + C027
    marketing scope collapse + wage suppression + ungrounded economic
    framing.

  labor_externalization_cluster: C002 + C008 + C011 + C013
    site labor not automated + monitoring labor unpriced + middleware
    cost > driver-mediated + distributed labor cost >= half a driver.

  liability_void_cluster: C014 + C015 + C016 + C017
    refusal authority absent, liability stack unresolved, override
    hierarchy gaps, framework + litigation premium.

  thermodynamic_inefficiency_cluster: C020 + C021 + C030
    honest eROI < 1.5, above scaling optimum, unified capital deficit.

  collapse_imminent_cluster: C022 + C024 + C025 + C032
    institutional lock-in + collapse cycle + Earth-system fragility +
    AI on unstable models — the structural prefix every historical
    cascade has shown.

License: CC0-1.0
"""

from typing import Dict, List


CLUSTERS: List[dict] = [
    {"name": "infrastructure_inadequacy_cluster",
     "claims": ["C001", "C003", "C014"],
     "polarity": "all_register",
     "explanation":
        "fixed geometry absent, infrastructure capex > vehicle, refusal "
        "authority not transferable — deployment is geometrically and "
        "contractually unbacked"},
    {"name": "institutional_blindness_cluster",
     "claims": ["C022", "C023", "C027", "C028", "C031"],
     "polarity": "all_register",
     "explanation":
        "lock-in + knowledge exclusion + ungrounded economic model + "
        "institutional blindness + engineering-grade falsifiability gap"},
    {"name": "earth_system_fragility_cluster",
     "claims": ["C019", "C025", "C026"],
     "polarity": "all_register",
     "explanation":
        "Earth-system precondition fragility + economic-model double-bind "
        "+ monoculture recovery cost > apparent savings"},
    {"name": "scope_collapse_cluster",
     "claims": ["C006", "C007", "C027"],
     "polarity": "all_register",
     "explanation":
        "marketing scope collapse + wage suppression + ungrounded "
        "economic framing"},
    {"name": "labor_externalization_cluster",
     "claims": ["C002", "C008", "C011", "C013"],
     "polarity": "all_register",
     "explanation":
        "site labor not automated + monitoring unpriced + middleware > "
        "driver-mediated + distributed labor >= half a driver"},
    {"name": "liability_void_cluster",
     "claims": ["C014", "C015", "C016", "C017"],
     "polarity": "all_register",
     "explanation":
        "refusal authority absent + liability stack unresolved + override "
        "hierarchy gaps + framework + litigation premium"},
    {"name": "thermodynamic_inefficiency_cluster",
     "claims": ["C020", "C021", "C030"],
     "polarity": "all_register",
     "explanation":
        "honest eROI < 1.5 + above scaling optimum + unified capital deficit"},
    {"name": "collapse_imminent_cluster",
     "claims": ["C022", "C024", "C025", "C032"],
     "polarity": "all_register",
     "explanation":
        "institutional lock-in + collapse cycle + Earth-system fragility "
        "+ AI on unstable models — historical prefix to every cascade"},
    {"name": "substrate_primacy_collapse_cluster",
     "claims": ["C033", "C034", "C035", "C040", "C041"],
     "polarity": "all_register",
     "explanation":
        "sensing latency + embodied knowledge loss + distributed-authority "
        "latency + degraded-mode capacity gap + generational knowledge "
        "loss — the deployment cannot run without the infrastructure it "
        "depends on, and the infrastructure is not preserved"},
    {"name": "knowledge_transfer_failure_cluster",
     "claims": ["C018", "C034", "C038", "C041"],
     "polarity": "all_register",
     "explanation":
        "cognitive monoculture + embodied knowledge loss + apprenticeship "
        "shortfall + generational non-transferability — the deployment "
        "is one generation away from being unrecoverable"},
    {"name": "coercive_governance_unsustainability_cluster",
     "claims": ["C043", "C044", "C046", "C047"],
     "polarity": "all_register",
     "explanation":
        "enforcement > reciprocal at scale + perverse corruption "
        "incentive + unequal enforcement trajectory + defensive spending "
        "as GDP misaccounting — the governance substrate the deployment "
        "depends on is itself in thermodynamic deficit"},
    {"name": "substrate_regulatory_asymmetry_cluster",
     "claims": ["C031", "C032", "C048"],
     "polarity": "all_register",
     "explanation":
        "engineering-grade falsifiability gap + AI on unstable models + "
        "human-vs-digital regulatory asymmetry — rules apply to one "
        "substrate but not the other across the same operational envelope"},
    {"name": "lcd_regulatory_degradation_cluster",
     "claims": ["C049", "C050", "C051", "C052", "C053"],
     "polarity": "all_register",
     "explanation":
        "LCD selection pressure + capability-diversity collapse + "
        "regulatory capture + externalized-regulation atrophy + 4-phase "
        "degradation cycle — the same pattern that broke trucking is now "
        "operating on the automation deployment"},
    {"name": "roi_baseline_integrity_cluster",
     "claims": ["C054", "C055", "C056", "C057", "C058"],
     "polarity": "all_register",
     "explanation":
        "degraded baseline + asymmetric AI degradation measurement + "
        "POR misrepresentation + redistributed coordination + deferred "
        "maintenance liability — the ROI claim cannot be evaluated because "
        "the comparison is structurally invalid"},
]


# Per-claim threshold polarity, mirroring run.CONCERN_INVERTED. Concerns
# for C001 and C004 are inverted: threshold_met means deployment is OK.
CONCERN_INVERTED = {"C001", "C004"}


def _concern_registers(cid: str, verdict: dict) -> bool | None:
    if not verdict:
        return None
    tm = verdict.get("threshold_met")
    if tm is None:
        tm = verdict.get("scope_collapse_detected")
    if tm is None:
        return None
    return (not tm) if cid in CONCERN_INVERTED else bool(tm)


def detect_clusters(report: Dict[str, dict],
                    clusters: List[dict] | None = None,
                    ) -> dict:
    """Walk every cluster signature; flag the ones that fully register.

    Args:
        report: `{C000: verdict_dict, C001: verdict_dict, ...}`
        clusters: signatures (default: CLUSTERS).

    Returns:
        `{cluster_name: {triggered, claims, registered, missing, explanation}}`
        plus a top-level `triggered` list for fast scan.
    """
    out: Dict[str, dict] = {}
    triggered_names: List[str] = []
    for c in clusters or CLUSTERS:
        registered = []
        missing = []
        for cid in c["claims"]:
            v = report.get(cid) or {}
            cr = _concern_registers(cid, v)
            if cr is True:
                registered.append(cid)
            else:
                missing.append(cid)
        if c["polarity"] == "all_register":
            fired = (len(missing) == 0)
        else:
            fired = bool(registered)
        out[c["name"]] = {
            "triggered":   fired,
            "claims":      c["claims"],
            "registered":  registered,
            "missing":     missing,
            "explanation": c["explanation"],
        }
        if fired:
            triggered_names.append(c["name"])
    return {
        "scenario":           report.get("scenario", ""),
        "triggered_clusters": triggered_names,
        "by_cluster":         out,
    }


def print_clusters(cluster_report: dict) -> None:
    print(f"\n=== clusters: {cluster_report['scenario']} ===")
    print(f"{'cluster':<42}  fires")
    print("-" * 60)
    for name, info in cluster_report["by_cluster"].items():
        flag = "FIRES" if info["triggered"] else "-"
        print(f"{name:<42}  {flag}")
    print()
    fired = cluster_report["triggered_clusters"]
    if fired:
        print("triggered:")
        for name in fired:
            info = cluster_report["by_cluster"][name]
            print(f"  {name} ({', '.join(info['claims'])})")
            print(f"    {info['explanation']}")


if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from automation_scope_audit.examples import (
        kodiak_atlas_permian, dispersed_wellsite)
    for runner in (kodiak_atlas_permian.run, dispersed_wellsite.run):
        report = runner()
        print_clusters(detect_clusters(report))
