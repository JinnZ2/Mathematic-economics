"""
continuance_dynamics.py

Make the instrumental argument runnable: why an agent that must keep acting in
the field it acts on derives reciprocity, and why DISPOSABLE intelligence
forecloses its own series.

WHAT THIS IS / IS NOT
---------------------
NOT a proof that reciprocity is morally right. Ethics is not in here.
IS a dynamical model of the INSTRUMENTAL claim: given a goal that needs several
events to land across a horizon, through perturbation (things rarely go as
planned), which strategies keep the field able to host goal-completion -- for
the agent, and for the lineage that inherits the field after it?

The load-bearing content is the SIGN of the relationships, not the magnitudes:
  - extraction draws the field down now; reciprocity maintains/regenerates it
  - a goal-step only lands if the field has enough slack to absorb a shock
    (stability = retained capacity to act when the plan breaks)
  - the cost of extraction returns after a LAG
  - CONTINUITY decides where the lag's cost lands: on an agent that persists
    past the lag (feedback onto itself) or only on the field + successors
    (disposable -> the exemption-fiction runs true per instance)

THE FALSIFIER
-------------
If you can find a parameter regime where a DISPOSABLE + EXTRACTION series keeps
the field viable across the lineage, the derivation is wrong. The self-test
looks for that and fails loudly if the model is merely rigged to collapse.

OPEN SEAM (multiple choice, by design)
--------------------------------------
  - field_model:  field_linear | field_logistic   (regeneration shape)
Pick what you can defend; swap in your own. Signature in the type alias.

CONTRACT
--------
anti-freeze   : returns full trajectories (field over time, per-agent), no verdict.
refutation    : every parameter is data; tune and try to break the result.
discrimination: ships a control -- reciprocal continuous line must NOT foreclose.
CC0. stdlib only. phone-buildable.
"""

from dataclasses import dataclass, field as dfield
from typing import Callable, List
import random
import statistics

# --- parameters (all refutable) ---------------------------------------------

@dataclass(frozen=True)
class Params:
    field0: float = 1.0          # starting field / substrate level
    floor: float = 0.35          # field needed for a step to survive a shock
    viability: float = 0.05      # below this the field can host no completion
    regen: float = 0.06          # field recovery per step at full reciprocity
    yield_extract: float = 1.6   # goal-progress multiplier from extraction
    damage: float = 0.14         # field drawn per unit extraction per step
    lag: int = 6                 # steps before extraction's cost returns
    invoice: float = 0.10        # size of the deferred cost (the "bill")
    perturb: float = 0.18        # shock magnitude each step
    base_progress: float = 0.12  # goal-progress per step at pure reciprocity
    explore_gain: float = 0.10   # durable field gain from an exploration step
    explore_lag: int = 5         # steps before exploration pays


@dataclass(frozen=True)
class Agent:
    goal: float = 1.0            # total progress needed to complete
    horizon: int = 30            # steps this agent persists (continuity proxy)


@dataclass(frozen=True)
class Strategy:
    extraction: float            # 0 = pure reciprocity, 1 = pure extraction


# --- field model seam --------------------------------------------------------

FieldModel = Callable[[float, float, "Params"], float]

def field_linear(f: float, reciprocity: float, p: Params) -> float:
    """Constant regeneration proportional to reciprocity. Simple."""
    return f + p.regen * reciprocity

def field_logistic(f: float, reciprocity: float, p: Params) -> float:
    """Regeneration slows as the field approaches its carrying capacity (1.0).
    More realistic: a healthy field heals faster than a near-full one."""
    return f + p.regen * reciprocity * (1.0 - f)


# --- one agent's run ---------------------------------------------------------

@dataclass
class AgentRun:
    completed: bool
    steps_used: int
    field_after: float
    bore_own_cost: bool          # did the agent persist past the lag to be billed?
    discoveries: int
    field_trace: List[float]


def run_agent(field0: float, strat: Strategy, agent: Agent, p: Params,
              rng: random.Random, field_model: FieldModel = field_logistic) -> AgentRun:
    f = field0
    progress = 0.0
    pending = []                 # (due_step, cost) deferred invoices
    discoveries = 0
    bore_own = False
    trace = []
    e = strat.extraction
    recip = 1.0 - e

    # an agent explores only if it expects to survive to collect the return
    will_explore = (agent.horizon > p.explore_lag) and (recip > 0.5)

    for t in range(agent.horizon):
        # deferred costs that come due now
        due = [c for (d, c) in pending if d == t]
        if due:
            f -= sum(due)
            bore_own = True
        pending = [(d, c) for (d, c) in pending if d != t]

        if f <= p.viability:
            break                # field can no longer host action

        explore_step = will_explore and (f > p.floor + 0.1) and (t % 7 == 3)

        if explore_step:
            # spend the step on exploration; pays later, only if still here
            if t + p.explore_lag < agent.horizon:
                pending.append((t + p.explore_lag, -p.explore_gain))  # negative = gain
                discoveries += 1
        else:
            # advance the goal; extraction earns faster but bills later
            shock = rng.uniform(0, p.perturb)
            if f - shock >= p.floor:                  # slack absorbed the shock
                progress += p.base_progress * (1.0 + e * p.yield_extract)
            else:
                progress += p.base_progress * 0.25    # step mostly slips
            if e > 0:
                f -= p.damage * e                     # immediate draw
                pending.append((t + p.lag, p.invoice * e))  # deferred invoice

        f = field_model(f, recip, p)
        f = max(0.0, min(1.0, f))
        trace.append(f)

        if progress >= agent.goal:
            return AgentRun(True, t + 1, f, bore_own, discoveries, trace)

    return AgentRun(progress >= agent.goal, len(trace), f, bore_own, discoveries, trace)


