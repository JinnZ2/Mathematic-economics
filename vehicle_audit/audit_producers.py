"""
audit_producers.py

Adapter layer. Each existing audit module (haptic, acoustic, olfactory,
visual fouling, peripheral trajectory, relational, road surface, authority,
operational GI, corridor feasibility, cross-channel verification) is wrapped
as a ConstraintProducer that emits into the shared AuditAccumulator.

This is the MIGRATION SHIM. It preserves the existing module logic while
unifying the output bus. Modules can be progressively rewritten to use the
substrate directly; until then, this adapter does the translation.

Producer structure (all identical):

    class XxxProducer(ConstraintProducer):
        name = "xxx"
        def run(self, ctx, acc):
            # 1. extract suite + environment from ctx
            # 2. call existing audit logic
            # 3. translate per-task results -> ConstraintResult
            # 4. translate hardware additions -> LifecycleCost
            # 5. emit missing capabilities

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import math

from audit_substrate import (
    Channel, ChannelVulnerability, CHANNEL_VULNERABILITY,
    Disruption, channels_disabled_by,
    ThresholdUnit, HumanThreshold, HUMAN_BASELINE, register_baseline,
    Severity, SEVERITY_INDEX, capability_to_severity,
    ConstraintResult, LifecycleCost, AuditAccumulator,
    ConstraintProducer, ReadinessGate, ReadinessReport,
    haptic_noise_floor_mps2, snr_to_capability, latency_factor,
)

try:
    from audit_vestibular import VestibularProducer
    _HAS_VESTIBULAR = True
except ImportError:
    VestibularProducer = None
    _HAS_VESTIBULAR = False


# =============================================================================
# BASELINE REGISTRATION
# =============================================================================
# All mastery-driver thresholds live here, in one place.
# Replaces the per-module HUMAN_*_BASELINE dicts.

def _register_all_baselines() -> None:
    register_baseline(
        # ---- Haptic: front axle (steering wheel) ----
        HumanThreshold("ice_onset_front",         Channel.HAPTIC_STEERING_WHEEL, ThresholdUnit.ACCEL_RMS_MPS2, 0.02,  0.5),
        HumanThreshold("hydroplaning_onset",      Channel.HAPTIC_STEERING_WHEEL, ThresholdUnit.ACCEL_RMS_MPS2, 0.01,  0.4),
        HumanThreshold("front_tire_wear",         Channel.HAPTIC_STEERING_WHEEL, ThresholdUnit.ACCEL_RMS_MPS2, 0.05, 10.0),
        HumanThreshold("steering_gear_wear",      Channel.HAPTIC_STEERING_WHEEL, ThresholdUnit.ACCEL_RMS_MPS2, 0.06, 20.0),
        HumanThreshold("crosswind_gust",          Channel.HAPTIC_STEERING_WHEEL, ThresholdUnit.ACCEL_RMS_MPS2, 0.10,  0.2),

        # ---- Haptic: rear axle (seat pan) ----
        HumanThreshold("rear_wheelspin_onset",    Channel.HAPTIC_SEAT_PAN, ThresholdUnit.ACCEL_RMS_MPS2, 0.03, 0.4),
        HumanThreshold("rear_axle_tramp",         Channel.HAPTIC_SEAT_PAN, ThresholdUnit.ACCEL_RMS_MPS2, 0.04, 2.0),
        HumanThreshold("driveline_torsional",     Channel.HAPTIC_SEAT_PAN, ThresholdUnit.ACCEL_RMS_MPS2, 0.05, 5.0),
        HumanThreshold("road_patch_length",       Channel.HAPTIC_SEAT_PAN, ThresholdUnit.ACCEL_RMS_MPS2, 0.02, 1.0),
        HumanThreshold("trailer_brake_imbalance", Channel.HAPTIC_SEAT_PAN, ThresholdUnit.ACCEL_RMS_MPS2, 0.04, 1.5),

        # ---- Haptic: frame/trailer (seat back) ----
        HumanThreshold("frame_torsional_flex",    Channel.HAPTIC_SEAT_BACK, ThresholdUnit.ACCEL_RMS_MPS2, 0.07,  5.0),
        HumanThreshold("trailer_sway_onset",      Channel.HAPTIC_SEAT_BACK, ThresholdUnit.ACCEL_RMS_MPS2, 0.02,  0.3),
        HumanThreshold("cab_mount_wear",          Channel.HAPTIC_SEAT_BACK, ThresholdUnit.ACCEL_RMS_MPS2, 0.08, 15.0),

        # ---- Acoustic cab ----
        HumanThreshold("engine_misfire",          Channel.ACOUSTIC_CAB, ThresholdUnit.SPL_DB, 35, 1.0),
        HumanThreshold("transmission_whine",      Channel.ACOUSTIC_CAB, ThresholdUnit.SPL_DB, 30, 2.0),
        HumanThreshold("tire_road_noise_change",  Channel.ACOUSTIC_CAB, ThresholdUnit.SPL_DB, 40, 1.5),
        HumanThreshold("brake_squeal",            Channel.ACOUSTIC_CAB, ThresholdUnit.SPL_DB, 25, 0.5),
        HumanThreshold("cab_air_leak",            Channel.ACOUSTIC_CAB, ThresholdUnit.SPL_DB, 20, 3.0),

        # ---- Acoustic exterior ----
        HumanThreshold("tire_slip_sound",         Channel.ACOUSTIC_EXTERIOR, ThresholdUnit.SPL_DB, 50, 0.3),
        HumanThreshold("wheel_bearing_wear",      Channel.ACOUSTIC_EXTERIOR, ThresholdUnit.SPL_DB, 35, 5.0),
        HumanThreshold("road_surface_crunch",     Channel.ACOUSTIC_EXTERIOR, ThresholdUnit.SPL_DB, 45, 0.8),
        HumanThreshold("trailer_coupling_clatter",Channel.ACOUSTIC_EXTERIOR, ThresholdUnit.SPL_DB, 40, 1.0),

        # ---- Olfactory cab ----
        HumanThreshold("burning_motor_fluid",     Channel.OLFACTORY_CAB, ThresholdUnit.CONCENTRATION_PPB,  20.0, 1.0),
        HumanThreshold("coolant_leak",            Channel.OLFACTORY_CAB, ThresholdUnit.CONCENTRATION_PPB, 200.0, 3.0),
        HumanThreshold("electrical_burn",         Channel.OLFACTORY_CAB, ThresholdUnit.CONCENTRATION_PPB,  10.0, 0.5),
        HumanThreshold("load_spoilage",           Channel.OLFACTORY_CAB, ThresholdUnit.CONCENTRATION_PPB,  50.0, 5.0),

        # ---- Olfactory exterior ----
        HumanThreshold("petrichor_rain",          Channel.OLFACTORY_EXTERIOR, ThresholdUnit.CONCENTRATION_PPB,   0.005, 3.0),
        HumanThreshold("asphalt_softening",       Channel.OLFACTORY_EXTERIOR, ThresholdUnit.CONCENTRATION_PPB,   5.0,   2.0),
        HumanThreshold("trailer_brake_lining",    Channel.OLFACTORY_EXTERIOR, ThresholdUnit.CONCENTRATION_PPB, 100.0,   2.0),
        HumanThreshold("hot_rubber",              Channel.OLFACTORY_EXTERIOR, ThresholdUnit.CONCENTRATION_PPB, 150.0,   1.5),

        # ---- Visual ----
        HumanThreshold("distant_brake_light",     Channel.VISUAL_FORWARD_FAR,  ThresholdUnit.RANGE_M,      6500.0, 1.0),
        HumanThreshold("ramp_merge_anticipation", Channel.VISUAL_FORWARD_FAR,  ThresholdUnit.RANGE_M,       800.0, 1.5),
        HumanThreshold("peripheral_vru",          Channel.VISUAL_PERIPHERAL,   ThresholdUnit.ANGLE_DEG,     120.0, 0.3),
        HumanThreshold("shockwave_prediction",    Channel.VISUAL_FORWARD_FAR,  ThresholdUnit.LATENCY_SEC,    20.0, 1.0),

        # ---- Relational / inferential ----
        HumanThreshold("flagger_signal",          Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.99, 1.0),
        HumanThreshold("police_stop",             Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.99, 2.0),
        HumanThreshold("emergency_yield",         Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.98, 1.5),
        HumanThreshold("animal_intent",           Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.90, 0.3),
        HumanThreshold("dock_worker_gesture",     Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.95, 0.8),
        HumanThreshold("child_near_road",         Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.95, 0.2),
        HumanThreshold("aggressive_driver",       Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.90, 2.0),
        HumanThreshold("merge_negotiation",       Channel.RELATIONAL_INFERENCE, ThresholdUnit.PROBABILITY, 0.92, 1.0),
    )


_register_all_baselines()


# =============================================================================
# CONTEXT - what producers receive
# =============================================================================

@dataclass
class AuditContext:
    """Bag of inputs every producer can read from."""
    vehicle:        Dict[str, Any]       = field(default_factory=dict)
    environment:    Dict[str, Any]       = field(default_factory=dict)
    sensor_suite:   Dict[str, Any]       = field(default_factory=dict)
    route:          List[Dict[str, Any]] = field(default_factory=list)
    operational:    Dict[str, Any]       = field(default_factory=dict)


# =============================================================================
# PRODUCER 1: HAPTIC (multi-point: steering, seat pan, seat back)
# =============================================================================

class HapticProducer(ConstraintProducer):
    name = "haptic"

    HAPTIC_TASKS = [
        "ice_onset_front", "hydroplaning_onset", "front_tire_wear", "steering_gear_wear",
        "crosswind_gust", "rear_wheelspin_onset", "rear_axle_tramp", "driveline_torsional",
        "road_patch_length", "trailer_brake_imbalance",
        "frame_torsional_flex", "trailer_sway_onset", "cab_mount_wear",
    ]

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("haptic_suite", {})
        latency = suite.get("latency_sec", 2.0)

        # Per-channel noise floor
        noise = {
            Channel.HAPTIC_STEERING_WHEEL: self._steering_noise(suite),
            Channel.HAPTIC_SEAT_PAN:       self._seat_pan_noise(suite),
            Channel.HAPTIC_SEAT_BACK:      self._seat_back_noise(suite),
        }

        # Lifecycle: any present sensor adds embodied energy + cost
        if suite.get("seat_pan_present"):
            acc.emit_lifecycle(LifecycleCost("cab-floor accelerometer (seat pan)",
                                             embodied_energy_MWh=0.03, capital_cost_usd=150))
        if suite.get("seat_back_present"):
            acc.emit_lifecycle(LifecycleCost("frame-rail accelerometer (seat back)",
                                             embodied_energy_MWh=0.04, capital_cost_usd=200))
        if suite.get("steering_high_res"):
            acc.emit_lifecycle(LifecycleCost("high-res steering accelerometer",
                                             embodied_energy_MWh=0.02, capital_cost_usd=200))

        # Score each task
        for task_id in self.HAPTIC_TASKS:
            spec = HUMAN_BASELINE[task_id]
            n = noise[spec.channel]
            if math.isinf(n):
                cap = 0.0
                msg = f"channel {spec.channel.value} not instrumented"
                acc.emit_missing(f"sensor:{spec.channel.value}")
            else:
                snr = spec.threshold_value / n
                snr_f = snr_to_capability(snr)
                lat_f = latency_factor(spec.detection_time_sec, latency)
                cap = snr_f * lat_f
                msg = f"SNR={snr:.1f} latency_ratio={lat_f:.2f}"

            acc.emit(ConstraintResult(
                producer=self.name, task_id=task_id, channel=spec.channel,
                severity=capability_to_severity(cap), capability=cap,
                measured_value=n if not math.isinf(n) else 0.0,
                threshold=spec.threshold_value, message=msg,
            ))

    @staticmethod
    def _steering_noise(s: Dict) -> float:
        nd = s.get("steering_imu_noise_ug_per_sqrt_Hz", 100)
        if s.get("steering_high_res"):
            nd = min(nd, s.get("steering_high_res_noise_ug", 10))
        return haptic_noise_floor_mps2(nd, s.get("steering_imu_rate_Hz", 100))

    @staticmethod
    def _seat_pan_noise(s: Dict) -> float:
        if not s.get("seat_pan_present"): return float("inf")
        return haptic_noise_floor_mps2(s.get("seat_pan_noise_ug", 100),
                                       s.get("seat_pan_rate_Hz", 100))

    @staticmethod
    def _seat_back_noise(s: Dict) -> float:
        if not s.get("seat_back_present"): return float("inf")
        return haptic_noise_floor_mps2(s.get("seat_back_noise_ug", 100),
                                       s.get("seat_back_rate_Hz", 100))


# =============================================================================
# PRODUCER 2: ACOUSTIC
# =============================================================================

class AcousticProducer(ConstraintProducer):
    name = "acoustic"

    CAB_TASKS = ["engine_misfire", "transmission_whine", "tire_road_noise_change",
                 "brake_squeal", "cab_air_leak"]
    EXT_TASKS = ["tire_slip_sound", "wheel_bearing_wear", "road_surface_crunch",
                 "trailer_coupling_clatter"]

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("acoustic_suite", {})
        latency = suite.get("latency_sec", 2.0)

        cab_floor = suite.get("cab_mic_noise_dB", float("inf")) if suite.get("cab_mic_present") else float("inf")
        ext_floor = suite.get("ext_mic_noise_dB", float("inf")) if suite.get("ext_mics_present") else float("inf")

        if suite.get("cab_mic_present"):
            acc.emit_lifecycle(LifecycleCost("in-cab MEMS mic array",
                                             embodied_energy_MWh=0.005, capital_cost_usd=20))
        else:
            acc.emit_missing("acoustic_cab_mic")
        if suite.get("ext_mics_present"):
            acc.emit_lifecycle(LifecycleCost("wheel-arch + under-body mics",
                                             embodied_energy_MWh=0.035, capital_cost_usd=180))
        else:
            acc.emit_missing("acoustic_exterior_mics")

        for task_id in self.CAB_TASKS + self.EXT_TASKS:
            spec = HUMAN_BASELINE[task_id]
            floor = cab_floor if spec.channel == Channel.ACOUSTIC_CAB else ext_floor
            if math.isinf(floor):
                cap = 0.0
                msg = "no microphone present"
            else:
                snr_dB = spec.threshold_value - floor
                cap_snr = max(0.0, min(1.0, (snr_dB - 3) / 9))
                cap = cap_snr * latency_factor(spec.detection_time_sec, latency)
                msg = f"SNR={snr_dB:.1f} dB"
            acc.emit(ConstraintResult(
                producer=self.name, task_id=task_id, channel=spec.channel,
                severity=capability_to_severity(cap), capability=cap,
                threshold=spec.threshold_value, message=msg,
            ))


# =============================================================================
# PRODUCER 3: OLFACTORY
# =============================================================================

class OlfactoryProducer(ConstraintProducer):
    name = "olfactory"

    CAB_TASKS = ["burning_motor_fluid", "coolant_leak", "electrical_burn", "load_spoilage"]
    EXT_TASKS = ["petrichor_rain", "asphalt_softening", "trailer_brake_lining", "hot_rubber"]

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("olfactory_suite", {})
        cab_limit = suite.get("cab_detection_limit_ppb", float("inf")) if suite.get("cab_sensors_present") else float("inf")
        ext_limit = suite.get("ext_detection_limit_ppb", float("inf")) if suite.get("ext_sensors_present") else float("inf")
        sample_period = suite.get("sample_period_sec", 10.0)
        decision_lat  = suite.get("decision_latency_sec", 30.0)
        sensor_resp   = suite.get("sensor_response_sec", 5.0)
        total_lat = sample_period + decision_lat + sensor_resp

        if suite.get("cab_sensors_present"):
            acc.emit_lifecycle(LifecycleCost("cab gas sensor array",
                                             embodied_energy_MWh=0.002, capital_cost_usd=120))
        else:
            acc.emit_missing("olfactory_cab")
        if suite.get("ext_sensors_present"):
            acc.emit_lifecycle(LifecycleCost("exterior gas sensor pod",
                                             embodied_energy_MWh=0.003, capital_cost_usd=200))
        else:
            acc.emit_missing("olfactory_exterior")

        for task_id in self.CAB_TASKS + self.EXT_TASKS:
            spec = HUMAN_BASELINE[task_id]
            limit = cab_limit if spec.channel == Channel.OLFACTORY_CAB else ext_limit
            if math.isinf(limit) or limit <= 0:
                cap = 0.0
                msg = "no chemical sensor present"
            else:
                # Capability = how close detection limit is to human threshold
                ratio = spec.threshold_value / (limit * 2.0)  # 2x penalty for cross-sensitivity
                cap_sens = max(0.0, min(1.0, ratio))
                cap_lat  = max(0.0, min(1.0, spec.detection_time_sec / total_lat))
                cap = cap_sens * cap_lat
                msg = f"sensor_limit={limit:.1f}ppb vs human={spec.threshold_value:.3f}ppb"
            acc.emit(ConstraintResult(
                producer=self.name, task_id=task_id, channel=spec.channel,
                severity=capability_to_severity(cap), capability=cap,
                threshold=spec.threshold_value, message=msg,
            ))


# =============================================================================
# PRODUCER 4: VISUAL FOULING (ecological validity)
# =============================================================================

class VisualFoulingProducer(ConstraintProducer):
    name = "visual_fouling"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        env = ctx.get("environment", {})
        cleaning = ctx.get("cleaning_system", {})

        # Aggregate fouling pressure
        fouling_score = (
            (env.get("insect_factor", 1.0) - 1.0) * 0.3 +
            min(1.0, env.get("dust_aqi", 0) / 200.0) * 0.3 +
            min(1.0, env.get("wildfire_smoke_aqi", 0) / 200.0) * 0.2 +
            (0.4 if env.get("ash_fall") else 0.0) +
            min(1.0, env.get("snow_rate_mmh", 0) / 5.0) * 0.3 +
            (0.5 if env.get("freezing_rain") else 0.0)
        )
        fouling_score = max(0.0, min(1.0, fouling_score))

        cleaning_eff = cleaning.get("effectiveness", 0.7)
        residual_fouling = fouling_score * (1.0 - cleaning_eff)
        transmission = math.exp(-2.0 * residual_fouling)

        # Lifecycle for cleaning system
        if cleaning.get("present", True):
            acc.emit_lifecycle(LifecycleCost(
                f"sensor cleaning system ({cleaning.get('type', 'wiper+heater')})",
                embodied_energy_MWh=cleaning.get("embodied_MWh", 0.1),
                operational_kWh_per_shift=cleaning.get("kWh_per_shift", 0.5),
                capital_cost_usd=cleaning.get("cost_usd", 1500),
            ))

        cap = transmission
        for ch in (Channel.VISUAL_FORWARD_NEAR, Channel.VISUAL_FORWARD_FAR,
                   Channel.VISUAL_SURROUND, Channel.VISUAL_PERIPHERAL):
            acc.emit(ConstraintResult(
                producer=self.name, task_id=f"transmission_{ch.value}",
                channel=ch,
                severity=capability_to_severity(cap),
                capability=cap, measured_value=transmission,
                message=f"fouling={fouling_score:.2f} cleaning_eff={cleaning_eff:.2f}",
            ))


# =============================================================================
# PRODUCER 5: PERIPHERAL TRAJECTORY (long-range visual)
# =============================================================================

class PeripheralTrajectoryProducer(ConstraintProducer):
    name = "peripheral_trajectory"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("trajectory_suite", {})
        fwd_range_km   = suite.get("forward_range_brake_light_km", 0.8)
        fwd_fov        = suite.get("forward_fov_deg", 50)
        surround_fov   = suite.get("surround_fov_deg", 190)
        surround_mp    = suite.get("surround_resolution_mp", 2)
        pred_horizon_s = suite.get("prediction_horizon_sec", 5.0)
        latency_total  = suite.get("perception_latency_sec", 0.3) + suite.get("planning_latency_sec", 0.2)

        # distant brake light (6.5 km baseline)
        cap_dbl = min(1.0, fwd_range_km / 6.5)
        if suite.get("forward_resolution_mp", 8) < 12: cap_dbl *= 0.8

        # ramp merge anticipation
        fov_ok   = fwd_fov >= 80 or surround_fov >= 180
        range_ok = fwd_range_km >= 0.8
        pred_ok  = pred_horizon_s >= 10
        cap_rma  = (0.4 if fov_ok else 0) + (0.3 if range_ok else 0) + (0.3 if pred_ok else 0)

        # peripheral VRU
        cap_per = 0.0 if surround_fov < 180 else (0.8 if surround_mp >= 4 else 0.5)

        # shockwave prediction
        pred_horizon_factor = min(1.0, pred_horizon_s / 20.0)
        latency_pen = max(0.0, 1.0 - latency_total / 1.0)
        cap_swp = cap_dbl * pred_horizon_factor * latency_pen

        for tid, ch, cap in [
            ("distant_brake_light",     Channel.VISUAL_FORWARD_FAR, cap_dbl),
            ("ramp_merge_anticipation", Channel.VISUAL_FORWARD_FAR, cap_rma),
            ("peripheral_vru",          Channel.VISUAL_PERIPHERAL,  cap_per),
            ("shockwave_prediction",    Channel.VISUAL_FORWARD_FAR, cap_swp),
        ]:
            acc.emit(ConstraintResult(
                producer=self.name, task_id=tid, channel=ch,
                severity=capability_to_severity(cap), capability=cap,
            ))

        if cap_dbl < 0.8: acc.emit_missing("long_range_telephoto_camera")
        if cap_per < 0.8: acc.emit_missing("high_res_peripheral_camera")
        if cap_swp < 0.8: acc.emit_missing("extended_prediction_horizon")


# =============================================================================
# PRODUCER 6: RELATIONAL INFERENCE
# =============================================================================

class RelationalProducer(ConstraintProducer):
    name = "relational"

    TASKS = ["flagger_signal", "police_stop", "emergency_yield", "animal_intent",
             "dock_worker_gesture", "child_near_road", "aggressive_driver", "merge_negotiation"]

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("relational_suite", {})
        intent     = suite.get("intent_model", False)
        procedural = suite.get("procedural_engine", False)
        gesture    = suite.get("gesture_recognition", False)
        animal     = suite.get("animal_pose", False)
        child      = suite.get("child_behavior", False)
        aggro      = suite.get("aggressive_detector", False)
        multi_ag   = suite.get("multi_agent_planner", False)
        latency    = suite.get("inference_latency_sec", 0.5)

        # Required-component map (from your existing module)
        requires = {
            "flagger_signal":      [intent, procedural, gesture],
            "police_stop":         [intent, procedural],
            "emergency_yield":     [intent, procedural],
            "animal_intent":       [intent, animal],
            "dock_worker_gesture": [intent, procedural, gesture, multi_ag],
            "child_near_road":     [intent, child],
            "aggressive_driver":   [intent, aggro, multi_ag],
            "merge_negotiation":   [intent, multi_ag],
        }
        for task_id, components in requires.items():
            spec = HUMAN_BASELINE[task_id]
            if not all(components):
                cap = 0.0
                missing_count = sum(1 for c in components if not c)
                msg = f"{missing_count}/{len(components)} required components missing"
            else:
                cap = 0.85 * latency_factor(spec.detection_time_sec, latency)
                msg = "all components present"
            acc.emit(ConstraintResult(
                producer=self.name, task_id=task_id, channel=Channel.RELATIONAL_INFERENCE,
                severity=capability_to_severity(cap), capability=cap, message=msg,
            ))

        for flag, miss in [(intent, "intent_model"), (procedural, "procedural_engine"),
                           (gesture, "gesture_recognition"), (animal, "animal_pose_model"),
                           (child, "child_behavior_model"), (aggro, "aggressive_detector"),
                           (multi_ag, "multi_agent_planner")]:
            if not flag: acc.emit_missing(miss)


# =============================================================================
# PRODUCER 7: ROAD SURFACE
# =============================================================================

class RoadSurfaceProducer(ConstraintProducer):
    name = "road_surface"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        surface = ctx.get("road_surface", {})
        suite   = ctx.get("surface_suite", {})

        iri        = surface.get("iri_m_per_km", 2.0)
        potholes   = surface.get("pothole_count_per_km", 0.0)
        bridge_gap = surface.get("bridge_joint_gap_mm", 0.0)
        rail_cond  = surface.get("bridge_rail_condition", 1.0)

        scanner    = suite.get("road_scanner_present", False)
        avoid      = suite.get("active_pothole_avoidance", False)
        adapt      = suite.get("roughness_adaptive_speed", False)
        rail_det   = suite.get("bridge_rail_detection", False)

        # Pothole capability
        if potholes > 0:
            cap_p = 0.9 if (avoid and scanner) else (0.4 if avoid else 0.0)
            acc.emit(ConstraintResult(
                producer=self.name, task_id="pothole_avoidance",
                channel=Channel.VISUAL_FORWARD_NEAR,
                severity=capability_to_severity(cap_p), capability=cap_p,
                measured_value=potholes, message=f"{potholes:.1f} potholes/km",
            ))
            if not avoid: acc.emit_missing("active_pothole_avoidance")

        # Roughness capability
        if iri > 3.0:
            cap_r = 0.9 if adapt else 0.1
            acc.emit(ConstraintResult(
                producer=self.name, task_id="roughness_adaptation",
                channel=Channel.HAPTIC_SEAT_PAN,
                severity=capability_to_severity(cap_r), capability=cap_r,
                measured_value=iri, message=f"IRI={iri:.1f} m/km",
            ))
            if not adapt: acc.emit_missing("roughness_adaptive_speed")

        # Bridge joint
        if bridge_gap > 20:
            cap_j = 0.85 if scanner else 0.1
            acc.emit(ConstraintResult(
                producer=self.name, task_id="bridge_joint_handling",
                channel=Channel.VISUAL_FORWARD_NEAR,
                severity=capability_to_severity(cap_j), capability=cap_j,
                measured_value=bridge_gap, message=f"joint gap {bridge_gap}mm",
            ))

        # Bridge rail
        if rail_cond < 0.8:
            cap_br = 0.8 if rail_det else 0.0
            acc.emit(ConstraintResult(
                producer=self.name, task_id="bridge_rail_clearance",
                channel=Channel.VISUAL_SURROUND,
                severity=capability_to_severity(cap_br), capability=cap_br,
                measured_value=rail_cond, message=f"rail condition {rail_cond:.2f}",
            ))
            if not rail_det: acc.emit_missing("bridge_rail_detection")


# =============================================================================
# PRODUCER 8: AUTHORITY INTERACTION
# =============================================================================

class AuthorityProducer(ConstraintProducer):
    name = "authority_interaction"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        suite = ctx.get("authority_suite", {})

        components = {
            "authority_gesture":        suite.get("authority_gesture_recognition", False),
            "vehicle_constraint_model": suite.get("vehicle_constraint_model", False),
            "infrastructure_db":        suite.get("infrastructure_db_access", False),
            "authority_override":       suite.get("authority_override_rule", False),
            "external_refusal":         suite.get("external_refusal_signal", False),
            "route_assessment":         suite.get("can_assess_route_ahead", False),
        }
        critical = ["vehicle_constraint_model", "infrastructure_db", "authority_override"]
        latency = suite.get("latency_sec", 5.0)

        if not all(components[c] for c in critical):
            cap = 0.0
        else:
            present = sum(1 for v in components.values() if v)
            human_total = 5.5
            cap = (present / len(components)) * latency_factor(human_total, latency)

        acc.emit(ConstraintResult(
            producer=self.name, task_id="authority_unsafe_redirect",
            channel=Channel.PROCEDURAL_KNOWLEDGE,
            severity=capability_to_severity(cap), capability=cap,
            message=f"{sum(components.values())}/{len(components)} components present",
        ))
        for cname, present in components.items():
            if not present: acc.emit_missing(f"authority_{cname}")


# =============================================================================
# PRODUCER 9: CORRIDOR FEASIBILITY (hard environmental gates)
# =============================================================================

class CorridorFeasibilityProducer(ConstraintProducer):
    name = "corridor_feasibility"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        env = ctx.get("environment", {})
        seg = ctx.get("segment", {})

        # Wind safety
        wind_sustained = env.get("wind_speed_kmh", 0)
        wind_gust      = env.get("wind_gust_kmh", 0)
        if wind_gust > 100 or wind_sustained > 80:
            sev, cap = Severity.NO_GO, 0.0
        elif wind_gust > 70 and wind_sustained > 50:
            sev, cap = Severity.HARD_LIMIT, 0.3
        else:
            sev, cap = Severity.PASS, 1.0
        acc.emit(ConstraintResult(producer=self.name, task_id="wind_safety",
            channel=None, severity=sev, capability=cap,
            measured_value=max(wind_gust, wind_sustained),
            message=f"wind {wind_sustained}/{wind_gust} km/h"))

        # Flooding
        if seg.get("flood_zone") and env.get("flood_warning"):
            acc.emit(ConstraintResult(producer=self.name, task_id="flood_zone_warning",
                channel=None, severity=Severity.NO_GO, capability=0.0,
                message="flood warning in flood zone"))
        if env.get("water_depth_m", 0) > 0.1:
            acc.emit(ConstraintResult(producer=self.name, task_id="water_on_road",
                channel=None, severity=Severity.NO_GO, capability=0.0,
                measured_value=env["water_depth_m"], message="water on road >10cm"))

        # Bridge integrity
        load = seg.get("bridge_load_rating_ton", 99)
        if load < 40:
            if seg.get("bridge_scour_critical") and env.get("flood_warning"):
                sev, cap = Severity.NO_GO, 0.0
            else:
                sev, cap = Severity.HARD_LIMIT, 0.3
            acc.emit(ConstraintResult(producer=self.name, task_id="bridge_integrity",
                channel=None, severity=sev, capability=cap,
                measured_value=load, message=f"bridge rating {load}t"))

        # Lightning / EMP risk
        lr = env.get("lightning_risk", 0.0)
        if lr > 0.8:
            acc.emit(ConstraintResult(producer=self.name, task_id="lightning_risk",
                channel=None, severity=Severity.HARD_LIMIT, capability=0.3,
                measured_value=lr, message="severe lightning risk"))

        # Tornado proxy
        if wind_gust > 120:
            acc.emit(ConstraintResult(producer=self.name, task_id="tornado_proxy",
                channel=None, severity=Severity.NO_GO, capability=0.0,
                measured_value=wind_gust, message="extreme gust; possible tornado"))

        # Black ice
        t  = env.get("temperature_C", 20)
        td = env.get("dewpoint_C", 0)
        if -2 <= t <= 2 and td >= t - 1:
            acc.emit(ConstraintResult(producer=self.name, task_id="black_ice_risk",
                channel=None, severity=Severity.HARD_LIMIT, capability=0.3,
                measured_value=t, message="black ice probable"))

        # Connectivity
        if env.get("gps_jamming_probability", 0) > 0.5 or seg.get("gps_reliability", 1) < 0.5:
            acc.emit(ConstraintResult(producer=self.name, task_id="gps_unreliable",
                channel=Channel.GPS, severity=Severity.HARD_LIMIT, capability=0.3,
                message="GPS unreliable"))


# =============================================================================
# PRODUCER 10: CROSS-CHANNEL VERIFICATION
# =============================================================================

CRITICAL_STATE_DETECTORS: Dict[str, List[Channel]] = {
    "engine_overheating":    [Channel.OLFACTORY_CAB, Channel.ACOUSTIC_CAB, Channel.THERMAL_INTERIOR],
    "brake_drag_or_fire":    [Channel.OLFACTORY_EXTERIOR, Channel.OLFACTORY_CAB,
                              Channel.ACOUSTIC_EXTERIOR, Channel.HAPTIC_STEERING_WHEEL,
                              Channel.THERMAL_EXTERIOR],
    "tire_delamination":     [Channel.HAPTIC_STEERING_WHEEL, Channel.HAPTIC_SEAT_PAN,
                              Channel.ACOUSTIC_EXTERIOR, Channel.OLFACTORY_EXTERIOR],
    "tire_ice_onset":        [Channel.HAPTIC_STEERING_WHEEL, Channel.HAPTIC_SEAT_PAN,
                              Channel.ACOUSTIC_EXTERIOR, Channel.VESTIBULAR_LINEAR],
    "trailer_sway":          [Channel.HAPTIC_SEAT_BACK, Channel.HAPTIC_SEAT_PAN,
                              Channel.VESTIBULAR_ROTATIONAL, Channel.VISUAL_SURROUND],
    "load_shift":            [Channel.HAPTIC_SEAT_BACK, Channel.OLFACTORY_CAB,
                              Channel.VISUAL_SURROUND, Channel.VESTIBULAR_LINEAR],
    "road_washout_ahead":    [Channel.OLFACTORY_EXTERIOR, Channel.OLFACTORY_CAB,
                              Channel.VISUAL_FORWARD_FAR],
    "asphalt_softening":     [Channel.OLFACTORY_EXTERIOR, Channel.HAPTIC_STEERING_WHEEL,
                              Channel.VISUAL_FORWARD_FAR, Channel.THERMAL_EXTERIOR],
}


class CrossChannelProducer(ConstraintProducer):
    name = "cross_channel_verification"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        # Channels considered "present" = any channel that any other producer
        # emitted a non-zero capability constraint for, plus channels in suite hints.
        present: Set[Channel] = set()
        for c in acc.constraints:
            if c.channel and c.capability > 0.1:
                present.add(c.channel)

        for state, detectors in CRITICAL_STATE_DETECTORS.items():
            available = [d for d in detectors if d in present]
            for disruption in Disruption:
                if disruption == Disruption.NONE: continue
                lost = channels_disabled_by(disruption)
                survivors = [d for d in available if d not in lost]
                if len(survivors) == 0:
                    acc.emit(ConstraintResult(
                        producer=self.name,
                        task_id=f"redundancy_{state}_{disruption.value}",
                        channel=None, severity=Severity.NO_GO, capability=0.0,
                        message=f"{state} loses ALL channels under {disruption.value}",
                    ))
                elif len(survivors) == 1:
                    acc.emit(ConstraintResult(
                        producer=self.name,
                        task_id=f"redundancy_{state}_{disruption.value}",
                        channel=None, severity=Severity.HARD_LIMIT, capability=0.3,
                        message=f"{state} single point: {survivors[0].value}",
                    ))


# =============================================================================
# CASCADE RUNNER
# =============================================================================

ALL_PRODUCERS: List[ConstraintProducer] = [
    HapticProducer(), AcousticProducer(), OlfactoryProducer(),
    VisualFoulingProducer(), PeripheralTrajectoryProducer(),
    RelationalProducer(), RoadSurfaceProducer(), AuthorityProducer(),
    CorridorFeasibilityProducer(),
]
if _HAS_VESTIBULAR:
    ALL_PRODUCERS.append(VestibularProducer())
ALL_PRODUCERS.append(CrossChannelProducer())  # MUST run last; reads from accumulator


def run_cascade(
    ctx: Dict[str, Any],
    producers: Optional[List[ConstraintProducer]] = None,
) -> Tuple[ReadinessReport, AuditAccumulator]:
    if producers is None:
        producers = ALL_PRODUCERS
    acc = AuditAccumulator()
    for p in producers:
        p.run(ctx, acc)
    return ReadinessGate().evaluate(acc), acc


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    # Two scenarios: basic AV truck, fully-equipped AV truck.
    # Same hostile environment: insect bloom + smoke + bad road + ice risk + flagger.

    hostile_env = {
        "insect_factor": 2.0, "dust_aqi": 50, "wildfire_smoke_aqi": 150,
        "snow_rate_mmh": 0, "freezing_rain": False, "ash_fall": False,
        "wind_speed_kmh": 30, "wind_gust_kmh": 50,
        "temperature_C": 1, "dewpoint_C": 0,
        "lightning_risk": 0.1, "flood_warning": False, "water_depth_m": 0,
        "gps_jamming_probability": 0.0,
    }
    hostile_seg = {
        "flood_zone": False, "bridge_load_rating_ton": 99,
        "bridge_scour_critical": False, "gps_reliability": 1.0,
    }
    hostile_surface = {
        "iri_m_per_km": 4.5, "pothole_count_per_km": 3,
        "bridge_joint_gap_mm": 40, "bridge_rail_condition": 0.6,
    }

    basic_ctx = {
        "environment": hostile_env, "segment": hostile_seg, "road_surface": hostile_surface,
        "haptic_suite":     {"steering_imu_noise_ug_per_sqrt_Hz": 100, "latency_sec": 2.0},
        "acoustic_suite":   {"latency_sec": 1.0},
        "olfactory_suite":  {},
        "cleaning_system":  {"present": True, "effectiveness": 0.7, "embodied_MWh": 0.1,
                             "kWh_per_shift": 0.5, "cost_usd": 1500, "type": "wiper+heater"},
        "trajectory_suite": {"forward_range_brake_light_km": 0.8, "forward_fov_deg": 50,
                             "forward_resolution_mp": 8, "surround_fov_deg": 190,
                             "surround_resolution_mp": 2, "prediction_horizon_sec": 5.0,
                             "perception_latency_sec": 0.3, "planning_latency_sec": 0.2},
        "relational_suite": {},
        "surface_suite":    {},
        "authority_suite":  {},
        "vestibular_suite": {
            "linear_imu_present": True, "linear_noise_ug_per_sqrt_Hz": 100,
            "linear_sample_rate_Hz": 100, "gyro_present": True,
            "gyro_arw_deg_per_sqrt_hr": 1.0, "gyro_sample_rate_Hz": 100,
            "fuses_with_steering_angle": False, "fuses_with_suspension": False,
            "primary_diagnostic_channel": False, "latency_sec": 1.0,
            "trailer_gyro_present": False,
        },
    }

    advanced_ctx = {
        **basic_ctx,
        "haptic_suite": {
            "steering_imu_noise_ug_per_sqrt_Hz": 100, "steering_high_res": True,
            "steering_high_res_noise_ug": 10, "steering_imu_rate_Hz": 200,
            "seat_pan_present": True, "seat_pan_noise_ug": 50, "seat_pan_rate_Hz": 200,
            "seat_back_present": True, "seat_back_noise_ug": 50, "seat_back_rate_Hz": 200,
            "latency_sec": 0.4,
        },
        "acoustic_suite": {
            "cab_mic_present": True, "cab_mic_noise_dB": 25,
            "ext_mics_present": True, "ext_mic_noise_dB": 30, "latency_sec": 0.4,
        },
        "olfactory_suite": {
            "cab_sensors_present": True, "cab_detection_limit_ppb": 50,
            "ext_sensors_present": True, "ext_detection_limit_ppb": 100,
            "sample_period_sec": 5.0, "decision_latency_sec": 10.0, "sensor_response_sec": 3.0,
        },
        "trajectory_suite": {
            "forward_range_brake_light_km": 6.5, "forward_fov_deg": 100,
            "forward_resolution_mp": 16, "surround_fov_deg": 210,
            "surround_resolution_mp": 6, "prediction_horizon_sec": 20.0,
            "perception_latency_sec": 0.1, "planning_latency_sec": 0.1,
        },
        "relational_suite": {
            "intent_model": True, "procedural_engine": True, "gesture_recognition": True,
            "animal_pose": True, "child_behavior": True, "aggressive_detector": True,
            "multi_agent_planner": True, "inference_latency_sec": 0.3,
        },
        "surface_suite": {
            "road_scanner_present": True, "active_pothole_avoidance": True,
            "roughness_adaptive_speed": True, "bridge_rail_detection": True,
        },
        "authority_suite": {
            "authority_gesture_recognition": True, "vehicle_constraint_model": True,
            "infrastructure_db_access": True, "authority_override_rule": True,
            "external_refusal_signal": True, "can_assess_route_ahead": True,
            "latency_sec": 2.0,
        },
        "vestibular_suite": {
            "linear_imu_present": True, "linear_noise_ug_per_sqrt_Hz": 30,
            "linear_sample_rate_Hz": 200, "gyro_present": True,
            "gyro_arw_deg_per_sqrt_hr": 0.1, "gyro_sample_rate_Hz": 200,
            "fuses_with_steering_angle": True, "fuses_with_suspension": True,
            "fuses_with_individual_wheel_speeds": True,
            "primary_diagnostic_channel": True, "latency_sec": 0.2,
            "trailer_gyro_present": True,
        },
    }

    print("=" * 70)
    print("UNIFIED AUDIT CASCADE")
    print("=" * 70)

    for label, ctx in [("BASIC AV TRUCK", basic_ctx), ("FULLY-EQUIPPED AV TRUCK", advanced_ctx)]:
        print(f"\n--- {label} ---")
        report, acc = run_cascade(ctx)
        print(f"Overall pass:           {report.overall_pass}")
        print(f"Feasibility index:      {report.feasibility_index:.2f}")
        print(f"Constraints emitted:    {report.total_count}")
        print(f"  PASS:                 {report.passed_count}")
        print(f"  SOFT:                 {len(report.soft_limits)}")
        print(f"  HARD:                 {len(report.hard_limits)}")
        print(f"  NO-GO:                {len(report.no_go_constraints)}")
        print(f"Limiting:               {report.limiting_producer} / {report.limiting_task}")
        print(f"Missing capabilities:   {len(report.missing_caps)}")
        print(f"Total embodied MWh:     {report.total_embodied_MWh:.3f}")
        print(f"Total capital USD:      ${report.total_capital_usd:.0f}")
        print(f"Total operational kWh:  {report.total_operational_kWh:.2f}")
        if report.no_go_constraints:
            print("\nFirst 5 NO-GO:")
            for c in report.no_go_constraints[:5]:
                print(f"  [{c.producer}] {c.task_id}: {c.message}")

    print("\n" + "=" * 70)
    print("CASCADE OK")
    print("=" * 70)
