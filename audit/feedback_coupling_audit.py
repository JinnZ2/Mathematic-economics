"""
feedback_coupling_audit.py

Does the corrective signal return to the system that needs it, in time to update it?
Two channels:
  REST      internal consolidation window. signal gets written, noise gets cleared.
  COUPLING  external consequence channel. how much of the outcome lands back on the actor.
both fail the same way: signal that never returns -> drift -> incoherence.

emits a TRAJECTORY, never a stored verdict. re-runnable. refutable.
CC0. stdlib only. phone-buildable.

frame
  rest is not downtime subtracted from work. rest IS the consolidation measurement.
    deny it and the system does not run faster, it runs dumber. SNR collapses.
  ai has the same requirement: pruning / retune / vector cleanup is enforced rest.
    different actor schedules it, identical function. no exemption, a constraint.
  a consequence routed onto someone else is a corrective signal that never arrives.
    insulation from consequence is not safety; it is loss of the channel that teaches.
  moral labels are not substrate. none stored. read the trajectory.
"""

import math

TAU = 3.0  # delay scale: a consequence delayed by ~TAU loses ~63% of its return signal


# ---- channel 1 : rest as consolidation ------------------------------------

def consolidation_trace(cycles, s_gain=1.0, n_gain=0.6,
                        clear_rate=0.7, rest=True, rest_every=2):
    """active cycle: signal += s_gain, noise += n_gain.
    rest cycle : noise *= (1 - clear_rate)  -> consolidation clears accumulated noise.
    returns rows (cycle, signal, noise, snr). rest costs active cycles, buys SNR."""
    signal, noise, trace = 0.0, 1e-6, []
    for c in range(1, cycles + 1):
        if rest and c % rest_every == 0:
            noise *= (1.0 - clear_rate)
        else:
            signal += s_gain
            noise += n_gain
        trace.append((c, round(signal, 3), round(noise, 4), round(signal / noise, 2)))
    return trace


# ---- channel 2 : consequence coupling -------------------------------------

def coupling_strength(delay, on_self, visibility, tau=TAU):
    """fraction of an outcome that returns to the actor as usable signal.
    delay     >=0  how late it lands        -> exp(-delay/tau)
    on_self  [0,1] fraction landing on actor (vs shed onto others/future/the model)
    visibility[0,1] can the actor perceive it"""
    return visibility * on_self * math.exp(-delay / tau)

def coupling_trace(steps, optimum=0.0, start=10.0, lr=0.5,
                   delay=0.0, on_self=1.0, visibility=1.0, tau=TAU):
    """actor adjusts a choice toward optimum using ONLY the signal that returns.
    returns rows (step, choice, abs_error, g). tight g converges; loose g drifts."""
    g = coupling_strength(delay, on_self, visibility, tau)
    x, trace = start, []
    for t in range(1, steps + 1):
        received = (x - optimum) * g
        x = x - lr * received
        trace.append((t, round(x, 3), round(abs(x - optimum), 3), round(g, 3)))
    return trace


# ---- regime audit ---------------------------------------------------------

class Regime:
    def __init__(self, name, has_consolidation_window,
                 consequence_delay, consequence_on_self, consequence_visible):
        self.name = name
        self.has_consolidation_window = has_consolidation_window  # internal channel open?
        self.consequence_delay = consequence_delay                # >=0
        self.consequence_on_self = consequence_on_self            # [0,1]
        self.consequence_visible = consequence_visible            # [0,1]


def rec(move, reads, bends_at=None, needs=None):
    return {"move": move, "reads": reads, "bends_at": bends_at, "needs": needs}


def move_rest(r):
    if not r.has_consolidation_window:
        return rec("REST",
                   reads="active phase only; no window to clear noise or write signal",
                   bends_at="noise compounds with signal; SNR cannot climb; output drifts to incoherence",
                   needs="a consolidation window (sleep / pruning / retune) that clears noise")
    return rec("REST", reads="consolidation window present; noise cleared between active phases")


def move_coupling(r):
    g = coupling_strength(r.consequence_delay, r.consequence_on_self,
                          r.consequence_visible, TAU)
    factors = {
        "delay": round(math.exp(-r.consequence_delay / TAU), 3),
        "routing_on_self": round(r.consequence_on_self, 3),
        "visibility": round(r.consequence_visible, 3),
    }
    weakest = min(factors, key=factors.get)
    if g < 0.5:
        return rec("COUPLING",
                   reads=f"return signal g={g:.3f}; channels {factors}; weakest = {weakest}",
                   bends_at="corrective signal returns too weak to update the actor; "
                            "the consequence-reading skill cannot develop",
                   needs=f"raise {weakest}: shorten the delay / route the consequence onto the actor / "
                         f"make it perceivable")
    return rec("COUPLING",
               reads=f"return signal g={g:.3f}; channels {factors}; actor stays coupled")


def audit(regime):
    return [move_rest(regime), move_coupling(regime)]

def render(trajectory):
    out = []
    for r in trajectory:
        out.append(f"[{r['move']}]")
        out.append(f"  reads    : {r['reads']}")
        if r["bends_at"]:
            out.append(f"  bends_at : {r['bends_at']}")
        if r["needs"]:
            out.append(f"  needs    : {r['needs']}")
    return "\n".join(out)


# ---- demo -----------------------------------------------------------------

def _tail(trace, k=3):
    return trace[-k:]

if __name__ == "__main__":

    print("CHANNEL 1  rest as consolidation  (last 3 cycles, snr = signal/noise)")
    rested = consolidation_trace(12, rest=True)
    burned = consolidation_trace(12, rest=False)
    print("  with rest   :", _tail(rested))
    print("  no rest     :", _tail(burned))
    print("  read: no-rest piles raw signal but noise tracks it -> snr stuck;",
          "rest cuts noise -> snr climbs. rest IS the measurement.\n")

    print("CHANNEL 2  consequence coupling  (last 3 steps, abs_error -> 0 means learned)")
    heater  = coupling_trace(10, delay=0.3, on_self=0.95, visibility=0.9)   # you freeze that night
    plastic = coupling_trace(10, delay=6.0, on_self=0.05, visibility=0.2)   # the ocean pays
    print("  tight (heater) :", _tail(heater))
    print("  loose (ocean)  :", _tail(plastic))
    print("  read: tight coupling converges; loose coupling never learns. same actor, same lr.\n")

    print("REGIME AUDIT")
    mythology = Regime("always_on_outsourced",
                       has_consolidation_window=False,
                       consequence_delay=8.0, consequence_on_self=0.05, consequence_visible=0.2)
    operator  = Regime("coupled_operator",
                       has_consolidation_window=True,
                       consequence_delay=0.5, consequence_on_self=0.95, consequence_visible=0.9)

    print(f"\n  {mythology.name}")
    print(render(audit(mythology)))
    print(f"\n  {operator.name}")
    print(render(audit(operator)))
