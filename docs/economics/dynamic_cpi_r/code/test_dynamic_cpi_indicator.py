"""Lightweight checks for the Dynamic CPI-R module."""

from pathlib import Path
import importlib.util
import sys

import numpy as np


MODULE_PATH = Path(__file__).resolve().parent / "dynamic_cpi_indicator.py"
spec = importlib.util.spec_from_file_location("dynamic_cpi_indicator", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def run_tests() -> None:
    weights = module.generate_true_weights(n_months=12)
    assert weights.shape == (12, 5)
    assert np.allclose(weights.sum(axis=1), 1.0)

    prices = module.generate_price_indices(n_months=12)
    assert prices.shape == (12, 5)

    result = module.run_backtest(n_months=24)
    assert result.estimated_weights.shape == (24, 5)
    assert result.true_weights.shape == (24, 5)
    assert result.overall_rms >= 0.0
    assert result.revision_count >= 1
    assert np.allclose(result.estimated_weights.sum(axis=1), 1.0)

    payload = module.create_api_payload(result)
    assert set(payload.keys()) == {
        "timestamp",
        "cpi_r_cumulative_since_dec2019",
        "cpi_r_monthly_annualized",
        "weights",
        "constraint_scores",
    }
    assert len(payload["weights"]) == 5

    print("All Dynamic CPI-R tests passed.")


if __name__ == "__main__":
    run_tests()
