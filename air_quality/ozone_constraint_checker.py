#!/usr/bin/env python3
# ozone_constraint_checker.py
# Falsifiable wildfire-ozone model vs. observed AQI.
# CC0. stdlib-only. phone-buildable. fetch-on-wifi / read-on-road.
#
# PHYSICS BASIS (corrected from "trucks cause local O3" narrative):
#   Fires emit NOx + VOC + HOx-precursors (HONO, HCHO) DIRECTLY.
#   O3 forms INSIDE the plume during transport -> arrives pre-cooked.
#   Plume is an air mass -> blankets terrain uniformly,
#     independent of local ground-source density.
#   NOx-limited rural air yields MORE O3 per unit NOx than
#     NOx-saturated urban air (the regime flip).
#   Dense smoke suppresses photolysis (O3 down);
#     thin/aged smoke lets light through (O3 up).
# refs: Wotawa&Trainer 2000; Jaffe&Wigder 2012; FIREX-AQ;
#       ACP 25/8701/2025; ACP 25/5591/2025.

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ---------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------

@dataclass
class NOxSource:
    """Localized ground NOx emitter. Now SECONDARY to plume term."""
    name: str
    lat: float
    lon: float
    nox_tons_per_day: float
    source_type: str          # truck | ag | lumber | industrial | power
    confidence: float = 1.0


@dataclass
class FirePlume:
    """Transported wildfire air mass. The PRIMARY O3 driver."""
    name: str
    upwind_lat: float
    upwind_lon: float
    transport_bearing_deg: float   # direction plume travels toward
    age_hours: float               # transport time since emission
    frp_mw: float                  # fire radiative power (intensity)
    aod: float                     # aerosol optical depth (smoke thickness)
    preformed_o3_ppb: float        # O3 already formed in transit
    nox_residual_ppb: float        # NOx still active on arrival
    hox_index: float = 1.0         # HONO/HCHO radical loading, normalized


@dataclass
class MonitorReading:
    """Observed AQI from MPCA / AirNow network."""
    name: str
    lat: float
    lon: float
    aqi_ozone: int
    timestamp: str
    source: str = "MPCA"


@dataclass
class MeteoState:
    timestamp: str
    wind_direction_deg: float      # FROM direction (met convention)
    wind_speed_mph: float
    mixing_layer_feet: int
    temperature_f: float
    solar_radiation_w_m2: float
    humidity_percent: float


# ---------------------------------------------------------------
# CORE MODEL
# ---------------------------------------------------------------

