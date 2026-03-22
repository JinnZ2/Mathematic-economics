"""
OSDI Sensitivity Analysis

Analyzes how the Overall Socialist Dependence Index responds to variation in
weights, component values, and classification thresholds. All parameters are
grounded in the physical/thermodynamic framework defined in README.md.

OSDI = (SID * w1) + (MSI * w2) + (ISR_norm * w3) + (BSC_norm * w4) + (MM_norm * w5)
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class OSDIWeights:
    """
    Default weighting scheme for the five OSDI components.
    Weights must sum to 1.0 — each reflects the relative importance
    of that structural indicator in the composite index.
    """
    w1_sid: float = 0.30   # Socialist Infrastructure Dependence
    w2_msi: float = 0.20   # Market Substitutability Index
    w3_isr: float = 0.20   # Infrastructure Socialization Ratio (normalized)
    w4_bsc: float = 0.15   # Basic Services Coverage (normalized)
    w5_mm: float = 0.15    # Market Monopolization (normalized)

    def as_array(self) -> np.ndarray:
        return np.array([
            self.w1_sid, self.w2_msi, self.w3_isr,
            self.w4_bsc, self.w5_mm,
        ])

    @property
    def names(self) -> List[str]:
        return ["w1_sid", "w2_msi", "w3_isr", "w4_bsc", "w5_mm"]


@dataclass
class OSDIComponents:
    """
    Default component values for OSDI calculation.
    Each component is a normalized [0, 1] indicator derived from
    physical measurement (energy flows, time allocation, resource access).
    """
    sid: float = 0.60      # Socialist Infrastructure Dependence
    msi: float = 0.98      # Market Substitutability Index
    isr_norm: float = 0.80 # Infrastructure Socialization Ratio (normalized)
    bsc_norm: float = 0.70 # Basic Services Coverage (normalized)
    mm_norm: float = 0.90  # Market Monopolization (normalized)

    def as_array(self) -> np.ndarray:
        return np.array([
            self.sid, self.msi, self.isr_norm,
            self.bsc_norm, self.mm_norm,
        ])

    @property
    def names(self) -> List[str]:
        return ["SID", "MSI", "ISR_norm", "BSC_norm", "MM_norm"]


@dataclass
class VEVLThresholds:
    """
    Value-Extraction / Value-Labour classification thresholds.
    VE/VL < productive_upper  => productive
    VE/VL > extractive_lower  => extractive
    Between the two           => ambiguous / transitional
    """
    productive_upper: float = 0.10
    extractive_lower: float = 0.30


PLOT_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")


# ============================================================================
# CORE COMPUTATION
# ============================================================================

def compute_osdi(weights: np.ndarray, components: np.ndarray) -> float:
    """Dot-product of weight vector and component vector."""
    return float(np.dot(weights, components))


def compute_osdi_default() -> float:
    """OSDI at baseline parameters."""
    return compute_osdi(OSDIWeights().as_array(), OSDIComponents().as_array())


# ============================================================================
# 1. WEIGHT SENSITIVITY
# ============================================================================

def weight_sensitivity(
    n_points: int = 200,
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    For each weight, sweep it from 0.05 to 0.50 while proportionally
    rescaling the remaining four weights so the total stays at 1.0.

    Returns a dict mapping weight name -> (sweep_values, osdi_values).
    """
    defaults = OSDIWeights()
    default_w = defaults.as_array()
    components = OSDIComponents().as_array()
    sweep = np.linspace(0.05, 0.50, n_points)

    results: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}

    for idx, name in enumerate(defaults.names):
        osdi_vals = np.empty(n_points)
        for j, w_val in enumerate(sweep):
            w = default_w.copy()
            # Proportionally redistribute remaining weight
            remaining_sum = 1.0 - default_w[idx]
            new_remaining = 1.0 - w_val
            if remaining_sum > 0:
                scale = new_remaining / remaining_sum
            else:
                scale = 0.0
            for k in range(len(w)):
                if k == idx:
                    w[k] = w_val
                else:
                    w[k] = default_w[k] * scale
            osdi_vals[j] = compute_osdi(w, components)
        results[name] = (sweep.copy(), osdi_vals)

    return results


