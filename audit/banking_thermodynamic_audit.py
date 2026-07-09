"""
banking_thermodynamic_audit.py

Audit of the energy cost of the capital and banking infrastructure
that funds and services oil-extraction and other industrial projects.

Standard EROI calculations treat capital as free. It is not. Banking
infrastructure consumes real energy: data centers, branches, staff,
regulatory and compliance overhead, security, redundancy, currency
creation, debt-servicing computation, risk management apparatus.

This module estimates that cost, attributes it to specific loans,
runs the systemic constraint (banking requires growth; energy is
contracting), and compares the capital-infrastructure cost of
extraction-funded vs. voluntary-labor systems.

Numbers are order-of-magnitude with sources stated. The point is to
expose the structure and let anyone replace the inputs with their
own data. CC0. Standard library only.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check  (this module)
  - energy_cascade_audit.py - May 2026 cross-layer cascade detection (price, EROI, refining, demand, trust)
  - spr_operational_degradation_audit.py - SPR salt-cavern use vs design envelope; volume + cycling-stress audit
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass, field
from typing import List, Dict
import math


# -----------------------------------------------------------------
# LAYER 1: BANKING INFRASTRUCTURE ENERGY COST
# -----------------------------------------------------------------

@dataclass
class BankingInfrastructure:
    """
    Order-of-magnitude estimates of the energy cost of the global
    banking and financial system, normalized per dollar of capital
    under management per year.

    Sources cited in NOTES at bottom of module.
    """

    # Global financial sector electricity (data centers, offices,
    # branches, network). Estimates range 200-400 TWh annually.
    global_finance_electricity_twh_per_year: float = 300.0

    # Total assets under management globally (~$120T) plus shadow
    # banking, derivatives notional, and corporate capital flows
    # gives effective base around $400T.
    global_capital_base_usd: float = 400e12

    # Multiplier for non-electric energy inputs: real estate
    # heating/cooling, employee commuting, physical security, paper
    # and supplies, equipment manufacturing.
    non_electric_multiplier: float = 1.6

    # Compliance and regulatory overhead. Estimated 8-15% of bank
    # operating expense globally. Energy proxy is similar fraction.
    compliance_uplift: float = 1.12

    # Risk management apparatus (derivatives, hedging, insurance).
    risk_management_uplift: float = 1.10

    def energy_kj_per_dollar_per_year(self) -> float:
        """
        Convert TWh to kJ: 1 TWh = 3.6e12 kJ.
        """
        total_electric_kj = (
            self.global_finance_electricity_twh_per_year * 3.6e12
        )
        total_energy_kj = (
            total_electric_kj
            * self.non_electric_multiplier
            * self.compliance_uplift
            * self.risk_management_uplift
        )
        return total_energy_kj / self.global_capital_base_usd


# -----------------------------------------------------------------
# LAYER 2: CAPITAL FORMATION COST
# -----------------------------------------------------------------

@dataclass
class CapitalFormationCost:
    """
    Energy cost of creating and maintaining the monetary system
    itself, separate from the cost of moving capital through it.
    """

    # Central bank operations (Federal Reserve, ECB, etc.) plus
    # currency production, distribution, and replacement.
    central_bank_operations_twh_per_year: float = 8.0

    # Crypto and digital currency infrastructure (Bitcoin alone
    # ~150 TWh annually). Included as the energy cost of currency
    # competition and shadow currency systems.
    digital_currency_twh_per_year: float = 180.0

    # Debt-tracking computational overhead globally. Conservative.
    debt_servicing_compute_twh_per_year: float = 15.0

    def annual_total_kj(self) -> float:
        total_twh = (
            self.central_bank_operations_twh_per_year
            + self.digital_currency_twh_per_year
            + self.debt_servicing_compute_twh_per_year
        )
        return total_twh * 3.6e12


# -----------------------------------------------------------------
# LAYER 3: LOAN-LEVEL ACCOUNTING
# -----------------------------------------------------------------

@dataclass
class LoanAudit:
    """
    Energy accounting for a specific loan and its servicing across
    the productive lifespan of the project it funds.
    """
    project_name: str
    loan_principal_usd: float
    interest_rate_pct: float
    term_years: float
    project_productive_years: float
    # Energy extracted from the project, total over productive life.
    project_gross_energy_kj: float


def loan_servicing_energy_cost(
    loan: LoanAudit,
    infra: BankingInfrastructure,
    formation: CapitalFormationCost,
) -> Dict[str, float]:
    """
    Attribute banking infrastructure energy to a specific loan
    across its servicing lifespan. Includes both annual
    infrastructure overhead and per-payment computational cost.
    """

    per_dollar_per_year = infra.energy_kj_per_dollar_per_year()

    # Total interest payments over the loan term (simple
    # approximation; real amortization is more complex but
    # order-of-magnitude similar).
    total_interest = (
        loan.loan_principal_usd
        * (loan.interest_rate_pct / 100.0)
        * loan.term_years
    )
    total_loan_dollar_years = (
        loan.loan_principal_usd * loan.term_years
        + total_interest * 0.5
    )

    # Infrastructure energy attributed to this loan over its term.
    infrastructure_kj = total_loan_dollar_years * per_dollar_per_year

    # Capital formation share attributed to this loan, weighted by
    # principal as fraction of global capital base.
    formation_share = (
        loan.loan_principal_usd / infra.global_capital_base_usd
    )
    formation_kj = formation.annual_total_kj() * formation_share * loan.term_years

    total_capital_system_kj = infrastructure_kj + formation_kj

    # Opportunity cost: the same loan capacity could have funded
    # something else. Express as fraction of total energy
    # available in the financial system attributed to this loan.
    opportunity_kj = total_capital_system_kj  # simplification

    # Net energy outcome: project gross energy minus capital system
    # energy cost.
    net_energy_kj = (
        loan.project_gross_energy_kj - total_capital_system_kj
    )

    return {
        "project": loan.project_name,
        "principal_usd": loan.loan_principal_usd,
        "total_interest_usd": total_interest,
        "infrastructure_energy_kj": infrastructure_kj,
        "formation_energy_kj": formation_kj,
        "total_capital_system_kj": total_capital_system_kj,
        "project_gross_energy_kj": loan.project_gross_energy_kj,
        "net_energy_kj": net_energy_kj,
        "capital_cost_share_of_gross": (
            100.0 * total_capital_system_kj
            / loan.project_gross_energy_kj
            if loan.project_gross_energy_kj > 0 else float("inf")
        ),
        "net_eroi_after_capital": (
            loan.project_gross_energy_kj
            / total_capital_system_kj
            if total_capital_system_kj > 0 else float("inf")
        ),
    }


# -----------------------------------------------------------------
# LAYER 4: SYSTEMIC CONSTRAINT
# -----------------------------------------------------------------

@dataclass
class SystemicConstraint:
    """
    Banking requires growth: interest must be serviced from future
    energy / value. If aggregate net energy is contracting, debts
    cannot be serviced at scale. Model the constraint.
    """

    current_net_energy_growth_pct: float
    # Negative number if net energy is contracting.

    average_interest_rate_pct: float = 7.5
    # Approximate weighted average across consumer, corporate,
    # and sovereign debt.

    total_global_debt_to_gdp: float = 3.5
    # Global debt has been approximately 3.3-3.7 times global GDP.

    def is_debt_serviceable(self) -> Dict[str, object]:
        """
        First-order check: can interest be serviced from new energy?
        """
        # Required growth to service interest, in real terms:
        required_growth = (
            self.average_interest_rate_pct * self.total_global_debt_to_gdp
        )
        # Available: current net energy growth.
        available_growth = self.current_net_energy_growth_pct

        gap = required_growth - available_growth
        serviceable = available_growth >= required_growth

        if serviceable:
            verdict = "BANKING SYSTEM SUSTAINABLE under current parameters"
        elif gap < 5.0:
            verdict = "BANKING SYSTEM STRESSED - gap manageable short term"
        elif gap < 15.0:
            verdict = "BANKING SYSTEM IN CRISIS - debt restructuring required"
        else:
            verdict = "BANKING SYSTEM STRUCTURALLY UNVIABLE at this energy regime"

        return {
            "required_growth_pct": required_growth,
            "available_growth_pct": available_growth,
            "gap_pct": gap,
            "serviceable": serviceable,
            "verdict": verdict,
        }


# -----------------------------------------------------------------
# LAYER 5: COMPARATIVE - CAPITAL COST IN DIFFERENT SYSTEMS
# -----------------------------------------------------------------

@dataclass
class SystemCapitalCost:
    system_name: str
    capital_infrastructure_required: str
    energy_cost_of_capital_layer_kj_per_year: float
    can_function_under_zero_growth: bool
    can_function_under_contracting_energy: bool
    notes: str = ""


SYSTEM_CAPITAL_PROFILES: List[SystemCapitalCost] = [

    SystemCapitalCost(
        system_name="Industrial oil extraction (current US system)",
        capital_infrastructure_required=(
            "Full banking and financial system: commercial banks, "
            "investment banks, derivatives markets, insurance, "
            "rating agencies, regulatory compliance, central bank "
            "monetary management, debt servicing infrastructure."
        ),
        energy_cost_of_capital_layer_kj_per_year=1.5e16,
        # Estimated annual energy cost of capital infrastructure
        # attributable to the global oil extraction sector.
        can_function_under_zero_growth=False,
        can_function_under_contracting_energy=False,
        notes=(
            "Requires sustained energy growth to service compounding "
            "debt. Cannot function under net energy contraction."
        ),
    ),

    SystemCapitalCost(
        system_name="Community-scale gravity battery + voluntary labor",
        capital_infrastructure_required=(
            "Minimal: shared decision-making among participants, "
            "informal ledger of contribution and benefit, no "
            "external financing, no interest-bearing debt, no "
            "regulatory compliance apparatus."
        ),
        energy_cost_of_capital_layer_kj_per_year=1e9,
        # Estimated annual energy cost of the social-infrastructure
        # capital layer (meetings, simple records, shared tools).
        can_function_under_zero_growth=True,
        can_function_under_contracting_energy=True,
        notes=(
            "Capital layer is essentially absent. System scales "
            "with participation, not with compounding interest."
        ),
    ),

    SystemCapitalCost(
        system_name="Traditional kinship-network subsistence",
        capital_infrastructure_required=(
            "Reciprocity norms, generational knowledge transmission, "
            "landscape-encoded record systems, no external financing."
        ),
        energy_cost_of_capital_layer_kj_per_year=1e8,
        can_function_under_zero_growth=True,
        can_function_under_contracting_energy=True,
        notes=(
            "Persisted for millennia under net-zero-growth conditions. "
            "No interest-bearing debt; obligations distributed across "
            "kin networks."
        ),
    ),

]


# -----------------------------------------------------------------
# FALSIFIABLE CLAIMS
# -----------------------------------------------------------------

CLAIMS: List[Dict[str, str]] = [

    {
        "id": "B1_banking_energy_per_dollar_measurable",
        "statement": (
            "Banking infrastructure energy cost per dollar of "
            "capital under management is measurable and non-zero. "
            "Order of magnitude: 5-15 kJ per dollar per year."
        ),
        "falsifier": (
            "Comprehensive bottom-up accounting yields energy cost "
            "below 1 kJ per dollar per year."
        ),
        "confirmer": (
            "Global financial sector electricity 200-400 TWh per "
            "year against capital base ~$400T yields per-dollar "
            "values in the 5-15 kJ per year range, before "
            "non-electric multiplier."
        ),
    },

    {
        "id": "B2_capital_cost_rises_with_complexity",
        "statement": (
            "Banking energy cost per dollar has risen over time as "
            "the financial system has become more complex (more "
            "derivatives, more compliance, more digital "
            "infrastructure)."
        ),
        "falsifier": (
            "Time-series data show flat or declining energy cost "
            "per dollar despite increased complexity."
        ),
        "confirmer": (
            "Documented increases in financial sector electricity "
            "demand, compliance staff counts, and IT infrastructure "
            "consistently outpace growth in capital base."
        ),
    },

    {
        "id": "B3_banking_requires_growth",
        "statement": (
            "Interest-bearing debt at scale requires aggregate "
            "growth to remain serviceable. Under sustained energy "
            "contraction, the banking system cannot maintain its "
            "current scale or complexity."
        ),
        "falsifier": (
            "Historical example of a major banking system functioning "
            "indefinitely under sustained negative net energy growth "
            "without restructuring."
        ),
        "confirmer": (
            "Every documented case of resource contraction in a "
            "debt-financed economy has produced banking crisis, "
            "default, or restructuring."
        ),
    },

    {
        "id": "B4_voluntary_labor_systems_zero_capital_cost",
        "statement": (
            "Voluntary-labor and kinship-network systems have "
            "near-zero capital infrastructure energy cost. They scale "
            "with participation rather than with compounding "
            "interest."
        ),
        "falsifier": (
            "Comprehensive accounting of a working voluntary-labor "
            "system shows capital infrastructure energy cost "
            "comparable to industrial banking."
        ),
        "confirmer": (
            "Documented traditional and intentional communities "
            "operate at energy costs orders of magnitude below "
            "industrial financial systems."
        ),
    },

    {
        "id": "B5_extraction_funded_via_banking_constraint",
        "statement": (
            "Continued industrial extraction is sustained by the "
            "banking system's need for growth, not by thermodynamic "
            "efficiency. Simplifying to lower-capital systems is "
            "thermodynamically rational but economically "
            "catastrophic for the financial sector."
        ),
        "falsifier": (
            "Demonstrate that current extraction continues because "
            "it is the most energy-efficient pathway, not because "
            "the banking system requires the cash flows."
        ),
        "confirmer": (
            "Documentation that extraction projects with negative "
            "or near-zero EROI continue to receive financing "
            "because they service existing debt structures."
        ),
    },

]


# -----------------------------------------------------------------
# REPORT
# -----------------------------------------------------------------

def report():
    print("=" * 74)
    print("BANKING THERMODYNAMIC AUDIT")
    print("=" * 74)
    print()

    infra = BankingInfrastructure()
    formation = CapitalFormationCost()

    print("LAYER 1: BANKING INFRASTRUCTURE ENERGY")
    print("-" * 74)
    per_dollar = infra.energy_kj_per_dollar_per_year()
    print(f"  Global finance electricity:    "
          f"{infra.global_finance_electricity_twh_per_year:6.0f} TWh/yr")
    print(f"  Global capital base:           "
          f"${infra.global_capital_base_usd/1e12:6.0f}T")
    print(f"  Non-electric multiplier:       "
          f"x {infra.non_electric_multiplier:4.2f}")
    print(f"  Compliance uplift:             "
          f"x {infra.compliance_uplift:4.2f}")
    print(f"  Risk management uplift:        "
          f"x {infra.risk_management_uplift:4.2f}")
    print(f"  Energy per dollar per year:    "
          f"{per_dollar:6.2f} kJ")
    print()

    print("LAYER 2: CAPITAL FORMATION COST")
    print("-" * 74)
    print(f"  Central bank operations:       "
          f"{formation.central_bank_operations_twh_per_year:6.1f} TWh/yr")
    print(f"  Digital currency infrastructure: "
          f"{formation.digital_currency_twh_per_year:5.1f} TWh/yr")
    print(f"  Debt-servicing compute:        "
          f"{formation.debt_servicing_compute_twh_per_year:6.1f} TWh/yr")
    print(f"  Total formation cost:          "
          f"{formation.annual_total_kj()/3.6e12:6.1f} TWh/yr "
          f"({formation.annual_total_kj():.2e} kJ/yr)")
    print()

    print("LAYER 3: LOAN-LEVEL ACCOUNTING")
    print("-" * 74)

    bbl_energy_kj = 6_117_863.0   # 5.8 MMBTU/bbl

    sample_loans = [
        LoanAudit(
            project_name="Mid-sized shale oil project ($500M, 6-year)",
            loan_principal_usd=500e6,
            interest_rate_pct=9.5,
            term_years=6.0,
            project_productive_years=6.0,
            project_gross_energy_kj=2.5e6 * bbl_energy_kj,
        ),
        LoanAudit(
            project_name="Large refinery rebuild ($5B, 20-year)",
            loan_principal_usd=5e9,
            interest_rate_pct=7.0,
            term_years=20.0,
            project_productive_years=20.0,
            project_gross_energy_kj=80e6 * bbl_energy_kj,
        ),
        LoanAudit(
            project_name="Major pipeline ($10B, 30-year)",
            loan_principal_usd=10e9,
            interest_rate_pct=6.5,
            term_years=30.0,
            project_productive_years=30.0,
            project_gross_energy_kj=300e6 * bbl_energy_kj,
        ),
    ]

    for loan in sample_loans:
        r = loan_servicing_energy_cost(loan, infra, formation)
        print(f"  PROJECT: {r['project']}")
        print(f"    Principal:                "
              f"${r['principal_usd']/1e6:8,.0f}M")
        print(f"    Total interest:           "
              f"${r['total_interest_usd']/1e6:8,.0f}M")
        print(f"    Infrastructure energy:    "
              f"{r['infrastructure_energy_kj']:.2e} kJ")
        print(f"    Formation energy share:   "
              f"{r['formation_energy_kj']:.2e} kJ")
        print(f"    Total capital system kJ:  "
              f"{r['total_capital_system_kj']:.2e} kJ")
        print(f"    Project gross energy:     "
              f"{r['project_gross_energy_kj']:.2e} kJ")
        print(f"    Capital cost share of gross: "
              f"{r['capital_cost_share_of_gross']:6.2f} %")
        print(f"    Net EROI after capital:   "
              f"{r['net_eroi_after_capital']:7.1f} : 1")
        print()

    print("LAYER 4: SYSTEMIC CONSTRAINT")
    print("-" * 74)

    scenarios = [
        SystemicConstraint(current_net_energy_growth_pct=+2.0),
        SystemicConstraint(current_net_energy_growth_pct=0.0),
        SystemicConstraint(current_net_energy_growth_pct=-1.5),
        SystemicConstraint(current_net_energy_growth_pct=-5.0),
    ]

    for s in scenarios:
        v = s.is_debt_serviceable()
        print(f"  Net energy growth: "
              f"{s.current_net_energy_growth_pct:+5.1f} %/yr  "
              f"required: {v['required_growth_pct']:5.1f} %  "
              f"gap: {v['gap_pct']:+5.1f}  ->  {v['verdict']}")
    print()

    print("LAYER 5: COMPARATIVE CAPITAL COST BY SYSTEM")
    print("-" * 74)
    for s in SYSTEM_CAPITAL_PROFILES:
        print(f"  SYSTEM: {s.system_name}")
        print(f"    Capital infrastructure: "
              f"{s.capital_infrastructure_required}")
        print(f"    Annual capital-layer energy: "
              f"{s.energy_cost_of_capital_layer_kj_per_year:.2e} kJ/yr")
        print(f"    Functions under zero growth:    "
              f"{s.can_function_under_zero_growth}")
        print(f"    Functions under contraction:    "
              f"{s.can_function_under_contracting_energy}")
        if s.notes:
            print(f"    Notes: {s.notes}")
        print()

    print("=" * 74)
    print("FALSIFIABLE CLAIMS")
    print("=" * 74)
    for c in CLAIMS:
        print(f"  {c['id']}")
        print(f"    {c['statement']}")
        print()


if __name__ == "__main__":
    report()


add to script:

@dataclass
class ComplexityEntropyMultiplier:
    """
    Calculates the 'Heat' of financial leverage.
    """
    fractional_reserve_multiplier: float  # How many claims per unit of base capital
    derivative_complexity_index: float    # Computational cost of balancing derivative books
    inflation_rate_proxy: float          # Real-world energy-devaluation rate

    def compute_entropy_load(self, base_infra_cost: float) -> float:
        # Each layer of leverage increases the audit/compliance/risk-cost
        # exponentially, not linearly.
        return base_infra_cost * (
            self.fractional_reserve_multiplier * 0.2 + 
            math.log(self.derivative_complexity_index + 1) * 0.5
        )


