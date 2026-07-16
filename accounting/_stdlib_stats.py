"""
_stdlib_stats.py -- CC0. Internal helper for accounting/ HVAC modules.

Small stdlib replacements for the numpy / scipy pieces the HVAC audits use:
  - poisson(rng, lam)               Poisson sampler (Knuth for small lam,
                                    Gaussian approximation for large)
  - welch_t_greater(a, b)           one-sided Welch's t-test (H1: mean(a) > mean(b))
  - student_t_cdf(t, dof)           Student's t CDF via regularized incomplete beta
  - correlation(x, y)               Pearson r
  - ols(X, y)                       ordinary least squares with intercept, returns
                                    coeffs, std_errors, t_stats, p_values, r_squared,
                                    partial_correlations (each len == n_features)

Kept in accounting/ (not core/) because it is specific to the HVAC audit
family and its API is not stable enough for the SURFACE.md contract.

Not registered in accounting/__init__.py -- leading underscore marks it
internal. The three consumers (HVAC_gradient, generic, unknown_variable_tester)
import it either as `import _stdlib_stats` (when run as a script from the
accounting/ directory) or `from accounting._stdlib_stats` (when imported as
part of the package).
"""

import math
import statistics


# ----------------------------------------------------------------------
# random sampling
# ----------------------------------------------------------------------

def poisson(rng, lam):
    """Poisson(lam) sample using the supplied random.Random instance.
    Knuth's multiplicative algorithm for lam < 30; Gaussian approximation
    (rounded, floored at 0) for larger lam so we don't loop 500+ times."""
    if lam < 0:
        raise ValueError("lambda must be >= 0")
    if lam == 0:
        return 0
    if lam < 30.0:
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while True:
            k += 1
            p *= rng.random()
            if p <= L:
                return k - 1
    return max(0, round(rng.gauss(lam, math.sqrt(lam))))


# ----------------------------------------------------------------------
# Student's t distribution CDF (via regularized incomplete beta)
# Numerical Recipes' betacf continued fraction; correct at any dof >= 1.
# ----------------------------------------------------------------------

def _betacf(x, a, b, iters=200, eps=1e-12):
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, iters + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            return h
    return h


def _incomplete_beta(x, a, b):
    """Regularized incomplete beta I(x; a, b) in [0, 1]."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    bt = math.exp(a * math.log(x) + b * math.log(1.0 - x) - lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(x, a, b) / a
    return 1.0 - bt * _betacf(1.0 - x, b, a) / b


def student_t_cdf(t, dof):
    """Student's t CDF at t with `dof` degrees of freedom."""
    if dof <= 0:
        return float("nan")
    x = dof / (dof + t * t)
    p = 0.5 * _incomplete_beta(x, dof / 2.0, 0.5)
    return 1.0 - p if t > 0 else p


# ----------------------------------------------------------------------
# Welch's t-test (one-sided; H1: mean(a) > mean(b))
# ----------------------------------------------------------------------

def welch_t_greater(a, b):
    """Returns (t_stat, p_value) for H0: mean(a) <= mean(b), H1: mean(a) > mean(b).
    Uses Welch-Satterthwaite dof."""
    a = list(a)
    b = list(b)
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return float("nan"), float("nan")
    ma, mb = statistics.mean(a), statistics.mean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    se2 = va / na + vb / nb
    if se2 <= 0.0:
        return (float("inf"), 0.0) if ma > mb else (0.0, 1.0)
    se = math.sqrt(se2)
    t = (ma - mb) / se
    num = se2 * se2
    den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    dof = num / den if den > 0 else (na + nb - 2)
    p = 1.0 - student_t_cdf(t, dof)
    return t, p


# ----------------------------------------------------------------------
# correlation
# ----------------------------------------------------------------------

def correlation(x, y):
    """Pearson r. Returns 0.0 if either input has zero variance."""
    n = len(x)
    if n != len(y) or n < 2:
        return 0.0
    mx = statistics.mean(x)
    my = statistics.mean(y)
    num = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    dx = math.sqrt(sum((x[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((y[i] - my) ** 2 for i in range(n)))
    if dx == 0.0 or dy == 0.0:
        return 0.0
    return num / (dx * dy)


# ----------------------------------------------------------------------
# linear algebra helpers  (small p; Gauss-Jordan is fine)
# ----------------------------------------------------------------------

def _mat_mul(A, B):
    n, m = len(A), len(A[0])
    p = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) for j in range(p)] for i in range(n)]


def _mat_vec(A, v):
    return [sum(A[i][k] * v[k] for k in range(len(v))) for i in range(len(A))]


def _transpose(A):
    n, m = len(A), len(A[0])
    return [[A[i][j] for i in range(n)] for j in range(m)]


def _invert(A):
    """Gauss-Jordan inverse of a square matrix. Raises on singular."""
    n = len(A)
    M = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        # partial pivot
        pivot = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[pivot][c]) < 1e-15:
            raise ValueError("singular matrix in _invert")
        M[c], M[pivot] = M[pivot], M[c]
        piv = M[c][c]
        M[c] = [x / piv for x in M[c]]
        for r in range(n):
            if r == c:
                continue
            factor = M[r][c]
            if factor == 0.0:
                continue
            M[r] = [M[r][k] - factor * M[c][k] for k in range(2 * n)]
    return [row[n:] for row in M]


