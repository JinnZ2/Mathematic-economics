"""
energy_cascade_audit.py
CC0 - Public Domain

Maps current energy market signals against thermodynamic constraint layers
to detect cascade failure modes hidden by financial-abstraction metrology.

Core hypothesis: oil price volatility reflects information-asymmetry games,
not physical supply-demand. Real cascade lives in EROI decline, refinery
utilization ceiling, infrastructure funding starvation, and demand
destruction masked as price relief.

Run: python3 energy_cascade_audit.py
Modify INPUTS block to test different scenarios.

See also (substrate-aware-accounting corpus):
  - substrate_damage_audit.py - population-level institutional damage
  - oil_extraction_thermodynamic_cascade_audit.py - ten cost vectors omitted from EROI
  - refinery_stress_cascade_module.py - 2025-2026 refinery incident data; cascade-failure cost vectors
  - shale_well_thermodynamic_reality_module.py - Arps decline curves; per-well EROI recalculation
  - eroi_real_time_audit.py - re-run published EROI against current-period prices and supply flags
  - banking_thermodynamic_audit.py - capital-layer overhead; growth-constraint check
  - energy_cascade_audit.py - May 2026 cross-layer cascade detection (price, EROI, refining, demand, trust)  (this module)
Corpus index: substrate_accounting/README.md  |  claims: substrate_accounting/CLAIMS_UNIFIED.json
"""

from dataclasses import dataclass, field
from typing import Callable


# ============================================================
# INPUTS - current observed signals (May 2026)
# Modify these to test different scenarios
# ============================================================

INPUTS = {
    # Price signals (observable, but corrupted)
    "brent_crude_usd_bbl": 101.0,           # oscillating 92-120
    "brent_volatility_pct_week": 15.0,      # weekly swing magnitude
    "price_narrative_reversals": 5,         # ceasefire announcements proven false

    # Physical supply (real constraint layer)
    "hormuz_loss_mbd": 13.0,                # million barrels/day lost
    "alt_route_capacity_mbd": 7.2,          # UAE/Saudi/Iraq workarounds
    "alt_route_compromised": True,          # UAE pipeline hit
    "global_supply_decline_mbd_2026": 1.0,  # IEA estimate

    # Refinery + reserves
    "us_refinery_utilization_pct": 95.0,    # near ceiling
    "us_refinery_count": 132,
    "us_refining_capacity_mbd": 18.0,
    "spr_drawdown_active": True,

    # Trade flows
    "us_petroleum_exports_mbd": 6.6,
    "us_net_petroleum_import_mbd": 7.0,     # still net importer of product

    # EROI metrology (the rotten foundation)
    "claimed_oil_eroi": 20.0,               # industry-cited
    "measured_oil_eroi": 6.0,               # physics-grounded estimate
    "shale_eroi": 4.5,                      # tight oil reality

    # Renewable layer
    "solar_storage_lcoe_usd_mwh": 68.0,     # IRENA 24/7 firm range midpoint
    "new_gas_lcoe_usd_mwh": 80.0,
    "new_coal_lcoe_usd_mwh": 100.0,
    "us_renewable_capacity_added_gw_2026": 55.0,
    "us_fossil_nuclear_added_gw_2026": 1.0,

    # Infrastructure funding
    "federal_fuel_tax_cents_gal": 18.4,
    "fuel_tax_suspended": True,
    "infrastructure_maintenance_backlog_billion": 1200.0,

    # Demand signals (hidden destruction)
    "global_crude_runs_decline_mbd": 1.0,   # refineries cutting runs
    "demand_destruction_signal": True,      # price drops despite supply loss

    # Institutional trust
    "media_narrative_failure_count": 5,
    "public_trust_decline_pct_yoy": 12.0,
}


# ============================================================
# CONSTRAINT LAYERS - thermodynamic + structural
# Each layer returns (status, confidence, evidence)
# ============================================================

@dataclass
class LayerResult:
    name: str
    status: str           # "stable" | "stressed" | "cascade" | "broken"
    confidence: float     # 0.0 to 1.0
    evidence: list = field(default_factory=list)
    derived: dict = field(default_factory=dict)


