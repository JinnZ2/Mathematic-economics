"""
automation_scope_audit.modules

Falsifiable audit modules for autonomous trucking ROI claims, with emphasis
on dispersed-well / oilfield contexts where the marketing narrative
diverges most sharply from operational physics.

License: CC0-1.0
"""

from . import (
    scope_geometry,
    infrastructure_precondition,
    embedded_labor_audit,
    lifecycle_eroi,
    stranded_asset_risk,
    condition_monitoring_audit,
    scope_collapse_detector,
    interface_labor_audit,
)

__all__ = [
    "scope_geometry",
    "infrastructure_precondition",
    "embedded_labor_audit",
    "lifecycle_eroi",
    "stranded_asset_risk",
    "condition_monitoring_audit",
    "scope_collapse_detector",
    "interface_labor_audit",
]
