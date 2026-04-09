#!/usr/bin/env python3
"""
Dynamic CPI-R Estimator for Bottom 60% Income Cohort
Implements:
  - Kalman filter with shock detection
  - Continuous constraint pressure (standardized co-movement)
  - Latent anchored rent subsystem
  - State-dependent CE correction
  - Credit leverage filter
Author: Anonymous (Thermodynamic Economics)
License: MIT
"""

import numpy as np
import warnings
from scipy.special import softmax

# -------------------------------
# 1. Synthetic Data Generation
# -------------------------------

def generate_true_weights(n_months=60, n_cat=5, random_seed=42):
    """Generate realistic bottom-60% expenditure weights (ground truth) for 2020-2024.
       Categories: Food, Energy, Rent, Core goods, Core services."""
    np.random.seed(random_seed)
    t = np.arange(n_months)
    # Base trends: rent slowly rising, energy spike in 2022 (month 24-36)
    rent = 0.32 + 0.0004 * t + 0.02 * np.exp(-((t-30)/10)**2)
    energy = 0.072 + 0.0001 * t + 0.025 * np.exp(-((t-28)/6)**2)
    food = 0.145 - 0.0001 * t + 0.005 * np.sin(t/12)
    core_goods = 0.213 - 0.0003 * t - 0.01 * (t>24) * (1 - np.exp(-(t-24)/12))
    core_services = 1 - (rent + energy + food + core_goods)
    # Add small noise
    noise = np.random.normal(0, 0.002, (n_months, n_cat))
    weights = np.column_stack([food, energy, rent, core_goods, core_services]) + noise
    weights = np.maximum(weights, 0.01)
    weights = weights / weights.sum(axis=1, keepdims=True)
    return weights

def generate_price_indices(n_months=60):
    """Simulate CPI price indices (cumulative) for each category."""
    # Base 2019 Dec = 100
    t = np.arange(n_months)
    # Food: steady
    food = 100 + 0.15 * t + 0.01 * t**1.1
    # Energy: spike 2022
    energy = 100 + 0.1 * t + 15 * np.exp(-((t-28)/8)**2)
    # Rent: smooth
    rent = 100 + 0.25 * t + 0.002 * t**1.2
    # Core goods: initially high then moderate
    core_goods = 100 + 0.1 * t + 0.005 * t**1.1
    # Core services: steady
    core_services = 100 + 0.2 * t + 0.001 * t**1.3
    return np.column_stack([food, energy, rent, core_goods, core_services])

def generate_credit_income_ratio(n_months=60):
    """Simulate credit usage / income ratio (scalar) with stress in 2022."""
    t = np.arange(n_months)
    base = 0.18
    spike = 0.08 * np.exp(-((t-30)/10)**2)
    noise = np.random.normal(0, 0.01, n_months)
    return np.clip(base + spike + noise, 0.1, 0.35)

def generate_external_rent_anchor(n_months=60):
    """Simulate external rent index (e.g., Apartment List) with less lag than CPI."""
    t = np.arange(n_months)
    # Faster response to market conditions
    anchor = 100 + 0.3 * t + 0.003 * t**1.2 + 2 * np.sin(t/6)
    # Normalize to weight level ~0.32-0.35
    weight_anchor = 0.32 + 0.0003 * t + 0.01 * np.sin(t/12)
    return weight_anchor

# -------------------------------
# 2. Core Algorithm
# -------------------------------

