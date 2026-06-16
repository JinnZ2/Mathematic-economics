# AI capex thermodynamic closure

Companion to `audit/ai_capex_thermodynamic_audit.py`. The prose lays
out the three converging constraints; the audit module computes the
closure on user-supplied numbers and reports which layer is actually
binding. The structural finding from running the audit on the
headline numbers is in the last section -- and it is sharper than
this essay was reaching for.

License: CC0-1.0.

---

## Economic model audit

What has to be true for 3-day AI model release cycles to close the
math. Three constraint layers converge:

```
CAPEX LAYER
  Quantum Factory cost:           $X billion
  Amortization window:            18-24 months (standard)
  Annual recovery required:       $X / 1.5  to  $X / 2

CHURN RATE REQUIREMENT
  Revenue per model release:      licensing + inference fees
                                  must cover: (capex/amortization) + opex

  Models needed annually:         $annual_recovery / $revenue_per_model

  At $25B capex, 24-month window, $100M per release:
    -> need 125 releases/year
    -> that's 2.4 models/week
    -> training cycle must support that
    -> 3-day training BARELY supports it (with overlap)

POWER CONSTRAINT (the binding limit -- claimed)
  Energy per model train:         ~100-500 GWh per major release
  Energy per model inference:     continuous draw (stacks linearly)

  If 125 models/year running simultaneously:
    total inference load = 125 * baseline load
    = unsustainable unless models die

  Therefore: model lifespan <= time to train next generation
    (or power grid collapses)

CUSTOMER LOCK-IN REQUIREMENT
  Integration cost per model swap: $millions + months of labor

  If churn rate > customer integration capacity:
    customer can't leave (switching cost exceeds staying cost)
    -> vendor capture achieved
    -> revenue becomes stable despite churn

  This is the actual monetization.
  Not the model. The lock-in.

THE CLAIMED CLOSURE
  Capex debt service forces:  train faster
  Power grid forces:          kill faster
  Customer physics forces:    stay locked in

  = three-day cycle is thermodynamically required
    not strategically chosen
```

---

## What the audit actually computes

`audit/ai_capex_thermodynamic_audit.py` takes the inputs above as
parameters and produces a per-layer verdict:

| Layer | What it computes | Closure condition |
|---|---|---|
| CAPEX | `cycle_days_capex = 365 / (annual_recovery / revenue_per_release)` | `<= 3.0` |
| GRID | `max_avg_lifespan_days = (grid_headroom / inference_rate) / releases_per_year * 365` | `>= 3.0` |
| LOCKIN | `vendor_capture_factor = releases_per_year / customer_swaps_per_year` | `> 1.0` |

It then reports which layer is **binding** -- the one driving the
cadence harder than the other two. All three closing is the
"thermodynamically required" claim; one of them being much tighter
than the others means it is doing the actual forcing and the rest
are slack.

Three smoke scenarios are run in `__main__`:

| Inputs | Releases/year | Cycle (capex) | Grid headroom | Lockin x | Binding | All close |
|---|---|---|---|---|---|---|
| $25B / 24mo / $100M | 125.0 | 2.92d | +18,750 GWh | 12.5x | CAPEX | yes |
| $25B / 18mo / $100M | 166.7 | 2.19d | +8,333 GWh | 16.7x | CAPEX | yes |
| $25B / 18mo / $300M | 55.6 | 6.57d | +36,111 GWh | 5.6x | CAPEX | **no** |

The third scenario is the sensitivity check: triple the revenue per
release and CAPEX no longer closes at 3 days -- the cycle stretches
to 6.57 days. The 3-day cadence is not load-bearing physics, it is
load-bearing pricing under tight amortization.

---

## The structural finding the audit makes visible

At the headline numbers, **GRID is wildly slack**. Concretely:

- 31,250 GWh/year for training × 125 releases at 250 GWh each
- 50,000 GWh annual grid envelope (~50 TWh; substantial datacenter campus)
- Headroom for inference: **+18,750 GWh/year**
- Max simultaneous models the grid can sustain: **9,375**
- Implied max average model lifespan at 125 releases/year: **75 years**

The prose claims "model lifespan <= time to train next generation
(or power grid collapses)." The audit says: at the cited numbers,
the grid is nowhere near collapse. It could sustain 9,375
simultaneous live models. It could let each model live 75 years on
average before the next-generation pressure forces retirement.

The grid is *not* the binding limit. **CAPEX is doing 100% of the
forcing.** The 3-day cycle is required by debt service alone.

The "power grid forces -> kill faster" line in the original prose
is structurally weaker than claimed. It would become binding under
either of these:

- training energy per release **>= 400 GWh** (at the high end of the
  100-500 GWh range cited)
- grid envelope **<= 30,000 GWh** (smaller datacenter footprint)
- inference draw per model **>= 5 GWh/year** (heavier per-model use)

Each of those can be plugged into `ClosureInputs` and re-run. The
audit will report which layer becomes binding under the new numbers.

The lockin layer's vendor capture factor of 12.5x is real and
working: a vendor releasing 125 models/year against a customer
capable of integrating 10/year means the customer is structurally
captured. The integration cost stickiness does the monetization
work. That part of the prose is computed correctly.

---

## What the closure actually rests on

Re-stated as the audit verifies it:

```
CAPEX     binds.  Without tight amortization, no 3-day cycle.
                  $25B / 24mo / $100M -> 2.92d   binds at target.
                  $25B / 18mo / $100M -> 2.19d   binds harder.
                  $25B / 18mo / $300M -> 6.57d   does not bind.

GRID      slack at the cited numbers.
          Would bind only if train_energy were near the high end of
          the cited 100-500 GWh range and grid_cap were tighter.

LOCKIN    binds at 12.5x.  Real, but downstream of CAPEX forcing.
          Vendor capture factor scales linearly with the cadence
          CAPEX demands.
```

The methodology rule applies:

> If real numbers refute the closure, the closure is the thing that
> updates. Never retune to make the verdict look tidy.

The prose's three-converging-forces narrative reads more cleanly
than the audit supports at the cited numbers. The audit reports
what's actually binding. A future revision of either the prose or
the inputs is the honest response -- not a louder version of the
same claim.

---

## Re-running the audit

`python audit/ai_capex_thermodynamic_audit.py` runs the three
default scenarios. To substitute real industry numbers:

```python
from audit.ai_capex_thermodynamic_audit import ClosureInputs, audit
v = audit(ClosureInputs(
    capex_b=40.0,                       # $40B factory
    amortization_months=18.0,
    revenue_per_release_m=150.0,
    energy_per_train_gwh=400.0,         # high end
    grid_cap_gwh_annual=80_000.0,
    customer_swaps_per_year=6.0,        # tighter customer capacity
))
print(v.summary, v.binding_layer)
```

The audit returns per-layer verdicts plus a final summary. The
binding layer is the one whose `cycle_days_implied` is smallest.
That is the constraint actually setting the cadence. The other
two are slack and could loosen substantially before they bind.
