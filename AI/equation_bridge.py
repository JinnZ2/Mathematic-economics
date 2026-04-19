"""
Equation Bridge Module
Connects the AI/ computational models to the 13 structural equations from README.md

Maps physical measurements (energy, time, resources) from the existing models
to the economic structure equations (VE/VL, SID, RI, etc.), enabling computation
of structural indices from thermodynamic inputs.
"""

import sys
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import numpy as np

# ---------------------------------------------------------------------------
# Attempt to import sibling modules (handle running standalone vs. imported)
# ---------------------------------------------------------------------------
_ai_dir = os.path.dirname(os.path.abspath(__file__))
if _ai_dir not in sys.path:
    sys.path.insert(0, _ai_dir)

try:
    from money_free_model import EnergyLedger, PhysicalConstraints, ResourceDepletion
    _HAS_MONEY_FREE = True
except Exception:
    _HAS_MONEY_FREE = False

try:
    from temporal_energy import ActivityCost, TemporalConstraints
    _HAS_TEMPORAL = True
except Exception:
    _HAS_TEMPORAL = False


# ============================================================================
# EQUATION RESULTS
# ============================================================================

class ThresholdStatus(Enum):
    """Classification of a measured value relative to defined thresholds."""
    BELOW = "below_threshold"
    WITHIN = "within_range"
    ABOVE = "above_threshold"
    UNKNOWN = "unknown"


@dataclass
class EquationResult:
    """Result of computing a single structural equation."""
    equation_id: str
    name: str
    value: float
    threshold_status: ThresholdStatus
    data_source: str
    notes: str = ""

    def __repr__(self) -> str:
        return (f"EquationResult({self.equation_id}: {self.value:.4f} "
                f"[{self.threshold_status.value}] via {self.data_source})")


@dataclass
class SystemMeasurement:
    """Complete structural measurement of an economic system."""
    results: Dict[str, EquationResult] = field(default_factory=dict)
    osdi: Optional[float] = None
    osdi_weights: Dict[str, float] = field(default_factory=lambda: {
        "SID": 0.3, "MSI": 0.2, "ISR": 0.2, "BSC": 0.15, "MM": 0.15
    })

    def add(self, result: EquationResult) -> None:
        self.results[result.equation_id] = result

    def compute_osdi(self) -> float:
        """Compute OSDI composite from available component measurements."""
        # Normalization: SID and MSI are already 0-1.
        # ISR, BSC, MM need clamping to [0, 1] for the composite.
        normalizers = {
            "SID": lambda v: v,  # Already 0-1
            "MSI": lambda v: v,  # Already 0-1
            "ISR": lambda v: min(v / 20.0, 1.0),  # 20x subsidy → 1.0
            "BSC": lambda v: min(v / 5.0, 1.0),   # BSC 5 → 1.0
            "MM": lambda v: min(v / 10.0, 1.0),   # MM 10 → 1.0
        }
        components = {}
        for eid, weight_key in [("SID", "SID"), ("MSI", "MSI"),
                                 ("ISR", "ISR"), ("BSC", "BSC"),
                                 ("MM", "MM")]:
            if eid in self.results:
                raw = self.results[eid].value
                components[weight_key] = normalizers[weight_key](raw)

        if not components:
            return float("nan")

        # Normalize weights to available components
        available_weights = {k: self.osdi_weights[k] for k in components}
        total_w = sum(available_weights.values())
        if total_w == 0:
            return float("nan")

        self.osdi = sum(
            components[k] * (available_weights[k] / total_w)
            for k in components
        )
        return self.osdi

    def summary_table(self) -> str:
        """Formatted summary of all measurements."""
        lines = [
            f"{'Equation':<8} {'Name':<35} {'Value':>10} {'Status':<20} {'Source'}",
            "-" * 100,
        ]
        for r in self.results.values():
            lines.append(
                f"{r.equation_id:<8} {r.name:<35} {r.value:>10.4f} "
                f"{r.threshold_status.value:<20} {r.data_source}"
            )
        if self.osdi is not None:
            lines.append("-" * 100)
            lines.append(f"{'OSDI':<8} {'Overall Socialist Dependence Index':<35} "
                         f"{self.osdi:>10.4f}")
        return "\n".join(lines)


# ============================================================================
# INDIVIDUAL EQUATION FUNCTIONS
# ============================================================================

def compute_ve_vl(value_extracted: float, value_labor: float) -> EquationResult:
    """
    Equation 1: Value Extraction / Value Labor ratio.
    Thermodynamic interpretation: fraction of system energy output
    captured by non-producing agents.
    """
    if value_labor == 0:
        ratio = float("inf")
    else:
        ratio = value_extracted / value_labor

    if ratio < 0.1:
        status = ThresholdStatus.BELOW  # Productive
    elif ratio > 0.3:
        status = ThresholdStatus.ABOVE  # Extraction-dominant
    else:
        status = ThresholdStatus.WITHIN

    return EquationResult("VE_VL", "Value Extraction Ratio", ratio,
                          status, "direct_input")


