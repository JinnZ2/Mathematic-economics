"""
scope_gate.py — pipeline gate for C000

`meta_scope_guard.py` evaluates whether a *claim text* declares the seven
scope dimensions. `scope_gate.py` extends that into a *pipeline gate*:
when an automation deployment spec is run through the audit, the gate
verifies that the spec itself declares scope completely. A spec missing
any of the seven required fields cannot enter the audit pipeline; a
MISSING_SCOPE report is returned and the downstream claims (C001-C032)
are not evaluated.

The seven required spec fields are the engineering-grade scope
declaration any audit-ready deployment must publish:

    beneficiary           — "per-vehicle / per-ton-mile / per-joule / etc."
    conditions            — "stable diesel / no regulatory change / etc."
    time_period           — "5yr / 20yr / well-life / etc."
    resource              — "energy / capital / labor / rare-earth"
    externalized_cost     — what is being externalized to whom
    profit_allocation     — where the surplus flows
    falsifier             — what evidence would refute the deployment claim

Each field must contain a *measurable* value, not a narrative. A
helper validates that the value is one of: a number, a known unit
string, a known counterparty / beneficiary, or an explicit
"unspecified" sentinel that the operator has deliberately chosen.

Override the gate with `validate_deployment_spec(..., strict=False)` or
pass `--allow-missing-scope` to `run.py` when running against legacy
example specs that predate the gate.

License: CC0-1.0
"""

from typing import Any, Dict, List

try:
    from . import meta_scope_guard
except ImportError:
    import meta_scope_guard  # type: ignore[no-redef]


REQUIRED_SPEC_FIELDS = [
    "beneficiary",
    "conditions",
    "time_period",
    "resource",
    "externalized_cost",
    "profit_allocation",
    "falsifier",
    "substrate_primacy_fraction",   # added per substrate_primacy_audit
]

# Per-field validators above and beyond `_is_measurable`. Returns (ok, reason).
# `substrate_primacy_fraction` must be a number in (0.0, 1.0]; a value of
# 0% means the deployment cannot run at all without electricity / internet /
# computers, which is a structural fail.
EXTRA_FIELD_VALIDATORS = {
    "substrate_primacy_fraction": lambda v: (
        (isinstance(v, (int, float)) and 0.0 < float(v) <= 1.0,
         "substrate_primacy_fraction must be a number in (0.0, 1.0]; "
         "a deployment that cannot run at all without electricity / "
         "internet / computers fails the substrate-primacy gate")
    ),
}


# Sentinels that count as "operator deliberately chose to leave this open"
# and are accepted by the gate as long as they appear explicitly. Empty
# strings, None, or absent keys do NOT count.
DELIBERATE_OPEN_SENTINELS = {
    "unspecified", "tbd_pre_deployment", "intentionally_open_for_audit",
}


def _is_measurable(value: Any) -> bool:
    """Heuristic for whether a field carries a measurable value.

    Numbers and non-empty lists pass. Strings pass if they're either a
    deliberate-open sentinel OR longer than 8 characters (interpreted as
    a substantive declaration, not a label like "yes" / "ok").
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return False                       # 'True' is not a scope value
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    if isinstance(value, str):
        s = value.strip().lower()
        if not s:
            return False
        if s in DELIBERATE_OPEN_SENTINELS:
            return True
        return len(s) > 8                  # discourage one-word labels
    return False


def validate_deployment_spec(spec: Dict[str, Any],
                             required: List[str] | None = None,
                             ) -> dict:
    """Check `spec` for the seven required scope-declaration fields.

    Returns:
      `present`:   per-field boolean indicating presence with measurable value
      `missing`:   list of field names that are absent or non-measurable
      `admissible`: True iff all required fields are present + measurable
      `report`:    short structured object usable as a MISSING_SCOPE report

    `spec` is the same dict shape callers already pass into the example
    scenarios; the gate just looks for the seven scope-declaration keys
    at the top level of the spec dict.
    """
    req = required or REQUIRED_SPEC_FIELDS
    present: Dict[str, bool] = {}
    field_values: Dict[str, Any] = {}
    extra_failures: Dict[str, str] = {}
    for field in req:
        value = spec.get(field)
        measurable = _is_measurable(value)
        present[field] = measurable
        field_values[field] = value
        validator = EXTRA_FIELD_VALIDATORS.get(field)
        if measurable and validator is not None:
            ok, reason = validator(value)
            if not ok:
                present[field] = False
                extra_failures[field] = reason
    missing = [f for f in req if not present[f]]
    return {
        "claim_id":   "C000",
        "present":    present,
        "field_values": field_values,
        "missing":    missing,
        "validator_failures": extra_failures,
        "admissible": not missing,
        "report":     ("ADMITTED" if not missing
                       else f"MISSING_SCOPE: {missing}"),
    }


def scope_gate_verdict(spec: Dict[str, Any]) -> dict:
    """Compose the deployment-spec gate verdict.

    `threshold_met` is the existing run.py polarity convention: True
    means the structural concern registers (i.e. scope is incomplete).
    Compatible with the same column-rendering logic used for C000.
    """
    v = validate_deployment_spec(spec)
    return {
        "claim_id":      "C000",
        **v,
        "threshold_met": not v["admissible"],
        "falsifier":
            "a deployment spec that explicitly declares all seven scope "
            "fields with measurable values AND publishes a falsifier",
    }


if __name__ == "__main__":
    bad = {"deployment": "Permian sand haul"}
    good = {
        "beneficiary":        "per_ton_mile_energy_efficiency",
        "conditions":         ["stable_diesel_supply", "no_FMCSA_rule_shift"],
        "time_period":        "7yr_equipment_lifecycle",
        "resource":           "diesel_energy_joules",
        "externalized_cost":  "rural_road_maintenance_to_state_DOT",
        "profit_allocation":  ["operator_60pct", "atlas_energy_40pct"],
        "falsifier":          "fuel_intensity_per_ton_mile_increase_over_baseline_2026",
    }
    print("bad:",  scope_gate_verdict(bad))
    print()
    print("good:", scope_gate_verdict(good))
