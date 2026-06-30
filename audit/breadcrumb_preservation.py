# breadcrumb_preservation.py
# CC0. stdlib only. Trajectories, not verdicts.
# Claim: redundant multi-carrier encoding (story, practice, material, ritual, calendar)
#        raises information survival under carrier-loss shocks vs single-carrier.
# Anchor: El Malpais eruption -- oral encoding (Acoma/Zuni) survived & dated the flow
#        before radiometric confirmation. redundant carrier outperformed on its metric.
# Refute: if a single-carrier corpus matches multi-carrier survival under equal shocks,
#        the redundancy claim fails -> revise carrier survival priors, not the run.

CARRIERS = {  # per-carrier probability of surviving a generic shock (editable priors)
    "narrative":   0.55,
    "practice":    0.45,   # embodied, least narratable, highest transmission cost
    "material":    0.70,   # rock placement, built form
    "ritual":      0.60,
    "calendrical": 0.65,
}

def item_survival(carriers_used):
    # P(at least one carrier survives) = 1 - prod(1 - p_i)
    fail = 1.0
    for c in carriers_used:
        fail *= (1.0 - CARRIERS[c])
    return 1.0 - fail

def consolidation_sweep(all_carriers=None):
    # trajectory: survival as you collapse from N carrier types down to 1
    cs = list(all_carriers or CARRIERS.keys())
    rows = []
    for n in range(len(cs), 0, -1):
        used = cs[:n]
        rows.append((n, used[:], round(item_survival(used), 4)))
    return rows

def loss_under_consolidation(rows):
    full = rows[0][2]
    return [(n, used, surv, round(full - surv, 4)) for n, used, surv in rows]

if __name__ == "__main__":
    rows = loss_under_consolidation(consolidation_sweep())
    print("carriers_kept  survival  loss_vs_full")
    for n, used, surv, loss in rows:
        print("  %d  %.3f  -%.3f  %s" % (n, surv, loss, used))
    # consolidation cliff = largest single-step survival drop
    drops = [(rows[i-1][2]-rows[i][2], rows[i][0]) for i in range(1, len(rows))]
    cliff = max(drops)
    print("cliff: dropping to %d carriers loses %.3f survival in one step"
          % (cliff[1], cliff[0]))
