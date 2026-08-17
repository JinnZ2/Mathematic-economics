import numpy as np
from collections import deque

class DynamicCPI_R:
    def __init__(self, n_categories=5, sigma_w=0.005, R_base=0.01,
                 lambda_c=0.25, phi=0.5, tau_shock=0.03, delta_max=0.2,
                 gamma_rent=0.9, shock_gain_factor=0.3):
        # ... (previous initialization code remains) ...
        
        # ---------- New Modules ----------
        # 1. Continuous error tracking
        self.error_history = []          # list of (t, error_vector)
        self.bias = np.zeros(n_categories)
        self.error_variance = np.zeros(n_categories)
        self.error_autocorr = 0.0        # scalar for simplicity (can be per category)
        
        # 2. Adaptive gain tuning
        self.pred_error_memory = deque(maxlen=12)   # last 12 prediction errors
        self.volatility_memory = deque(maxlen=12)
        
        # 3. External validation (stubs, to be fed from outside)
        self.external_metrics = {}        # e.g., {'delinquency_rate': 0.05, 'rent_arrears': 0.07}
        self.validation_correlation = {}  # store correlation with real-world stress
        
        # 4. Drift detection
        self.drift_window = 12            # months
        self.drift_threshold = 0.05       # absolute change in sum of weights
        self.drift_flag = False
        
        # 5. Revision accountability
        self.revision_log = []            # list of (time, pre_correction_weights, post_correction_weights, delta)
        
    # ------------------------------------------------------------
    # Module 1: Continuous Error Tracking
    # ------------------------------------------------------------
    def update_error_tracking(self, t, w_est, w_ce_lagged):
        """Call when a new CE (lagged) becomes available."""
        error = w_est - w_ce_lagged
        self.error_history.append((t, error))
        # Update bias (exponential moving average)
        alpha = 0.1
        self.bias = (1 - alpha) * self.bias + alpha * error
        # Update variance (rolling window of last 12 errors)
        recent_errors = np.array([e for (_, e) in self.error_history[-12:]])
        if len(recent_errors) > 1:
            self.error_variance = np.var(recent_errors, axis=0)
        # Autocorrelation (lag-1) for each category, then average
        if len(recent_errors) >= 3:
            corr_sum = 0
            for i in range(self.n):
                e_series = recent_errors[:, i]
                if np.std(e_series) > 1e-6:
                    corr = np.corrcoef(e_series[:-1], e_series[1:])[0,1]
                    corr_sum += corr
            self.error_autocorr = corr_sum / self.n
        else:
            self.error_autocorr = 0.0
            
    # ------------------------------------------------------------
    # Module 2: Adaptive Gain Tuning
    # ------------------------------------------------------------
    def compute_adaptive_gain(self, prediction_error, current_volatility):
        """
        prediction_error: scalar (norm of innovation vector)
        current_volatility: e.g., standard deviation of price changes over last 3 months
        Returns a multiplier for the Kalman gain (or directly a new R_eff)
        """
        # Store recent prediction errors and volatilities
        self.pred_error_memory.append(prediction_error)
        self.volatility_memory.append(current_volatility)
        
        if len(self.pred_error_memory) < 6:
            return 1.0   # nominal gain
        
        # Mean prediction error over recent window
        mean_error = np.mean(self.pred_error_memory)
        # Mean volatility
        mean_vol = np.mean(self.volatility_memory)
        
        # Rule: high error + stable regime → increase gain (reduce R)
        # High volatility → decrease gain (increase R)
        error_ratio = mean_error / (np.mean(self.pred_error_memory[-3:]) + 1e-8)  # recent vs older
        if mean_error > 0.02 and mean_vol < 0.01:
            gain_mult = 1.5   # correct faster
        elif mean_vol > 0.03:
            gain_mult = 0.5   # be cautious
        else:
            gain_mult = 1.0
        
        # Also adjust based on error autocorrelation (if drifting)
        if self.error_autocorr > 0.5:
            gain_mult = min(gain_mult * 1.2, 2.0)   # increase gain to catch up
            
        return np.clip(gain_mult, 0.3, 2.0)
    
    # ------------------------------------------------------------
    # Module 3: External Validation Layer
    # ------------------------------------------------------------
    def external_validation(self, metric_name, real_world_stress_series, model_series):
        """
        metric_name: e.g., 'cpi_r'
        real_world_stress_series: array of delinquency rates, etc.
        model_series: array of CPI-R values over same time window
        Returns correlation coefficient and passes/fail flag.
        """
        if len(real_world_stress_series) < 3 or len(model_series) < 3:
            return 0.0, False
        corr = np.corrcoef(real_world_stress_series, model_series)[0,1]
        self.validation_correlation[metric_name] = corr
        # Baseline threshold: e.g., must be > 0.5 for essentials
        is_valid = corr > 0.5
        return corr, is_valid
    
    # ------------------------------------------------------------
    # Module 4: Drift Detection
    # ------------------------------------------------------------
    def detect_drift(self, w_current):
        """Maintains a history of weight vectors and checks for persistent drift."""
        if not hasattr(self, 'weight_history_drift'):
            self.weight_history_drift = deque(maxlen=self.drift_window)
        self.weight_history_drift.append(w_current.copy())
        
        if len(self.weight_history_drift) == self.drift_window:
            w_old = self.weight_history_drift[0]
            w_new = self.weight_history_drift[-1]
            total_drift = np.sum(np.abs(w_new - w_old))
            self.drift_flag = total_drift > self.drift_threshold
            # Optional: log drift
            if self.drift_flag:
                print(f"Warning: Drift detected at time step {len(self.weight_history_drift)}: {total_drift:.4f}")
        return self.drift_flag
    
    # ------------------------------------------------------------
    # Module 5: Revision Accountability
    # ------------------------------------------------------------
    def log_revision(self, t, pre_weights, post_weights, ce_weights):
        """Called after a CE correction."""
        delta = np.linalg.norm(post_weights - pre_weights)
        self.revision_log.append({
            'time': t,
            'pre': pre_weights.copy(),
            'post': post_weights.copy(),
            'ce': ce_weights.copy(),
            'delta': delta
        })
        # Optional: check if corrections are growing over time
        if len(self.revision_log) >= 3:
            recent_deltas = [entry['delta'] for entry in self.revision_log[-3:]]
            if np.mean(recent_deltas) > 0.1:   # large average correction
                print(f"Warning: Large CE corrections persisting. Model may be degrading.")
    
    # ------------------------------------------------------------
    # Modified main step() to incorporate new modules
    # ------------------------------------------------------------
    def step(self, t, true_weights, price_indices, spend_shares_truth, sigma_P, sigma_E,
             external_rent_anchor, ce_weights=None, ce_release=False,
             external_stress_series=None):   # new optional input for validation
        """
        ... (previous code) ...
        """
        # 1. Predict
        w_pred = self.w.copy()
        P_pred = self.P + self.sigma_w**2
        
        # 2. Get observation
        z = self.observation_model(true_weights, t)
        
        # 3. Adaptive gain: compute prediction error (innovation)
        innovation = z - w_pred
        pred_error_norm = np.linalg.norm(innovation)
        current_volatility = np.std(price_indices[max(0,t-3):t+1]) if t>0 else 0.01
        gain_mult = self.compute_adaptive_gain(pred_error_norm, current_volatility)
        
        # 4. Shock detection (may override gain)
        if self.shock_detected(self.w, z):
            R_eff = self.R_base * self.shock_gain_factor / gain_mult   # gain_mult reduces R when >1
        else:
            R_eff = self.R_base / gain_mult   # larger gain_mult -> smaller R_eff
        
        # 5. Kalman update
        w_updated, P_updated, K = self.kalman_update(w_pred, P_pred, z, R_eff)
        
        # 6. Constraint pressure (unchanged)
        # ...
        
        # 7. Rent anchoring (unchanged)
        # ...
        
        # 8. Drift detection
        self.detect_drift(w_final)
        
        # 9. If CE release, update error tracking and log revision
        if ce_release and ce_weights is not None:
            # Use the estimated weight *before* correction for error tracking
            self.update_error_tracking(t, self.w, ce_weights)
            # Log revision (pre-correction state is w_final before CE correction)
            pre_corr = self.w.copy()
            # Perform CE correction (as before)
            # ... (CE correction code from earlier) ...
            self.log_revision(t, pre_corr, self.w, ce_weights)
        
        # 10. External validation (if external series provided)
        if external_stress_series is not None and t % 12 == 0:   # validate annually
            # Assume we have stored enough history of CPI-R
            cpi_r_series = self.compute_cpi_r_history()   # method to compute cumulative inflation
            corr, valid = self.external_validation('cpi_r', external_stress_series, cpi_r_series)
            if not valid:
                print(f"Warning: External validation failed at t={t}, correlation={corr:.2f}")
        
        return self.w
