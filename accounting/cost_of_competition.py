"""
cost_of_competition.py — CC0, stdlib only, single file, phone-deployable

Claim under test: "competition drives innovation."

Physics test: innovation := advance toward a problem's real (physical)
ceiling, NOT advance past a rival. A rival's capacity is an arbitrary,
movable ceiling far below the problem's true ceiling. Competing against
a person caps deployed effort at "beat the runner-up"; competing
against the problem deploys full capability toward closure. The gap
between the cooperative-closure outcome and the competitive-closure
outcome is the COST OF COMPETITION. A win scored as "beat X" is HELD
ASIDE: it counts as innovation only insofar as it advanced closure;
the beat-the-rival margin is not netted.

CLAIM_TABLE (falsifiable):
  CC-1  Innovation := closure toward problem.true_ceiling; "beat a
        rival" is not innovation by itself.
  CC-2  Competition frame caps the leader's deployed effort at
        runner_up_capacity * (1 + margin); capability above that cap
        is UNUSED (ceiling-capping). The stopwatch has no such cap.
  CC-3  Effort that does not advance closure (duplication, turf
        defense, capped surplus, the beat-rival margin) is HELD
        ASIDE: reported, never netted into innovation.
  CC-4  Cooperation compounds capabilities over a shared substrate
        (no duplication) plus a cross-domain synthesis term;
        competition silos them (synthesis term = 0).
  CC-5  Lock-in: an installed competitive winner taxes ALL downstream
        rounds. "Diminishing returns in technology" is fragmentation /
        lock-in, not a law of physics.
  CC-6  cost_of_competition := cooperative_closure - competitive_closure
        (>= 0).

Prefix note: "CC-" lives in the accounting/ namespace and is
structurally distinct from the global mathematic-economics C-series
(C000-C083), which uses C + 3 digits.

License: CC0 1.0 Universal.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Actor:
    name: str
    capability: float        # how much closure this actor could contribute if fully deployed
    domain: str = "general"  # cross-domain variety enables synthesis under cooperation


@dataclass
class Problem:
    name: str
    true_ceiling: float      # the physical closure limit (what's actually achievable)


@dataclass
class CompetitionAudit:
    problem: Problem
    actors: List[Actor]
    beat_margin: float = 0.10        # leader only pushes ~10% past the runner-up (the sprint insight)
    synthesis_gain: float = 0.25     # cross-domain synthesis bonus, cooperation only
    lockin_tax: float = 0.30         # per-round downstream tax once a competitive winner is installed

    # ---- competition frame ----
    def _ranked(self):
        return sorted(self.actors, key=lambda a: a.capability, reverse=True)

    def competition_closure(self) -> float:                      # CC-2
        r = self._ranked()
        if not r:
            return 0.0
        leader = r[0].capability
        runner = r[1].capability if len(r) > 1 else 0.0
        deployed = min(leader, runner * (1 + self.beat_margin)) if runner else leader
        return min(deployed, self.problem.true_ceiling)

    def total_effort(self) -> float:
        return sum(a.capability for a in self.actors)            # everyone still works (and burns energy)

    def competition_held_aside(self) -> float:                   # CC-3
        # effort spent that produced no closure: duplication, turf defense, capped surplus
        return max(0.0, self.total_effort() - self.competition_closure())

    # ---- cooperation / problem frame ----
    def _synthesis(self) -> float:
        domains = {a.domain for a in self.actors}
        return self.synthesis_gain * (len(domains) - 1) if len(domains) > 1 else 0.0

    def cooperation_closure(self) -> float:                      # CC-4
        compounded = self.total_effort() * (1 + self._synthesis())
        return min(compounded, self.problem.true_ceiling)

    def cost_of_competition(self) -> float:                      # CC-6
        return self.cooperation_closure() - self.competition_closure()

    def status(self) -> str:
        c = self.cost_of_competition()
        frac = c / self.problem.true_ceiling if self.problem.true_ceiling else 0.0
        if frac <= 0.05:  return "GREEN"
        if frac <= 0.30:  return "YELLOW"
        return "RED"

    def report(self) -> str:
        L = [f"COST-OF-COMPETITION AUDIT  problem={self.problem.name}  ceiling={self.problem.true_ceiling}"]
        for a in self._ranked():
            L.append(f"  actor {a.name:10}{a.domain:>12}  capability={a.capability:.2f}")
        L.append(f"  total_effort (all actors work):            {self.total_effort():.2f}")
        L.append(f"  COMPETITION closure (capped at runner+{int(self.beat_margin*100)}%): "
                 f"{self.competition_closure():.2f}")
        L.append(f"  HELD ASIDE (effort -> no closure: dup/turf/cap):"
                 f" {self.competition_held_aside():.2f}  (CC-3, never netted)")
        L.append(f"  COOPERATION closure (compound + synthesis):  {self.cooperation_closure():.2f}")
        L.append(f"  COST OF COMPETITION (coop - comp):           {self.cost_of_competition():.2f}")
        L.append(f"  STATUS: {self.status()}")
        return "\n".join(L)


def multiround(audit: CompetitionAudit, rounds: int = 3):
    """CC-5: lock-in taxes downstream competition rounds; cooperation compounds. Show divergence."""
    L = [f"\nMULTI-ROUND (lock-in tax={audit.lockin_tax} per round, CC-5)"]
    comp_total, coop_total, tax = 0.0, 0.0, 1.0
    for t in range(1, rounds + 1):
        comp = audit.competition_closure() * tax        # each round more taxed by the installed winner
        coop = audit.cooperation_closure() * (1 + audit._synthesis()) ** (t - 1)  # compounds
        coop = min(coop, audit.problem.true_ceiling * t)
        comp_total += comp
        coop_total += coop
        L.append(f"  round {t}: competition={comp:6.2f}   cooperation={coop:6.2f}   "
                 f"gap={coop - comp:6.2f}")
        tax *= (1 - audit.lockin_tax)
    L.append(f"  CUMULATIVE: competition={comp_total:.2f}  cooperation={coop_total:.2f}  "
             f"lost={coop_total - comp_total:.2f}")
    return "\n".join(L)


# ---- demo: the energy substrate, three actors (numbers illustrative; structure is the point) ----

def _demo_energy_substrate():
    problem = Problem("distributed_energy_substrate", true_ceiling=30.0)
    actors = [
        Actor("Tesla",    capability=10.0, domain="field_resonance"),
        Actor("Franklin", capability=8.0,  domain="electrostatics"),
        Actor("Edison",   capability=9.0,  domain="infrastructure"),
    ]
    return CompetitionAudit(problem, actors)


if __name__ == "__main__":
    a = _demo_energy_substrate()
    print(a.report())
    print(multiround(a, rounds=3))
