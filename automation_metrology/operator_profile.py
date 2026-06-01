"""
operator_profile.py  -- CC0, stdlib-only

Two honest corrections to the human-vs-automation frame:

1. PER-OPERATOR PROFILE. The fleet-average HUMAN_PARALLEL vector is a statistical
   stand-in, not a person. Drift-resistance (fatigue, skill-decay, habituation)
   and energy/stamina are NOT constants -- they are parameters you measure on
   the actual operator, the way you strip equipment aids at the start of an
   archery session to read YOUR baseline instead of a generic one. A high-adapted
   operator (reduced sleep need, body-as-machine-extension, machine-as-sensory-
   extension) runs a different C4/C5 and a longer duty cycle. Encode the real
   node, don't inherit the average -- and don't pretend humans never drift either.

2. THE HIRING-CHOICE CONFOUND. 'Automation beats humans' usually varies TWO
   things at once: substrate type AND operator quality. If automation only
   becomes best-fit when you assume a LOW-qualified operator, then automation is
   COVERAGE FOR A HIRING CHOICE, not a substrate-capability finding. The honest
   label:
     - hire quality bodies  -> use them on fatiguing tasks; keep automation out
                               of out-of-scope (chaos/extrap/safety) roles.
     - choose lower-qualified bodies -> ADMIT it, and use automation to cover the
                               tasks those bodies find fatiguing.
     - either way: automation/regulation = coverage for the hiring choice,
                   NOT a narrative datapoint about machine > human.
"""

from contextlib import contextmanager
from dataclasses import dataclass, field
import substrate_allocation as SA
from substrate_allocation import best_fit, audit_setup, demo_tasks, CAPS


@dataclass
class OperatorProfile:
    name: str
    # supply over CAPS: C1det C2chaos C3interp C3extrap C4drift C5energy
    vector: list
    duty_cycle_h: float = 11.0      # sustainable hours before drift dominates
    measured: bool = False          # measured on the real operator, or assumed?
    notes: str = ""

    def __post_init__(self):
        if len(self.vector) != len(CAPS):
            raise ValueError(f"profile vector must have {len(CAPS)} axes.")


# the current model default -- a statistical stand-in, NOT a person
FLEET_AVERAGE = OperatorProfile(
    "fleet_average", [0.30, 0.95, 0.40, 0.90, 0.90, 0.55],
    duty_cycle_h=11.0, measured=False,
    notes="population placeholder; do not mistake for any individual.")

# illustrative high-adapted operator (PLACEHOLDER until measured per archery-
# baseline method): stronger chaos/extrap, higher drift-resistance + stamina,
# longer sustainable duty cycle. flagged measured=False until clocked.
HIGH_ADAPTED = OperatorProfile(
    "high_adapted", [0.30, 0.97, 0.45, 0.95, 0.95, 0.75],
    duty_cycle_h=14.0, measured=False,
    notes="reduced sleep need; body-as-machine + machine-as-sensory coupling. "
          "MEASURE these on the real operator; do not assume.")

# a lower-qualified operator the industry may actually be hiring: weaker chaos
# handling, lower extrap, fatigues faster (low C4), lower stamina, shorter cycle.
LOW_QUALIFIED = OperatorProfile(
    "low_qualified", [0.30, 0.70, 0.35, 0.55, 0.55, 0.40],
    duty_cycle_h=9.0, measured=False,
    notes="finds chaotic/extrapolative tasks fatiguing; drifts sooner.")


@contextmanager
def operator(profile: OperatorProfile):
    """Temporarily score the model against a specific operator's substrate."""
    saved = SA.SUBSTRATES["HUMAN_PARALLEL"]
    SA.SUBSTRATES["HUMAN_PARALLEL"] = list(profile.vector)
    try:
        yield
    finally:
        SA.SUBSTRATES["HUMAN_PARALLEL"] = saved


def audit_under(profile: OperatorProfile, tasks=None):
    tasks = tasks or demo_tasks()
    with operator(profile):
        return audit_setup(tasks)


def _bestfit_map(profile, tasks):
    with operator(profile):
        return {t.name: best_fit(t)["substrate"] for t in tasks}