class DynamicCPI_R:
    def __init__(self, n_categories=5, sigma_w=0.005, R_base=0.01,
                 lambda_c=0.25, phi=0.5, tau_shock=0.03, delta_max=0.2,
                 gamma_rent=0.9, shock_gain_factor=0.3):
        self.n = n_categories
        self.sigma_w = sigma_w          # process noise std
        self.R_base = R_base            # base measurement noise std
        self.lambda_c = lambda_c        # constraint pressure sensitivity
        self.phi = phi                  # credit discount factor
        self.tau_shock = tau_shock      # shock detection threshold
        self.delta_max = delta_max      # max CE correction weight
        self.gamma_rent = gamma_rent    # anchor trust for rent
        self.shock_gain_factor = shock_gain_factor  # reduce R during shock

        # State initialization
        self.w = np.ones(n_categories) / n_categories
        self.P = np.ones(n_categories) * (sigma_w**2)   # diagonal covariance

        # History for drift computation
        self.history_w = []
        self.last_ce_weights = None
        self.last_ce_time = -12   # months since last CE

    def renormalize(self, w):
        return w / np.sum(w)

    def observation_model(self, true_weights, t, noise_std=None):
        """Simulate real-time observables: transaction flows + income proxy + credit adjustment."""
        if noise_std is None:
            noise_std = self.R_base
        # Base observation (transaction flows) with noise
        z = true_weights + np.random.normal(0, noise_std, self.n)
        # Income-stratified proxy: rent under-reported, energy over-reported
        bias = np.array([0.005, 0.01, -0.02, 0.0, 0.0])   # food, energy, rent, goods, services
        z_inc = z + bias
        # Credit adjustment
        L = generate_credit_income_ratio(len(true_weights))[t] if t < len(true_weights) else 0.2
        z_adj = z_inc * (1 - self.phi * L)
        return np.maximum(z_adj, 0)

    def shock_detected(self, w_prev, z_curr):
        S = np.sum(np.abs(z_curr - w_prev))
        return S > self.tau_shock

    def constraint_pressure(self, w, price_changes, spend_changes, sigma_P, sigma_E):
        """Continuous constraint pressure using standardized co-movement."""
        # Standardized changes
        delta_P = price_changes / (sigma_P + 1e-6)
        delta_E = spend_changes / (sigma_E + 1e-6)
        C = delta_E * delta_P
        C = np.clip(C, -3, 3)
        w_new = w * np.exp(self.lambda_c * C)
        return self.renormalize(w_new)

    def kalman_update(self, w_pred, P_pred, z, R_eff):
        """Diagonal Kalman update."""
        innovation = z - w_pred
        K = P_pred / (P_pred + R_eff + 1e-8)
        w_new = w_pred + K * innovation
        P_new = (1 - K) * P_pred
        return w_new, P_new, K

    def ce_correction(self, w_est, w_ce, sigma_drift, sigma_ce_hist):
        """State-dependent correction using CE release."""
        delta = min(self.delta_max, sigma_drift / (sigma_ce_hist + 1e-8))
        w_corr = (1 - delta) * w_est + delta * w_ce
        return self.renormalize(w_corr)

    def step(self, t, true_weights, price_indices, spend_shares_truth, sigma_P, sigma_E,
             external_rent_anchor, ce_weights=None, ce_release=False):
        """
        Perform one month update.
        true_weights: ground truth (only for observation simulation)
        price_indices: array of price levels at t (for constraint pressure)
        spend_shares_truth: actual spend shares (for constraint pressure)
        sigma_P, sigma_E: precomputed historical volatilities
        external_rent_anchor: scalar anchor weight for rent
        ce_weights: if ce_release, the new CE weights (ground truth with lag)
        """
        # 1. Predict
        w_pred = self.w.copy()
        P_pred = self.P + self.sigma_w**2

        # 2. Get observation (simulated from truth)
        z = self.observation_model(true_weights, t)

        # 3. Shock detection -> adjust measurement noise
        if self.shock_detected(self.w, z):
            R_eff = self.R_base * self.shock_gain_factor
        else:
            R_eff = self.R_base

        # 4. Kalman update
        w_updated, P_updated, K = self.kalman_update(w_pred, P_pred, z, R_eff)

        # 5. Constraint pressure (if price and spend changes available)
        if price_indices is not None and spend_shares_truth is not None:
            # Compute month-to-month changes
            delta_P = price_indices[t] - price_indices[t-1] if t > 0 else np.zeros(self.n)
            delta_E = spend_shares_truth[t] - spend_shares_truth[t-1] if t > 0 else np.zeros(self.n)
            w_constrained = self.constraint_pressure(w_updated, delta_P, delta_E, sigma_P, sigma_E)
        else:
            w_constrained = w_updated

        # 6. Rent anchoring (latent subsystem)
        rent_idx = 2  # assuming rent is third category
        w_constrained[rent_idx] = self.gamma_rent * external_rent_anchor + \
                                  (1 - self.gamma_rent) * w_constrained[rent_idx]
        w_final = self.renormalize(w_constrained)

        # 7. Update state
        self.w = w_final
        self.P = P_updated
        self.history_w.append(self.w.copy())

        # 8. CE correction (if release this month)
        if ce_release and ce_weights is not None:
            # Compute drift over past 12 months
            if len(self.history_w) >= 12:
                recent_weights = np.array(self.history_w[-12:])
                sigma_drift = np.std(recent_weights, axis=0)
            else:
                sigma_drift = np.zeros(self.n)
            # Use historical volatility of CE (here we assume 0.01 for all)
            sigma_ce_hist = 0.01 * np.ones(self.n)
            self.w = self.ce_correction(self.w, ce_weights, sigma_drift, sigma_ce_hist)
            self.P = self.P * 0.5   # reset uncertainty

        return self.w

