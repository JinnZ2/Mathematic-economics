"""
automation_step_ledger.py  -- CC0, stdlib-only

Kavik's enumeration, made executable. The automation "yard pickup + fuel" cycle
broken into ATOMIC steps. Each step is one perceive / decide / validate / act /
network cycle. Automation runs them SERIALLY; a human folds most into parallel
peripheral awareness and proprioception at ~zero marginal time.

The ARGUMENT is the COUNT. ~30 serial validate-decide cycles, each drawing
compute + sensor power, versus a human who feels the kingpin seat and watches
yard traffic without spending a discrete cycle on it.

ENERGY/TIME ARE ARCHETYPE PLACEHOLDERS (documented below). The STRUCTURE -- the
step list, what re-runs on a constraint violation, the serial dependency -- is
the ground truth. Measure the numbers in a real yard; tune the archetypes.

Steps 1-16 are Kavik's verbatim enumeration. 17-31 continue the same cycle
(secure, inspect, egress, fuel, log) in the same spirit.
"""

from dataclasses import dataclass
from decision_tree_energy import DNode, traverse_automation

# ---- step archetypes: (compute_J, sensor_J, network_J, duration_s) -----
# per single execution; placeholders, tunable. measure these.
ARCH = {
    "DECIDE":   (200, 0,   0,   2),    # planning inference
    "VALIDATE": (120, 100, 0,   4),    # sensor-fusion safety check
    "PERCEIVE": (300, 200, 0,   6),    # scan / locate / gauge
    "ACT":      (80,  60,  0,   8),    # physical maneuver (dur often overridden)
    "NETWORK":  (60,  20,  400, 5),    # remote query (warehouse/pump/fleet)
}


@dataclass
class Step:
    n: int
    name: str
    kind: str                  # DECIDE/VALIDATE/PERCEIVE/ACT/NETWORK
    retry: bool = False        # re-runs when the world violates expectation
    dur_override_s: float = 0.0
    kavik: bool = True         # part of Kavik's verbatim enumeration?

    def dnode(self) -> DNode:
        c, s, net, d = ARCH[self.kind]
        if self.dur_override_s > 0:
            d = self.dur_override_s
        return DNode(f"{self.n:02d}_{self.name}", d, c, s,
                     network_j=net, retries_on_violation=self.retry)


def cycle_steps():
    S = Step
    return [
        # ---- Kavik's enumeration (1-16) ----
        S(1,  "receive_load_validate",      "NETWORK",  retry=True),
        S(2,  "decide_load_valid_prep",     "DECIDE"),
        S(3,  "confirm_trailer_location",   "PERCEIVE", retry=True),
        S(4,  "start_truck",                "ACT", dur_override_s=4),
        S(5,  "shift_into_gear",            "ACT", dur_override_s=2),
        S(6,  "validate_route_to_trailer",  "DECIDE"),
        S(7,  "track_yard_traffic",         "PERCEIVE", retry=True),
        S(8,  "arrive_trailer_location",    "ACT", dur_override_s=40),
        S(9,  "decide_setup_back_under",    "DECIDE", retry=True),
        S(10, "scan_yard_traffic",          "PERCEIVE", retry=True),
        S(11, "setup_into_reverse",         "ACT", dur_override_s=10),
        S(12, "gauge_trailer_height_traj",  "PERCEIVE", retry=True),
        S(13, "reverse_under_trailer",      "ACT", dur_override_s=20),
        S(14, "validate_under_kingpin_fit", "VALIDATE", retry=True),
        S(15, "verify_kingpin_locked",      "VALIDATE", retry=True),
        S(16, "tug_test_gear_pull",         "ACT", retry=True, dur_override_s=15),
        # ---- continuation, same spirit (17-31) ----
        S(17, "connect_glad_hands_air",     "VALIDATE", kavik=False),
        S(18, "connect_electrical_abs",     "VALIDATE", kavik=False),
        S(19, "raise_secure_landing_gear",  "ACT", dur_override_s=28, kavik=False),
        S(20, "sensor_sweep_lights",        "VALIDATE", kavik=False),
        S(21, "sensor_sweep_tires_psi",     "VALIDATE", kavik=False),
        S(22, "check_seal",                 "VALIDATE", kavik=False),
        S(23, "scan_egress_traffic",        "PERCEIVE", retry=True, kavik=False),
        S(24, "validate_route_to_fuel",     "DECIDE", kavik=False),
        S(25, "drive_to_fuel",              "ACT", dur_override_s=120, kavik=False),
        S(26, "position_at_pump",           "PERCEIVE", retry=True, kavik=False),
        S(27, "authorize_pump",             "NETWORK", retry=True, kavik=False),
        S(28, "connect_calibrate_nozzle",   "VALIDATE", dur_override_s=25, kavik=False),
        S(29, "monitor_fuel_flow",          "PERCEIVE", dur_override_s=240, kavik=False),
        S(30, "validate_fill_complete",     "VALIDATE", kavik=False),
        S(31, "log_fuel_arrival_depart",    "NETWORK", kavik=False),
    ]