def hiring_confound(tasks=None, high=HIGH_ADAPTED, low=LOW_QUALIFIED):
    """
    Decompose 'automation advantage' into substrate-effect vs hiring-choice.
    A task whose best-fit FLIPS away from the human when operator quality drops
    is COVERAGE for the hiring choice. Crucially we track WHICH substrate covers:

      flip HUMAN -> DEDICATED : honest coverage by the correct (low-entropy) tool
      flip HUMAN -> GENERAL_AI: AI-as-coverage -- a DOUBLE error (coverage for a
                                hiring choice AND the wrong substrate for it,
                                since AI shares the human's weak axes: chaos,
                                extrapolation, drift, stamina).
    """
    tasks = tasks or demo_tasks()
    bf_high = _bestfit_map(high, tasks)
    bf_low = _bestfit_map(low, tasks)

    cover_by_dedicated, cover_by_ai = [], []
    for t in tasks:
        was, now = bf_high[t.name], bf_low[t.name]
        if was == "HUMAN_PARALLEL" and now != "HUMAN_PARALLEL":
            (cover_by_dedicated if now == "DEDICATED" else cover_by_ai).append(t.name)

    intrinsic_ai = sorted(n for n, s in bf_high.items() if s == "GENERAL_AI")

    if cover_by_ai:
        verdict = ("AI_AS_COVERAGE_DOUBLE_ERROR: tasks flip to GENERAL_AI only "
                   "under a low-qualified operator AND AI shares the human's weak "
                   "axes -> coverage for a hiring choice routed to the wrong "
                   "substrate. Should be DEDICATED or a quality body.")
    elif cover_by_dedicated:
        verdict = ("HONEST_COVERAGE_BY_DEDICATED: lowering operator quality moves "
                   "tasks to DEDICATED structures (the correct low-entropy tool). "
                   "This is coverage for a hiring choice -- label it as such, not "
                   "as 'automation/AI beats humans'.")
    else:
        verdict = ("NO_HIRING_CONFOUND: best-fit set unchanged by operator "
                   "quality. note: AI rarely covers a degraded human anyway, "
                   "because AI is weak on the SAME axes humans degrade on "
                   "(chaos, extrapolation, drift, stamina).")

    return {
        "coverage_by_DEDICATED": sorted(cover_by_dedicated),
        "coverage_by_GENERAL_AI": sorted(cover_by_ai),
        "intrinsic_ai_tasks": intrinsic_ai,
        "verdict": verdict,
        "structural_note": ("the axes a human degrades on (C2 chaos, C3_extrap, "
                            "C4 drift, C5 stamina) are AI's weak axes too. honest "
                            "coverage of a low-qualified body is usually DEDICATED "
                            "structure, NOT general AI. selling AI as that "
                            "coverage is a substrate error on top of a hiring one."),
        "falsifier": ("if a task flips HUMAN->GENERAL_AI under low quality, AI "
                      "genuinely covers there; if it flips HUMAN->DEDICATED, the "
                      "'dumb' tool covers and the AI narrative is doubly wrong."),
    }


if __name__ == "__main__":
    tasks = demo_tasks()
    print("MISALLOCATION TAX BY OPERATOR PROFILE (same tasks, same assigns):")
    for p in (FLEET_AVERAGE, HIGH_ADAPTED, LOW_QUALIFIED):
        a = audit_under(p, tasks)
        flag = "" if p.measured else "  [ASSUMED - measure this]"
        print(f"  {p.name:14s} duty={p.duty_cycle_h:4.1f}h  "
              f"total_tax={a['total_tax']:6.2f}  "
              f"misallocated={a['n_misallocated']}/{a['n_tasks']}{flag}")

    print("\nHIRING-CHOICE CONFOUND DECOMPOSITION:")
    c = hiring_confound(tasks)
    for k, v in c.items():
        print(f"  {k}: {v}")

    print("\n  THE HONEST FORK:")
    print("  - hire quality bodies   -> they cover the fatiguing (chaos/extrap)")
    print("                             tasks; keep automation out of scope.")
    print("  - hire lower-qualified   -> ADMIT it; automation covers what those")
    print("                             bodies find fatiguing.")
    print("  - either way: automation = coverage for the hiring choice,")
    print("                NOT evidence that machine > human.")