def plot_weight_sensitivity(
    results: Dict[str, Tuple[np.ndarray, np.ndarray]],
) -> None:
    """Save weight-sensitivity plot to PLOT_DIR."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, (x, y) in results.items():
        ax.plot(x, y, label=name, linewidth=1.5)
    ax.axhline(compute_osdi_default(), color="grey", linestyle="--",
               linewidth=0.8, label="baseline OSDI")
    ax.set_xlabel("Weight value")
    ax.set_ylabel("OSDI")
    ax.set_title("OSDI sensitivity to individual weight variation (sum = 1)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "weight_sensitivity.png"), dpi=150)
    plt.close(fig)


# ============================================================================
# 2. COMPONENT SENSITIVITY
# ============================================================================

def component_sensitivity(
    n_points: int = 200,
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Vary each component value +/-50 % from its default while holding
    the others fixed.  Components are clipped to [0, 1].

    Returns dict mapping component name -> (sweep_values, osdi_values).
    """
    defaults = OSDIComponents()
    default_c = defaults.as_array()
    weights = OSDIWeights().as_array()

    results: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}

    for idx, name in enumerate(defaults.names):
        lo = max(0.0, default_c[idx] * 0.50)
        hi = min(1.0, default_c[idx] * 1.50)
        sweep = np.linspace(lo, hi, n_points)
        osdi_vals = np.empty(n_points)
        for j, c_val in enumerate(sweep):
            c = default_c.copy()
            c[idx] = c_val
            osdi_vals[j] = compute_osdi(weights, c)
        results[name] = (sweep, osdi_vals)

    return results