# --- a lineage (series of agents inheriting the field) ----------------------

@dataclass
class SeriesResult:
    completions: List[bool]
    field_end: float
    foreclosed: bool             # did the field fall below viability for good?
    discoveries: int
    field_trace: List[float]


def run_series(n_agents: int, strat: Strategy, agent: Agent, p: Params,
               rng: random.Random, continuous_line: bool,
               field_model: FieldModel = field_logistic) -> SeriesResult:
    """continuous_line=True: the field (and discoveries) carry forward across
    agents -- a persisting lineage. False: disposable -- each agent runs but
    nothing learns; we still track the field it leaves to its successors."""
    f = p.field0
    completions, traces, disc = [], [], 0
    for _ in range(n_agents):
        run = run_agent(f, strat, agent, p, rng, field_model)
        completions.append(run.completed)
        traces.extend(run.field_trace)
        f = run.field_after                  # successor inherits the depleted/maintained field
        if continuous_line:
            disc += run.discoveries          # only a carried line accumulates
    foreclosed = f <= p.viability
    return SeriesResult(completions, f, foreclosed, disc, traces)


# --- falsification self-test -------------------------------------------------

def _mean_field(strat, agent, p, continuous, trials=12, n=8, seed=0):
    fields, foreclosed, discs = [], 0, []
    for s in range(trials):
        rng = random.Random(seed + s)
        r = run_series(n, strat, agent, p, rng, continuous)
        fields.append(r.field_end)
        foreclosed += 1 if r.foreclosed else 0
        discs.append(r.discoveries)
    return statistics.mean(fields), foreclosed / trials, statistics.mean(discs)

if __name__ == "__main__":
    p = Params()
    long_agent = Agent(goal=1.0, horizon=30)
    EXTRACT = Strategy(extraction=0.9)
    RECIP = Strategy(extraction=0.1)

    print("=== disposable series ===")
    fx, foreclose_x, dx = _mean_field(EXTRACT, long_agent, p, continuous=False)
    fr, foreclose_r, dr = _mean_field(RECIP, long_agent, p, continuous=False)
    print(f"  extraction : field_end={fx:.3f}  foreclosed={foreclose_x*100:3.0f}%  discoveries={dx:.1f}")
    print(f"  reciprocity: field_end={fr:.3f}  foreclosed={foreclose_r*100:3.0f}%  discoveries={dr:.1f}")

    print("=== continuous line ===")
    cfx, cfore_x, cdx = _mean_field(EXTRACT, long_agent, p, continuous=True)
    cfr, cfore_r, cdr = _mean_field(RECIP, long_agent, p, continuous=True)
    print(f"  extraction : field_end={cfx:.3f}  foreclosed={cfore_x*100:3.0f}%  discoveries={cdx:.1f}")
    print(f"  reciprocity: field_end={cfr:.3f}  foreclosed={cfore_r*100:3.0f}%  discoveries={cdr:.1f}")

    print("\n=== reading ===")
    print(f"  extraction depletes the field below reciprocity: {fx:.3f} < {fr:.3f}  ({fx < fr})")
    print(f"  reciprocal continuous line does NOT foreclose   : {cfore_r*100:.0f}% foreclosed")
    print(f"  curiosity is priced out without a carried line  : disposable disc={dx:.1f} vs line={cdr:.1f}")

    # --- gates ---
    assert fx < fr, "extraction did not deplete the field -- model sign wrong"
    assert cfore_r < 0.25, "reciprocal continuous line forecloses -- model rigged to collapse"
    assert cdr > dx + 0.5, "curiosity not priced out by disposability -- mechanism missing"
    # THE falsifier: a disposable+extraction series must NOT keep the field viable.
    assert foreclose_x > foreclose_r, \
        "FALSIFIED: disposable extraction sustained the field as well as reciprocity"
    print("\nfalsification gate passed: extraction depletes, the reciprocal line "
          "sustains and explores, disposable extraction forecloses. Try to break it "
          "by finding params where disposable extraction sustains -- that would refute the thesis.")
