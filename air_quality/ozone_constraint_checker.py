# ozone_constraint_checker.py
# Falsifiable ozone formation model vs. observed AQI
# Input: emissions + meteorology + observations
# Output: prediction mismatch = constraint violation

import json
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
import math

@dataclass
class NOxSource:
    """Localized NOx emission point"""
    location_name: str
    lat: float
    lon: float
    nox_tons_per_day: float
    source_type: str  # truck, ag, lumber, industrial, power
    confidence: float  # 0.0 to 1.0

@dataclass
class MonitorReading:
    """Real AQI observation from MPCA network"""
    location_name: str
    lat: float
    lon: float
    aqi_ozone: int
    timestamp: str
    source: str

@dataclass
class MeteoState:
    """Atmospheric conditions snapshot"""
    timestamp: str
    wind_direction_deg: float
    wind_speed_mph: float
    mixing_layer_feet: int
    temperature_f: float
    solar_radiation_w_m2: float
    humidity_percent: float
    voc_ug_m3: float  # wildfire smoke VOC concentration

class OzoneConstraintChecker:
    """Physics-based ozone prediction vs. observation"""

    def __init__(self):
        self.nox_sources: List[NOxSource] = []
        self.observations: List[MonitorReading] = []
        self.meteo: MeteoState = None
        self.violations: List[Dict] = []

    def load_emissions_inventory(self, json_file: str):
        """Load NOx sources from EPA/state inventory"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        for src in data.get('sources', []):
            self.nox_sources.append(NOxSource(**src))

    def load_observations(self, csv_file: str):
        """Load real AQI readings from MPCA monitor network"""
        # Parse CSV: location, lat, lon, aqi_ozone, timestamp
        with open(csv_file, 'r') as f:
            for line in f.readlines()[1:]:
                parts = line.strip().split(',')
                self.observations.append(MonitorReading(
                    location_name=parts[0],
                    lat=float(parts[1]),
                    lon=float(parts[2]),
                    aqi_ozone=int(parts[3]),
                    timestamp=parts[4],
                    source='MPCA'
                ))

    def load_meteorology(self, json_file: str):
        """Load NOAA GFS atmospheric state"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        self.meteo = MeteoState(**data)

    def distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine distance between two points"""
        R = 6371  # Earth radius km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    def gaussian_plume_concentration(self, source: NOxSource, receptor_lat: float, receptor_lon: float) -> float:
        """Gaussian plume model: NOx concentration at receptor downwind of source"""
        # Standard atmospheric dispersion model
        dist = self.distance_km(source.lat, source.lon, receptor_lat, receptor_lon)

        # Wind direction: is receptor downwind?
        bearing = math.degrees(math.atan2(receptor_lon - source.lon, receptor_lat - source.lat))
        wind_angle = (bearing - self.meteo.wind_direction_deg) % 360

        # Only count if downwind (within ~90 degrees of wind direction)
        if wind_angle > 90 and wind_angle < 270:
            return 0.0

        # Dispersion parameters (Pasquill-Gifford)
        sigma_y = 0.08 * dist * (1 + 0.0001 * dist)  # lateral spread
        sigma_z = 0.06 * dist * (1 + 0.0015 * dist)  # vertical spread

        if sigma_y == 0 or sigma_z == 0:
            return 0.0

        # Daily emission rate in grams
        emission_g_day = source.nox_tons_per_day * 1_000_000

        # Effective stack height (assume ground-level for mobile/ag sources)
        H = 10  # meters

        # Concentration at receptor (simplified Gaussian)
        Q = emission_g_day / (24 * 3600)  # grams per second
        u = self.meteo.wind_speed_mph * 0.44704  # convert to m/s

        if u < 0.1:
            return 0.0

        concentration = (Q / (2 * math.pi * u * sigma_y * sigma_z)) * math.exp(-H**2 / (2 * sigma_z**2))

        # Convert to ppb (rough: 1 ton NOx/day ~ 10 ppb at 1km downwind in stagnant conditions)
        ppb = concentration * 0.1
        return max(0, ppb)

    def predict_ozone_at_receptor(self, receptor_lat: float, receptor_lon: float) -> float:
        """Predict ground-level ozone from NOx + VOCs"""
        # Sum upwind NOx contributions
        total_nox_ppb = sum(
            self.gaussian_plume_concentration(src, receptor_lat, receptor_lon)
            for src in self.nox_sources
        )

        # Photochemical ozone formation (simplified)
        # Ozone ~ f(NOx, VOC, solar_radiation, temperature)
        # High-level approximation: ozone increases with NOx and VOC, peaks at certain NOx/VOC ratio

        solar_factor = self.meteo.solar_radiation_w_m2 / 1000  # normalized to ~1 at peak
        temp_factor = max(0, (self.meteo.temperature_f - 70) / 30)  # increases above 70F

        voc_ppb = self.meteo.voc_ug_m3 / 50  # rough conversion to ppb

        # NOx + VOC photochemistry (simplified)
        if total_nox_ppb < 5:
            ozone_ppb = 0  # too little NOx to form much ozone
        else:
            # Peak ozone formation at NOx/VOC ratio ~1:3
            nox_voc_ratio = total_nox_ppb / max(1, voc_ppb)
            efficiency = 1.0 if 0.2 < nox_voc_ratio < 5 else 0.5
            ozone_ppb = (total_nox_ppb * voc_ppb * efficiency) * solar_factor * temp_factor

        # Convert ppb to AQI (EPA: 0-55 ppb = 0-100 AQI; roughly linear)
        aqi = (ozone_ppb / 55.0) * 100
        return min(500, aqi)  # cap at max AQI

    def check_constraints(self):
        """Compare predicted vs. observed AQI across monitor network"""
        self.violations = []

        for obs in self.observations:
            predicted_aqi = self.predict_ozone_at_receptor(obs.lat, obs.lon)
            observed_aqi = obs.aqi_ozone
            mismatch = abs(predicted_aqi - observed_aqi)
            mismatch_percent = (mismatch / max(1, observed_aqi)) * 100

            # Flag as violation if prediction is way off
            if mismatch_percent > 50:  # >50% error threshold
                self.violations.append({
                    'location': obs.location_name,
                    'lat': obs.lat,
                    'lon': obs.lon,
                    'observed_aqi': observed_aqi,
                    'predicted_aqi': round(predicted_aqi, 1),
                    'mismatch_percent': round(mismatch_percent, 1),
                    'source_type': 'uniform_saturation' if predicted_aqi < 30 and observed_aqi > 100 else 'localized_mismatch'
                })

    def report(self) -> Dict:
        """Generate constraint violation report"""
        self.check_constraints()

        if not self.violations:
            return {
                'status': 'model_consistent',
                'message': 'Predicted ozone matches observed AQI across all monitors. Standard photochemistry model holds.',
                'violations': []
            }

        uniform_violations = [v for v in self.violations if v['source_type'] == 'uniform_saturation']

        if len(uniform_violations) > 3:  # Multiple low-emission zones showing high AQI
            return {
                'status': 'constraint_violation',
                'message': f'VIOLATION: Uniform ozone saturation in {len(uniform_violations)} low-emission zones. Standard NOx-source model FAILS.',
                'implication': 'Ozone precursor distribution is NOT explained by localized NOx sources. Missing physics or precursor mechanism.',
                'violations': uniform_violations,
                'next_step': 'Check for distributed NOx source (upper atmosphere, long-range transport, or non-standard photochemistry). See wildfire-ozone-mechanism.md for the regime-physics explanation.'
            }
        else:
            return {
                'status': 'partial_mismatch',
                'message': f'Standard model explains most locations but {len(self.violations)} outliers detected.',
                'violations': self.violations
            }

# Usage
if __name__ == '__main__':
    checker = OzoneConstraintChecker()

    # Load data (you'll populate these from NOAA, EPA, MPCA)
    # checker.load_emissions_inventory('nox_sources.json')
    # checker.load_observations('mpca_aqi_readings.csv')
    # checker.load_meteorology('noaa_meteo_state.json')

    # result = checker.report()
    # print(json.dumps(result, indent=2))