def plot_component_sensitivity(
    results: Dict[str, Tuple[np.ndarray, np.ndarray]],
) -> None:
    """Save component-sensitivity plot to PLOT_DIR."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, (x, y) in results.items():
        ax.plot(x, y, label=name, linewidth=1.5)
    ax.axhline(compute_osdi_default(), color="grey", linestyle="--",
               linewidth=0.8, label="baseline OSDI")
    ax.set_xlabel("Component value")
    ax.set_ylabel("OSDI")
    ax.set_title("OSDI sensitivity to individual component variation (\u00b150 %)")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "component_sensitivity.png"), dpi=150)
    plt.close(fig)


# ============================================================================
# 3. THRESHOLD SENSITIVITY (VE/VL CLASSIFICATION)
# ============================================================================

def classify_ve_vl(ratio: float, thresholds: VEVLThresholds) -> str:
    """Classify a VE/VL ratio as productive, extractive, or transitional."""
    if ratio < thresholds.productive_upper:
        return "productive"
    elif ratio > thresholds.extractive_lower:
        return "extractive"
    else:
        return "transitional"


def threshold_sensitivity(
    n_points: int = 300,
) -> Dict[str, np.ndarray]:
    """
    Move both VE/VL thresholds +/-50 % and evaluate how the fraction
    of a fixed test population classified as each category changes.

    Returns dict with keys: productive_upper_sweep, extractive_lower_sweep,
    and 2-D arrays for each category fraction.
    """
    defaults = VEVLThresholds()

    # Fixed test population: 500 ratios uniformly distributed in [0, 0.5]
    rng = np.random.default_rng(seed=42)
    population = rng.uniform(0.0, 0.5, size=500)

    prod_sweep = np.linspace(
        defaults.productive_upper * 0.50,
        defaults.productive_upper * 1.50,
        n_points,
    )
    extr_sweep = np.linspace(
        defaults.extractive_lower * 0.50,
        defaults.extractive_lower * 1.50,
        n_points,
    )

    # Vary productive threshold (keep extractive fixed)
    frac_prod_by_prod_thresh = np.empty(n_points)
    frac_extr_by_prod_thresh = np.empty(n_points)
    frac_tran_by_prod_thresh = np.empty(n_points)
    for i, p_thresh in enumerate(prod_sweep):
        th = VEVLThresholds(productive_upper=p_thresh,
                            extractive_lower=defaults.extractive_lower)
        labels = np.array([classify_ve_vl(r, th) for r in population])
        frac_prod_by_prod_thresh[i] = np.mean(labels == "productive")
        frac_extr_by_prod_thresh[i] = np.mean(labels == "extractive")
        frac_tran_by_prod_thresh[i] = np.mean(labels == "transitional")

    # Vary extractive threshold (keep productive fixed)
    frac_prod_by_extr_thresh = np.empty(n_points)
    frac_extr_by_extr_thresh = np.empty(n_points)
    frac_tran_by_extr_thresh = np.empty(n_points)
    for i, e_thresh in enumerate(extr_sweep):
        th = VEVLThresholds(productive_upper=defaults.productive_upper,
                            extractive_lower=e_thresh)
        labels = np.array([classify_ve_vl(r, th) for r in population])
        frac_prod_by_extr_thresh[i] = np.mean(labels == "productive")
        frac_extr_by_extr_thresh[i] = np.mean(labels == "extractive")
        frac_tran_by_extr_thresh[i] = np.mean(labels == "transitional")

    return {
        "prod_sweep": prod_sweep,
        "extr_sweep": extr_sweep,
        "frac_prod_by_prod_thresh": frac_prod_by_prod_thresh,
        "frac_extr_by_prod_thresh": frac_extr_by_prod_thresh,
        "frac_tran_by_prod_thresh": frac_tran_by_prod_thresh,
        "frac_prod_by_extr_thresh": frac_prod_by_extr_thresh,
        "frac_extr_by_extr_thresh": frac_extr_by_extr_thresh,
        "frac_tran_by_extr_thresh": frac_tran_by_extr_thresh,
    }


def plot_threshold_sensitivity(results: Dict[str, np.ndarray]) -> None:
    """Save threshold-sensitivity plots to PLOT_DIR."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left panel: vary productive threshold
    ax = axes[0]
    ax.plot(results["prod_sweep"], results["frac_prod_by_prod_thresh"],
            label="productive", linewidth=1.5)
    ax.plot(results["prod_sweep"], results["frac_tran_by_prod_thresh"],
            label="transitional", linewidth=1.5)
    ax.plot(results["prod_sweep"], results["frac_extr_by_prod_thresh"],
            label="extractive", linewidth=1.5)
    ax.axvline(VEVLThresholds().productive_upper, color="grey",
               linestyle="--", linewidth=0.8, label="default threshold")
    ax.set_xlabel("Productive upper threshold")
    ax.set_ylabel("Population fraction")
    ax.set_title("Classification vs. productive threshold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Right panel: vary extractive threshold
    ax = axes[1]
    ax.plot(results["extr_sweep"], results["frac_prod_by_extr_thresh"],
            label="productive", linewidth=1.5)
    ax.plot(results["extr_sweep"], results["frac_tran_by_extr_thresh"],
            label="transitional", linewidth=1.5)
    ax.plot(results["extr_sweep"], results["frac_extr_by_extr_thresh"],
            label="extractive", linewidth=1.5)
    ax.axvline(VEVLThresholds().extractive_lower, color="grey",
               linestyle="--", linewidth=0.8, label="default threshold")
    ax.set_xlabel("Extractive lower threshold")
    ax.set_ylabel("Population fraction")
    ax.set_title("Classification vs. extractive threshold")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "threshold_sensitivity.png"), dpi=150)
    plt.close(fig)


# ============================================================================
# 4. MONTE CARLO ANALYSIS
# ============================================================================

@dataclass
class MonteCarloResult:
    """Summary statistics from Monte Carlo sampling of OSDI."""
    samples: np.ndarray
    mean: float
    median: float
    percentile_5: float
    percentile_95: float


