# substrate_scope_envelopes.py
# CC0. stdlib only. Trajectories, not verdicts.
# Pluggable competence-envelope sources for substrate_scope_validator.validate().
# All three return: dict axis -> (lo, hi). Swap freely; validator stays unchanged.

# --- MODE A: fixed spec envelope (vendor sheet / design assumption) -------------
def envelope_fixed(spec):
    # spec: dict axis->(lo,hi). pass-through, but flagged as ASSUMED not OBSERVED.
    return dict(spec), "fixed_spec"

# --- MODE B: observed field-failure logs (data-driven, shrinks to reality) ------
def envelope_from_failures(field_logs, axes, margin=0.0):
    # field_logs: list of {axis: value, "ok": bool}.
    # envelope = bounding box of OK observations only, optionally shrunk by margin.
    bounds = {}
    for ax in axes:
        oks = [r[ax] for r in field_logs if r.get("ok")]
        if not oks:
            bounds[ax] = (0.0, 0.0)  # zero competence: no successful observation
            continue
        lo, hi = min(oks), max(oks)
        span = hi - lo
        bounds[ax] = (lo + margin * span / 2, hi - margin * span / 2)
    return bounds, "observed_failures"

# --- MODE C: intersection (spec AND observed -- the honest one) -----------------
def envelope_intersect(spec, field_logs, axes, margin=0.0):
    # competent only where the sheet CLAIMS it and the field CONFIRMS it.
    a, _ = envelope_fixed(spec)
    b, _ = envelope_from_failures(field_logs, axes, margin)
    out = {}
    for ax in axes:
        lo = max(a[ax][0], b[ax][0])
        hi = min(a[ax][1], b[ax][1])
        out[ax] = (lo, hi) if lo <= hi else (0.0, 0.0)  # empty = spec/field disagree
    return out, "spec_AND_observed"

def envelope(mode, **kw):
    # dispatcher: mode in {"fixed","failures","intersect"}
    if mode == "fixed":     return envelope_fixed(kw["spec"])
    if mode == "failures":  return envelope_from_failures(kw["field_logs"], kw["axes"],
                                                          kw.get("margin", 0.0))
    if mode == "intersect": return envelope_intersect(kw["spec"], kw["field_logs"],
                                                      kw["axes"], kw.get("margin", 0.0))
    raise ValueError("mode: fixed|failures|intersect")

if __name__ == "__main__":
    from substrate_scope_validator import validate
    axes = {"heat": (0, 100, 5), "load": (0, 100, 5)}
    task = {"heat": (0, 100), "load": (0, 100)}
    spec = {"heat": (10, 70), "load": (0, 60)}            # what the sheet claims
    logs = [  # field reality: failures cluster hot + high-load
        {"heat": 30, "load": 20, "ok": True},
        {"heat": 55, "load": 40, "ok": True},
        {"heat": 68, "load": 55, "ok": False},            # near edge, failed
        {"heat": 40, "load": 10, "ok": True},
        {"heat": 62, "load": 50, "ok": False},
    ]
    for mode, kw in (("fixed", {"spec": spec}),
                     ("failures", {"field_logs": logs, "axes": axes}),
                     ("intersect", {"spec": spec, "field_logs": logs, "axes": axes})):
        env, src = envelope(mode, **kw)
        out = validate(task, env, axes)
        print("%-10s src=%-16s coverage=%.3f blindspots=%d env=%s"
              % (mode, src, out["coverage_frac"], len(out["blindspots"]), env))
