# Relation to `automation_scope_audit/`

License: CC0-1.0

See `../automation_scope_audit/RELATION.md` for the full discussion.
Short form:

`vehicle_audit/` (this folder) is the **per-channel sensory /
operational feasibility** audit of a single autonomous-vehicle
deployment, organized around a producer / accumulator architecture
with a single `ReadinessGate` feasibility decision.

`automation_scope_audit/` is the **structural-claim audit** of an
autonomous-trucking ROI narrative, organized around 33 independently
falsifiable claims (C000-C032) and an explicit `scope_gate` that
refuses to evaluate a deployment whose spec doesn't declare
beneficiary, conditions, time period, resource, externalized cost,
profit allocation, and falsifier.

The two are complementary. Passing `vehicle_audit/`'s `ReadinessGate`
does not satisfy any of `automation_scope_audit`'s structural claims,
and vice versa. Do not merge them.
