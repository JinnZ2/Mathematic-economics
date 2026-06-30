# substrate_scope_validator.py
# CC0. stdlib only. Trajectories, not verdicts. No should/shouldn't in the structure.
# Claim: a substrate's outputs are licensed only inside its competence envelope.
#        scope exceedance = task conditions landing in zero-competence cells.
# Refute: if a substrate produces field-correct output in a flagged blindspot cell,
#        the competence kernel is wrong -> widen the envelope, never the task.

def grid(axes):  # axes: dict name->(lo,hi,n). returns list of cell-center dicts
    names = list(axes)
    def rec(i, acc):
        if i == len(names):
            yield dict(acc); return
        lo, hi, n = axes[names[i]]
        for j in range(n):
            c = lo + (hi - lo) * (j + 0.5) / n
            acc[names[i]] = round(c, 4)
            yield from rec(i + 1, acc)
    return list(rec(0, {}))

def competence(cell, envelope):
    # envelope: dict axis->(lo,hi). returns coverage in [0,1): product of per-axis fit.
    fit = 1.0
    for ax, (lo, hi) in envelope.items():
        x = cell[ax]
        if x < lo or x > hi:
            return 0.0
        # soft edge: full in center, taper toward bounds (asymptotic, never exactly 1)
        span = hi - lo
        d = min(x - lo, hi - x) / (span / 2)
        fit *= 0.5 + 0.49 * d
    return round(fit, 4)

def validate(task_region, substrate_envelope, axes):
    cells = grid(axes)
    in_task = [c for c in cells
               if all(task_region[a][0] <= c[a] <= task_region[a][1] for a in task_region)]
    rows, blind = [], []
    for c in in_task:
        cov = competence(c, substrate_envelope)
        rows.append((c, cov))
        if cov == 0.0:
            blind.append(c)
    covered = [r for r in rows if r[1] > 0]
    coverage_frac = round(len(covered) / max(len(in_task), 1), 4)
    return {"cells": len(in_task), "coverage_frac": coverage_frac,
            "blindspots": blind, "trajectory": sorted(rows, key=lambda r: r[1])}

if __name__ == "__main__":
    axes = {"heat": (0, 100, 5), "load": (0, 100, 5)}
    task = {"heat": (0, 100), "load": (0, 100)}            # asked to cover everything
    env  = {"heat": (10, 70), "load": (0, 60)}             # robot actually competent here
    out = validate(task, env, axes)
    print("coverage_frac=%.3f over %d cells; %d blindspots"
          % (out["coverage_frac"], out["cells"], len(out["blindspots"])))
    print("worst cells (low->high competence):")
    for cell, cov in out["trajectory"][:6]:
        print("  ", cell, "cov=%.3f" % cov)
