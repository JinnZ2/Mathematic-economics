"""
claims.py  --  CC0, stdlib only, mobile-runnable
C1-C10 falsifiable claims about the solvability auditor's detection accuracy.

Each claim is a falsifiable assertion about what the auditor MUST detect on
a known input.  If a claim FAILs, the auditor's contract is falsified in
that mode -- the maintainer must either fix the detector, weaken the claim,
or document the new edge case.

Run:  python claims.py     (exit 0 if all hold; 1 if any falsified)
"""

import json
import sys
import solvability_audit as sa


def _ok(idx, label, cond, detail=""):
    mark = "OK " if cond else "FAIL"
    line = f"  C{idx:>2}  {mark}  {label}"
    if detail:
        line += f"  -- {detail}"
    print(line)
    return cond


def run():
    print("== C1-C10 falsifiable claims about the auditor ==")
    res = []
    t = [0.0, 0.5, 1.0, 1.5, 2.0]

    # ------------------------------------------------------------------
    # C1: silent domains alone do NOT kill (P1 invariant).
    #     4 unknowns, 3 constraints, all .domain=None -> UNDERDETERMINED,
    #     latent < LATENT_KILL.  Falsifier: silence pushes score >= kill.
    # ------------------------------------------------------------------
    r = sa.audit(sa.ingest_formal(
        [sa.Variable(n, known=False) for n in ("a","b","c","d")],
        [sa.Constraint(f"eq{i}") for i in range(3)], claim="predict d"))
    res.append(_ok(1, "silent domains do not kill (P1)",
                   r.solvability is sa.Solvability.UNDERDETERMINED
                   and r.latent_score < sa.LATENT_KILL,
                   f"sol={r.solvability.name} latent={r.latent_score}"))

    # ------------------------------------------------------------------
    # C2: stationarity + coupled cross-domain NL -> UNKNOWN.
    #     Falsifier: same input returns a non-UNKNOWN band.
    # ------------------------------------------------------------------
    txt = ("Global insect population growth drives crop yield because temperature "
           "is held constant and emission effects are negligible.")
    r = sa.audit(sa.ingest_language(txt))
    res.append(_ok(2, "stationary + cross-domain + optimism -> UNKNOWN",
                   r.solvability is sa.Solvability.UNKNOWN
                   and r.latent_score >= sa.LATENT_KILL,
                   f"latent={r.latent_score}"))

    # ------------------------------------------------------------------
    # C3: asserted-unbounded is distinguished from silent.
    #     Both L0 and L1 must fire, and L1 weight strictly > L0 weight.
    #     Falsifier: only one fires, or weights collapse.
    # ------------------------------------------------------------------
    vs = [sa.Variable("a", False, sa.UNBOUNDED)] + [sa.Variable(n, False) for n in ("b","c","d")]
    r = sa.audit(sa.ingest_formal(vs, [sa.Constraint(f"eq{i}") for i in range(3)], claim="predict d"))
    codes = {f.code for f in r.flags}
    res.append(_ok(3, "L0 and L1 both fire and L1 weight > L0 weight",
                   "L0" in codes and "L1" in codes
                   and sa.SEVERITY["L1"] > sa.SEVERITY["L0"]))

    # ------------------------------------------------------------------
    # C4: single-domain causal NL must NOT raise cross-domain flags.
    #     Falsifier: L3 or L3w fires on a pure single-domain claim.
    # ------------------------------------------------------------------
    r = sa.audit(sa.ingest_language("Force drives stress because load increases strain."))
    codes = {f.code for f in r.flags}
    res.append(_ok(4, "single-domain NL raises no cross-domain flag",
                   "L3" not in codes and "L3w" not in codes,
                   f"flags={sorted(codes)}"))

    # ------------------------------------------------------------------
    # C5: ODE with k1*k2 coupling -> deficiency=1, no zero col,
    #     tier names sensitivity-rank (local or global).
    #     Falsifier: product coupling reported as IDENTIFIABLE.
    # ------------------------------------------------------------------
    r = sa.audit_model(
        f=lambda x,th:[-(th[0]*th[1])*x[0]], g=lambda x,th:[x[0]],
        theta=[0.7, 1.1], t_points=t, x0=[1.0], labels=["k1","k2"],
        global_sweep=False)
    res.append(_ok(5, "k1*k2 coupling -> deficiency=1 via sensitivity-rank tier",
                   r.solvability is sa.Solvability.UNDERDETERMINED
                   and r.dof == 1
                   and r.tier.startswith("sensitivity-rank"),
                   f"tier={r.tier} dof={r.dof}"))

    # ------------------------------------------------------------------
    # C6: ODE with unused param w -> w appears in scope_out
    #     (zero-column detector).  Falsifier: w not flagged.
    # ------------------------------------------------------------------
    r = sa.audit_model(
        f=lambda x,th:[-th[0]*x[0]], g=lambda x,th:[x[0]],
        theta=[0.7, 0.3], t_points=t, x0=[1.0], labels=["k","w"],
        global_sweep=False)
    res.append(_ok(6, "unused-param w detected as unrecoverable",
                   "w" in r.scope_out
                   and r.solvability is sa.Solvability.UNDERDETERMINED,
                   f"scope_out='{r.scope_out}'"))

    # ------------------------------------------------------------------
    # C7: adding observable y2=k2*x recovers identifiability.
    #     Falsifier: still non-identifiable with the second observable.
    # ------------------------------------------------------------------
    r = sa.audit_model(
        f=lambda x,th:[-th[0]*x[0]], g=lambda x,th:[x[0], th[1]*x[0]],
        theta=[0.7, 1.1], t_points=t, x0=[1.0], labels=["k1","k2"],
        global_sweep=False)
    res.append(_ok(7, "two-observable variant is identifiable",
                   r.solvability is sa.Solvability.DETERMINED and r.dof == 0,
                   f"sol={r.solvability.name} dof={r.dof}"))

    # ------------------------------------------------------------------
    # C8: linear matrix path sets tier='linear-rank'.
    #     Falsifier: tier conflated with heuristic or sensitivity branch.
    # ------------------------------------------------------------------
    r = sa.audit_model(A=[[1,1,0,0],[0,1,1,0],[0,0,1,1]], labels=["a","b","c","d"])
    res.append(_ok(8, "linear matrix routes to tier='linear-rank' with dof=1",
                   r.tier == "linear-rank" and r.dof == 1,
                   f"tier={r.tier} dof={r.dof}"))

    # ------------------------------------------------------------------
    # C9: L5 optimism-marker severity is bounded by L5_CAP regardless of
    #     marker count.  Falsifier: severity exceeds the cap.
    # ------------------------------------------------------------------
    blob = ("assume negligible ignore approximately roughly should "
            "stable steady constant fixed held constant")
    r = sa.audit(sa.ingest_language(f"Money drives growth because price {blob}."))
    l5 = next((f for f in r.flags if f.code == "L5"), None)
    res.append(_ok(9, "L5 severity capped at L5_CAP",
                   l5 is not None and l5.severity <= sa.L5_CAP + 1e-9,
                   f"L5 sev={l5.severity if l5 else 'absent'} cap={sa.L5_CAP}"))

    # ------------------------------------------------------------------
    # C10: AuditResult round-trips through JSON.  Tier, solvability, dof
    #      survive serialization.  Falsifier: schema drift or enum loss.
    # ------------------------------------------------------------------
    r = sa.audit_model(A=[[1,1,0,0],[0,1,1,0],[0,0,1,1]], labels=["a","b","c","d"])
    payload = sa.to_json(r)
    j = json.loads(payload)
    res.append(_ok(10, "JSON round-trip preserves tier + solvability + dof",
                   j["solvability"] == r.solvability.name
                   and j["tier"] == r.tier
                   and j["dof"] == r.dof
                   and isinstance(j["flags"], list)))

    print()
    passed = sum(res)
    total  = len(res)
    print(f"{passed}/{total} claims hold."
          + (" all green." if passed == total else " falsifications above."))
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