# ----------------------------------------------------------------------
# ordinary least squares regression with intercept
# ----------------------------------------------------------------------

def ols(X, y):
    """OLS regression of y on X (list of feature rows). Adds an intercept column.

    Returns dict with:
      coefficients        [intercept, b1, b2, ...]
      std_errors          matching std errors
      t_stats             coefficient / std_error
      p_values            two-sided p-value from student_t_cdf
      r_squared           1 - RSS/TSS
      partial_correlations [r for each non-intercept feature after residualizing]
    """
    n = len(y)
    if n == 0:
        raise ValueError("empty y")
    p_features = len(X[0])
    # augment with intercept
    Xa = [[1.0] + list(row) for row in X]
    p = p_features + 1

    XtX = _mat_mul(_transpose(Xa), Xa)
    Xty = _mat_vec(_transpose(Xa), y)
    XtX_inv = _invert(XtX)
    coeffs = _mat_vec(XtX_inv, Xty)

    y_pred = _mat_vec(Xa, coeffs)
    residuals = [y[k] - y_pred[k] for k in range(n)]
    ss_res = sum(r * r for r in residuals)
    dof = n - p
    mse = ss_res / dof if dof > 0 else float("nan")
    std_errors = [math.sqrt(XtX_inv[i][i] * mse) if dof > 0 else float("nan") for i in range(p)]

    y_mean = statistics.mean(y)
    ss_tot = sum((y[k] - y_mean) ** 2 for k in range(n))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    t_stats = [coeffs[i] / std_errors[i] if std_errors[i] not in (0.0, float("nan")) and not math.isnan(std_errors[i])
               else float("nan") for i in range(p)]
    p_values = [2.0 * (1.0 - student_t_cdf(abs(t), dof)) if not math.isnan(t) else float("nan")
                for t in t_stats]

    # partial correlations for non-intercept features
    partial_corrs = []
    if p_features > 1 and dof > 0:
        for i in range(p_features):
            others_idx = [j for j in range(p_features) if j != i]
            # Regress y on intercept + others
            Xo = [[1.0] + [X[k][j] for j in others_idx] for k in range(n)]
            Xo_t = _transpose(Xo)
            try:
                inv_o = _invert(_mat_mul(Xo_t, Xo))
            except ValueError:
                partial_corrs.append(0.0)
                continue
            coef_y = _mat_vec(inv_o, _mat_vec(Xo_t, y))
            resid_y = [y[k] - sum(Xo[k][m] * coef_y[m] for m in range(len(coef_y))) for k in range(n)]
            xi = [X[k][i] for k in range(n)]
            coef_x = _mat_vec(inv_o, _mat_vec(Xo_t, xi))
            resid_x = [xi[k] - sum(Xo[k][m] * coef_x[m] for m in range(len(coef_x))) for k in range(n)]
            partial_corrs.append(correlation(resid_y, resid_x))
    elif p_features == 1:
        partial_corrs.append(correlation([X[k][0] for k in range(n)], y))

    return {
        "coefficients": coeffs,
        "std_errors": std_errors,
        "t_stats": t_stats,
        "p_values": p_values,
        "r_squared": r_squared,
        "partial_correlations": partial_corrs,
        "dof": dof,
        "n": n,
        "n_features": p_features,
    }


# ----------------------------------------------------------------------
# self-test
# ----------------------------------------------------------------------

if __name__ == "__main__":
    import random
    rng = random.Random(42)

    # 1) Welch t-test on two Gaussian samples with a real mean difference.
    a = [rng.gauss(100.0, 5.0) for _ in range(50)]
    b = [rng.gauss(90.0, 5.0) for _ in range(50)]
    t, p = welch_t_greater(a, b)
    print(f"welch_t_greater  t={t:.3f}  p={p:.4g}   (expect p tiny; mean(a) > mean(b))")

    # 2) Poisson
    counts = [poisson(rng, 3.0) for _ in range(1000)]
    print(f"poisson(3.0)     mean={statistics.mean(counts):.3f}  var={statistics.variance(counts):.3f}"
          f"   (expect both ~3.0)")

    # 3) OLS: y = 2*x1 + 3*x2 + noise, intercept 5.
    X = [[rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)] for _ in range(200)]
    y = [5.0 + 2.0 * row[0] + 3.0 * row[1] + rng.gauss(0.0, 0.5) for row in X]
    r = ols(X, y)
    print(f"ols coefficients (intercept, b1, b2) = "
          f"{[round(c, 3) for c in r['coefficients']]}   (expect ~[5, 2, 3])")
    print(f"ols R^2 = {r['r_squared']:.4f}   (expect ~0.99)")
    print(f"ols p-values = {[f'{p:.2e}' for p in r['p_values']]}")