# -------------------------------
# 3. Backtest Runner
# -------------------------------

def run_backtest():
    print("Generating synthetic data for 2020-2024 (60 months)...")
    n_months = 60
    true_weights = generate_true_weights(n_months)
    price_indices = generate_price_indices(n_months)
    spend_shares = true_weights.copy()   # In reality spend shares = weights * quantity, but for sim we use same
    external_rent_anchor = generate_external_rent_anchor(n_months)
    
    # Precompute historical volatilities for constraint pressure (using first 12 months)
    sigma_P = np.std(np.diff(price_indices, axis=0), axis=0)
    sigma_E = np.std(np.diff(spend_shares, axis=0), axis=0)
    
    # Simulate CE releases (annual, with 12-month lag)
    # CE for year Y becomes available in Dec of Y+1
    ce_release_months = [12, 24, 36, 48]   # Dec 2020, 2021, 2022, 2023 (lagged)
    ce_weights_dict = {}
    for m in ce_release_months:
        # The "truth" from 12 months ago
        ce_weights_dict[m] = true_weights[m-12]   # CE release at month m gives weights for month m-12
    
    # Initialize estimator
    estimator = DynamicCPI_R()
    estimated_weights = []
    
    print("Running dynamic weighting filter...")
    for t in range(n_months):
        ce_weights = ce_weights_dict.get(t, None)
        ce_release = (ce_weights is not None)
        w_est = estimator.step(t, true_weights[t], price_indices, spend_shares,
                               sigma_P, sigma_E, external_rent_anchor[t],
                               ce_weights, ce_release)
        estimated_weights.append(w_est)
    
    estimated_weights = np.array(estimated_weights)
    
    # Compute RMS error per category and overall
    errors = estimated_weights - true_weights
    rms_per_cat = np.sqrt(np.mean(errors**2, axis=0))
    overall_rms = np.sqrt(np.mean(errors**2))
    
    print("\n===== Backtest Results (2020-2024) =====")
    cat_names = ["Food", "Energy", "Rent", "Core goods", "Core services"]
    for i, name in enumerate(cat_names):
        print(f"{name:15s} RMS error: {rms_per_cat[i]:.4f} absolute")
    print(f"\nOverall RMS error (all categories): {overall_rms:.4f} absolute")
    print(f"Relative error (relative to typical weight ~0.2-0.3): {overall_rms/0.25*100:.1f}%")
    
    # Compare final estimated weights vs true
    print("\nFinal weights (month 60):")
    print("Category     Estimated   True")
    for i, name in enumerate(cat_names):
        print(f"{name:12s} {estimated_weights[-1,i]:.3f}      {true_weights[-1,i]:.3f}")
    
    return estimated_weights, true_weights

# -------------------------------
# 4. Real-time API Stub (Flask)
# -------------------------------

def create_api():
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    # In production, you would load a persistent estimator that updates daily
    estimator = DynamicCPI_R()
    # ... (hook to real data feeds)
    
    @app.route('/v1/cpi-r/current', methods=['GET'])
    def current_cpi_r():
        # Placeholder: return last computed values
        return jsonify({
            "timestamp": "2026-04-09",
            "cpi_r_cumulative_since_dec2019": 32.4,
            "cpi_r_monthly_annualized": 4.1,
            "weights": {
                "food": 0.152,
                "energy": 0.082,
                "rent": 0.341,
                "core_goods": 0.194,
                "core_services": 0.231
            }
        })
    
    @app.route('/v1/weights/current', methods=['GET'])
    def current_weights():
        return jsonify({"weights": [0.152, 0.082, 0.341, 0.194, 0.231]})
    
    return app

# -------------------------------
# 5. Main
# -------------------------------
if __name__ == "__main__":
    # Run backtest simulation
    est, truth = run_backtest()
    
    # Optional: start API (uncomment to run)
    # app = create_api()
    # app.run(host='0.0.0.0', port=5000, debug=False)
    
    print("\nSimulation complete. To run real-time API, uncomment the Flask block.")
