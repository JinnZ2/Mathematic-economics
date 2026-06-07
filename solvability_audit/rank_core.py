"""
rank_core.py  --  CC0, stdlib only, mobile-runnable. Companion to solvability_audit.py
StrucID-style identifiability via sensitivity-matrix rank. No numpy.

Contract: do not forecast. Measure whether the unknowns are recoverable.
Two entry points:
    jacobian_rank_linear(A)                 # static/linear constraint matrix
    sensitivity_rank(f, g, theta, t, x0)    # dynamical ODE model (finite-diff S)

Three cases (Heinrich et al. 2025, StrucID):
    rank == p            -> locally identifiable          (DETERMINED)
    zero column j        -> output insensitive to theta_j -> param j unrecoverable
    rank < p, no zero col-> columns linearly dependent    -> params coupled
"""

import math
import random
from dataclasses import dataclass

RTOL_RANK     = 1e-7    # singular value counts as zero below RTOL_RANK * s_max
RTOL_ZCOL     = 1e-8    # column counts as zero below RTOL_ZCOL * max_col_norm
NEAR_RANK_TOL = 1e-4    # min/max sval ratio below this -> NEAR-DEFICIENT (marginal)
FD_REL        = 1e-6    # finite-difference step, relative to |theta_j|

# ----------------------------------------------------------------------
# 1. STDLIB LINEAR ALGEBRA
# ----------------------------------------------------------------------

def _transpose(M):
    return [list(col) for col in zip(*M)] if M else []

def _gram(S):
    """S^T S  (p x p) for S of shape (rows x p)."""
    p = len(S[0])
    G = [[0.0]*p for _ in range(p)]
    for r in S:
        for i in range(p):
            ri = r[i]
            if ri == 0.0: continue
            for j in range(i, p):
                G[i][j] += ri * r[j]
    for i in range(p):
        for j in range(i):
            G[i][j] = G[j][i]
    return G

def _jacobi_eigvals(A, iters=100, eps=1e-14):
    """Eigenvalues of symmetric A via cyclic Jacobi rotations. p small."""
    n = len(A)
    A = [row[:] for row in A]
    for _ in range(iters):
        off = 0.0; p = q = 0
        for i in range(n):
            for j in range(i+1, n):
                if abs(A[i][j]) > off:
                    off = abs(A[i][j]); p, q = i, j
        if off < eps:
            break
        app, aqq, apq = A[p][p], A[q][q], A[p][q]
        phi = 0.5 * math.atan2(2*apq, aqq - app) if aqq != app else math.pi/4
        c, s = math.cos(phi), math.sin(phi)
        for k in range(n):
            akp, akq = A[k][p], A[k][q]
            A[k][p] = c*akp - s*akq
            A[k][q] = s*akp + c*akq
        for k in range(n):
            akp, akq = A[p][k], A[q][k]
            A[p][k] = c*akp - s*akq
            A[q][k] = s*akp + c*akq
    return sorted((A[i][i] for i in range(n)), reverse=True)

def singular_values(S):
    """Singular values of S = sqrt(eigenvalues of S^T S), descending."""
    if not S or not S[0]:
        return []
    ev = _jacobi_eigvals(_gram(S))
    return [math.sqrt(v) if v > 0 else 0.0 for v in ev]

def _col_norms(S):
    p = len(S[0])
    return [math.sqrt(sum(r[j]*r[j] for r in S)) for j in range(p)]

# ----------------------------------------------------------------------
# 2. RANK REPORT
# ----------------------------------------------------------------------

@dataclass
class RankReport:
    p: int                 # number of parameters / unknown columns
    rank: int
    deficiency: int        # p - rank  == rigorous DOF
    singular_values: list
    zero_cols: list        # indices insensitive to output (structurally non-id.)
    classification: str
    note: str = ""

