"""
ai_capex_thermodynamic_audit.py -- CC0, stdlib only, mobile-runnable.

ECONOMIC MODEL AUDIT
What has to be true for 3-day AI model release cycles to close the math.

Contract: do not predict whether the cycle happens. Audit whether the
math closes under three converging forcings.

  CAPEX     debt service forces -> train faster (push release rate up)
  GRID      power envelope forces -> kill faster (push lifespan down)
  LOCKIN    integration cost forces -> stay locked in (customer
            accepts whatever cadence is imposed)

The three converge on a fixed cycle period. The audit computes what
that period actually is given user-supplied numbers, and reports which
of the three layers is the binding constraint -- the one driving the
cadence harder than the other two.

Methodology rule (carried from the other JinnZ2/* repos):
    if real numbers refute the closure, the closure is the thing that
    updates. never retune to make the verdict look tidy.

Layers in detail

CAPEX layer
    annual_recovery = capex / (amortization_months / 12) + opex_annual
    releases_required_per_year = annual_recovery / revenue_per_release
    cycle_days_capex = 365 / releases_required_per_year

  Closure condition (3-day): cycle_days_capex <= 3.0
  If 4 days, capex demands a slower cadence than the headline claims;
  the cycle is NOT thermodynamically required at 3 days. If 2 days,
  capex demands EVEN FASTER than 3.

GRID layer
    annual_train_draw = releases_per_year * energy_per_train_gwh
    grid_headroom_for_inference = grid_cap_annual - annual_train_draw
    max_simultaneous_models = headroom / energy_per_inference_per_year
    max_avg_lifespan_years = max_simultaneous_models / releases_per_year

  Closure condition (3-day): max_avg_lifespan_years * 365 >= 3.0
  Iff the grid can support keeping at least one model alive for 3 days
  on average at this release rate. If headroom is negative, grid CANNOT
  sustain inference at this rate at all -- the cycle isn't forced by
  the grid, the grid is the floor that the rest of the math broke.

LOCKIN layer
    vendor_capture_factor = releases_per_year / customer_swaps_per_year

  Closure condition (lockin works): vendor_capture_factor > 1.0
  When the vendor releases more often than the customer can integrate,
  the customer is captured by switching cost. Monetization is the
  lock-in, not the model.

The verdict reports which layer is BINDING -- the tightest of the
three constraints. If all three close at the same cycle period, the
"thermodynamically required" claim holds. If one is much tighter, it
is doing the actual forcing and the others are slack.
"""

from dataclasses import dataclass, asdict
from typing import Optional


# ----------------------------------------------------------------------
# 1. INPUTS  (all falsifiable; tune against real industry numbers)
# ----------------------------------------------------------------------

@dataclass
class ClosureInputs:
    # CAPEX layer
    capex_b: float = 25.0                    # $B factory CAPEX
    amortization_months: float = 24.0        # debt service window (18-24mo standard)
    opex_b_annual: float = 0.0               # $B annual operations
    revenue_per_release_m: float = 100.0     # $M per release (licensing + inference)

    # GRID layer
    energy_per_train_gwh: float = 250.0           # per major release training
    energy_per_inference_gwh_per_year: float = 2.0  # continuous draw per live model
    grid_cap_gwh_annual: float = 50_000.0    # 50 TWh -- large but real datacenter envelope

    # LOCKIN layer
    integration_cost_m: float = 10.0         # $M per customer per model swap
    customer_swaps_per_year: float = 10.0    # integrations a customer can absorb / year

    # closure target
    target_cycle_days: float = 3.0


# ----------------------------------------------------------------------
# 2. PER-LAYER VERDICT
# ----------------------------------------------------------------------

@dataclass
class LayerVerdict:
    name: str
    closes_at_target: bool
    cycle_days_implied: float       # the cadence this layer compels
    binding_factor: float           # cycle_days_implied / target. <1 = binds tighter
    note: str


# ----------------------------------------------------------------------
# 3. FINAL VERDICT
# ----------------------------------------------------------------------

@dataclass
class ClosureVerdict:
    capex: LayerVerdict
    grid: LayerVerdict
    lockin: LayerVerdict
    all_close: bool
    binding_layer: str
    releases_required_per_year: float
    annual_recovery_b: float
    annual_train_draw_gwh: float
    grid_headroom_gwh: float
    max_simultaneous_models: float
    max_avg_lifespan_days: float
    vendor_capture_factor: float
    summary: str


# ----------------------------------------------------------------------
# 4. AUDIT
# ----------------------------------------------------------------------

