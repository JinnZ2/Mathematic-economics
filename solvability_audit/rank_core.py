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
from dataclasses import dataclass

RTOL_RANK = 1e-7    # singular value counts as zero below RTOL_RANK * s_max
RTOL_ZCOL = 1e-8    # column counts as zero below RTOL_ZCOL * max_col_norm
FD_REL    = 1e-6    # finite-difference step, relative to |theta_j|

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
    if deficiency == 0:
        cls, note = "IDENTIFIABLE", "rank == p (locally)"
    elif zero_cols:
        cls, note = "NON_IDENTIFIABLE", f"output insensitive to: {zero_cols}"
    else:
        cls, note = "NON_IDENTIFIABLE", "rank-deficient: columns linearly dependent (coupled params)"
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
    """Build S[r][j] = d y_r / d theta_j by forward finite difference, then rank.
    f(x,theta)->dx ; g(x,theta)->observables. Pure numerics, model-agnostic."""
    p = len(theta)
    labels = labels or [f"theta{j}" for j in range(p)]
    base = _observe(g, _rk4(f, x0, theta, t_points), theta)
    rows = len(base)
    S = [[0.0]*p for _ in range(rows)]
    for j in range(p):
        d = FD_REL * (abs(theta[j]) if theta[j] != 0 else 1.0)
        tp = list(theta); tp[j] += d
        pert = _observe(g, _rk4(f, x0, tp, t_points), tp)
        for r in range(rows):
            S[r][j] = (pert[r] - base[r]) / d
    return _classify_rank(p, singular_values(S), _col_norms(S), labels)

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