def _classify_rank(p, svals, col_norms, labels):
    smax = max(svals) if svals else 0.0
    rank = sum(1 for s in svals if smax > 0 and s > RTOL_RANK * smax)
    cmax = max(col_norms) if col_norms else 0.0
    zero_cols = [labels[j] for j, cn in enumerate(col_norms)
                 if cmax == 0.0 or cn < RTOL_ZCOL * cmax]
    deficiency = p - rank

    # near-rank-deficiency guard: smallest *counted-nonzero* sval close to threshold
    # means a small perturbation could flip the rank.  Mark as MARGINAL.
    near = ""
    if smax > 0 and rank > 0:
        nonzero = [s for s in svals if s > RTOL_RANK * smax]
        if nonzero:
            ratio = min(nonzero) / smax
            if ratio < NEAR_RANK_TOL:
                near = f"  [MARGINAL: min/max sval = {ratio:.2e} < {NEAR_RANK_TOL:.0e}]"

    if deficiency == 0:
        cls, note = "IDENTIFIABLE", "rank == p (locally)" + near
    elif zero_cols:
        cls, note = "NON_IDENTIFIABLE", f"output insensitive to: {zero_cols}" + near
    else:
        cls, note = "NON_IDENTIFIABLE", "rank-deficient: columns linearly dependent (coupled params)" + near
    return RankReport(p, rank, deficiency, [round(s, 6) for s in svals], zero_cols, cls, note)

# ----------------------------------------------------------------------
# 3. STATIC / LINEAR BRANCH  (Rouche-Capelli via rank)
# ----------------------------------------------------------------------

def jacobian_rank_linear(A, labels=None):
    """A: rows = constraints, cols = unknowns. deficiency = solution-space DOF."""
    p = len(A[0]) if A else 0
    labels = labels or [f"x{j}" for j in range(p)]
    return _classify_rank(p, singular_values(A), _col_norms(A), labels)

# ----------------------------------------------------------------------
# 4. DYNAMICAL BRANCH  (sensitivity matrix by finite difference)
# ----------------------------------------------------------------------

def _rk4(f, x0, theta, t_points, nsub=4):
    """Integrate dx/dt=f(x,theta); return states at each t in t_points."""
    x = list(x0); out = [list(x)]
    for a, b in zip(t_points, t_points[1:]):
        h = (b - a) / nsub
        for _ in range(nsub):
            k1 = f(x, theta)
            k2 = f([xi + 0.5*h*k1i for xi, k1i in zip(x, k1)], theta)
            k3 = f([xi + 0.5*h*k2i for xi, k2i in zip(x, k2)], theta)
            k4 = f([xi + h*k3i for xi, k3i in zip(x, k3)], theta)
            x = [xi + (h/6)*(a1+2*a2+2*a3+a4)
                 for xi, a1, a2, a3, a4 in zip(x, k1, k2, k3, k4)]
        out.append(list(x))
    return out

def _observe(g, states, theta):
    """Flatten g(x,theta) over all time points -> vector."""
    vec = []
    for x in states:
        vec.extend(g(x, theta))
    return vec

def sensitivity_rank(f, g, theta, t_points, x0, labels=None):
    """Build S[r][j] = d y_r / d theta_j by *central* finite difference, then rank.
    Central diff cancels the O(h) truncation term -> conditioning ~ h^2 + eps/h.
    f(x,theta)->dx ; g(x,theta)->observables. Pure numerics, model-agnostic.
    Near-rank-deficiency surfaces via the [MARGINAL] tag in the report note."""
    p = len(theta)
    labels = labels or [f"theta{j}" for j in range(p)]
    S = None
    for j in range(p):
        d = FD_REL * (abs(theta[j]) if theta[j] != 0 else 1.0)
        tp_plus  = list(theta); tp_plus[j]  += d
        tp_minus = list(theta); tp_minus[j] -= d
        y_plus  = _observe(g, _rk4(f, x0, tp_plus,  t_points), tp_plus)
        y_minus = _observe(g, _rk4(f, x0, tp_minus, t_points), tp_minus)
        if S is None:
            S = [[0.0]*p for _ in range(len(y_plus))]
        inv2d = 0.5 / d
        for r in range(len(y_plus)):
            S[r][j] = (y_plus[r] - y_minus[r]) * inv2d
    return _classify_rank(p, singular_values(S), _col_norms(S), labels)

# ----------------------------------------------------------------------
# 4b. GLOBAL SWEEP  (sample-and-aggregate identifiability)
# ----------------------------------------------------------------------