def audit(I: ClosureInputs) -> ClosureVerdict:
    # ---- CAPEX ----
    years_window = I.amortization_months / 12.0
    annual_recovery_b = I.capex_b / years_window + I.opex_b_annual
    rev_per_release_b = I.revenue_per_release_m / 1_000.0
    R_year = annual_recovery_b / rev_per_release_b if rev_per_release_b > 0 else float("inf")
    cycle_capex_days = 365.0 / R_year if R_year > 0 else float("inf")
    capex_closes = cycle_capex_days <= I.target_cycle_days
    capex = LayerVerdict(
        name="CAPEX",
        closes_at_target=capex_closes,
        cycle_days_implied=cycle_capex_days,
        binding_factor=cycle_capex_days / I.target_cycle_days,
        note=(f"annual_recovery=${annual_recovery_b:.2f}B requires "
              f"{R_year:.1f} releases/year @ ${I.revenue_per_release_m:.0f}M each "
              f"-> cycle {cycle_capex_days:.2f}d"),
    )

    # ---- GRID ----
    annual_train_draw = R_year * I.energy_per_train_gwh
    headroom = I.grid_cap_gwh_annual - annual_train_draw
    if I.energy_per_inference_gwh_per_year > 0 and headroom > 0:
        N_max = headroom / I.energy_per_inference_gwh_per_year
        L_max_years = N_max / R_year if R_year > 0 else float("inf")
    else:
        N_max = 0.0
        L_max_years = 0.0
    L_max_days = L_max_years * 365.0
    grid_closes = L_max_days >= I.target_cycle_days
    grid_note = (
        f"train_draw {annual_train_draw:.0f} GWh/yr vs grid_cap "
        f"{I.grid_cap_gwh_annual:.0f}; headroom {headroom:+.0f} GWh; "
        f"max_simul_models {N_max:.1f}; max_lifespan {L_max_days:.2f}d"
        if headroom > 0 else
        f"NEGATIVE HEADROOM {headroom:+.0f} GWh: grid cannot sustain "
        f"{R_year:.1f} releases/year at {I.energy_per_train_gwh:.0f} GWh per train"
    )
    grid = LayerVerdict(
        name="GRID",
        closes_at_target=grid_closes,
        cycle_days_implied=L_max_days,
        binding_factor=L_max_days / I.target_cycle_days if I.target_cycle_days else 0.0,
        note=grid_note,
    )

    # ---- LOCKIN ----
    vendor_capture = R_year / I.customer_swaps_per_year if I.customer_swaps_per_year > 0 else float("inf")
    customer_cycle_days = 365.0 / I.customer_swaps_per_year if I.customer_swaps_per_year > 0 else float("inf")
    lockin_closes = vendor_capture > 1.0 and cycle_capex_days <= customer_cycle_days
    lockin = LayerVerdict(
        name="LOCKIN",
        closes_at_target=lockin_closes,
        cycle_days_implied=customer_cycle_days,
        binding_factor=customer_cycle_days / I.target_cycle_days,
        note=(f"customer absorbs {I.customer_swaps_per_year:.1f} swaps/yr "
              f"(cycle {customer_cycle_days:.1f}d) vs vendor {R_year:.1f}/yr "
              f"-> capture factor {vendor_capture:.1f}x"),
    )

    # ---- BINDING LAYER ----
    layers = [capex, grid, lockin]
    binding = min(layers, key=lambda L: L.cycle_days_implied
                  if L.cycle_days_implied >= 0 else float("inf"))
    all_close = all(L.closes_at_target for L in layers)

    if all_close:
        summary = (f"All three layers close at <= {I.target_cycle_days:.1f}d. "
                   f"Binding constraint: {binding.name} at {binding.cycle_days_implied:.2f}d. "
                   f"Cycle thermodynamically required, not chosen.")
    else:
        failed = [L.name for L in layers if not L.closes_at_target]
        summary = (f"Closure FAILS at target {I.target_cycle_days:.1f}d. "
                   f"Failing layer(s): {failed}. "
                   f"Binding (tightest demand): {binding.name} "
                   f"@ {binding.cycle_days_implied:.2f}d.")

    return ClosureVerdict(
        capex=capex, grid=grid, lockin=lockin,
        all_close=all_close, binding_layer=binding.name,
        releases_required_per_year=R_year,
        annual_recovery_b=annual_recovery_b,
        annual_train_draw_gwh=annual_train_draw,
        grid_headroom_gwh=headroom,
        max_simultaneous_models=N_max,
        max_avg_lifespan_days=L_max_days,
        vendor_capture_factor=vendor_capture,
        summary=summary,
    )


# ----------------------------------------------------------------------
# 5. SMOKE
# ----------------------------------------------------------------------

def _show(tag: str, v: ClosureVerdict) -> None:
    print(f"\n== {tag} ==")
    print(f"  releases/year required: {v.releases_required_per_year:.1f}")
    print(f"  annual recovery:        ${v.annual_recovery_b:.2f}B")
    print(f"  CAPEX  : {v.capex.note}")
    print(f"           closes at target? {v.capex.closes_at_target}")
    print(f"  GRID   : {v.grid.note}")
    print(f"           closes at target? {v.grid.closes_at_target}")
    print(f"  LOCKIN : {v.lockin.note}")
    print(f"           closes at target? {v.lockin.closes_at_target}")
    print(f"  ----")
    print(f"  binding constraint: {v.binding_layer}")
    print(f"  {v.summary}")


if __name__ == "__main__":
    # Headline example: $25B CAPEX, $100M per release.
    # Run twice to expose how amortization window shifts the verdict.
    _show("24-month amortization (headline 125/yr case)",
          audit(ClosureInputs(capex_b=25.0, amortization_months=24.0,
                              revenue_per_release_m=100.0)))
    _show("18-month amortization (tighter window)",
          audit(ClosureInputs(capex_b=25.0, amortization_months=18.0,
                              revenue_per_release_m=100.0)))
    # Sensitivity: triple revenue per release -- does CAPEX layer still bind at 3d?
    _show("18-month, $300M per release (revenue offsets cadence)",
          audit(ClosureInputs(capex_b=25.0, amortization_months=18.0,
                              revenue_per_release_m=300.0)))
