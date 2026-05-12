"""
spr_operational_degradation_audit.py

Audit of Strategic Petroleum Reserve infrastructure use against
its design envelope. The SPR salt-cavern infrastructure was
designed for large, sustained drawdown events (e.g., major supply
disruption). Current use is closer to sustained low-rate exchange
operations: continuous small releases via swap agreements, no
refilling, extended timelines.

This module:

1. Records design-spec operating envelope.
2. Records observed use pattern (2022-2026).
3. Audits the mismatch between design use and actual use.
4. Estimates operational degradation as a function of cycling
   frequency under non-designed conditions.
5. Flags when the reserve has crossed operational thresholds
   even if volume remains.

Numbers are order-of-magnitude with public-source basis. The point
is to expose the structure of the audit so anyone can run it with
better data.

CC0. Standard library only.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check
  - energy_cascade_audit.py - May 2026 cross-layer cascade detection (price, EROI, refining, demand, trust)
  - spr_operational_degradation_audit.py - SPR salt-cavern use vs design envelope; volume + cycling-stress audit  (this module)
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass
from typing import List


# -----------------------------------------------------------------
# DESIGN ENVELOPE  (what SPR salt-cavern infrastructure was built for)
# -----------------------------------------------------------------

@dataclass
class DesignEnvelope:
    """
    Original design parameters of the four major SPR sites:
    Bayou Choctaw, Big Hill, Bryan Mound, West Hackberry.
    """
    max_aggregate_drawdown_rate_bpd: float = 4_400_000.0
    # Combined design throughput when all caverns drawing.

    sustained_drawdown_duration_days: int = 90
    # Designed for ~90-day sustained release in major disruption.

    expected_cycles_per_decade: int = 2
    # Designed for 1-2 major drawdown-refill cycles per decade.

    refill_window_months: int = 18
    # Caverns are pressure-managed; designed for measured refill.

    minimum_volume_for_stability_pct: float = 0.20
    # Below ~20 percent of cavern volume, structural integrity
    # of remaining oil cap is harder to maintain; risk of brine
    # intrusion or pressure imbalance rises.


# -----------------------------------------------------------------
# OBSERVED USE (2022-2026)
# -----------------------------------------------------------------

@dataclass
class ObservedUse:
    pre_drawdown_volume_mbbl: float = 638.0
    post_biden_drawdown_volume_mbbl: float = 350.0
    current_volume_mbbl: float = 200.0
    # Approximate current as of May 2026; subject to update.

    biden_drawdown_period_months: int = 8
    biden_drawdown_total_mbbl: float = 288.0
    biden_drawdown_pattern: str = "large sustained release"

    subsequent_use_period_months: int = 24
    subsequent_drawdown_total_mbbl: float = 150.0
    subsequent_drawdown_pattern: str = (
        "continuous small releases via exchange agreements"
    )

    refilling_active: bool = False
    refill_attempts_mbbl: float = 14.0
    # Some small attempts, no sustained refill.


# -----------------------------------------------------------------
# OPERATIONAL STRESS FACTORS
# -----------------------------------------------------------------

@dataclass
class CavernStress:
    """
    Salt caverns under repeated pressure cycling experience
    structural changes. Stress accumulates non-linearly with
    cycle frequency.
    """

    micro_fracture_threshold_cycles: int = 12
    # Approximate threshold; above this, micro-fracturing
    # accelerates.

    brine_migration_risk_threshold_pct: float = 0.20
    # When volume drops below 20 percent, brine intrusion and
    # density-instability risk rises.

    cycle_frequency_design_per_year: float = 0.3
    # Roughly 3 cycles per decade.

    cycle_frequency_observed_per_year: float = 4.0
    # Continuous exchange operations represent many small cycles
    # per year.


def degradation_factor(stress: CavernStress) -> float:
    """
    First-order estimate of degradation acceleration due to
    off-design cycling. Returns multiplier on baseline wear rate.
    """
    ratio = (
        stress.cycle_frequency_observed_per_year
        / stress.cycle_frequency_design_per_year
    )
    # Non-linear because micro-fracturing compounds.
    return ratio ** 1.3


# -----------------------------------------------------------------
# AUDIT
# -----------------------------------------------------------------

@dataclass
class SPRAuditResult:
    design_envelope: DesignEnvelope
    observed: ObservedUse
    stress: CavernStress
    current_volume_pct_of_design: float
    below_stability_threshold: bool
    degradation_multiplier: float
    days_of_import_protection: float
    flags: List[str]
    verdict: str


def audit_spr(
    design: DesignEnvelope = None,
    observed: ObservedUse = None,
    stress: CavernStress = None,
    us_net_imports_bpd: float = 1_600_000.0,
) -> SPRAuditResult:

    design = design or DesignEnvelope()
    observed = observed or ObservedUse()
    stress = stress or CavernStress()

    design_capacity_mbbl = 727.0   # Approximate SPR design capacity.
    current_pct = observed.current_volume_mbbl / design_capacity_mbbl

    below_stability = (
        current_pct < design.minimum_volume_for_stability_pct
    )

    deg = degradation_factor(stress)

    days_protection = (
        observed.current_volume_mbbl * 1_000_000.0
        / us_net_imports_bpd
    )

    flags = []
    if below_stability:
        flags.append(
            "VOLUME below stability threshold "
            f"({current_pct:.1%} < "
            f"{design.minimum_volume_for_stability_pct:.0%})"
        )

    if deg > 5.0:
        flags.append(
            "CAVERN cycling rate severely above design "
            f"({stress.cycle_frequency_observed_per_year:.1f}x/yr vs "
            f"{stress.cycle_frequency_design_per_year:.1f}x/yr; "
            f"degradation multiplier {deg:.1f}x)"
        )

    if not observed.refilling_active:
        flags.append(
            "REFILL not active; one-way drawdown under non-"
            "designed cycling pattern."
        )

    if observed.subsequent_drawdown_pattern.startswith(
        "continuous small releases"
    ):
        flags.append(
            "EXCHANGE-based releases extend drawdown timeline, "
            "increase coordination overhead, accelerate cavern "
            "cycling stress beyond design spec."
        )

    # Verdict combines volume status and operational degradation.
    if below_stability or days_protection < 30:
        verdict = (
            "CRITICAL: reserve functionally depleted for buffer "
            "purposes. Volume at or below stability threshold and/"
            "or import protection below 30 days."
        )
    elif deg > 5.0 and not observed.refilling_active:
        verdict = (
            "DEGRADED: volume nominally adequate, but operational "
            "cycling and lack of refill have moved infrastructure "
            "outside design envelope. Effective buffer is less "
            "than nominal volume implies."
        )
    elif days_protection < 60:
        verdict = (
            "SEVERE: import protection below 60 days. Buffer "
            "exists in name only; cannot absorb major disruption."
        )
    elif days_protection < 90:
        verdict = (
            "STRESSED: import protection at minimum design level. "
            "Cannot absorb sustained major disruption."
        )
    else:
        verdict = (
            "ADEQUATE: volume and operational parameters within "
            "design envelope."
        )

    return SPRAuditResult(
        design_envelope=design,
        observed=observed,
        stress=stress,
        current_volume_pct_of_design=current_pct,
        below_stability_threshold=below_stability,
        degradation_multiplier=deg,
        days_of_import_protection=days_protection,
        flags=flags,
        verdict=verdict,
    )


# -----------------------------------------------------------------
# CLAIMS
# -----------------------------------------------------------------

CLAIMS = [

    {
        "id": "SPR1_designed_for_large_sustained_releases",
        "statement": (
            "SPR salt-cavern infrastructure is designed for large, "
            "sustained drawdown events (~90 days, 4+ million bpd "
            "throughput), not for continuous small releases via "
            "exchange agreements."
        ),
        "falsifier": (
            "DOE / SPR technical documentation showing infrastructure "
            "optimized for sustained low-rate exchange operations."
        ),
        "confirmer": (
            "Public SPR design specifications consistently emphasize "
            "major-disruption response, not continuous market "
            "management."
        ),
        "confidence": "high",
    },

    {
        "id": "SPR2_biden_drawdown_closer_to_design_use",
        "statement": (
            "The 2022-2023 large drawdown, while politically "
            "controversial, was thermodynamically closer to the "
            "infrastructure's design use than the subsequent "
            "continuous exchange-based releases."
        ),
        "falsifier": (
            "Engineering analysis showing that continuous low-rate "
            "exchange operations are within design envelope and "
            "large sustained releases are not."
        ),
        "confirmer": (
            "Salt-cavern engineering literature supports infrequent "
            "large cycling over frequent small cycling."
        ),
        "confidence": "moderate",
    },

    {
        "id": "SPR3_current_pattern_degrades_infrastructure",
        "statement": (
            "Continuous exchange-based releases produce more "
            "cumulative cavern cycling stress per barrel released "
            "than designed large drawdown patterns. Infrastructure "
            "degrades faster than volume depletion alone implies."
        ),
        "falsifier": (
            "Engineering monitoring data showing cavern integrity "
            "improving or stable under current use pattern."
        ),
        "confirmer": (
            "Non-linear stress-frequency relationship in salt-"
            "cavern literature predicts compounding degradation."
        ),
        "confidence": "moderate",
    },

    {
        "id": "SPR4_current_volume_at_or_below_stability_threshold",
        "statement": (
            "Current SPR volume (~200 MMbbl) is at or near the "
            "minimum volume threshold below which cavern stability "
            "and brine-migration risk rise."
        ),
        "falsifier": (
            "DOE assessment confirming current volume is within "
            "comfortable operational envelope."
        ),
        "confirmer": (
            "Public discussion of SPR minimum operational levels "
            "places concern threshold near current volume."
        ),
        "confidence": "moderate",
    },

    {
        "id": "SPR5_buffer_function_effectively_lost",
        "statement": (
            "Current SPR volume provides fewer than 30-60 days of "
            "import-protection buffer. The reserve no longer "
            "fulfills its design role as a major-disruption buffer."
        ),
        "falsifier": (
            "Current volume divided by net US imports yields more "
            "than 90 days of protection."
        ),
        "confirmer": (
            "Approximately 200 MMbbl against ~1.6 mbpd net imports "
            "yields ~125 days; adjusted for stability minimum and "
            "drawdown rate limits, usable buffer is shorter."
        ),
        "confidence": "high",
    },

]


# -----------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------

def report():
    print("=" * 74)
    print("SPR OPERATIONAL DEGRADATION AUDIT")
    print("=" * 74)
    print()

    result = audit_spr()

    print("DESIGN ENVELOPE")
    print("-" * 74)
    d = result.design_envelope
    print(f"  Max aggregate drawdown:     "
          f"{d.max_aggregate_drawdown_rate_bpd:>10,.0f} bbl/day")
    print(f"  Sustained drawdown design:  "
          f"{d.sustained_drawdown_duration_days:>6d} days")
    print(f"  Expected cycles per decade: "
          f"{d.expected_cycles_per_decade:>6d}")
    print(f"  Refill window design:       "
          f"{d.refill_window_months:>6d} months")
    print(f"  Min volume for stability:   "
          f"{d.minimum_volume_for_stability_pct:>6.0%}")
    print()

    print("OBSERVED USE (2022-2026)")
    print("-" * 74)
    o = result.observed
    print(f"  Pre-drawdown volume:        "
          f"{o.pre_drawdown_volume_mbbl:>6.0f} MMbbl")
    print(f"  Post-Biden volume:          "
          f"{o.post_biden_drawdown_volume_mbbl:>6.0f} MMbbl")
    print(f"  Current volume:             "
          f"{o.current_volume_mbbl:>6.0f} MMbbl")
    print(f"  Biden drawdown:             "
          f"{o.biden_drawdown_total_mbbl:>6.0f} MMbbl over "
          f"{o.biden_drawdown_period_months} months")
    print(f"    Pattern: {o.biden_drawdown_pattern}")
    print(f"  Subsequent drawdown:        "
          f"{o.subsequent_drawdown_total_mbbl:>6.0f} MMbbl over "
          f"{o.subsequent_use_period_months} months")
    print(f"    Pattern: {o.subsequent_drawdown_pattern}")
    print(f"  Refilling active:           "
          f"{o.refilling_active}")
    print()

    print("OPERATIONAL STRESS")
    print("-" * 74)
    print(f"  Design cycle frequency:     "
          f"{result.stress.cycle_frequency_design_per_year:>6.1f} /yr")
    print(f"  Observed cycle frequency:   "
          f"{result.stress.cycle_frequency_observed_per_year:>6.1f} /yr")
    print(f"  Degradation multiplier:     "
          f"{result.degradation_multiplier:>6.1f} x baseline wear")
    print()

    print("STATUS")
    print("-" * 74)
    print(f"  Current volume vs design:   "
          f"{result.current_volume_pct_of_design:>6.1%}")
    print(f"  Below stability threshold:  "
          f"{result.below_stability_threshold}")
    print(f"  Days of import protection:  "
          f"{result.days_of_import_protection:>6.1f}")
    print()

    if result.flags:
        print("FLAGS")
        print("-" * 74)
        for f in result.flags:
            print(f"  - {f}")
        print()

    print("VERDICT")
    print("-" * 74)
    print(f"  {result.verdict}")
    print()

    print("FALSIFIABLE CLAIMS")
    print("-" * 74)
    for c in CLAIMS:
        print(f"  {c['id']}")
        print(f"    {c['statement']}")
        print(f"    Confidence: {c['confidence']}")
        print()


if __name__ == "__main__":
    report()
