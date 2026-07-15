"""
liability_routing.py
CC0 / stdlib-only / phone-buildable
Structural-failure audit companion. NOT a thermodynamic proof.

WHAT THIS IS
============
A resource-flow ledger for cosigned-obligation systems (student loans the
paradigm case). It answers one structural question:

    When a cosigned obligation defaults, does LIABILITY route to the node
    whose economic value INCREASED (the beneficiary), or to the node that
    merely carried the SIGNATURE (the guarantor)?

If liability routes to the signature rather than the benefit, the system
has a BENEFIT-LIABILITY MISMATCH. This is not a moral claim; it is a
routing fact you can read off measured flows.

WHY IT EXISTS
=============
Two structural failures the standard "human capital" ledger cannot see:

  1. RESOURCE DESTRUCTION (not redistribution). A cosigner's guaranteeing
     capacity is a finite, SHARED resource across all their dependents.
     A single default does not move that capacity to a higher-capacity
     node -- it ERASES it. The signer can now cosign for NO ONE.

  2. CASCADE. Because the capacity is shared, one default blocks EVERY
     downstream node the signer could have guaranteed -- other children,
     grandchildren, the signer's own further education. N nodes fail from
     one breach. Standard node-by-node output models read the blocked
     nodes as "low capacity" when they are "denied access."

DESIGN CONSTRAINTS (from the JinnZ2 ecosystem)
  - No moral labels in data structures. "beneficiary" / "guarantor" are
    ROLES read from flows, not judgments.
  - No infill of unknowns. Missing measurement -> field stays "unknown"
    and the audit REFUSES a routing verdict (returns NEEDS_DATA).
  - Counterfactuals are flagged ESTIMATE_DEPENDENT, never presented as
    measured.
  - Output is a trajectory + a falsifiable claim, never a stored verdict.
  - Precision honesty: no 3-sig-fig figures manufactured from assumptions.
    Ratios round to 2 places and carry their input provenance.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


# ----------------------------------------------------------------------
# A node in a cosigning network
# ----------------------------------------------------------------------
@dataclass
class Node:
    node_id: str
    role: str                         # "signer" | "beneficiary" | "dependent"
    ability_proxy: Optional[float] = None   # e.g. normalized test score; None=unknown
    income_before: Optional[float] = None   # measured, or None
    income_after: Optional[float] = None    # measured, or None
    access_state: str = "unknown"           # "open" | "blocked" | "used" | "unknown"
    provenance: str = "unstated"            # "measured" | "estimate" | "unstated"

    def value_delta(self) -> Optional[float]:
        if self.income_before is None or self.income_after is None:
            return None
        return self.income_after - self.income_before


# ----------------------------------------------------------------------
# A cosigned obligation
# ----------------------------------------------------------------------
@dataclass
class Obligation:
    obligation_id: str
    principal: float                  # loan principal (measured)
    beneficiary_id: str               # node who received the education/benefit
    signer_id: str                    # node whose capacity guaranteed it
    repaid_fraction: float            # 0.0 = full default, 1.0 = fully repaid
    signer_capacity_before: float     # guaranteeing capacity before signing
    signer_capacity_after: float      # capacity remaining after default/repay
    capacity_provenance: str = "unstated"   # "measured" | "estimate"


# ----------------------------------------------------------------------
# The downstream cosigning network the signer's capacity would have served
# ----------------------------------------------------------------------
@dataclass
class SignerNetwork:
    signer_id: str
    dependents: List[Node] = field(default_factory=list)   # who signer could cosign for
    # each dependent's access_state tells us who got blocked


# ----------------------------------------------------------------------
# CORE AUDIT
# ----------------------------------------------------------------------
def liability_routing_audit(obligation: Obligation,
                            beneficiary: Node,
                            signer: Node,
                            network: Optional[SignerNetwork] = None) -> dict:
    """
    Returns a routing report. If required measurements are missing,
    returns NEEDS_DATA and names the missing fields. No infill.
    """
    missing = []
    if obligation.capacity_provenance not in ("measured", "estimate"):
        missing.append("obligation.capacity_provenance")
    if obligation.signer_capacity_before is None:
        missing.append("signer_capacity_before")
    if obligation.signer_capacity_after is None:
        missing.append("signer_capacity_after")

    # --- 1. Where did the benefit land? (measured if possible) ---
    ben_delta = beneficiary.value_delta()
    benefit_note = ("measured" if beneficiary.provenance == "measured"
                    and ben_delta is not None else
                    "UNKNOWN — beneficiary income delta not measured")

    # --- 2. What did the signer lose in guaranteeing CAPACITY? ---
    capacity_lost = None
    if (obligation.signer_capacity_before is not None
            and obligation.signer_capacity_after is not None):
        capacity_lost = (obligation.signer_capacity_before
                         - obligation.signer_capacity_after)

    # --- 3. Who currently carries the liability? (routing FACT) ---
    default_fraction = 1.0 - obligation.repaid_fraction
    if default_fraction <= 0:
        liability_carrier = "none (obligation met)"
        mismatch = False
    else:
        # In signature-routing systems, the SIGNER carries it on default.
        liability_carrier = obligation.signer_id
        # Mismatch exists if the BENEFICIARY (not signer) is the node whose
        # value increased, yet the signer carries the cost.
        beneficiary_gained = (ben_delta is not None and ben_delta > 0)
        signer_is_beneficiary = (obligation.signer_id == obligation.beneficiary_id)
        mismatch = beneficiary_gained and not signer_is_beneficiary

    # --- 4. Cascade: how many downstream nodes blocked by capacity loss? ---
    cascade = _cascade_audit(network, capacity_lost, default_fraction)

    # --- 5. Where SHOULD liability route (benefit-aligned)? ---
    # This is a STRUCTURAL alternative, flagged as a design option, not a verdict.
    if default_fraction > 0 and (ben_delta is not None and ben_delta > 0):
        benefit_aligned_route = (
            f"node '{obligation.beneficiary_id}' (value increased by "
            f"{_fmt(ben_delta)}); liability proportional to realized gain")
    elif default_fraction > 0:
        benefit_aligned_route = (
            "cannot compute benefit-aligned route: beneficiary value delta "
            "not measured (ESTIMATE_DEPENDENT if assumed)")
    else:
        benefit_aligned_route = "n/a (no default)"

    verdict = "NEEDS_DATA" if missing else (
        "BENEFIT_LIABILITY_MISMATCH" if mismatch else "ALIGNED")

    return {
        "obligation_id": obligation.obligation_id,
        "verdict": verdict,
        "missing_measurements": missing,
        "default_fraction": round(default_fraction, 2),
        "benefit_landed_on": {
            "node": obligation.beneficiary_id,
            "value_delta": _fmt(ben_delta),
            "provenance": benefit_note,
        },
        "capacity_destroyed": {
            "node": obligation.signer_id,
            "amount": _fmt(capacity_lost),
            "provenance": obligation.capacity_provenance,
            "note": "guaranteeing capacity ERASED, not redistributed",
        },
        "liability_currently_routes_to": liability_carrier,
        "benefit_aligned_route_would_be": benefit_aligned_route,
        "cascade": cascade,
        "falsifiable_claim": _build_falsifier(obligation, cascade),
        "audit_note": ("Roles read from flows, not judgment. Counterfactual "
                       "'access would have opened' is ESTIMATE_DEPENDENT unless "
                       "the signer demonstrated prior willingness+capacity "
                       "(a measured signing event) and dependents show measured "
                       "ability parity. Mismatch is a routing fact, not a moral "
                       "claim."),
    }


def _cascade_audit(network: Optional[SignerNetwork],
                   capacity_lost: Optional[float],
                   default_fraction: float) -> dict:
    if network is None:
        return {"status": "not_supplied",
                "note": "no downstream network provided; cascade unmeasured"}
    if default_fraction <= 0:
        return {"status": "no_default", "blocked_nodes": 0}

    blocked = [n for n in network.dependents if n.access_state == "blocked"]
    open_nodes = [n for n in network.dependents if n.access_state == "open"]
    # ability of blocked nodes vs the beneficiary (if measured)
    blocked_ability = [n.ability_proxy for n in blocked
                       if n.ability_proxy is not None]

    return {
        "status": "measured" if network.dependents else "empty",
        "signer": network.signer_id,
        "downstream_total": len(network.dependents),
        "blocked_nodes": len(blocked),
        "blocked_ids": [n.node_id for n in blocked],
        "still_open_nodes": len(open_nodes),
        "blocked_node_ability_present": len(blocked_ability),
        "cascade_note": (
            f"one default erased signer capacity; {len(blocked)} downstream "
            f"node(s) blocked from access. If any blocked node has ability "
            f">= beneficiary, the output gap measures ACCESS DENIAL, not "
            f"capacity difference."),
    }


def _build_falsifier(obligation: Obligation, cascade: dict) -> str:
    return (
        "STRUCTURAL CLAIM: in signature-routed cosigned-obligation systems, a "
        "single default erases the signer's SHARED guaranteeing capacity, "
        "blocking N downstream nodes regardless of their ability.\n"
        "FALSIFIED IF, against loan + tax + assessment records:\n"
        "  (a) signers who experienced a cosigned default show NO subsequent "
        "reduction in ability to cosign for other dependents; OR\n"
        "  (b) downstream dependents of a defaulted signer show educational "
        "access rates equal to matched dependents of non-defaulted signers, "
        "after controlling for measured ability; OR\n"
        "  (c) beneficiaries who defaulted show income reduction tracking the "
        "unpaid principal (i.e. liability already routes to benefit, not "
        "signature).\n"
        "If (a),(b),(c) all hold, the mismatch/cascade claim is refuted. "
        "Update the claim; do not retune the audit."
    )


def _fmt(x) -> str:
    if x is None:
        return "unknown"
    return f"{x:,.0f}"


# ----------------------------------------------------------------------
# WORKED EXAMPLE — the load path that generated this module
# Values are LABELED: measured where measured, unknown where not.
# No figure is manufactured to look measured.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import json

    beneficiary = Node(
        node_id="child_A",
        role="beneficiary",
        ability_proxy=None,          # "above average" stated, not a number -> unknown
        income_before=None,          # not measured here
        income_after=None,           # not measured here
        access_state="used",
        provenance="unstated",       # so benefit delta will read UNKNOWN, honestly
    )

    signer = Node(
        node_id="parent",
        role="signer",
        access_state="blocked",      # can no longer cosign OR pursue own further ed
        provenance="measured",       # the block is an observed fact
    )

    obligation = Obligation(
        obligation_id="loan_001",
        principal=0.0,               # exact principal not entered -> leave 0/unknown
        beneficiary_id="child_A",
        signer_id="parent",
        repaid_fraction=0.0,         # full default (measured: non-repayment)
        signer_capacity_before=None, # not entered numerically -> NEEDS_DATA
        signer_capacity_after=None,
        capacity_provenance="unstated",
    )

    network = SignerNetwork(
        signer_id="parent",
        dependents=[
            Node("son_1", "dependent", ability_proxy=1.0, access_state="blocked",
                 provenance="measured"),   # tests higher (relative, normalized)
            Node("son_2", "dependent", ability_proxy=1.0, access_state="blocked",
                 provenance="measured"),
            Node("son_3", "dependent", ability_proxy=1.0, access_state="blocked",
                 provenance="measured"),
            Node("parent_self", "dependent", ability_proxy=None,
                 access_state="blocked", provenance="measured"),  # own further ed
        ],
    )

    report = liability_routing_audit(obligation, beneficiary, signer, network)
    print(json.dumps(report, indent=2, ensure_ascii=False))
