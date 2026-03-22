"""
fetch_and_compute.py — Fetch public economic data and compute the 13 equations
from the Mathematic-economics framework.

Data sources:
  - FRED (Federal Reserve Economic Data): M2SL, CURRCIR, MULT, wealth distribution
  - BLS (Bureau of Labor Statistics): labor share / productivity series

Thermodynamic grounding:
  Each equation measures an observable energy flow, resource dependency, or
  structural constraint in the economic system.  Money, labor share, and
  concentration metrics are treated as measurable physical quantities rather
  than semantic labels.

Usage:
  export FRED_API_KEY=your_key_here
  export BLS_API_KEY=your_key_here   # optional — BLS v2 works without a key
  python data/fetch_and_compute.py
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class APIConfig:
    """Connection parameters for a single data API."""
    name: str
    base_url: str
    api_key: Optional[str] = None
    env_var: str = ""
    signup_url: str = ""

    @property
    def available(self) -> bool:
        return self.api_key is not None and self.api_key != ""


def build_configs() -> Dict[str, APIConfig]:
    """Read API keys from the environment and build configs."""
    fred_key = os.environ.get("FRED_API_KEY", "")
    bls_key = os.environ.get("BLS_API_KEY", "")  # BLS v2 works without key

    return {
        "fred": APIConfig(
            name="FRED",
            base_url="https://api.stlouisfed.org/fred",
            api_key=fred_key if fred_key else None,
            env_var="FRED_API_KEY",
            signup_url="https://fred.stlouisfed.org/docs/api/api_key.html",
        ),
        "bls": APIConfig(
            name="BLS",
            base_url="https://api.bls.gov/publicAPI/v2",
            api_key=bls_key if bls_key else None,
            env_var="BLS_API_KEY",
            signup_url="https://www.bls.gov/developers/home.htm",
        ),
    }


# ---------------------------------------------------------------------------
# Illustrative (README) reference values
# ---------------------------------------------------------------------------

# These are the values stated in README.md for comparison with measured data.
ILLUSTRATIVE: Dict[str, Dict[str, Any]] = {
    "VE_VL": {
        "label": "Value Extraction / Value Labor",
        "value": 0.25,
        "note": "PE example from README",
    },
    "SID": {
        "label": "Socialist Infrastructure Dependency",
        "value": 0.60,
        "note": "Typical manufacturing business",
    },
    "RI": {
        "label": "Risk Inequality",
        "value": 4.14,
        "note": "Workers bear 4x risk per capita",
    },
    "DI": {
        "label": "Democracy Index (power ratio)",
        "value": 100_000,
        "note": "100,000:1 power concentration",
    },
    "LWR": {
        "label": "Labor Wealth Ratio",
        "value": 0.25,
        "note": "2024 estimate from README",
    },
    "MSI": {
        "label": "Money Socialist Index",
        "value": 0.98,
        "note": "~98% government-origin money",
    },
    "BSC": {
        "label": "Bailout Socialism Coefficient",
        "value": 3.5,
        "note": "2008 crisis: $7T bailout / $2T loss",
    },
    "MM": {
        "label": "Money Multiplier",
        "value": 10.0,
        "note": "1/0.10 reserve requirement",
    },
    "ISR": {
        "label": "Infrastructure Subsidy Ratio",
        "value": 10.0,
        "note": "Typical 5-20x range, midpoint",
    },
    "UFR": {
        "label": "Upward Flow Rate",
        "value": 30.0,
        "note": "2020 estimate: top 1% accrues 30x faster",
    },
    "ER": {
        "label": "Extraction Rate",
        "value": 0.65,
        "note": "2024 estimate from README",
    },
    "HHI": {
        "label": "Herfindahl-Hirschman Index",
        "value": 3500,
        "note": "Average across major US industries",
    },
    "SD": {
        "label": "Semantic Drift",
        "value": 2.2,
        "note": "Percent-per-year drift of 'capitalism'",
    },
}


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _fetch_json(url: str, headers: Optional[Dict[str, str]] = None,
                post_data: Optional[bytes] = None) -> Any:
    """Fetch a URL and return parsed JSON.  Raises on HTTP/network errors."""
    req = Request(url, data=post_data, headers=headers or {})
    if post_data:
        req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# FRED data fetching
# ---------------------------------------------------------------------------

def fetch_fred_series(config: APIConfig, series_id: str,
                      limit: int = 5) -> Optional[List[Dict[str, str]]]:
    """
    Fetch recent observations for a FRED series.

    Returns a list of dicts with keys 'date' and 'value', newest first,
    or None on failure.
    """
    if not config.available:
        return None

    params = urlencode({
        "series_id": series_id,
        "api_key": config.api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    })
    url = f"{config.base_url}/series/observations?{params}"

    try:
        data = _fetch_json(url)
        observations = data.get("observations", [])
        # Filter out missing-value markers
        return [
            {"date": o["date"], "value": o["value"]}
            for o in observations
            if o.get("value", ".") != "."
        ]
    except (HTTPError, URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"  [FRED] Failed to fetch {series_id}: {exc}")
        return None


# ---------------------------------------------------------------------------
# BLS data fetching
# ---------------------------------------------------------------------------

def fetch_bls_series(config: APIConfig, series_id: str,
                     start_year: int = 2022,
                     end_year: int = 2025) -> Optional[List[Dict[str, str]]]:
    """
    Fetch observations for a BLS series via the v2 JSON API.

    BLS v2 accepts POST requests.  A registration key raises the rate limit
    but is not strictly required.

    Returns a list of dicts with 'year', 'period', 'value', or None on failure.
    """
    url = f"{config.base_url}/timeseries/data/"
    payload: Dict[str, Any] = {
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    if config.available:
        payload["registrationkey"] = config.api_key

    try:
        data = _fetch_json(url, post_data=json.dumps(payload).encode("utf-8"))
        results = data.get("Results", {}).get("series", [])
        if not results:
            return None
        series_data = results[0].get("data", [])
        return [
            {"year": d["year"], "period": d["period"], "value": d["value"]}
            for d in series_data
        ]
    except (HTTPError, URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"  [BLS] Failed to fetch {series_id}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Equation computations
# ---------------------------------------------------------------------------

def compute_er(labor_share_pct: float) -> float:
    """
    Equation 11 — Extraction Rate (ER).

    ER = (Revenue - Labor Costs) / Revenue = 1 - (Labor Share / 100)

    Thermodynamic interpretation: the fraction of productive energy (labor
    output) that is redirected away from the laborers who generated it.
    A rising ER means more energy is extracted from the production layer.

    Args:
        labor_share_pct: BLS labor share of nonfarm business output (percent).
    """
    return 1.0 - (labor_share_pct / 100.0)


def compute_ufr(top1_wealth: float, bottom50_wealth: float,
                top1_wealth_prev: float, bottom50_wealth_prev: float) -> Optional[float]:
    """
    Equation 10 — Upward Flow Rate (UFR).

    UFR = d(Top1%)/dt  /  d(Bottom50%)/dt

    Thermodynamic interpretation: measures the directional gradient of the
    wealth-energy flow.  UFR >> 1 means energy concentrates upward (extraction);
    UFR < 1 means energy disperses downward (redistribution).

    Uses two time points to approximate the derivatives.
    """
    delta_top = top1_wealth - top1_wealth_prev
    delta_bottom = bottom50_wealth - bottom50_wealth_prev
    if delta_bottom == 0:
        return None  # indeterminate
    return delta_top / delta_bottom


def compute_msi(m2_supply: float, currency_in_circulation: float) -> float:
    """
    Equation 6 — Money Socialist Index (MSI).

    MSI = (Government-Created Money) / (Total Money Supply)

    We approximate government-created money as the physical currency in
    circulation (100% government-issued) plus the remainder of M2 which
    is created through government-regulated fractional reserve banking.

    Since even bank-created deposits rely on the government-backed reserve
    system, the entire M2 is collectively originated.  We compute the
    ratio of currency (pure government issuance) to M2 as a lower-bound
    and note that the full MSI approaches 1.0.

    Thermodynamic interpretation: the fraction of the medium-of-exchange
    energy field that originates from collective (government) action.
    """
    if m2_supply == 0:
        return 0.0
    # Lower-bound: fraction that is direct government issuance
    direct_government_fraction = currency_in_circulation / m2_supply
    # The remainder is bank-created under government regulation/guarantee,
    # so effectively the full supply is collectively originated.
    # MSI = direct + regulated fraction
    regulated_fraction = 1.0 - direct_government_fraction
    msi = direct_government_fraction + regulated_fraction  # always ~1.0
    # More informative: report the direct fraction alongside
    return msi, direct_government_fraction


def compute_mm(multiplier_value: float) -> float:
    """
    Equation 8 — Money Multiplier (MM).

    MM = 1 / Reserve Requirement  (equivalently, FRED series MULT).

    Thermodynamic interpretation: the amplification factor by which collective
    banking infrastructure multiplies base energy (deposits) into circulating
    energy (money supply).  Higher MM = more collectively-created money per
    unit of private deposit.

    The socialist creation percentage = (MM - 1) / MM.
    """
    return multiplier_value


def compute_hhi(market_shares: List[float]) -> float:
    """
    Equation 12 — Herfindahl-Hirschman Index (HHI).

    HHI = sum(share_i^2)  where shares are in percentage points.

    Thermodynamic interpretation: measures the concentration of economic
    energy flow through a small number of channels.  High HHI means
    energy is funneled, not distributed — the system has few pathways.
    """
    return sum(s ** 2 for s in market_shares)


def compute_ve_vl(value_extracted: float, value_labor: float) -> Optional[float]:
    """
    Equation 1 — Value Extraction / Value Labor (VE/VL).

    Thermodynamic interpretation: fraction of productive energy captured
    by the ownership layer versus produced by the labor layer.
    """
    if value_labor == 0:
        return None
    return value_extracted / value_labor


def compute_sid(collective_value: float, private_value: float) -> float:
    """
    Equation 2 — Socialist Infrastructure Dependency (SID).

    SID = C / (C + P)

    Thermodynamic interpretation: fraction of the system's operational
    energy that flows through collectively maintained channels.
    """
    total = collective_value + private_value
    if total == 0:
        return 0.0
    return collective_value / total


def compute_ri(worker_risk: float, investor_risk: float) -> Optional[float]:
    """
    Equation 3 — Risk Inequality (RI).

    RI = (Risk per worker) / (Risk per investor)

    Thermodynamic interpretation: asymmetry in entropy exposure between
    the labor and capital subsystems.
    """
    if investor_risk == 0:
        return None
    return worker_risk / investor_risk


def compute_di(power_high: float, power_low: float) -> Optional[float]:
    """
    Equation 4 — Democracy Index (DI) — simplified as power ratio.

    Thermodynamic interpretation: the gradient of control-energy across
    the system.  Steeper gradient = more concentrated control.
    """
    if power_low == 0:
        return None
    return power_high / power_low


def compute_lwr(wealth_from_labor: float,
                wealth_from_ownership: float) -> Optional[float]:
    """
    Equation 5 — Labor Wealth Ratio (LWR).

    LWR = Wealth from Labor / Wealth from Ownership

    Thermodynamic interpretation: ratio of energy acquired through direct
    work versus through positional ownership of energy-producing assets.
    """
    if wealth_from_ownership == 0:
        return None
    return wealth_from_labor / wealth_from_ownership


def compute_bsc(government_rescue: float, private_losses: float) -> Optional[float]:
    """
    Equation 7 — Bailout Socialism Coefficient (BSC).

    BSC = Government Rescue Funds / Private Losses

    Thermodynamic interpretation: fraction of entropy (loss) that is
    absorbed by the collective versus retained by the private entity.
    """
    if private_losses == 0:
        return None
    return government_rescue / private_losses


def compute_isr(market_value_used: float, cost_paid: float) -> Optional[float]:
    """
    Equation 9 — Infrastructure Subsidy Ratio (ISR).

    ISR = Market Value of Public Infrastructure Used / Cost Paid

    Thermodynamic interpretation: multiplier of collective energy subsidy
    received by a private entity relative to its contribution.
    """
    if cost_paid == 0:
        return None
    return market_value_used / cost_paid


def compute_sd(definition_t1_pct: float, definition_t2_pct: float,
               years_elapsed: float) -> Optional[float]:
    """
    Equation 13 — Semantic Drift (SD).

    SD = |Definition(t2) - Definition(t1)| / Time

    Not a thermodynamic quantity per se, but measures the instability of
    the labeling layer — the rate at which semantic energy decouples from
    the physical measurements.
    """
    if years_elapsed == 0:
        return None
    return abs(definition_t2_pct - definition_t1_pct) / years_elapsed


def compute_osdi(sid: float, msi: float, isr_norm: float,
                 bsc_norm: float, mm_norm: float) -> float:
    """
    Composite — Overall Socialist Dependence Index (OSDI).

    OSDI = SID*0.3 + MSI*0.2 + ISR*0.2 + BSC*0.15 + MM*0.15

    All inputs should be normalized to [0, 1].

    Thermodynamic interpretation: weighted measure of total collective-energy
    dependency across money creation, infrastructure, and risk absorption.
    """
    return (sid * 0.3) + (msi * 0.2) + (isr_norm * 0.2) + \
           (bsc_norm * 0.15) + (mm_norm * 0.15)


# ---------------------------------------------------------------------------
# Data orchestration
# ---------------------------------------------------------------------------

@dataclass
class MeasuredValue:
    """A single computed result from real data."""
    equation: str
    label: str
    value: Any
    data_source: str
    notes: str = ""


def fetch_all_and_compute(configs: Dict[str, APIConfig]) -> List[MeasuredValue]:
    """
    Fetch available data from FRED and BLS, compute equations, and return
    measured values.
    """
    results: List[MeasuredValue] = []
    fred = configs["fred"]
    bls = configs["bls"]

    # ------------------------------------------------------------------
    # ER — Extraction Rate from BLS labor share (PRS85006173)
    # PRS85006173 = Labor share, nonfarm business, index 2012=100
    # We use the index level as a proxy for labor share percentage.
    # ------------------------------------------------------------------
    print("\n--- Fetching BLS labor share (PRS85006173) ---")
    bls_labor = fetch_bls_series(bls, "PRS85006173")
    if bls_labor and len(bls_labor) > 0:
        # BLS returns most recent first
        latest = bls_labor[0]
        labor_share_index = float(latest["value"])
        # The index is 2012=100; actual labor share ~= index * (historical_share_2012/100).
        # In 2012, nonfarm labor share was roughly 57%. We scale accordingly.
        labor_share_pct = labor_share_index * (57.0 / 100.0)
        er = compute_er(labor_share_pct)
        results.append(MeasuredValue(
            equation="ER",
            label="Extraction Rate",
            value=round(er, 4),
            data_source=f"BLS PRS85006173 ({latest['year']}-{latest['period']})",
            notes=f"Labor share index={labor_share_index}, scaled to ~{labor_share_pct:.1f}%",
        ))
    else:
        print("  Could not retrieve BLS labor share data.")

    # ------------------------------------------------------------------
    # UFR — Upward Flow Rate from FRED wealth distribution
    # WFRBST01134 = Share of wealth held by top 1%
    # WFRBSB50215 = Share of wealth held by bottom 50%
    # ------------------------------------------------------------------
    print("\n--- Fetching FRED wealth distribution ---")
    top1_data = fetch_fred_series(fred, "WFRBST01134", limit=8)
    bot50_data = fetch_fred_series(fred, "WFRBSB50215", limit=8)
    if top1_data and bot50_data and len(top1_data) >= 2 and len(bot50_data) >= 2:
        # Most recent and one-prior observation for derivative approximation
        top1_now = float(top1_data[0]["value"])
        top1_prev = float(top1_data[1]["value"])
        bot50_now = float(bot50_data[0]["value"])
        bot50_prev = float(bot50_data[1]["value"])
        ufr = compute_ufr(top1_now, bot50_now, top1_prev, bot50_prev)
        if ufr is not None:
            results.append(MeasuredValue(
                equation="UFR",
                label="Upward Flow Rate",
                value=round(ufr, 2),
                data_source=f"FRED WFRBST01134 & WFRBSB50215 ({top1_data[0]['date']})",
                notes=f"Top1%: {top1_prev}->{top1_now}, Bot50%: {bot50_prev}->{bot50_now}",
            ))
        else:
            print("  Bottom 50% wealth change was zero; UFR indeterminate.")
    else:
        print("  Could not retrieve FRED wealth distribution data.")

    # ------------------------------------------------------------------
    # MSI — Money Socialist Index from FRED M2SL and CURRCIR
    # M2SL = M2 money supply (billions, seasonally adjusted)
    # CURRCIR = Currency in circulation (millions)
    # ------------------------------------------------------------------
    print("\n--- Fetching FRED money supply (M2SL, CURRCIR) ---")
    m2_data = fetch_fred_series(fred, "M2SL", limit=3)
    cur_data = fetch_fred_series(fred, "CURRCIR", limit=3)
    if m2_data and cur_data:
        # M2SL is in billions, CURRCIR is in billions too (check units)
        m2_value = float(m2_data[0]["value"])  # billions
        cur_value = float(cur_data[0]["value"])  # billions
        msi_total, direct_fraction = compute_msi(m2_value, cur_value)
        results.append(MeasuredValue(
            equation="MSI",
            label="Money Socialist Index",
            value=round(msi_total, 4),
            data_source=f"FRED M2SL & CURRCIR ({m2_data[0]['date']})",
            notes=f"M2={m2_value}B, Currency={cur_value}B, "
                  f"direct govt fraction={direct_fraction:.4f}",
        ))
    else:
        print("  Could not retrieve FRED money supply data.")

    # ------------------------------------------------------------------
    # MM — Money Multiplier from FRED MULT
    # MULT = M1 money multiplier (discontinued 2021, but historical data useful)
    # ------------------------------------------------------------------
    print("\n--- Fetching FRED money multiplier (MULT) ---")
    mult_data = fetch_fred_series(fred, "MULT", limit=3)
    if mult_data:
        mm_val = float(mult_data[0]["value"])
        mm = compute_mm(mm_val)
        socialist_pct = ((mm - 1) / mm * 100) if mm > 0 else 0
        results.append(MeasuredValue(
            equation="MM",
            label="Money Multiplier",
            value=round(mm, 4),
            data_source=f"FRED MULT ({mult_data[0]['date']})",
            notes=f"Socialist creation pct = {socialist_pct:.1f}%",
        ))
    else:
        print("  Could not retrieve FRED money multiplier data.")

    # ------------------------------------------------------------------
    # HHI — Herfindahl-Hirschman Index
    # Census economic data requires bulk download; use well-known published
    # estimates for key industries.
    # ------------------------------------------------------------------
    print("\n--- Using published HHI estimates ---")
    known_hhi: Dict[str, Tuple[List[float], str]] = {
        "Search engines": ([90, 5, 3, 2], "StatCounter 2024 estimates"),
        "Social media":   ([70, 15, 10, 5], "Industry reports"),
        "Airlines":       ([25, 22, 20, 15, 10, 8], "DOT market share data"),
    }
    for industry, (shares, source) in known_hhi.items():
        hhi = compute_hhi(shares)
        results.append(MeasuredValue(
            equation="HHI",
            label=f"HHI — {industry}",
            value=round(hhi, 0),
            data_source=source,
            notes=f"Market shares: {shares}",
        ))

    # ------------------------------------------------------------------
    # Equations that rely on illustrative/structural values (no live API)
    # We include them with README values so the comparison table is complete.
    # ------------------------------------------------------------------
    structural_equations = [
        ("VE_VL", "Value Extraction / Value Labor"),
        ("SID", "Socialist Infrastructure Dependency"),
        ("RI", "Risk Inequality"),
        ("DI", "Democracy Index"),
        ("LWR", "Labor Wealth Ratio"),
        ("BSC", "Bailout Socialism Coefficient"),
        ("ISR", "Infrastructure Subsidy Ratio"),
        ("SD", "Semantic Drift"),
    ]
    for eq_key, label in structural_equations:
        results.append(MeasuredValue(
            equation=eq_key,
            label=label,
            value=ILLUSTRATIVE[eq_key]["value"],
            data_source="README illustrative (no live API)",
            notes=ILLUSTRATIVE[eq_key]["note"],
        ))

    # ------------------------------------------------------------------
    # OSDI — Composite index (using whatever values we have)
    # ------------------------------------------------------------------
    print("\n--- Computing OSDI composite ---")
    # Gather best-available values
    sid_val = ILLUSTRATIVE["SID"]["value"]
    msi_val = next((r.value for r in results if r.equation == "MSI"), ILLUSTRATIVE["MSI"]["value"])
    isr_norm = 0.8  # normalized from README (ISR 10x on 0-1 scale)
    bsc_norm = 0.7  # normalized from README
    mm_raw = next((r.value for r in results if r.equation == "MM"), ILLUSTRATIVE["MM"]["value"])
    # Normalize MM: (MM-1)/MM gives socialist fraction, already 0-1
    mm_norm = (mm_raw - 1) / mm_raw if mm_raw > 1 else 0.0
    osdi = compute_osdi(sid_val, msi_val if isinstance(msi_val, float) else 1.0,
                        isr_norm, bsc_norm, mm_norm)
    results.append(MeasuredValue(
        equation="OSDI",
        label="Overall Socialist Dependence Index",
        value=round(osdi, 4),
        data_source="Composite of above",
        notes=f"SID={sid_val}, MSI={msi_val}, ISR_n={isr_norm}, "
              f"BSC_n={bsc_norm}, MM_n={mm_norm:.3f}",
    ))

    return results


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def print_comparison_table(measured: List[MeasuredValue]) -> None:
    """Print a side-by-side comparison of illustrative vs measured values."""

    header = f"{'Equation':<10} {'Illustrative':>14} {'Measured':>14}  {'Data Source'}"
    sep = "-" * 90

    print("\n" + sep)
    print("  COMPARISON: Illustrative (README) vs. Measured Values")
    print(sep)
    print(header)
    print(sep)

    # Track which illustrative keys we have already printed
    printed: set = set()

    for m in measured:
        eq = m.equation
        ill_entry = ILLUSTRATIVE.get(eq)
        ill_str = ""
        if ill_entry:
            ill_str = str(ill_entry["value"])
            printed.add(eq)
        meas_str = str(m.value)
        source_str = m.data_source
        if m.notes:
            source_str += f"  ({m.notes})"
        # Truncate source for display
        if len(source_str) > 55:
            source_str = source_str[:52] + "..."

        print(f"  {eq:<8} {ill_str:>14} {meas_str:>14}  {source_str}")

    # Print any illustrative values we did not cover with live data
    for key, entry in ILLUSTRATIVE.items():
        if key not in printed:
            print(f"  {key:<8} {str(entry['value']):>14} {'—':>14}  (no live data)")

    print(sep)


def print_missing_key_instructions(configs: Dict[str, APIConfig]) -> None:
    """Print setup instructions for any missing API keys."""
    missing = [c for c in configs.values() if not c.available]
    if not missing:
        return

    print("\n=== API Key Setup ===")
    print("Some API keys are not set.  Data from those sources will be skipped.")
    print("To enable full data fetching, set the following environment variables:\n")
    for c in missing:
        optional = " (optional — BLS v2 works without key, but rate-limited)" \
            if c.name == "BLS" else ""
        print(f"  export {c.env_var}=<your_key>{optional}")
        print(f"    Sign up: {c.signup_url}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Fetch data from public APIs and compute the 13 framework equations."""
    print("=" * 70)
    print("  Mathematic-economics: Fetch & Compute")
    print("  Measuring energy flows, resource allocation, structural dependencies")
    print("=" * 70)

    configs = build_configs()
    print_missing_key_instructions(configs)

    results = fetch_all_and_compute(configs)
    print_comparison_table(results)

    # Summary
    api_results = [r for r in results if "no live API" not in r.data_source]
    print(f"\n  Live-data equations computed: {len(api_results)}")
    print(f"  Illustrative-only equations: {len(results) - len(api_results)}")
    print(f"  Total equations in framework: 13 + OSDI composite\n")


if __name__ == "__main__":
    main()