def layer_price_signal_integrity(d: dict) -> LayerResult:
    """Detects whether price reflects physical reality or information games."""
    physical_loss = d["hormuz_loss_mbd"] - (
        d["alt_route_capacity_mbd"] if not d["alt_route_compromised"]
        else d["alt_route_capacity_mbd"] * 0.4
    )
    expected_premium_pct = (physical_loss / 100.0) * 100  # rough heuristic
    actual_volatility = d["brent_volatility_pct_week"]

    signal_corruption = actual_volatility / max(expected_premium_pct, 1.0)
    narrative_failure_load = d["price_narrative_reversals"]

    evidence = [
        f"physical supply loss: {physical_loss:.1f} mbd",
        f"weekly price volatility: {actual_volatility:.1f}%",
        f"narrative reversals: {narrative_failure_load}",
        f"signal corruption ratio: {signal_corruption:.2f}",
    ]

    if signal_corruption > 3.0 and narrative_failure_load >= 3:
        return LayerResult("price_signal", "broken", 0.85, evidence,
                           {"corruption": signal_corruption})
    if signal_corruption > 1.5:
        return LayerResult("price_signal", "cascade", 0.7, evidence,
                           {"corruption": signal_corruption})
    return LayerResult("price_signal", "stressed", 0.6, evidence,
                       {"corruption": signal_corruption})


def layer_eroi_substrate(d: dict) -> LayerResult:
    """EROI mismatch between claimed and measured = metrology failure."""
    claimed = d["claimed_oil_eroi"]
    measured = d["measured_oil_eroi"]
    shale = d["shale_eroi"]
    gap = claimed / measured

    # Civilization-scale minimum EROI is debated 7-12 range
    civilization_floor = 10.0
    below_floor = measured < civilization_floor
    shale_below_floor = shale < civilization_floor

    evidence = [
        f"claimed EROI: {claimed:.1f} : 1",
        f"measured EROI: {measured:.1f} : 1",
        f"shale/tight EROI: {shale:.1f} : 1",
        f"metrology gap: {gap:.1f}x overstatement",
        f"civilization floor (~10:1) breached: {below_floor}",
    ]

    if below_floor and shale_below_floor:
        return LayerResult("eroi_substrate", "cascade", 0.8, evidence,
                           {"gap": gap, "floor_breach": True})
    if gap > 2.5:
        return LayerResult("eroi_substrate", "broken", 0.75, evidence,
                           {"gap": gap})
    return LayerResult("eroi_substrate", "stressed", 0.6, evidence, {"gap": gap})


def layer_refining_capacity(d: dict) -> LayerResult:
    """Refineries at 95% utilization = no shock absorber."""
    util = d["us_refinery_utilization_pct"]
    headroom = 100.0 - util
    global_runs_decline = d["global_crude_runs_decline_mbd"]

    evidence = [
        f"US refinery utilization: {util:.1f}%",
        f"available headroom: {headroom:.1f}%",
        f"global crude runs declining: {global_runs_decline:.1f} mbd",
    ]

    if util > 93 and global_runs_decline > 0:
        return LayerResult("refining_capacity", "cascade", 0.8, evidence,
                           {"headroom": headroom})
    if util > 90:
        return LayerResult("refining_capacity", "stressed", 0.7, evidence,
                           {"headroom": headroom})
    return LayerResult("refining_capacity", "stable", 0.6, evidence,
                       {"headroom": headroom})


def layer_demand_destruction(d: dict) -> LayerResult:
    """Price drops with supply loss = consumption breaking, not supply solved."""
    supply_loss = d["hormuz_loss_mbd"] - d["alt_route_capacity_mbd"]
    supply_loss_real = supply_loss > 3.0 or d["alt_route_compromised"]
    price_falling = d["demand_destruction_signal"]

    evidence = [
        f"net supply loss: {supply_loss:.1f} mbd",
        f"alt routes compromised: {d['alt_route_compromised']}",
        f"price declining despite loss: {price_falling}",
        "if true: demand destruction, not supply resolution",
    ]

    if supply_loss_real and price_falling:
        return LayerResult("demand_destruction", "cascade", 0.85, evidence,
                           {"hidden": True})
    if price_falling:
        return LayerResult("demand_destruction", "stressed", 0.6, evidence, {})
    return LayerResult("demand_destruction", "stable", 0.5, evidence, {})