def compute_sid(collective_value: float, private_value: float) -> EquationResult:
    """
    Equation 2: Socialist Infrastructure Dependency.
    Thermodynamic interpretation: fraction of energy inputs sourced
    from collectively maintained infrastructure.
    """
    total = collective_value + private_value
    sid = collective_value / total if total > 0 else 0.0

    if sid > 0.8:
        status = ThresholdStatus.ABOVE
    elif sid > 0.5:
        status = ThresholdStatus.WITHIN
    else:
        status = ThresholdStatus.BELOW

    return EquationResult("SID", "Infrastructure Dependency", sid,
                          status, "direct_input")


def compute_ri(worker_risk: float, n_workers: int,
               investor_risk: float, n_investors: int) -> EquationResult:
    """
    Equation 3: Risk Inequality.
    Thermodynamic interpretation: asymmetry in consequence exposure
    per energy-contributing agent.
    """
    worker_per_capita = worker_risk / n_workers if n_workers > 0 else 0
    investor_per_capita = investor_risk / n_investors if n_investors > 0 else 0
    ri = worker_per_capita / investor_per_capita if investor_per_capita > 0 else float("inf")

    if abs(ri - 1.0) < 0.5:
        status = ThresholdStatus.WITHIN
    elif ri > 1.0:
        status = ThresholdStatus.ABOVE
    else:
        status = ThresholdStatus.BELOW

    return EquationResult("RI", "Risk Inequality", ri,
                          status, "direct_input")


def compute_di(power_scores: List[float]) -> EquationResult:
    """
    Equation 4: Democracy Index (variance in decision-making power).
    Thermodynamic interpretation: entropy of control distribution
    over system energy flows.
    """
    if len(power_scores) < 2:
        return EquationResult("DI", "Democracy Index", 0.0,
                              ThresholdStatus.UNKNOWN, "insufficient_data")
    variance = float(np.var(power_scores))
    # High variance = oligarchic
    status = ThresholdStatus.ABOVE if variance > 1e6 else ThresholdStatus.WITHIN

    return EquationResult("DI", "Democracy Index", variance,
                          status, "direct_input")


def compute_lwr(wealth_from_labor: float,
                wealth_from_ownership: float) -> EquationResult:
    """
    Equation 5: Labor Wealth Ratio.
    Thermodynamic interpretation: fraction of accumulated energy
    attributable to direct work vs. ownership position.
    """
    lwr = (wealth_from_labor / wealth_from_ownership
           if wealth_from_ownership > 0 else float("inf"))

    if lwr > 1.0:
        status = ThresholdStatus.ABOVE  # Labor-dominant
    elif lwr < 0.5:
        status = ThresholdStatus.BELOW  # Ownership-dominant
    else:
        status = ThresholdStatus.WITHIN

    return EquationResult("LWR", "Labor Wealth Ratio", lwr,
                          status, "direct_input")


def compute_msi(gov_money: float, total_money: float) -> EquationResult:
    """
    Equation 6: Money Socialist Index.
    Thermodynamic interpretation: fraction of the system's exchange
    medium originating through collective mechanisms.
    """
    msi = gov_money / total_money if total_money > 0 else 0.0
    status = ThresholdStatus.ABOVE if msi > 0.9 else ThresholdStatus.WITHIN

    return EquationResult("MSI", "Money Socialist Index", msi,
                          status, "direct_input")


def compute_bsc(gov_rescue: float, private_losses: float) -> EquationResult:
    """
    Equation 7: Bailout Socialism Coefficient.
    Thermodynamic interpretation: ratio of collective energy
    redirected to cover private-agent losses.
    """
    bsc = gov_rescue / private_losses if private_losses > 0 else 0.0

    if bsc == 0:
        status = ThresholdStatus.BELOW  # Pure market
    elif bsc > 1:
        status = ThresholdStatus.ABOVE  # Super-coverage
    else:
        status = ThresholdStatus.WITHIN

    return EquationResult("BSC", "Bailout Socialism Coefficient", bsc,
                          status, "direct_input")


def compute_mm(reserve_requirement: float) -> EquationResult:
    """
    Equation 8: Money Multiplier.
    Thermodynamic interpretation: amplification factor of collectively
    pooled deposits through fractional reserve.
    """
    if reserve_requirement <= 0:
        mm = float("inf")
    else:
        mm = 1.0 / reserve_requirement
    status = ThresholdStatus.ABOVE if mm > 5 else ThresholdStatus.WITHIN

    return EquationResult("MM", "Money Multiplier", mm, status, "direct_input")


