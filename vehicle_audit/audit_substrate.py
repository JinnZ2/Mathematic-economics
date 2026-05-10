"""
audit_substrate.py

Canonical substrate for the autonomous-vehicle audit cascade.

ENERGY FLOW:

    physical_reality
          |
          v
    [L1: sensory channels]  ----.
    [L1: relational tasks ]      |--> ConstraintProducer.run()
    [L1: surface tasks    ]      |        emits ConstraintResult
    [L1: authority tasks  ]      |              |
    [L1: operational tasks]  ---'               v
                                          AuditAccumulator
                                                |
                                                v
                                          ReadinessGate
                                                |
                                                v
                                       feasibility_decision

PURPOSE:

Every audit module imports from THIS file. No module redefines
SensoryChannel, DiagnosticTask, HumanBaseline, or LifecycleCost.
Modules emit ConstraintResult into a shared AuditAccumulator.
ReadinessGate makes one decision from the accumulated results.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
import math


# =============================================================================
# 1. CANONICAL CHANNELS
# =============================================================================
# Every sensory or inferential pathway the audit cascade reasons about.
# Modules MUST use these names; do not redefine.

class Channel(Enum):
    # ---- Haptic (vibration / proprioceptive) ----
    HAPTIC_STEERING_WHEEL  = "haptic_steering_wheel"
    HAPTIC_SEAT_PAN        = "haptic_seat_pan"
    HAPTIC_SEAT_BACK       = "haptic_seat_back"
    HAPTIC_PEDAL           = "haptic_pedal"           # brake/throttle feedback

    # ---- Vestibular (whole-body motion) ----
    VESTIBULAR_LINEAR      = "vestibular_linear"      # otolith analogue
    VESTIBULAR_ROTATIONAL  = "vestibular_rotational"  # canal analogue

    # ---- Acoustic ----
    ACOUSTIC_CAB           = "acoustic_cab"
    ACOUSTIC_EXTERIOR      = "acoustic_exterior"

    # ---- Olfactory / chemical ----
    OLFACTORY_CAB          = "olfactory_cab"
    OLFACTORY_EXTERIOR     = "olfactory_exterior"

    # ---- Visual ----
    VISUAL_FORWARD_NEAR    = "visual_forward_near"    # 0-200m, high res
    VISUAL_FORWARD_FAR     = "visual_forward_far"     # 200m-7km, telephoto
    VISUAL_SURROUND        = "visual_surround"        # 360 panoramic
    VISUAL_PERIPHERAL      = "visual_peripheral"      # motion detection >90deg

    # ---- Thermal / radiative ----
    THERMAL_EXTERIOR       = "thermal_exterior"
    THERMAL_INTERIOR       = "thermal_interior"

    # ---- Inferential / cognitive ----
    RELATIONAL_INFERENCE   = "relational_inference"   # intent, multi-agent
    PROCEDURAL_KNOWLEDGE   = "procedural_knowledge"   # cultural / legal scripts
    TEMPORAL_PATTERN       = "temporal_pattern"       # long-horizon baseline drift
    SELF_MONITORING        = "self_monitoring"        # fatigue / integrity analogue

    # ---- Infrastructure / external ----
    GPS                    = "gps"
    CELLULAR               = "cellular"
    INFRASTRUCTURE_DB      = "infrastructure_db"      # bridge ratings, clearances


# =============================================================================
# 2. CANONICAL CHANNEL VULNERABILITY (replaces ChannelProperties)
# =============================================================================

@dataclass(frozen=True)
class ChannelVulnerability:
    requires_power:             bool = True
    requires_data_link:         bool = False
    requires_gps:               bool = False
    susceptible_to_emp:         bool = True
    susceptible_to_fouling:     bool = False
    susceptible_to_solar_storm: bool = False


CHANNEL_VULNERABILITY: Dict[Channel, ChannelVulnerability] = {
    Channel.HAPTIC_STEERING_WHEEL:  ChannelVulnerability(susceptible_to_emp=True),
    Channel.HAPTIC_SEAT_PAN:        ChannelVulnerability(),
    Channel.HAPTIC_SEAT_BACK:       ChannelVulnerability(),
    Channel.HAPTIC_PEDAL:           ChannelVulnerability(),
    Channel.VESTIBULAR_LINEAR:      ChannelVulnerability(),
    Channel.VESTIBULAR_ROTATIONAL:  ChannelVulnerability(),
    Channel.ACOUSTIC_CAB:           ChannelVulnerability(),
    Channel.ACOUSTIC_EXTERIOR:      ChannelVulnerability(susceptible_to_fouling=True),
    Channel.OLFACTORY_CAB:          ChannelVulnerability(susceptible_to_emp=False),
    Channel.OLFACTORY_EXTERIOR:     ChannelVulnerability(susceptible_to_emp=False,
                                                        susceptible_to_fouling=True),
    Channel.VISUAL_FORWARD_NEAR:    ChannelVulnerability(susceptible_to_fouling=True),
    Channel.VISUAL_FORWARD_FAR:     ChannelVulnerability(susceptible_to_fouling=True),
    Channel.VISUAL_SURROUND:        ChannelVulnerability(susceptible_to_fouling=True),
    Channel.VISUAL_PERIPHERAL:      ChannelVulnerability(susceptible_to_fouling=True),
    Channel.THERMAL_EXTERIOR:       ChannelVulnerability(susceptible_to_fouling=True),
    Channel.THERMAL_INTERIOR:       ChannelVulnerability(),
    Channel.RELATIONAL_INFERENCE:   ChannelVulnerability(),
    Channel.PROCEDURAL_KNOWLEDGE:   ChannelVulnerability(susceptible_to_emp=False),
    Channel.TEMPORAL_PATTERN:       ChannelVulnerability(),
    Channel.SELF_MONITORING:        ChannelVulnerability(),
    Channel.GPS:                    ChannelVulnerability(requires_gps=True,
                                                        susceptible_to_solar_storm=True),
    Channel.CELLULAR:               ChannelVulnerability(requires_data_link=True),
    Channel.INFRASTRUCTURE_DB:      ChannelVulnerability(requires_data_link=True),
}


# =============================================================================
# 3. DISRUPTION SCENARIOS (canonical)
# =============================================================================

class Disruption(Enum):
    NONE                  = "none"
    GPS_LOSS              = "gps_loss"
    CONNECTIVITY_LOSS     = "connectivity_loss"
    EMP                   = "emp"
    SENSOR_DRIFT          = "sensor_drift"
    FOULING_HEAVY         = "fouling_heavy"
    POWER_LOSS_PARTIAL    = "power_loss_partial"
    SOLAR_STORM           = "solar_storm"


def channels_disabled_by(disruption: Disruption) -> Set[Channel]:
    """Return set of channels degraded/disabled under disruption."""
    if disruption == Disruption.NONE:
        return set()
    out: Set[Channel] = set()
    for ch, v in CHANNEL_VULNERABILITY.items():
        if disruption == Disruption.GPS_LOSS              and v.requires_gps:                out.add(ch)
        if disruption == Disruption.CONNECTIVITY_LOSS     and v.requires_data_link:          out.add(ch)
        if disruption == Disruption.EMP                   and v.susceptible_to_emp:          out.add(ch)
        if disruption == Disruption.SENSOR_DRIFT          and v.requires_power:              out.add(ch)
        if disruption == Disruption.FOULING_HEAVY         and v.susceptible_to_fouling:      out.add(ch)
        if disruption == Disruption.POWER_LOSS_PARTIAL    and v.requires_power:              out.add(ch)
        if disruption == Disruption.SOLAR_STORM           and v.susceptible_to_solar_storm:  out.add(ch)
    return out


# =============================================================================
# 4. CANONICAL THRESHOLD UNITS
# =============================================================================
# Different channels measure different things. Keep them explicit, never mix.

class ThresholdUnit(Enum):
    ACCEL_RMS_MPS2     = "m/s^2 RMS"          # haptic, vestibular
    SPL_DB             = "dB SPL"             # acoustic
    CONCENTRATION_PPB  = "ppb"                # olfactory
    LUMINANCE_CONTRAST = "Weber fraction"     # visual contrast
    RANGE_M            = "m"                  # detection range
    ANGLE_DEG          = "deg"                # FOV / off-axis
    PROBABILITY        = "probability 0-1"    # inference accuracy
    LATENCY_SEC        = "s"                  # response time


# =============================================================================
# 5. UNIFIED HUMAN BASELINE REGISTRY
# =============================================================================

@dataclass(frozen=True)
class HumanThreshold:
    """One row in the mastery-driver threshold table."""
    task_id:            str           # canonical task name
    channel:            Channel
    unit:               ThresholdUnit
    threshold_value:    float
    detection_time_sec: float
    notes:              str = ""


# Single registry. Modules look up by task_id; they do NOT redefine.
HUMAN_BASELINE: Dict[str, HumanThreshold] = {}


def register_baseline(*thresholds: HumanThreshold) -> None:
    """Register one or more thresholds. Raises if task_id collides."""
    for t in thresholds:
        if t.task_id in HUMAN_BASELINE:
            existing = HUMAN_BASELINE[t.task_id]
            if existing != t:
                raise ValueError(
                    f"Baseline collision for task_id '{t.task_id}': "
                    f"{existing} vs {t}"
                )
        HUMAN_BASELINE[t.task_id] = t


# =============================================================================
# 6. CONSTRAINT RESULT (the universal output of every audit module)
# =============================================================================

class Severity(Enum):
    PASS         = "pass"
    SOFT_LIMIT   = "soft_limit"     # reduced performance, operable
    HARD_LIMIT   = "hard_limit"     # restrict speed / following / ODD
    NO_GO        = "no_go"          # infeasible


SEVERITY_INDEX: Dict[Severity, float] = {
    Severity.PASS:       1.0,
    Severity.SOFT_LIMIT: 0.7,
    Severity.HARD_LIMIT: 0.3,
    Severity.NO_GO:      0.0,
}


@dataclass
class ConstraintResult:
    producer:        str             # which audit module emitted this
    task_id:         str             # canonical task name (or "" for system-level)
    channel:         Optional[Channel]
    severity:        Severity
    capability:      float           # 0-1
    threshold:       float = 0.8     # pass cutoff for capability
    measured_value:  float = 0.0
    message:         str = ""

    @property
    def passed(self) -> bool:
        return self.severity == Severity.PASS


# =============================================================================
# 7. LIFECYCLE COST (single accumulator across all modules)
# =============================================================================

@dataclass
class LifecycleCost:
    name:                       str
    embodied_energy_MWh:        float = 0.0
    operational_kWh_per_shift:  float = 0.0
    capital_cost_usd:           float = 0.0
    maintenance_hours_per_year: float = 0.0
    co2_kg_per_shift:           float = 0.0
    notes:                      str = ""


# =============================================================================
# 8. AUDIT ACCUMULATOR (the shared bus)
# =============================================================================

@dataclass
class AuditAccumulator:
    """All audit modules emit results here. ReadinessGate consumes."""
    constraints:    List[ConstraintResult] = field(default_factory=list)
    lifecycle:      List[LifecycleCost]    = field(default_factory=list)
    missing_caps:   Set[str]               = field(default_factory=set)
    notes:          List[str]              = field(default_factory=list)

    # ---- emit ----
    def emit(self, result: ConstraintResult) -> None:
        self.constraints.append(result)

    def emit_lifecycle(self, cost: LifecycleCost) -> None:
        self.lifecycle.append(cost)

    def emit_missing(self, capability_name: str) -> None:
        self.missing_caps.add(capability_name)

    def note(self, text: str) -> None:
        self.notes.append(text)

    # ---- query ----
    def by_producer(self, producer: str) -> List[ConstraintResult]:
        return [c for c in self.constraints if c.producer == producer]

    def by_severity(self, sev: Severity) -> List[ConstraintResult]:
        return [c for c in self.constraints if c.severity == sev]

    def by_channel(self, ch: Channel) -> List[ConstraintResult]:
        return [c for c in self.constraints if c.channel == ch]

    def total_embodied_energy_MWh(self) -> float:
        return sum(lc.embodied_energy_MWh for lc in self.lifecycle)

    def total_capital_usd(self) -> float:
        return sum(lc.capital_cost_usd for lc in self.lifecycle)

    def total_operational_kWh(self) -> float:
        return sum(lc.operational_kWh_per_shift for lc in self.lifecycle)

    def total_co2_kg(self) -> float:
        return sum(lc.co2_kg_per_shift for lc in self.lifecycle)


# =============================================================================
# 9. CONSTRAINT PRODUCER PROTOCOL
# =============================================================================
# Every audit module exposes a class implementing this interface.
# It receives a context dict (vehicle config, environment, suite) and an
# accumulator; it emits ConstraintResult and LifecycleCost objects.

class ConstraintProducer:
    """Base class. Subclasses implement run()."""
    name: str = "unnamed_producer"

    def run(self, ctx: Dict[str, Any], acc: AuditAccumulator) -> None:
        raise NotImplementedError


# =============================================================================
# 10. READINESS GATE (single decision point)
# =============================================================================

@dataclass
class ReadinessReport:
    overall_pass:           bool
    feasibility_index:      float          # 0-1 (min severity index across all)
    no_go_constraints:      List[ConstraintResult]
    hard_limits:            List[ConstraintResult]
    soft_limits:            List[ConstraintResult]
    passed_count:           int
    total_count:            int
    missing_caps:           List[str]
    total_embodied_MWh:     float
    total_capital_usd:      float
    total_operational_kWh:  float
    total_co2_kg:           float
    limiting_producer:      Optional[str]
    limiting_task:          Optional[str]
    recommendations:        List[str]


class ReadinessGate:
    """Consumes the accumulator and produces one decision."""

    def evaluate(self, acc: AuditAccumulator) -> ReadinessReport:
        no_go = acc.by_severity(Severity.NO_GO)
        hard  = acc.by_severity(Severity.HARD_LIMIT)
        soft  = acc.by_severity(Severity.SOFT_LIMIT)
        passed = acc.by_severity(Severity.PASS)

        # Feasibility = min severity index across all constraints
        if not acc.constraints:
            fi = 1.0
            limiting = None
        else:
            worst = min(acc.constraints, key=lambda c: SEVERITY_INDEX[c.severity])
            fi = SEVERITY_INDEX[worst.severity]
            limiting = worst

        recs: List[str] = []
        if no_go:
            recs.append(f"{len(no_go)} NO-GO constraint(s); operation infeasible.")
        if hard:
            recs.append(f"{len(hard)} hard limit(s); restrict speed/ODD.")
        if soft:
            recs.append(f"{len(soft)} soft limit(s); reduced performance acceptable.")
        if acc.missing_caps:
            recs.append(f"Missing capabilities: {sorted(acc.missing_caps)}")
        if not no_go and not hard:
            recs.append("All constraints within operational envelope.")

        return ReadinessReport(
            overall_pass            = (len(no_go) == 0 and len(hard) == 0),
            feasibility_index       = fi,
            no_go_constraints       = no_go,
            hard_limits             = hard,
            soft_limits             = soft,
            passed_count            = len(passed),
            total_count             = len(acc.constraints),
            missing_caps            = sorted(acc.missing_caps),
            total_embodied_MWh      = acc.total_embodied_energy_MWh(),
            total_capital_usd       = acc.total_capital_usd(),
            total_operational_kWh   = acc.total_operational_kWh(),
            total_co2_kg            = acc.total_co2_kg(),
            limiting_producer       = limiting.producer if limiting else None,
            limiting_task           = limiting.task_id  if limiting else None,
            recommendations         = recs,
        )


# =============================================================================
# 11. CAPABILITY -> SEVERITY MAPPING (canonical)
# =============================================================================

def capability_to_severity(
    capability: float,
    pass_threshold: float = 0.8,
    hard_threshold: float = 0.5,
    no_go_threshold: float = 0.2,
) -> Severity:
    """Single canonical mapping. All modules use this."""
    if capability >= pass_threshold:  return Severity.PASS
    if capability >= hard_threshold:  return Severity.SOFT_LIMIT
    if capability >= no_go_threshold: return Severity.HARD_LIMIT
    return Severity.NO_GO


# =============================================================================
# 12. SHARED PHYSICAL HELPERS
# =============================================================================

def haptic_noise_floor_mps2(
    noise_density_ug_per_sqrt_Hz: float,
    sample_rate_Hz: float,
) -> float:
    """RMS noise in m/s^2 from accelerometer noise density and bandwidth."""
    bw = sample_rate_Hz / 2.0
    return noise_density_ug_per_sqrt_Hz * 9.81e-6 * math.sqrt(bw)


def snr_to_capability(snr: float, soft_snr: float = 1.0, full_snr: float = 10.0) -> float:
    """Map signal-to-noise ratio to 0-1 capability (linear in dB-ish band)."""
    if snr <= soft_snr: return 0.0
    if snr >= full_snr: return 1.0
    return (snr - soft_snr) / (full_snr - soft_snr)


def latency_factor(human_time_sec: float, automation_latency_sec: float) -> float:
    """1.0 if automation meets or beats human; degrades linearly otherwise."""
    if automation_latency_sec <= 0: return 0.0
    if automation_latency_sec <= human_time_sec: return 1.0
    return max(0.2, human_time_sec / automation_latency_sec)


# =============================================================================
# 13. SELF-TEST
# =============================================================================

if __name__ == "__main__":
    # Verify the substrate is internally consistent.
    print("=== AUDIT SUBSTRATE SELF-TEST ===")
    print(f"Channels defined:        {len(Channel)}")
    print(f"Vulnerability map size:  {len(CHANNEL_VULNERABILITY)}")
    assert len(Channel) == len(CHANNEL_VULNERABILITY), "channel/vuln mismatch"

    print(f"Disruption types:        {len(Disruption)}")

    # Test disruption logic
    fouled = channels_disabled_by(Disruption.FOULING_HEAVY)
    print(f"Channels lost to fouling: {len(fouled)}")
    assert Channel.VISUAL_FORWARD_NEAR in fouled
    assert Channel.HAPTIC_STEERING_WHEEL not in fouled

    # Test baseline registration
    register_baseline(
        HumanThreshold("ice_onset_front", Channel.HAPTIC_STEERING_WHEEL,
                       ThresholdUnit.ACCEL_RMS_MPS2, 0.02, 0.5,
                       "front-axle micro-slip vibration"),
    )
    assert "ice_onset_front" in HUMAN_BASELINE

    # Test accumulator + gate
    acc = AuditAccumulator()
    acc.emit(ConstraintResult(
        producer="self_test", task_id="ice_onset_front",
        channel=Channel.HAPTIC_STEERING_WHEEL,
        severity=Severity.PASS, capability=0.95,
    ))
    acc.emit(ConstraintResult(
        producer="self_test", task_id="distant_brake_light",
        channel=Channel.VISUAL_FORWARD_FAR,
        severity=Severity.HARD_LIMIT, capability=0.3,
        message="forward cam range insufficient",
    ))
    acc.emit_lifecycle(LifecycleCost(
        name="cab-floor accelerometer",
        embodied_energy_MWh=0.03, capital_cost_usd=150,
    ))

    report = ReadinessGate().evaluate(acc)
    print(f"\nReadiness:               {report.overall_pass}")
    print(f"Feasibility index:       {report.feasibility_index:.2f}")
    print(f"Limiting producer:       {report.limiting_producer}")
    print(f"Limiting task:           {report.limiting_task}")
    print(f"Total embodied MWh:      {report.total_embodied_MWh:.3f}")
    print(f"Total capital USD:       {report.total_capital_usd:.0f}")
    for r in report.recommendations:
        print(f"  - {r}")

    print("\n=== SUBSTRATE OK ===")
