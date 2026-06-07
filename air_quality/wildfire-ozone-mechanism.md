# Wildfire ozone mechanism — physics basis + falsification contract

Companion to `ozone_constraint_checker.py`. The checker is built around
the physics in this note. Specifically: it does **not** treat
uniform high O3 as a violation by default. It treats it as **expected**
when a wildfire plume is present upwind, and as **REAL_ANOMALY** only
when the standard transport + regime story cannot account for it.

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

The plume is a **self-driving ozone reactor in transit**. It does not
need to find local NOx sources downwind to produce O3. The ground-level
monitor network sees high O3 in rural low-NOx zones because the O3
arrived already formed, not because hidden local NOx sources are
emitting.

In `ozone_constraint_checker.py` this is the `FirePlume` dataclass —
the **primary** O3 driver, with `preformed_o3_ppb` as the load-bearing
term. The pre-existing `NOxSource` machinery (Gaussian plume from
trucks / ag / industrial) is now a *secondary* term, intentionally.

---

## The HOx radical piece

```
fires emit HONO, formaldehyde, aldehydes
  -> photolyze into HOx radicals (OH + HO2)
  -> these CATALYZE the VOC -> O3 chain
  -> plume self-perpetuates as a moving photoreactor
```

Implemented as `FirePlume.hox_index` (normalized HONO/HCHO loading) and
applied multiplicatively in the in-place chemistry path of
`predict_aqi()`. Default 1.0; higher for younger / nitrogen-richer
plumes.

---

## Regime physics — the NOx-limited / NOx-saturated flip

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

Implemented as `_regime(local_nox_ppb)` and `_yield_factor(regime)`:

| Regime | Threshold (ppb local NOx) | Yield factor |
|---|---|---|
| `NOx_limited` | `< 8` | **1.6** |
| `transitional` | `8 – 25` | 1.0 |
| `NOx_saturated` | `> 25` | 0.45 |

A rural receptor with ~0 ppb local NOx receives the **1.6 multiplier on
imported plume NOx** — exactly the amplification the literature
describes.

---

## Aerosol photolysis gate

```
dense smoke   = dark   -> REDUCES photolysis -> SUPPRESSES O3
thin/aged smoke = NOx + radicals present, light still gets through
                -> ENHANCES O3
```

Implemented as a three-band AOD gate inside `_plume_o3_ppb()`:

| AOD | Photolysis factor | Regime |
|---|---|---|
| `>= 2.5` | 0.3 | dark plume core (suppressed) |
| `1.0 – 2.5` | 0.7 | moderate smoke |
| `< 1.0` | 1.0 | thin / aged plume (full sun) |

The nonlinearity is deliberate. Operational models that smooth this
out are **known to underestimate fire-driven O3 enhancement** (Nevada
Rim Fire studies). This checker reads thick smoke as *suppressing* O3
and thin smoke as *enhancing* it — same direction as observation.

---

## Falsification contract (now baked into code)

The contract that v1 only documented is now executable:

```
H0   : statewide O3 = transported wildfire plume + regime-flip yield
PASS : uniform saturation occurs ONLY when FIRMS shows upwind plume
       (status = "model_consistent")
FAIL : high uniform O3 with NO plume + low local NOx
       (status = "REAL_ANOMALY_no_plume_high_O3")
       -> H0 refuted, a real missing variable exists. Investigate.
```

Methodology rule (carried from other JinnZ2/* repos):

> If field data refutes a claim, update the claim.
> Never retune the model to hide the refutation.

The `REAL_ANOMALY` band is not a bug. It is the whole point of the
tool. It says: the operator loaded the data, the standard transport
+ regime physics still cannot explain the observation, **so the
operator now owes themselves a real hypothesis**, not a parameter
tweak.

---

## Known seam — the `plume_present` gate is global

```
predict_aqi() returns plume_present = bool(self.plumes)
```

This is a coarse check. It asks "are *any* plumes loaded into the
system?" rather than "is *this* receptor under a plume cone?" The
operational rationale: if the operator has supplied plume data at
all, the system has plume awareness, and unexplained mismatches are
more likely calibration error than missing physics.

The honest cost: a receptor 500 km outside every plume cone, with
local NOx < 8 ppb and observed O3 > 100 AQI, will be classified as
`calibration_gap` rather than `REAL_ANOMALY` as long as *some* plume
is loaded anywhere in the system. The smoke test for this module
exercises that case (case 3 in the commit's smoke harness) and
intentionally lets the current behavior stand.

A v3 tightening would per-receptor evaluate "is this receptor under
the cone of any plume?" and only set `plume_present = True` for the
specific receptor. That is the right next move when the v2 starts
making decisions that matter. Until then, operators reading the
report should know: the `calibration_gap` band can hide a
`REAL_ANOMALY` if a far-away plume is loaded.

---

## Sources

- Wotawa, G. & Trainer, M. (2000). The influence of Canadian forest
  fires on pollutant concentrations in the United States.
  *Science* 288: 324-328.
- Jaffe, D. A. & Wigder, N. L. (2012). Ozone production from wildfires:
  A critical review. *Atmospheric Environment*.
- FIREX-AQ campaign (NASA / NOAA, 2019 fire-chemistry field study).
- ACP 25/8701/2025; ACP 25/5591/2025 (recent regime + photolysis
  measurements).
- Nevada Rim Fire studies — operational models underestimate O3
  enhancement in the same direction as this checker's regime-aware
  prediction.

The point of citing these is not to assert universality. It is to
make explicit that the `REAL_ANOMALY` band — when it fires under a
documented plume — is a falsification of the physics that this
literature supports, and is worth carrying upstream to the operator
as exactly that.
