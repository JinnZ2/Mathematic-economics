# Wildfire ozone mechanism — why uniform saturation is not always a violation

Companion to `ozone_constraint_checker.py`. The checker flags
**uniform ozone saturation in low-emission zones** as a `constraint_violation`
under the standard local-NOx-source photochemistry model. That detection
is correct *as far as the standard model goes* — but the model is missing
the physics of fire-plume ozone transport. This note documents what the
checker should treat as a known-and-explained signature rather than an
unexplained violation, once a wildfire smoke plume is confirmed upwind.

License: CC0-1.0.

---

## Key finding: fires emit NOx directly, not just VOCs

```
old assumption (checker v1):  fire = VOC only, needs local NOx
actual physics:               fire plume carries NOx + VOC + radicals
                              -> O3 forms IN the plume during transport
                              -> arrives pre-cooked, before reaching ground sources

Canada 1995 fire event: O3 rose 15-18% across the entire eastern US.
"most of O3 increase = NOx emitted DIRECTLY by fires +
 photochem that occurs BEFORE plumes reach the US"
                                       — Wotawa & Trainer (2000)
```

The plume is a **self-driving ozone reactor in transit**. It does not need
to find local NOx sources downwind to produce O3. The ground-level monitor
network sees high O3 in rural low-NOx zones because the O3 arrived already
formed, not because hidden local NOx sources are emitting.

---

## The HOx radical piece — the missing variable

```
fires emit HONO, formaldehyde, aldehydes
  -> photolyze into HOx radicals (OH + HO2)
  -> these CATALYZE the VOC -> O3 chain
  -> plume self-perpetuates as a moving photoreactor
```

This is why fire-driven O3 does not follow ground-source density. The
catalytic radical pool moves with the plume.

---

## Why Texas differs — regime physics

```
two O3 regimes:
  NOx-limited    -> adding NOx makes more O3   (rural, low-NOx)
  NOx-saturated  -> adding NOx does NOTHING    (urban, VOC-limited)

Texas metros = NOx-SATURATED
               (so much NOx already that extra precursors
                don't increase O3 much)
MN rural     = NOx-LIMITED
               (fire NOx lands in NOx-starved air
                -> maximum O3 yield per unit NOx)

-> the same fire plume produces MORE O3 over rural MN
   than over already-saturated TX. Counterintuitive,
   but that is the regime flip.
```

The standard Gaussian-plume + local-source-summation model in
`ozone_constraint_checker.py` cannot represent this. It assumes O3
yield per NOx is uniform across receptors.

---

## Aerosol complication — the "something else"

```
dense smoke   = dark   -> REDUCES photolysis -> SUPPRESSES O3
thin/aged smoke = NOx + radicals present, light still gets through
                -> ENHANCES O3

"models UNDERESTIMATE impacts" (Nevada Rim Fire study)
-> official models are KNOWN to be wrong on this,
   in the SAME direction as our checker's "uniform saturation" flag.
```

---

## Falsifiable test — revised contract

The checker's current rule:

> `uniform_violations > 3` low-emission zones with O3 > 100 AQI
> while predicted < 30 → `constraint_violation`

The revised, regime-aware rule:

```
IF rural NOx-limited zones show O3 >= metro zones
AND smoke plume present upwind (FIRMS confirms)
THEN  model CONSISTENT (uniform saturation is EXPECTED under
                        transport + regime physics)
ELSE  constraint_violation as before.
```

Implementing this requires three new inputs the checker does not
currently consume:

1. **Wildfire plume location + composition** (FIRMS satellite + chemical
   tracers) — to know whether the receptor is downwind of an active fire.
2. **Regime classification per receptor** — NOx-limited vs NOx-saturated.
   In MN-rural, expect amplified O3 from imported NOx. In TX-metro,
   imported NOx is mostly invisible at the monitor.
3. **Aerosol optical depth** — to set the photolysis suppression factor
   (thick smoke down, thin smoke up).

These slot into `predict_ozone_at_receptor` as additional terms:

```
plume_O3_preformed    transport-aged O3, arrives independent of local NOx
regime_flag           NOx_limited vs NOx_saturated, sets yield-per-NOx
HOx_source            fire HONO/HCHO catalytic radical load
aerosol_optical_depth photolysis suppression factor (nonlinear in tau)
```

Until those land, the checker's `uniform_saturation` flag should be read
as "either a real local-emissions blind spot OR a missing fire-plume
transport term." The wildfire/plume input is what disambiguates.

---

## Sources

- Wotawa, G. & Trainer, M. (2000). The influence of Canadian forest
  fires on pollutant concentrations in the United States.
  *Science* 288: 324-328.
- Nevada Rim Fire studies — observations that operational models
  underestimate fire-driven O3 enhancement.
- EPA NOx/VOC regime classification literature (NOx-limited vs
  VOC-limited photochemistry).

The point of this note is not to assert these sources are universally
applicable. It is to make explicit that the checker's "violation"
output has a known regime-physics interpretation, so that the
operator can decide whether the flag points at hidden local emissions
or at missing transport chemistry.