def compute_isr(infrastructure_value: float,
                cost_paid: float) -> EquationResult:
    """
    Equation 9: Infrastructure Subsidy Ratio.
    Thermodynamic interpretation: ratio of collectively maintained
    energy infrastructure consumed vs. energy contributed to its maintenance.
    """
    isr = infrastructure_value / cost_paid if cost_paid > 0 else float("inf")
    if isr > 10:
        status = ThresholdStatus.ABOVE
    elif isr > 5:
        status = ThresholdStatus.WITHIN
    else:
        status = ThresholdStatus.BELOW

    return EquationResult("ISR", "Infrastructure Subsidy Ratio", isr,
                          status, "direct_input")


def compute_ufr(top1_delta: float, bottom50_delta: float) -> EquationResult:
    """
    Equation 10: Upward Flow Rate.
    Thermodynamic interpretation: ratio of energy accumulation rates
    between system apex and base.
    """
    ufr = (top1_delta / bottom50_delta
           if bottom50_delta != 0 else float("inf"))

    if abs(ufr - 1.0) < 0.5:
        status = ThresholdStatus.WITHIN
    elif ufr > 1.0:
        status = ThresholdStatus.ABOVE
    else:
        status = ThresholdStatus.BELOW

    return EquationResult("UFR", "Upward Flow Rate", ufr,
                          status, "direct_input")


def compute_er(revenue: float, labor_costs: float) -> EquationResult:
    """
    Equation 11: Extraction Rate.
    Thermodynamic interpretation: fraction of system output energy
    not returned to the producing agents.
    """
    er = (revenue - labor_costs) / revenue if revenue > 0 else 0.0

    if er > 0.55:
        status = ThresholdStatus.ABOVE
    elif er < 0.35:
        status = ThresholdStatus.BELOW
    else:
        status = ThresholdStatus.WITHIN

    return EquationResult("ER", "Extraction Rate", er,
                          status, "direct_input")


def compute_hhi(market_shares: List[float]) -> EquationResult:
    """
    Equation 12: Herfindahl-Hirschman Index.
    Thermodynamic interpretation: concentration of energy flow
    control among system agents.
    """
    hhi = sum(s ** 2 for s in market_shares)

    if hhi > 2500:
        status = ThresholdStatus.ABOVE
    elif hhi > 1500:
        status = ThresholdStatus.WITHIN
    else:
        status = ThresholdStatus.BELOW

    return EquationResult("HHI", "Herfindahl-Hirschman Index", hhi,
                          status, "direct_input")


def compute_sd(def_t1: float, def_t2: float,
               years_elapsed: float) -> EquationResult:
    """
    Equation 13: Semantic Drift Rate.
    Measures instability of term definitions over time.
    """
    sd = abs(def_t2 - def_t1) / years_elapsed if years_elapsed > 0 else 0.0
    status = ThresholdStatus.ABOVE if sd > 1.0 else ThresholdStatus.WITHIN

    return EquationResult("SD", "Semantic Drift Rate", sd,
                          status, "direct_input")


# ============================================================================
# BRIDGE: ENERGY LEDGER → STRUCTURAL EQUATIONS
# ============================================================================

def from_energy_ledger(
    energy_inputs: Dict[str, float],
    energy_outputs: Dict[str, float],
    constraints: Optional[object] = None,
) -> SystemMeasurement:
    """
    Derive structural equation values from energy accounting data.

    Maps thermodynamic measurements to economic structure indices:
    - Energy extracted vs. produced → VE/VL proxy
    - Collective vs. private energy sources → SID
    - Regeneration vs. extraction → sustainability (ISR proxy)

    Parameters
    ----------
    energy_inputs : dict
        Keys should include 'solar', 'fossil', 'human_labor', 'collective_infra',
        'private_resources'. Values in MJ.
    energy_outputs : dict
        Keys should include 'useful_work', 'heat_loss', 'stored_energy',
        'extracted_by_capital'. Values in MJ.
    constraints : PhysicalConstraints, optional
        Physical constraints from money_free_model.

    Returns
    -------
    SystemMeasurement with derivable equations populated.
    """
    sm = SystemMeasurement()

    # --- VE/VL from energy flows ---
    extracted = energy_outputs.get("extracted_by_capital", 0)
    labor_output = energy_outputs.get("useful_work", 0)
    if labor_output > 0:
        sm.add(compute_ve_vl(extracted, labor_output))

    # --- SID from energy source classification ---
    collective = energy_inputs.get("collective_infra", 0)
    private = energy_inputs.get("private_resources", 0)
    if collective + private > 0:
        sm.add(compute_sid(collective, private))

    # --- ISR proxy: infrastructure energy value vs. contribution ---
    infra_value = energy_inputs.get("collective_infra", 0)
    # Approximate cost_paid as fraction of useful_work contributed back
    cost_paid = energy_outputs.get("useful_work", 0) * 0.1  # ~10% tax proxy
    if cost_paid > 0:
        sm.add(compute_isr(infra_value, cost_paid))

    # --- ER from energy accounting ---
    total_output = sum(energy_outputs.values())
    labor_energy = energy_inputs.get("human_labor", 0)
    if total_output > 0:
        sm.add(compute_er(total_output, labor_energy))

    # --- Sustainability check (not a numbered equation, but thermodynamically relevant) ---
    stored = energy_outputs.get("stored_energy", 0)
    heat_loss = energy_outputs.get("heat_loss", 0)
    if constraints and _HAS_MONEY_FREE:
        regen = constraints.soil_regeneration_mm_per_year  # proxy
        # Could extend with full regeneration accounting

    sm.compute_osdi()
    return sm