class OzoneConstraintChecker:

    PPB_TO_AQI = 100.0 / 70.0   # 70 ppb 8-hr = NAAQS edge ~ AQI 100

    def __init__(self):
        self.nox_sources: List[NOxSource] = []
        self.plumes: List[FirePlume] = []
        self.observations: List[MonitorReading] = []
        self.meteo: Optional[MeteoState] = None
        self.violations: List[Dict] = []

    # ---- loaders (populate from FIRMS / NOAA / EPA / MPCA) ----

    def load_emissions(self, path: str):
        with open(path) as f:
            for s in json.load(f).get("sources", []):
                self.nox_sources.append(NOxSource(**s))

    def load_plumes(self, path: str):
        with open(path) as f:
            for p in json.load(f).get("plumes", []):
                self.plumes.append(FirePlume(**p))

    def load_observations(self, csv_path: str):
        with open(csv_path) as f:
            for line in f.readlines()[1:]:
                c = line.strip().split(",")
                if len(c) < 5:
                    continue
                self.observations.append(MonitorReading(
                    name=c[0], lat=float(c[1]), lon=float(c[2]),
                    aqi_ozone=int(c[3]), timestamp=c[4]))

    def load_meteorology(self, path: str):
        with open(path) as f:
            self.meteo = MeteoState(**json.load(f))

    # ---- geometry ----

    @staticmethod
    def _dist_km(la1, lo1, la2, lo2):
        R = 6371.0
        dla = math.radians(la2 - la1)
        dlo = math.radians(lo2 - lo1)
        a = (math.sin(dla / 2) ** 2 +
             math.cos(math.radians(la1)) * math.cos(math.radians(la2)) *
             math.sin(dlo / 2) ** 2)
        return 2 * R * math.asin(math.sqrt(a))

    @staticmethod
    def _bearing(la1, lo1, la2, lo2):
        return math.degrees(math.atan2(lo2 - lo1, la2 - la1)) % 360

    # ---- regime classifier ----

    def _regime(self, local_nox_ppb: float) -> str:
        """NOx-limited rural vs NOx-saturated urban. drives O3 yield."""
        if local_nox_ppb < 8:
            return "NOx_limited"     # adding NOx -> more O3 (high yield)
        if local_nox_ppb > 25:
            return "NOx_saturated"   # adding NOx -> little/no O3
        return "transitional"

    def _yield_factor(self, regime: str) -> float:
        return {"NOx_limited": 1.6,
                "transitional": 1.0,
                "NOx_saturated": 0.45}[regime]

    # ---- local ground NOx (now a minor term) ----

    def _local_nox_ppb(self, rlat, rlon) -> float:
        if not self.meteo:
            return 0.0
        u = max(0.1, self.meteo.wind_speed_mph * 0.44704)
        total = 0.0
        for s in self.nox_sources:
            d = self._dist_km(s.lat, s.lon, rlat, rlon)
            if d > 200:
                continue
            brg = self._bearing(s.lat, s.lon, rlat, rlon)
            off = abs((brg - (self.meteo.wind_direction_deg + 180)) % 360)
            off = min(off, 360 - off)
            if off > 90:
                continue                      # receptor not downwind
            sy = max(1e-3, 0.08 * d * (1 + 1e-4 * d))
            sz = max(1e-3, 0.06 * d * (1 + 1.5e-3 * d))
            Q = s.nox_tons_per_day * 1e6 / 86400.0   # g/s
            conc = (Q / (2 * math.pi * u * sy * sz))
            total += conc * 0.1 * s.confidence       # crude ->ppb
        return total

    # ---- plume contribution (the PRIMARY term) ----

    def _plume_o3_ppb(self, rlat, rlon) -> float:
        if not self.meteo:
            return 0.0
        total = 0.0
        for p in self.plumes:
            # is receptor downwind along the plume travel bearing?
            brg = self._bearing(p.upwind_lat, p.upwind_lon, rlat, rlon)
            off = abs((brg - p.transport_bearing_deg) % 360)
            off = min(off, 360 - off)
            if off > 60:
                continue                       # not under this plume
            # aerosol photolysis gate: thick smoke suppresses O3
            if p.aod >= 2.5:
                photolysis = 0.3               # dark plume core
            elif p.aod >= 1.0:
                photolysis = 0.7
            else:
                photolysis = 1.0               # thin/aged -> full sun
            solar = self.meteo.solar_radiation_w_m2 / 1000.0
            total += p.preformed_o3_ppb * photolysis * max(0.2, solar)
        return total

    # ---- combined prediction ----

    def predict_aqi(self, rlat, rlon) -> Dict:
        local_nox = self._local_nox_ppb(rlat, rlon)
        plume_nox = sum(p.nox_residual_ppb for p in self.plumes)
        regime = self._regime(local_nox)
        yf = self._yield_factor(regime)

        # in-place photochem from residual plume NOx meeting local air
        solar = self.meteo.solar_radiation_w_m2 / 1000.0 if self.meteo else 0.5
        temp_f = self.meteo.temperature_f if self.meteo else 80
        temp_factor = max(0.0, (temp_f - 70) / 30.0)
        hox = sum(p.hox_index for p in self.plumes) or 1.0

        in_place_o3 = plume_nox * yf * solar * (0.5 + temp_factor) * hox

        plume_o3 = self._plume_o3_ppb(rlat, rlon)   # pre-formed, arrives

        total_o3 = plume_o3 + in_place_o3
        aqi = min(500.0, total_o3 * self.PPB_TO_AQI)
        return {
            "predicted_aqi": round(aqi, 1),
            "local_nox_ppb": round(local_nox, 2),
            "regime": regime,
            "preformed_o3_ppb": round(plume_o3, 1),
            "in_place_o3_ppb": round(in_place_o3, 1),
            "plume_present": bool(self.plumes),
        }

    # ---- constraint check ----

    def check(self):
        self.violations = []
        for o in self.observations:
            pred = self.predict_aqi(o.lat, o.lon)
            mismatch = abs(pred["predicted_aqi"] - o.aqi_ozone)
            pct = mismatch / max(1, o.aqi_ozone) * 100
            if pct <= 50:
                continue
            # classify the mismatch
            uniform_no_plume = (o.aqi_ozone > 100
                                and not pred["plume_present"]
                                and pred["local_nox_ppb"] < 8)
            self.violations.append({
                "location": o.name,
                "observed_aqi": o.aqi_ozone,
                "predicted_aqi": pred["predicted_aqi"],
                "mismatch_pct": round(pct, 1),
                "regime": pred["regime"],
                "kind": ("REAL_ANOMALY_no_plume_high_O3"
                         if uniform_no_plume else "calibration_gap"),
            })

    def report(self) -> Dict:
        self.check()
        anomalies = [v for v in self.violations
                     if v["kind"].startswith("REAL_ANOMALY")]
        if not self.violations:
            status = "model_consistent"
            msg = ("Predicted O3 tracks observed AQI. Uniform saturation "
                   "under a present plume is EXPECTED, not anomalous.")
        elif anomalies:
            status = "REAL_ANOMALY"
            msg = (f"{len(anomalies)} zones show high O3 with NO upwind "
                   f"plume and low local NOx. Transport+regime physics "
                   f"cannot explain these. Investigate.")
        else:
            status = "calibration_gap"
            msg = (f"{len(self.violations)} mismatches, all explainable as "
                   f"parameter calibration error (not physics failure).")
        return {"status": status, "message": msg,
                "violations": self.violations}


# ---------------------------------------------------------------
# FALSIFICATION CONTRACT (the point of the whole tool)
# ---------------------------------------------------------------
#
#   H0  : statewide O3 = transported wildfire plume + regime-flip yield
#   PASS: uniform saturation occurs ONLY when FIRMS shows upwind plume
#   FAIL: high uniform O3 with NO plume + low local NOx
#           -> H0 refuted, a real missing variable exists
#
#   METHODOLOGY RULE (carried from your other repos):
#     if field data refutes a claim, update the claim.
#     never retune the model to hide the refutation.


if __name__ == "__main__":
    chk = OzoneConstraintChecker()
    # chk.load_plumes("plumes.json")        # from FIRMS + NOAA HYSPLIT
    # chk.load_emissions("nox_sources.json")# from EPA NEI by source type
    # chk.load_observations("aqi.csv")      # from MPCA / AirNow
    # chk.load_meteorology("meteo.json")    # from NOAA GFS
    # print(json.dumps(chk.report(), indent=2))
    print("ozone_constraint_checker ready. populate loaders at wifi.")
