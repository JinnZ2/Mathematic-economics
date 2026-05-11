"""
Claude_Code_Coordinator.py

Coordination layer across the three substrate-aware-accounting
repositories:

- earth-systems-physics
- mathematics-economy
- infrastructure

Routes queries to relevant modules across repos, loads unified
claims, runs cross-repo audits, returns substrate-aware verdicts.

Designed to be importable by AI systems or human users. Does not
require external dependencies. Standard library only.

CC0.
"""

import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional


# -----------------------------------------------------------------
# REPOSITORY DESCRIPTORS
# -----------------------------------------------------------------

@dataclass
class Repository:
    name: str
    url: str
    layer: str
    description: str
    keywords: List[str]
    modules: List[str]


REPOS = [

    Repository(
        name="earth-systems-physics",
        url="https://github.com/JinnZ2/earth-systems-physics",
        layer="thermodynamic base",
        description=(
            "Coupled differential equation framework mapping Earth "
            "physics as constraint layers. Electromagnetic base "
            "layer -> magnetosphere -> ionosphere -> atmosphere "
            "-> hydrosphere -> lithosphere -> biosphere."
        ),
        keywords=[
            "physics", "thermodynamics", "earth systems",
            "constraint cascade", "regime", "holocene",
            "differential equations", "climate", "magnetic field",
            "atmosphere", "hydrology", "biosphere",
        ],
        modules=[
            "constraint_cascade",
            "regime_audit",
            "assumption_validator",
            "coupled_differential_framework",
        ],
    ),

    Repository(
        name="mathematics-economy",
        url="https://github.com/JinnZ2/mathematics-economy",
        layer="capital and labor",
        description=(
            "Labor thermodynamics, banking energy cost, value "
            "convergence audits, substrate damage accounting, "
            "metrology audit of monetary units against physical "
            "quantities."
        ),
        keywords=[
            "banking", "capital", "debt", "interest", "labor",
            "workforce", "metrology", "monetary", "value",
            "convergence", "substrate damage", "epigenetic",
            "stress", "compounding", "growth",
        ],
        modules=[
            "labor_thermodynamics",
            "substrate_audit",
            "value_convergence_audit",
            "banking_thermodynamic_audit",
            "substrate_damage_audit",
        ],
    ),

    Repository(
        name="infrastructure",
        url="https://github.com/JinnZ2/infrastructure",
        layer="operational systems",
        description=(
            "Oil extraction audits, refinery cascade analysis, "
            "shale well decline reality, EROI real-time "
            "recalculation, gravity battery resilience design, "
            "full-cost system comparison."
        ),
        keywords=[
            "oil", "extraction", "eroi", "refinery", "shale",
            "well", "decline", "cascade", "supply chain",
            "gravity battery", "resilience", "energy",
            "production", "pipeline", "tariff",
        ],
        modules=[
            "oil_extraction_thermodynamic_cascade_audit",
            "refinery_stress_cascade_module",
            "shale_well_thermodynamic_reality_module",
            "eroi_real_time_audit",
            "gravity_battery_metamaterial_sim",
            "full_cost_energy_comparison",
        ],
    ),

]


# -----------------------------------------------------------------
# QUERY ROUTING
# -----------------------------------------------------------------

def find_relevant_modules(query: str) -> List[Dict[str, str]]:
    """
    Match query keywords against repo and module keywords.
    Returns list of relevant modules across all repos.
    """
    query_lower = query.lower()
    relevant = []

    for repo in REPOS:
        matched_keywords = [
            k for k in repo.keywords if k in query_lower
        ]
        if matched_keywords:
            for module in repo.modules:
                relevant.append({
                    "repo": repo.name,
                    "module": module,
                    "layer": repo.layer,
                    "matched_keywords": matched_keywords,
                    "url": (
                        f"{repo.url}/blob/main/{module}.py"
                    ),
                })

    return relevant


# -----------------------------------------------------------------
# UNIFIED CLAIMS LOADING
# -----------------------------------------------------------------

def load_unified_claims(
    path: str = "CLAIMS_UNIFIED.json",
) -> Dict:
    """
    Load the unified claims file. Returns dict with claims list
    and metadata.
    """
    if not os.path.exists(path):
        return {
            "error": (
                f"CLAIMS_UNIFIED.json not found at {path}. "
                "Coordinator must be run from substrate-aware-"
                "accounting repo root, or path must be supplied."
            )
        }
    with open(path) as f:
        return json.load(f)