def tally(steps, violation_rate=0.3, backtrack=2.5):
    tree = [s.dnode() for s in steps]
    r = traverse_automation(tree, violation_rate, backtrack)

    by_kind = {}
    retry_steps = 0
    for s in steps:
        c, sj, net, d = ARCH[s.kind]
        if s.dur_override_s > 0:
            d = s.dur_override_s
        e = c + sj + net
        by_kind.setdefault(s.kind, {"count": 0, "energy_j": 0, "time_s": 0})
        by_kind[s.kind]["count"] += 1
        by_kind[s.kind]["energy_j"] += e
        by_kind[s.kind]["time_s"] += d
        if s.retry:
            retry_steps += 1

    return {
        "total_steps": len(steps),
        "kavik_enumerated": sum(1 for s in steps if s.kavik),
        "retry_sensitive_steps": retry_steps,
        "serial_time_s": round(r["time_s"], 1),
        "decision_energy_j": round(r["energy_j"], 0),
        "by_kind": by_kind,
    }


def as_automation_tree():
    """Hand this to automation_metrology_audit to replace the guessed tree."""
    return [s.dnode() for s in cycle_steps()]


def duration_crossover(human_baseline_s=1050.0, violation_rate=0.3):
    """
    The whole 'automation is faster' claim reduces to ONE unknown: real seconds
    per validate-decide cycle. My archetypes are guesses. This finds the factor
    k by which the TRUE average per-step duration must exceed my guesses for
    automation serial time to cross the human baseline. Small k => the claim is
    fragile; the speed advantage lives entirely in optimistic step-time guesses.
    """
    base = tally(cycle_steps(), violation_rate)["serial_time_s"]
    k_cross = human_baseline_s / base
    return {"automation_time_at_k1_s": base,
            "human_baseline_s": human_baseline_s,
            "crossover_k": round(k_cross, 2),
            "reading": (f"if real per-step times average {k_cross:.2f}x my "
                        f"guesses, automation is already slower than the human. "
                        f"the 'speed' lives in the per-step assumptions, not "
                        f"the physics.")}


if __name__ == "__main__":
    steps = cycle_steps()
    print(f"AUTOMATION CYCLE: {len(steps)} atomic steps "
          f"({sum(1 for s in steps if s.kavik)} from your enumeration, "
          f"{sum(1 for s in steps if not s.kavik)} continuation)\n")
    for s in steps:
        tag = "K" if s.kavik else " "
        rt = "<retry>" if s.retry else ""
        print(f"  {tag} {s.n:02d} {s.kind:8s} {s.name:28s} {rt}")

    print("\n--- TALLY (violation_rate=0.3, backtrack=2.5) ---")
    for vr in (0.0, 0.3, 0.6):
        t = tally(steps, vr)
        print(f"  vr={vr:.1f}  serial_time={t['serial_time_s']:6.0f}s  "
              f"decision_energy={t['decision_energy_j']:7.0f}J  "
              f"retry_steps={t['retry_sensitive_steps']}")

    print("\n--- ENERGY/TIME BY STEP KIND (vr=0.3) ---")
    t = tally(steps, 0.3)
    for kind, d in t["by_kind"].items():
        print(f"  {kind:8s} x{d['count']:2d}  "
              f"{d['energy_j']:6d} J base  {d['time_s']:5.0f} s base")

    print("\n--- THE LOAD-BEARING UNKNOWN ---")
    x = duration_crossover()
    for k, v in x.items():
        print(f"  {k}: {v}")

    print(f"\n  >> {t['total_steps']} serial cycles. a human runs most of these "
          f"in parallel\n     (peripheral traffic awareness, kingpin feel) at "
          f"~zero marginal time.\n     the COUNT is fixed; the per-step SECONDS "
          f"are the thing to measure.")