def layer_infrastructure_funding(d: dict) -> LayerResult:
    """Tax suspension during price spike = future infrastructure debt."""
    tax = d["federal_fuel_tax_cents_gal"]
    suspended = d["fuel_tax_suspended"]
    backlog = d["infrastructure_maintenance_backlog_billion"]

    annual_us_gasoline_gal = 134_000_000_000  # ~134B gal/yr
    annual_revenue_loss_billion = (
        (tax / 100.0) * annual_us_gasoline_gal / 1e9 if suspended else 0
    )

    evidence = [
        f"federal fuel tax: {tax:.1f} cents/gal",
        f"currently suspended: {suspended}",
        f"annual revenue loss: ${annual_revenue_loss_billion:.1f}B/yr",
        f"existing maintenance backlog: ${backlog:.0f}B",
    ]

    if suspended and backlog > 1000:
        return LayerResult("infrastructure_funding", "cascade", 0.8, evidence,
                           {"revenue_loss_b": annual_revenue_loss_billion})
    if suspended:
        return LayerResult("infrastructure_funding", "stressed", 0.7, evidence, {})
    return LayerResult("infrastructure_funding", "stable", 0.6, evidence, {})


def layer_renewable_displacement(d: dict) -> LayerResult:
    """Renewable cost crossover + capacity additions = displacement underway."""
    solar = d["solar_storage_lcoe_usd_mwh"]
    gas = d["new_gas_lcoe_usd_mwh"]
    coal = d["new_coal_lcoe_usd_mwh"]
    renewable_add = d["us_renewable_capacity_added_gw_2026"]
    fossil_add = d["us_fossil_nuclear_added_gw_2026"]

    cost_advantage_vs_gas = (gas - solar) / gas * 100
    capacity_ratio = renewable_add / max(fossil_add, 0.1)

    evidence = [
        f"solar+storage LCOE: ${solar}/MWh",
        f"new gas LCOE: ${gas}/MWh ({cost_advantage_vs_gas:.0f}% renewable advantage)",
        f"new coal LCOE: ${coal}/MWh",
        f"2026 capacity additions: {renewable_add}GW renewable vs {fossil_add}GW fossil",
        f"capacity ratio: {capacity_ratio:.0f}:1 renewable",
    ]

    # Note: displacement does NOT mean replacement of liquid fuels for transport
    # This is electricity sector only
    if capacity_ratio > 20 and cost_advantage_vs_gas > 10:
        return LayerResult("renewable_displacement", "stable", 0.8, evidence,
                           {"electricity_only": True, "ratio": capacity_ratio})
    return LayerResult("renewable_displacement", "stressed", 0.6, evidence,
                       {"electricity_only": True})


def layer_institutional_trust(d: dict) -> LayerResult:
    """Trust collapse propagates faster than physical cascade."""
    failures = d["media_narrative_failure_count"]
    trust_decline = d["public_trust_decline_pct_yoy"]

    evidence = [
        f"narrative failures (ceasefire reversals): {failures}",
        f"public trust decline: {trust_decline:.1f}% YoY",
        "consequence: alternative info sources fill vacuum (good and bad)",
    ]

    if failures >= 4 and trust_decline > 10:
        return LayerResult("institutional_trust", "broken", 0.85, evidence,
                           {"propagation": "fast"})
    if failures >= 2:
        return LayerResult("institutional_trust", "cascade", 0.7, evidence, {})
    return LayerResult("institutional_trust", "stressed", 0.5, evidence, {})


# ============================================================
# CASCADE COUPLING - how layers reinforce each other
# ============================================================

def detect_cascade_coupling(results: list) -> dict:
    """Identify which layer failures amplify each other."""
    statuses = {r.name: r.status for r in results}
    couplings = []

    # Coupling 1: corrupted price signal + demand destruction = hidden physical reality
    if statuses.get("price_signal") in ("broken", "cascade") and \
       statuses.get("demand_destruction") == "cascade":
        couplings.append({
            "pair": ("price_signal", "demand_destruction"),
            "mechanism": "Price oscillation masks actual demand collapse. "
                         "Consumers can't see true scarcity until rationing arrives.",
            "severity": "high",
        })

    # Coupling 2: EROI decline + refining ceiling = no slack absorption
    if statuses.get("eroi_substrate") in ("cascade", "broken") and \
       statuses.get("refining_capacity") in ("cascade", "stressed"):
        couplings.append({
            "pair": ("eroi_substrate", "refining_capacity"),
            "mechanism": "Declining EROI means more energy spent extracting energy. "
                         "Refinery ceiling means no buffer for supply shocks. "
                         "Net energy to society contracts.",
            "severity": "high",
        })

    # Coupling 3: infrastructure funding cut + trust collapse = deferred breakdown
    if statuses.get("infrastructure_funding") in ("cascade", "stressed") and \
       statuses.get("institutional_trust") in ("broken", "cascade"):
        couplings.append({
            "pair": ("infrastructure_funding", "institutional_trust"),
            "mechanism": "Tax suspension buys short-term political calm at cost of "
                         "long-term decay. When roads/bridges fail, public won't "
                         "connect cause to original policy.",
            "severity": "medium",
        })

    # Coupling 4: renewable displacement is electricity-only, doesn't solve liquid fuel
    if statuses.get("renewable_displacement") == "stable":
        couplings.append({
            "pair": ("renewable_displacement", "liquid_fuel_gap"),
            "mechanism": "Solar/wind growth real but DOES NOT replace diesel for "
                         "trucks, ships, planes, ag equipment. Liquid fuel cascade "
                         "is not solved by electricity sector wins.",
            "severity": "structural_blind_spot",
        })

    return {"couplings": couplings, "count": len(couplings)}