def find_relevant_claims(
    query: str,
    claims_data: Dict,
) -> List[Dict]:
    """
    Match claims against query keywords.
    """
    if "error" in claims_data:
        return []

    query_lower = query.lower()
    relevant = []

    for claim in claims_data.get("claims", []):
        # Match on statement text, module name, or repo
        haystack = (
            claim.get("statement", "")
            + " " + claim.get("module", "")
            + " " + claim.get("repo", "")
        ).lower()

        if any(word in haystack for word in query_lower.split()):
            relevant.append(claim)

    return relevant


# -----------------------------------------------------------------
# CROSS-REPO AUDIT WORKFLOW
# -----------------------------------------------------------------

@dataclass
class AuditPlan:
    query: str
    relevant_modules: List[Dict[str, str]]
    relevant_claims: List[Dict]
    recommended_workflow: List[str]


def plan_audit(
    query: str,
    claims_path: str = "CLAIMS_UNIFIED.json",
) -> AuditPlan:
    """
    Given a query, plan which modules to consult, which claims
    apply, and in what order.
    """
    modules = find_relevant_modules(query)
    claims_data = load_unified_claims(claims_path)
    claims = find_relevant_claims(query, claims_data)

    # Order workflow by repo layer: physics -> economy -> infra.
    layer_order = {
        "thermodynamic base": 0,
        "capital and labor": 1,
        "operational systems": 2,
    }
    modules_sorted = sorted(
        modules,
        key=lambda m: layer_order.get(m["layer"], 99),
    )

    workflow = [
        f"{m['repo']}/{m['module']}" for m in modules_sorted
    ]

    return AuditPlan(
        query=query,
        relevant_modules=modules_sorted,
        relevant_claims=claims,
        recommended_workflow=workflow,
    )


# -----------------------------------------------------------------
# REPO INTROSPECTION
# -----------------------------------------------------------------

def list_all_repos() -> List[Dict[str, str]]:
    return [
        {
            "name": r.name,
            "url": r.url,
            "layer": r.layer,
            "description": r.description,
            "module_count": len(r.modules),
        }
        for r in REPOS
    ]


def get_repo(name: str) -> Optional[Repository]:
    for r in REPOS:
        if r.name == name:
            return r
    return None


# -----------------------------------------------------------------
# DEMO
# -----------------------------------------------------------------

def demo():
    print("=" * 74)
    print("CLAUDE CODE COORDINATOR  (substrate-aware-accounting)")
    print("=" * 74)
    print()
    print("Registered repositories:")
    for r in REPOS:
        print(f"  - {r.name} ({r.layer})")
        print(f"    {r.url}")
        print(f"    Modules: {len(r.modules)}")
    print()

    sample_queries = [
        "Is current US oil EROI sustainable through 2030?",
        "What happens to global banking if net energy contracts?",
        "How resilient is a small community to industrial collapse?",
        "Does refinery cascade affect delivered fuel EROI?",
        "How does substrate damage compound across generations?",
    ]

    for q in sample_queries:
        plan = plan_audit(q)
        print("-" * 74)
        print(f"QUERY: {q}")
        print(f"  Relevant modules: {len(plan.relevant_modules)}")
        print(f"  Relevant claims:  {len(plan.relevant_claims)}")
        print(f"  Workflow order:")
        for step in plan.recommended_workflow:
            print(f"    -> {step}")
        print()


# -----------------------------------------------------------------
# README-COMPATIBLE ALIASES
# -----------------------------------------------------------------
# README.md quick-start imports `load_repos` and `run_unified_audit`.
# These are thin wrappers over `list_all_repos` and `plan_audit` so
# the documented entry points work without renaming.

load_repos = list_all_repos


def run_unified_audit(
    relevant_modules: List[Dict[str, str]],
    repos: List[Dict[str, str]],
    claims_path: str = "CLAIMS_UNIFIED.json",
) -> Dict:
    """
    README-compatible: given a relevant-modules list (output of
    `find_relevant_modules`) and a repos descriptor list (output of
    `load_repos`), assemble a unified verdict dict with the
    layer-ordered workflow and the claims that apply to those
    modules.
    """
    layer_order = {
        "thermodynamic base": 0,
        "capital and labor": 1,
        "operational systems": 2,
    }
    modules_sorted = sorted(
        relevant_modules,
        key=lambda m: layer_order.get(m.get("layer", ""), 99),
    )
    workflow = [
        f"{m['repo']}/{m['module']}" for m in modules_sorted
    ]
    claims_data = load_unified_claims(claims_path)
    module_names = {m["module"] for m in modules_sorted}
    claims = [
        c for c in claims_data.get("claims", [])
        if c.get("module") in module_names
    ]
    return {
        "relevant_modules": modules_sorted,
        "workflow": workflow,
        "matching_claims": claims,
        "repos": repos,
    }


if __name__ == "__main__":
    demo()
