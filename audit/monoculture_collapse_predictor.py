# monoculture_collapse_predictor.py
# CC0. stdlib only. Refutation protocol: output trajectories, not stored verdicts.
# Claim: diversity sets the barrier height that holds a system out of collapse.
#        consolidation (apex-broadcast) eats the barrier. Below spinodal -> escape.
# Refute: if an observed system survives past the predicted spinodal under a
#        held consolidation level, update the kernel (D0, k, temp), never the sim.
import math

def barrier(diversity, consolidation, broadcast, D0=1.0, k=1.0):
    # barrier(t) = D0*diversity - k*consolidation*broadcast
    return D0 * diversity - k * consolidation * broadcast

def escape_rate(b, temp=0.15, attempt=1.0):
    # Kramers: rate ~ attempt * exp(-barrier/temp). barrier<=0 => unbarriered escape.
    return attempt * math.exp(-max(b, 0.0) / temp)

def sweep(diversity, broadcast, reciprocity, c_lo=0.0, c_hi=2.0, steps=40,
          temp=0.15, escape_threshold=0.5):
    # reciprocity R in (0,1] scales effective diversity (degraded R thins the well)
    fwd, rev = [], []
    cs = [c_lo + (c_hi - c_lo) * i / steps for i in range(steps + 1)]
    state = "diverse"
    for c in cs:
        b = barrier(diversity * reciprocity, c, broadcast)
        r = escape_rate(b, temp)
        if state == "diverse" and r >= escape_threshold:
            state = "collapsed"
        fwd.append((round(c, 4), round(b, 4), round(r, 4), state))
    for c in reversed(cs):
        b = barrier(diversity * reciprocity, c, broadcast)
        r = escape_rate(b, temp)
        if state == "collapsed" and r < escape_threshold * 0.5:  # asymmetric reset
            state = "diverse"
        rev.append((round(c, 4), round(b, 4), round(r, 4), state))
    return fwd, rev  # hysteresis = flip points differ between fwd and rev

if __name__ == "__main__":
    f, r = sweep(diversity=1.0, broadcast=1.0, reciprocity=0.85)
    print("FORWARD (consolidation rising):")
    for row in f: print("  c=%.3f bar=%+.3f rate=%.3f %s" % row)
    print("REVERSE (consolidation falling):")
    for row in r: print("  c=%.3f bar=%+.3f rate=%.3f %s" % row)
    fc = next((c for c,_,_,s in f if s=="collapsed"), None)
    rc = next((c for c,_,_,s in r if s=="diverse"), None)
    print("spinodal_fwd=%s  recover_rev=%s  hysteresis_gap=%s"
          % (fc, rc, None if (fc is None or rc is None) else round(fc-rc,3)))