# ============================================================
# FALSIFIABLE PREDICTIONS
# What we'd expect to see if this model is right
# ============================================================

PREDICTIONS = [
    {
        "claim": "Diesel prices will diverge upward from crude prices through 2026-2027",
        "mechanism": "Refinery ceiling + middle distillate demand from trucking/ag",
        "falsifier": "Diesel-crude spread narrows below $15/bbl for 6+ months",
    },
    {
        "claim": "Demand destruction will appear first in long-haul trucking and small ag",
        "mechanism": "Lowest EROI users with thinnest margins fail first",
        "falsifier": "Trucking fleet hours-of-service unchanged through Q4 2026",
    },
    {
        "claim": "Infrastructure failures (bridges, roads) will visibly accelerate 12-24 months "
                 "after fuel tax suspension",
        "mechanism": "Maintenance deferred during funding gap, decay compounds",
        "falsifier": "Federal Highway Administration condition metrics improve 2026-2028",
    },
    {
        "claim": "Public will increasingly distrust crude price as scarcity signal",
        "mechanism": "Repeated narrative-reversal cycles train pattern recognition",
        "falsifier": "Consumer sentiment surveys show rising trust in oil market data",
    },
    {
        "claim": "Renewable electricity additions will accelerate but NOT close liquid fuel gap",
        "mechanism": "Different energy carrier, different infrastructure, different physics",
        "falsifier": "Diesel demand drops faster than electricity demand growth 2026-2028",
    },
]


# ============================================================
# RUN PIPELINE
# ============================================================

def run_audit(inputs: dict) -> None:
    layers: list[Callable] = [
        layer_price_signal_integrity,
        layer_eroi_substrate,
        layer_refining_capacity,
        layer_demand_destruction,
        layer_infrastructure_funding,
        layer_renewable_displacement,
        layer_institutional_trust,
    ]

    print("=" * 60)
    print("ENERGY CASCADE AUDIT - May 2026 snapshot")
    print("=" * 60)

    results = []
    for layer_fn in layers:
        r = layer_fn(inputs)
        results.append(r)
        print(f"\n[{r.status.upper():>9}] {r.name}  (confidence: {r.confidence:.2f})")
        for e in r.evidence:
            print(f"    - {e}")

    print("\n" + "=" * 60)
    print("CASCADE COUPLING ANALYSIS")
    print("=" * 60)
    coupling = detect_cascade_coupling(results)
    for c in coupling["couplings"]:
        print(f"\n  {c['pair'][0]} <--> {c['pair'][1]}  [severity: {c['severity']}]")
        print(f"    {c['mechanism']}")

    print("\n" + "=" * 60)
    print("FALSIFIABLE PREDICTIONS")
    print("=" * 60)
    for i, p in enumerate(PREDICTIONS, 1):
        print(f"\n  {i}. {p['claim']}")
        print(f"     mechanism: {p['mechanism']}")
        print(f"     falsifier: {p['falsifier']}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    cascade_count = sum(1 for r in results if r.status in ("cascade", "broken"))
    print(f"  Layers in cascade/broken state: {cascade_count}/{len(results)}")
    print(f"  Cross-layer couplings detected: {coupling['count']}")
    print(f"  Critical blind spot: liquid fuel substitution gap")


if __name__ == "__main__":
    run_audit(INPUTS)