def monte_carlo_osdi(
    n_samples: int = 1000,
    perturbation_fraction: float = 0.30,
    seed: int = 42,
) -> MonteCarloResult:
    """
    Sample all weights and components uniformly within +/-perturbation_fraction
    of their defaults.  Weights are renormalized to sum to 1 after sampling.
    Components are clipped to [0, 1].

    Returns MonteCarloResult with the OSDI distribution.
    """
    rng = np.random.default_rng(seed=seed)
    default_w = OSDIWeights().as_array()
    default_c = OSDIComponents().as_array()

    osdi_samples = np.empty(n_samples)

    for i in range(n_samples):
        # Sample weights within +/-30 % of defaults
        w_lo = default_w * (1.0 - perturbation_fraction)
        w_hi = default_w * (1.0 + perturbation_fraction)
        w = rng.uniform(w_lo, w_hi)
        w = w / w.sum()  # Renormalize so weights sum to 1

        # Sample components within +/-30 % of defaults, clipped to [0, 1]
        c_lo = np.maximum(0.0, default_c * (1.0 - perturbation_fraction))
        c_hi = np.minimum(1.0, default_c * (1.0 + perturbation_fraction))
        c = rng.uniform(c_lo, c_hi)

        osdi_samples[i] = compute_osdi(w, c)

    return MonteCarloResult(
        samples=osdi_samples,
        mean=float(np.mean(osdi_samples)),
        median=float(np.median(osdi_samples)),
        percentile_5=float(np.percentile(osdi_samples, 5)),
        percentile_95=float(np.percentile(osdi_samples, 95)),
    )


