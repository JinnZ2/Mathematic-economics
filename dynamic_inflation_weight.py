# ============================================================
# Dynamic Inflation Weighting Estimator (Bottom 60%)
# Implements: Kalman filter + constraint pressure + shock detection
# ============================================================

import numpy as np
from scipy.special import softmax

# --- Parameters ---
n_categories = 5  # Food, Energy, Rent, Core goods, Core services
sigma_w = 0.005   # process noise std (weights drift slowly)
R_base = 0.01     # measurement noise std (transaction flows)
lambda_c = 0.25   # constraint pressure sensitivity
phi = 0.5         # credit discount factor
tau_shock = 0.03  # shock detection threshold (sum of absolute changes)
delta_max = 0.2   # max CE correction weight
gamma_rent = 0.9  # anchor trust for rent (90% anchor, 10% free)

# --- State variables ---
w = np.ones(n_categories) / n_categories   # initial equal weights
P = np.eye(n_categories) * sigma_w**2      # error covariance
K = np.zeros((n_categories, n_categories)) # Kalman gain (will be diagonal approx)

# --- Helper: renormalize to simplex ---
def renormalize(w):
    return w / np.sum(w)

# --- 1. Observation model: transaction flows + income stratification + credit adjustment ---
def get_observation(t, true_weights, noise_std=R_base):
    # Simulate observed spend shares (in reality, from card data)
    z_obs = true_weights + np.random.normal(0, noise_std, n_categories)
    # Income‑stratified proxy: e.g., debit/credit split (here just add small bias)
    z_inc = z_obs + np.array([0.01, 0.01, -0.02, 0.0, 0.0])  # rent under‑reported
    # Credit adjustment: if credit usage > income growth, discount
    L = simulate_credit_income_ratio(t)   # returns scalar
    z_adj = z_inc * (1 - phi * L)
    return np.maximum(z_adj, 0)   # non‑negative

# --- 2. Shock detection (flow‑based) ---
def shock_detected(w_prev, w_curr, threshold=tau_shock):
    S = np.sum(np.abs(w_curr - w_prev))
    return S > threshold

# --- 3. Constraint pressure (continuous) ---
def constraint_pressure(w, price_changes, spend_changes, sigma_P, sigma_E):
    # Standardized co‑movement
    C = (spend_changes / sigma_E) * (price_changes / sigma_P)
    # Clip extreme values
    C = np.clip(C, -3, 3)
    # Multiplicative update
    w_new = w * np.exp(lambda_c * C)
    return renormalize(w_new)

# --- 4. Kalman filter update (diagonal approximation) ---
def kalman_update(w_pred, P_pred, z, R):
    # Innovation
    y = z - w_pred
    # Kalman gain (diagonal)
    K_diag = P_pred / (P_pred + R)
    w_new = w_pred + K_diag * y
    P_new = (1 - K_diag) * P_pred
    return w_new, P_new, K_diag

# --- 5. Periodic CE correction (state‑dependent delta) ---
def ce_correction(w_est, w_ce, sigma_drift, sigma_ce_hist):
    delta = min(delta_max, sigma_drift / sigma_ce_hist)
    w_corrected = (1 - delta) * w_est + delta * w_ce
    return renormalize(w_corrected)

# --- Main loop over months t = 1..T ---
w_est = initial_weights.copy()
P = np.ones(n_categories) * sigma_w**2   # diagonal
history_w = []

for t in range(1, T+1):
    # --- Predict step ---
    w_pred = w_est
    P_pred = P + sigma_w**2
    
    # --- Get observation ---
    z = get_observation(t, true_weights[t], R_base)
    
    # --- Shock detection: if large flow change, increase Kalman gain ---
    if shock_detected(w_est, z, tau_shock):
        R_effective = R_base * 0.3   # lower measurement noise = higher gain
    else:
        R_effective = R_base
    
    # --- Kalman update ---
    w_updated, P_updated, K_diag = kalman_update(w_pred, P_pred, z, R_effective)
    
    # --- Constraint pressure (if price & spend data available) ---
    if price_changes[t] is not None and spend_changes[t] is not None:
        w_constrained = constraint_pressure(w_updated, price_changes[t], spend_changes[t],
                                            sigma_P[category], sigma_E[category])
    else:
        w_constrained = w_updated
    
    # --- Special handling for rent: anchor subsystem ---
    rent_anchor = get_external_rent_anchor(t)   # e.g., Apartment List index
    w_constrained[rent_idx] = gamma_rent * rent_anchor + (1-gamma_rent) * w_constrained[rent_idx]
    w_constrained = renormalize(w_constrained)
    
    # --- Store estimate ---
    w_est = w_constrained
    P = P_updated
    history_w.append(w_est)
    
    # --- When CE release arrives (annually, with lag) ---
    if t == ce_release_time:
        sigma_drift = compute_rms_drift(history_w[-12:], ce_weights_previous)
        sigma_ce_hist = historical_volatility_of_ce(category)
        w_est = ce_correction(w_est, ce_weights_new, sigma_drift, sigma_ce_hist)
        P = P * 0.5   # reset uncertainty after correction
