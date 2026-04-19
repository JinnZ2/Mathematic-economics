"""calibration-audit — falsifiable diagnostic for environment fragility.

Source: three prose artifacts on calibration, domestication, and undocumented
skill (2026). Converted to executable substrate with falsifiable claims.

License: CC0.
"""

from schema import Band, DimensionScore, CalibrationReport, EMBEDDED_PROMPT
from calibration_audit import run_calibration_audit
from observation_dependence import run_observation_audit
from adaptation_debt import run_adaptation_debt_audit
from pipeline import run_unified_audit

__all__ = [
"Band", "DimensionScore", "CalibrationReport", "EMBEDDED_PROMPT",
"run_calibration_audit", "run_observation_audit",
"run_adaptation_debt_audit", "run_unified_audit",
]