def plot_monte_carlo(result: MonteCarloResult) -> None:
    """Save Monte Carlo histogram to PLOT_DIR."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(result.samples, bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(result.mean, color="red", linestyle="-",
               linewidth=1.5, label=f"mean = {result.mean:.4f}")
    ax.axvline(result.median, color="orange", linestyle="--",
               linewidth=1.5, label=f"median = {result.median:.4f}")
    ax.axvline(result.percentile_5, color="blue", linestyle=":",
               linewidth=1.2, label=f"5th pctl = {result.percentile_5:.4f}")
    ax.axvline(result.percentile_95, color="blue", linestyle=":",
               linewidth=1.2, label=f"95th pctl = {result.percentile_95:.4f}")
    ax.axvline(compute_osdi_default(), color="green", linestyle="-.",
               linewidth=1.2, label=f"baseline = {compute_osdi_default():.4f}")
    ax.set_xlabel("OSDI value")
    ax.set_ylabel("Frequency")
    ax.set_title(f"Monte Carlo OSDI distribution ({len(result.samples)} samples, \u00b130 % perturbation)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, "monte_carlo_osdi.png"), dpi=150)
    plt.close(fig)


# ============================================================================
# 5. ELASTICITY / SENSITIVITY SUMMARY TABLE
# ============================================================================

def compute_elasticities() -> List[Tuple[str, float, float]]:
    """
    Compute the elasticity of OSDI with respect to each weight and component.

    Elasticity = (dOSDI / dx) * (x / OSDI)

    Uses central finite differences with a small perturbation (1 %).
    For weights, the perturbation is applied and remaining weights rescaled.

    Returns list of (parameter_name, partial_derivative, elasticity) sorted
    by absolute elasticity descending.
    """
    default_w = OSDIWeights().as_array()
    default_c = OSDIComponents().as_array()
    osdi_base = compute_osdi(default_w, default_c)
    eps = 0.01  # 1 % perturbation

    rows: List[Tuple[str, float, float]] = []
    weight_names = OSDIWeights().names
    component_names = OSDIComponents().names

    # Weight elasticities
    for idx, name in enumerate(weight_names):
        delta = default_w[idx] * eps
        if delta < 1e-12:
            rows.append((name, 0.0, 0.0))
            continue

        # Forward
        w_fwd = default_w.copy()
        w_fwd[idx] += delta
        remaining = 1.0 - default_w[idx]
        if remaining > 0:
            scale = (1.0 - w_fwd[idx]) / remaining
            for k in range(len(w_fwd)):
                if k != idx:
                    w_fwd[k] = default_w[k] * scale
        osdi_fwd = compute_osdi(w_fwd, default_c)

        # Backward
        w_bwd = default_w.copy()
        w_bwd[idx] -= delta
        if remaining > 0:
            scale = (1.0 - w_bwd[idx]) / remaining
            for k in range(len(w_bwd)):
                if k != idx:
                    w_bwd[k] = default_w[k] * scale
        osdi_bwd = compute_osdi(w_bwd, default_c)

        partial = (osdi_fwd - osdi_bwd) / (2 * delta)
        elasticity = partial * (default_w[idx] / osdi_base)
        rows.append((name, partial, elasticity))

    # Component elasticities (straightforward: OSDI is linear in components)
    for idx, name in enumerate(component_names):
        delta = default_c[idx] * eps
        if delta < 1e-12:
            rows.append((name, 0.0, 0.0))
            continue

        c_fwd = default_c.copy()
        c_fwd[idx] = min(1.0, default_c[idx] + delta)
        osdi_fwd = compute_osdi(default_w, c_fwd)

        c_bwd = default_c.copy()
        c_bwd[idx] = max(0.0, default_c[idx] - delta)
        osdi_bwd = compute_osdi(default_w, c_bwd)

        partial = (osdi_fwd - osdi_bwd) / (c_fwd[idx] - c_bwd[idx])
        elasticity = partial * (default_c[idx] / osdi_base)
        rows.append((name, partial, elasticity))

    # Sort by absolute elasticity descending
    rows.sort(key=lambda r: abs(r[2]), reverse=True)
    return rows


def print_sensitivity_table(rows: List[Tuple[str, float, float]]) -> None:
    """Print a formatted summary table of parameter sensitivities."""
    header = f"{'Parameter':<14} {'dOSDI/dx':>12} {'Elasticity':>12}"
    separator = "-" * len(header)
    print("\n" + separator)
    print("OSDI SENSITIVITY SUMMARY")
    print(f"Baseline OSDI = {compute_osdi_default():.4f}")
    print(separator)
    print(header)
    print(separator)
    for name, partial, elasticity in rows:
        print(f"{name:<14} {partial:>12.6f} {elasticity:>12.6f}")
    print(separator)
    print("Elasticity = (dOSDI/dx) * (x / OSDI)")
    print("Higher |elasticity| => OSDI is more sensitive to that parameter")
    print(separator + "\n")


# ============================================================================
# MAIN
# ============================================================================

def run_all_analyses() -> None:
    """Execute all sensitivity analyses, print results, and save plots."""
    os.makedirs(PLOT_DIR, exist_ok=True)

    print("=" * 60)
    print("OSDI SENSITIVITY ANALYSIS")
    print("=" * 60)

    # 1. Weight sensitivity
    print("\n[1/5] Running weight sensitivity analysis ...")
    w_results = weight_sensitivity()
    plot_weight_sensitivity(w_results)
    print(f"      Saved: {os.path.join(PLOT_DIR, 'weight_sensitivity.png')}")

    # 2. Component sensitivity
    print("[2/5] Running component sensitivity analysis ...")
    c_results = component_sensitivity()
    plot_component_sensitivity(c_results)
    print(f"      Saved: {os.path.join(PLOT_DIR, 'component_sensitivity.png')}")

    # 3. Threshold sensitivity
    print("[3/5] Running VE/VL threshold sensitivity analysis ...")
    t_results = threshold_sensitivity()
    plot_threshold_sensitivity(t_results)
    print(f"      Saved: {os.path.join(PLOT_DIR, 'threshold_sensitivity.png')}")

    # 4. Monte Carlo
    print("[4/5] Running Monte Carlo analysis (1000 samples) ...")
    mc = monte_carlo_osdi(n_samples=1000)
    plot_monte_carlo(mc)
    print(f"      Saved: {os.path.join(PLOT_DIR, 'monte_carlo_osdi.png')}")
    print(f"      Mean     = {mc.mean:.4f}")
    print(f"      Median   = {mc.median:.4f}")
    print(f"      5th pctl = {mc.percentile_5:.4f}")
    print(f"      95th pctl= {mc.percentile_95:.4f}")

    # 5. Sensitivity summary table
    print("[5/5] Computing elasticities ...")
    rows = compute_elasticities()
    print_sensitivity_table(rows)

    print("All analyses complete.")


if __name__ == "__main__":
    run_all_analyses()