# ============================================================================
# COMPUTE ALL FROM RAW INPUTS
# ============================================================================

def compute_all(
    ve: float = 0, vl: float = 0,
    collective_value: float = 0, private_value: float = 0,
    worker_risk: float = 0, n_workers: int = 1,
    investor_risk: float = 0, n_investors: int = 1,
    power_scores: Optional[List[float]] = None,
    wealth_labor: float = 0, wealth_ownership: float = 0,
    gov_money: float = 0, total_money: float = 0,
    gov_rescue: float = 0, private_losses: float = 0,
    reserve_requirement: float = 0.1,
    infra_value: float = 0, cost_paid: float = 0,
    top1_delta: float = 0, bottom50_delta: float = 0,
    revenue: float = 0, labor_costs: float = 0,
    market_shares: Optional[List[float]] = None,
    def_t1: float = 0, def_t2: float = 0, years: float = 1,
) -> SystemMeasurement:
    """Compute all 13 equations from raw inputs and return SystemMeasurement."""
    sm = SystemMeasurement()

    sm.add(compute_ve_vl(ve, vl))
    sm.add(compute_sid(collective_value, private_value))
    sm.add(compute_ri(worker_risk, n_workers, investor_risk, n_investors))
    sm.add(compute_di(power_scores or []))
    sm.add(compute_lwr(wealth_labor, wealth_ownership))
    sm.add(compute_msi(gov_money, total_money))
    sm.add(compute_bsc(gov_rescue, private_losses))
    sm.add(compute_mm(reserve_requirement))
    sm.add(compute_isr(infra_value, cost_paid))
    sm.add(compute_ufr(top1_delta, bottom50_delta))
    sm.add(compute_er(revenue, labor_costs))
    sm.add(compute_hhi(market_shares or []))
    sm.add(compute_sd(def_t1, def_t2, years))

    sm.compute_osdi()
    return sm


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 100)
    print("Equation Bridge: Illustrative values from README.md")
    print("=" * 100)

    # Compute using README illustrative values
    measurement = compute_all(
        # Eq 1: VE/VL (private equity example)
        ve=200, vl=500,
        # Eq 2: SID (typical manufacturing)
        collective_value=380_000, private_value=250_000,
        # Eq 3: RI
        worker_risk=0.725, n_workers=1,
        investor_risk=0.175, n_investors=1,
        # Eq 4: DI (CEO vs worker)
        power_scores=[500_000_000, 5_000],
        # Eq 5: LWR (2024 estimate)
        wealth_labor=25, wealth_ownership=100,
        # Eq 6: MSI
        gov_money=98, total_money=100,
        # Eq 7: BSC (2008 crisis)
        gov_rescue=7_000_000_000_000, private_losses=2_000_000_000_000,
        # Eq 8: MM
        reserve_requirement=0.10,
        # Eq 9: ISR (typical business)
        infra_value=350_000, cost_paid=50_000,
        # Eq 10: UFR (2020 estimate)
        top1_delta=30, bottom50_delta=1,
        # Eq 11: ER
        revenue=10_000_000, labor_costs=4_000_000,
        # Eq 12: HHI (search engines example)
        market_shares=[80, 10, 5, 3, 2],
        # Eq 13: SD
        def_t1=70, def_t2=70, years=64,  # Meaning inverted but magnitude same
    )

    print(measurement.summary_table())

    print()
    print("=" * 100)
    print("Energy Ledger Bridge: Deriving equations from thermodynamic inputs")
    print("=" * 100)

    energy_measurement = from_energy_ledger(
        energy_inputs={
            "solar": 8000,
            "fossil": 200,
            "human_labor": 50,
            "collective_infra": 300,
            "private_resources": 150,
        },
        energy_outputs={
            "useful_work": 100,
            "heat_loss": 8000,
            "stored_energy": 150,
            "extracted_by_capital": 40,
        },
    )

    print(energy_measurement.summary_table())
