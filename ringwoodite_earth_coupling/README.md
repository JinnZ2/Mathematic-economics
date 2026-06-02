# ringwoodite-earth-coupling  (CC0, stdlib-only)

Couples deep-mantle water (ringwoodite) into the earth-systems forcing stack
and tests it against the geographic/temporal clustering of flood &
island-subsidence narratives. Built to FALSIFY itself, not confirm.

## PIPELINE (read top-to-bottom = energy flow up through the Earth)

```
 MINERAL PHYSICS  [MEASURED]            ringwoodite_phase.py
   ringwoodite H2O capacity(T)
   660 km Clapeyron boundary(T)
   dehydration flux at 660  [kg H2O/m2/yr]
            |
            v  collapse to ONE slow scalar
   deep_water_baseline (0..1)           << SLOW. drifts on >10 kyr. CPL-02
            |
 COUPLING CHAIN  [DERIVED]              mantle_crust_coupling.py
   hydrolytic weakening -> viscosity drop
   -> basal heat-flux x-multiplier
   -> aquifer pore-pressure headroom
            |
            v
   crustal SENSITIVITY  S_base (0..1)   << how reactive the crust is
            |
 FAST FORCING  [proxy, structure-only]  forcing_functions.py
   chandler/annual wobble  (1.0, 1.19 yr)
   solar  (11, 88, 210, 2400 yr)
   insolation/Milankovitch (19,23,41,100,405 kyr)
   glacial unloading RATE  (lagged d/dt)
   -> forcing_alignment(t)  (0..1)      << constructive interference only
            |
            v
 EVENT MODEL                            coupled_model.py
   gain = 1 + alpha*gain*(S_base - S_ref)   << alpha=0 -> NULL (fast only)
   P_event(t) = sigmoid(k * gain * align - theta)
   -> probability timeseries + peaks, last 150 kyr
   -> emits earth-systems-physics hydrosphere boundary forcing
            |
            v
 FALSIFIER                              narrative_crossval.py
   overlap(predicted peaks, dated narratives)
   vs Monte-Carlo shuffle null  AND  vs alpha=0 null
   verdict EVT-01: does the deep baseline EARN its place?

 ----------------------------------------------------------------
 MECHANISM BRANCH  (water FROM the ground, not from the sky)
 ----------------------------------------------------------------
 SEISMIC EMERGENCE  [MEASURED]          aquifer_pressure_head.py
   seismic energy density e(M,r)  [Wang 2007]
   poroelastic dp = B * d_sigma   [Skempton, AQ-01]
   classify: NONE / WATER_LEVEL / SPRING / LIQUEFACTION_UPWELLING
   s_base lowers the threshold (AQ-03)  << mantle state meets quake
            |
            v
 TWO SEPARATE TESTS                     paleoseismic_crossval.py
   SYN-01 CO-DATING : narratives vs REGIONAL paleoseismic markers
                      (turbidite/liquefaction/tsunami) vs shuffle null
                      -> the DEFENSIBLE local claim
   SYN-02 SYNCHRONY : cross-continental clustering vs POISSON null
                      with dating smear
                      -> the SEDUCTIVE claim, built to stay DEAD
                         unless data overwhelms chance

 METROLOGICAL SKIN over everything      claim_ledger.py
   no quantity travels without unit + sanity range
   no claim exists without a falsifier + evidence_class
   CLAIM_TABLE.earth.json  <- self-falsifying ledger (15 claims)
```

## SNOWBALL BRANCH  (the crust is not a smooth sphere)   geothermal_refugia.py

```
 SUB-ICE OCEAN   H_eq = k(T_f - T_surf)/Q_geo  [GEO-01 MEASURED]
   ~800 m sea ice over a 3700 m LIQUID ocean. it never froze to the bottom.
   deep trenches: liquid. whole sub-ice ocean: one connected refugium.

 CONTINENTAL ICE  wet-based iff Q_geo > k(T_pmp(H) - T_surf)/H  [GEO-02]
   thin craton ice -> COLD_BASED_FROZEN
   thick ice (>~2 km) -> WET_BASED (pressure-melt + insulation) even on craton
   hotspot/ridge flux -> always wet -> hydrothermal refugia

 TWO ACCOUNTS, never blurred:
   sub-ice liquid fraction  -> LIFE refugia (ice-capped, albedo-neutral) GEO-03
   open-water fraction      -> ALBEDO-relevant. ~0 in hard Snowball.    GEO-04
   => refugia SUSTAIN life; CO2 ENDS the freeze. refugia do not melt the planet.
```

## THE HONESTY SPINE  (CPL-02 / EVT-01)

Ringwoodite is the DIMMER SWITCH, not the trigger.
Mantle overturn ~1e8-1e9 yr >> narrative window ~1e4-1e5 yr.
So the deep-water term may ONLY set a slow background sensitivity; the actual
flood events are tripped by FAST forcing (orbital, glacial unloading, solar,
wobble) riding on that base.

The model is wired so alpha=0 turns the deep term OFF (pure fast-forcing NULL).
EVT-01's falsifier: if alpha>0 does not beat alpha=0 above a shuffle null,
DROP the deep baseline. As shipped, on PLACEHOLDER narrative data, it returns
NOT SUPPORTED. That is correct. It is testing the pipeline, not the world.

## TO MAKE IT TEST THE WORLD

Replace `NARRATIVES` in narrative_crossval.py with real, INDEPENDENTLY dated
entries (sediment cores, drowned-shoreline dates, oral-tradition chronologies
with provenance). Then re-run. Let it tell you whether the old knowledge and
the deep water cycle actually line up.

## RUN

```
python3 claim_ledger.py          # write the ledger (11 claims)
python3 coupled_model.py         # full vs null peaks (rainfall-cycle branch)
python3 narrative_crossval.py    # EVT-01 verdict
python3 aquifer_pressure_head.py # seismic emergence mechanism
python3 paleoseismic_crossval.py # SYN-01 (local) + SYN-02 (synchrony) verdicts
python3 geothermal_refugia.py    # Snowball: sub-ice ocean + patchy refugia
```

## THE SYNCHRONY TRAP  (SYN-01 vs SYN-02)

"Water from the ground in distinct cultures around the same time" is TWO
claims, not one. The build refuses to let them blur:

SYN-01  each region's emergence is triggered LOCALLY by its own seismicity.
Defensible. Mechanism is MEASURED (Wang/Skempton/Manga).
SYN-02  the regions fired SYNCHRONOUSLY (a common pacing). Most likely a
dating-resolution illusion. Stays FALSIFIED unless real, tight dates
beat an independent-Poisson null.

On placeholder data: SYN-01 SUPPORTED, SYN-02 NOT SUPPORTED. That is the
honest default. Bring provenanced dates to move SYN-02 - or to keep it dead.

stdlib only. no numpy. no network. runs from a phone.
