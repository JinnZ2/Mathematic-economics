"""
timescale_phenomenon_match.py — Phase 8 Task 8.4

For long-horizon claims (institutional lock-in C022, coercive scale
C043, enforcement equality C046, defensive spending C047), the audit
must declare that its *verification horizon* is at least as long as
the *phenomenon's natural timescale*. An audit run at a single point
in time cannot empirically resolve a century-scale institutional
collapse cycle; the most the framework can do is *flag* that the
verification horizon is below the phenomenon horizon.

Acceptance: produces "verification horizon exceeds decision horizon"
warning for any claim whose phenomenon_timescale_years exceeds the
audit's stated verification_horizon_years.

License: CC0-1.0
"""

from typing import Dict, List


# Phenomenon natural timescales for affected claims (years). Drawn from
# the historical record bundled in the claim modules themselves
# (institutional collapse cycles ~ 1-3 centuries; coercive scale
# trajectories ~ 50-300 yr; defensive-spending GDP shifts ~ 30+ yr).
DEFAULT_PHENOMENON_TIMESCALES_YEARS: Dict[str, float] = {
    "C022":  150.0,    # institutional lock-in (Roman, Soviet, Kodak, etc.)
    "C023":  100.0,    # knowledge exclusion (multi-generation publishing cycles)
    "C024":  200.0,    # collapse cycle (Phase 4-5 over decades)
    "C025":   30.0,    # Earth-system fragility (10-30 yr window per the spec)
    "C026":   20.0,    # economic double-bind feedback
    "C043":  100.0,    # coercive scale (USSR + East Germany cycles)
    "C044":   50.0,    # corruption growth (multi-decade institutional)
    "C046":   50.0,    # enforcement equality trajectory
    "C047":   30.0,    # defensive spending share of GDP
    "C051":   50.0,    # regulatory capture cycle
    "C052":   80.0,    # cross-domain neuroplasticity atrophy
    "C053":   80.0,    # 4-phase degradation cycle
    "C063":   30.0,    # blame externalization institutional cycle
    "C064":   30.0,    # care + authority preconditions evolution
    "C068":   50.0,    # 12-case library spans 20-30 yr; pattern cycle longer
    "C069":   30.0,    # institutional learning vs blame routing
}


def timescale_match_check(
    verification_horizon_years: float,
    claim_id: str,
    phenomenon_timescales: Dict[str, float] | None = None,
) -> dict:
    """For one claim, check audit horizon vs phenomenon timescale."""
    table = {**DEFAULT_PHENOMENON_TIMESCALES_YEARS,
              **(phenomenon_timescales or {})}
    phenomenon = table.get(claim_id)
    if phenomenon is None:
        return {
            "claim_id":              claim_id,
            "phenomenon_timescale":  None,
            "verification_horizon":  verification_horizon_years,
            "horizon_adequate":      True,
            "note":                  "no phenomenon timescale registered; claim is short-horizon",
        }
    adequate = verification_horizon_years >= phenomenon
    return {
        "claim_id":              claim_id,
        "phenomenon_timescale":  phenomenon,
        "verification_horizon":  verification_horizon_years,
        "horizon_adequate":      adequate,
        "note":                  (None if adequate else
                                   f"verification horizon ({verification_horizon_years}yr) "
                                   f"< phenomenon timescale ({phenomenon}yr); claim verdict "
                                   f"is structurally provisional"),
    }


def audit_horizon_report(
    verification_horizon_years: float,
    claim_ids: List[str] | None = None,
    phenomenon_timescales: Dict[str, float] | None = None,
) -> dict:
    """Run the timescale check over all registered long-horizon claims."""
    table = {**DEFAULT_PHENOMENON_TIMESCALES_YEARS,
              **(phenomenon_timescales or {})}
    targets = claim_ids if claim_ids is not None else list(table.keys())
    rows = [timescale_match_check(verification_horizon_years, cid, table)
            for cid in targets]
    inadequate = [r["claim_id"] for r in rows if not r["horizon_adequate"]]
    return {
        "verification_horizon_years": verification_horizon_years,
        "per_claim":                  rows,
        "inadequate_horizon_claims":  inadequate,
        "horizon_adequate_for_all":   not inadequate,
    }


if __name__ == "__main__":
    # Audit run at default 1-year verification horizon
    print("1-yr audit:")
    r = audit_horizon_report(verification_horizon_years=1.0)
    print(f"  inadequate for {len(r['inadequate_horizon_claims'])} claims: "
          f"{r['inadequate_horizon_claims']}")
    print()
    # Audit running over 200-yr horizon (e.g., historical cliometric study)
    print("200-yr audit:")
    r = audit_horizon_report(verification_horizon_years=200.0)
    print(f"  inadequate for {len(r['inadequate_horizon_claims'])} claims: "
          f"{r['inadequate_horizon_claims']}")