@dataclass
class GlobalRankReport:
    p: int
    generic_rank: int           # max rank attained across samples (~almost-everywhere)
    deficiency: int             # p - generic_rank
    singular_values: list       # spectrum at the sample that attained generic_rank
    persistent_zero_cols: list  # zero in EVERY sample -> structurally insensitive
    classification: str
    note: str = ""
    n_samples: int = 0

def jitter_points(theta, n=8, frac=0.5, seed=0):
    """Return n parameter samples: theta itself, then n-1 uniform [-frac, +frac]
    relative jitters.  Used by the global sweep to probe genericity of rank."""
    rng = random.Random(seed)
    pts = [list(theta)]
    for _ in range(max(0, n - 1)):
        pts.append([v + (abs(v) if v != 0 else 1.0) * frac * (2*rng.random() - 1)
                    for v in theta])
    return pts

def sensitivity_rank_global(f, g, theta_points, t_points, x0, labels=None):
    """Sweep rank across theta samples.  Generic rank = max attained (rank holds
    almost everywhere; lower-rank points are measure-zero pathologies in the
    StrucID sense).  Persistent zero col = zero at every sample -> param truly
    structurally insensitive, not just zero at one degenerate point."""
    p = len(theta_points[0])
    labels = labels or [f"theta{j}" for j in range(p)]
    reports = [sensitivity_rank(f, g, th, t_points, x0, labels) for th in theta_points]

    ranks = [r.rank for r in reports]
    generic_rank = max(ranks)
    best = next(r for r in reports if r.rank == generic_rank)

    persistent = set(reports[0].zero_cols)
    for r in reports[1:]:
        persistent &= set(r.zero_cols)
    persistent_zero_cols = [c for c in labels if c in persistent]

    deficiency = p - generic_rank
    if deficiency == 0:
        cls = "IDENTIFIABLE"
        note = f"generic rank == p across {len(theta_points)} samples"
    elif persistent_zero_cols:
        cls = "NON_IDENTIFIABLE"
        note = f"persistently insensitive across all samples: {persistent_zero_cols}"
    else:
        cls = "NON_IDENTIFIABLE"
        note = f"generic-rank deficient by {deficiency}: coupling holds across all {len(theta_points)} samples"
    return GlobalRankReport(p, generic_rank, deficiency, best.singular_values,
                            persistent_zero_cols, cls, note, len(theta_points))

# ----------------------------------------------------------------------
# 5. SMOKE TESTS  (known identifiability outcomes)
# ----------------------------------------------------------------------

def _show(tag, rr):
    print(f"== {tag} ==")
    print(f"  {rr.classification} | p={rr.p} rank={rr.rank} deficiency={rr.deficiency}")
    print(f"  singular values: {rr.singular_values}")
    print(f"  {rr.note}\n")

if __name__ == "__main__":
    t = [0.0, 0.5, 1.0, 1.5, 2.0]

    # A) identifiable: dx/dt=-k x, y=x, one param -> rank 1 == p
    _show("A identifiable  dx/dt=-k x, y=x",
          sensitivity_rank(lambda x,th: [-th[0]*x[0]],
                           lambda x,th: [x[0]],
                           [0.7], t, [1.0], labels=["k"]))

    # B) zero-column: param w unused -> structurally non-identifiable, zero col
    _show("B zero-column   w unused",
          sensitivity_rank(lambda x,th: [-th[0]*x[0]],
                           lambda x,th: [x[0]],
                           [0.7, 0.3], t, [1.0], labels=["k","w"]))

    # C) coupled product: dx/dt=-(k1 k2) x, y=x -> columns dependent, deficiency 1
    _show("C coupled       dx/dt=-(k1 k2) x, y=x",
          sensitivity_rank(lambda x,th: [-(th[0]*th[1])*x[0]],
                           lambda x,th: [x[0]],
                           [0.7, 1.1], t, [1.0], labels=["k1","k2"]))

    # D) static linear: 3 equations, 4 unknowns -> deficiency 1
    A = [[1,1,0,0],[0,1,1,0],[0,0,1,1]]
    _show("D static linear 3 eq / 4 unknown",
          jacobian_rank_linear(A, labels=["a","b","c","d"]))
