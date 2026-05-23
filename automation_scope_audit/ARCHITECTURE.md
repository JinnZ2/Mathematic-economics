# automation_scope_audit / 6-layer architecture

License: CC0-1.0.

The 65 claims (C000 + C001..C064) are not independent. They sit in a
6-layer architecture with a closed coupling cycle: a break in any
layer propagates forward through the cycle and returns to the layer
it depends on. When every layer has at least one firing claim, the
cycle has *closed* — the deployment is structurally untenable, even
if many individual claims are clearing.

## Layers and ownership

| Layer | Name           | Role                                | Claims                                                                      |
|-------|----------------|-------------------------------------|-----------------------------------------------------------------------------|
| 1     | technical      | What breaks                         | C001, C003, C004, C005                                                       |
| 2     | operational    | How the operation responds          | C008, C009, C010, C011, C012, C013, C014, C015, C016, C017                  |
| 3     | behavioral     | How agents respond once degraded    | C018, C019, C033, C034, C035, C038, C042                                     |
| 4     | institutional  | What governance the layer demands   | C022, C023, C024, C051, C052, C060, C061, C062, C063, C064                  |
| 5     | energy         | Costs of enforcing institutional    | C020, C021, C025, C026, C043, C044, C045, C046, C047, C048                  |
| 6     | economic       | True cost accounting (closes cycle) | C027, C028, C029, C030, C054, C055, C058                                    |
|  *    | cross-cutting  | Spans multiple layers or pre-cycle  | C000, C002, C006, C007, C031, C032, C036, C037, C039, C040, C041, C049, C050, C053, C056, C057, C059 |

Coverage check (`architecture.coverage_check()`) verifies every claim
appears in exactly one layer or in the cross-cutting band; no
duplicates, no orphans.

## Coupling cycle

```
    1 technical      ── what breaks ─────────────────▶ 2 operational
                                                              │
    ▲                                                         │ how agents respond
    │ ROI feasibility check                                   ▼
    │                                                  3 behavioral
    6 economic                                                │
                                                              │ what governance is needed
    ▲                                                         ▼
    │ true cost accounting                            4 institutional
    │                                                         │
    5 energy ◀── costs of enforcement ──────────────────── 4 institutional
```

The six forward edges:

| upstream → downstream      | label                          |
|----------------------------|--------------------------------|
| technical → operational    | what breaks                    |
| operational → behavioral   | how agents respond             |
| behavioral → institutional | what governance is needed      |
| institutional → energy     | costs of enforcement           |
| energy → economic          | true cost accounting           |
| economic → technical       | ROI feasibility check          |

When `economic` returns concern back to `technical`, the cycle has
closed and the deployment is in a steady-state failure mode: no
single fix can rescue it, because every layer is feeding the next.

## Per-layer status

For a given audit report, each layer's status is computed from the
fraction of its claims that register concern:

- **GREEN** — zero claims register; the layer is admissible.
- **YELLOW** — some claims register, some clear; the layer is in
  partial failure, and the deployment is fixable layer-by-layer.
- **RED** — every claim in the layer registers; the layer is in total
  failure; no internal-to-the-layer remediation is possible.

## Cycle status

`architecture.cycle_status(report)` returns one of:

- `ADMISSIBLE` — no layer registers concern at all.
- `PARTIAL_FAILURE` — at least one layer registers, but not every layer.
  Some forward edges of the cycle are quiescent; remediation in the
  failing layer may restore admissibility.
- `UNTENABLE_CYCLE_CLOSED` — every load-bearing layer has at least one
  firing claim. The cycle is closed; concern propagates around it and
  no single intervention restores admissibility.

## Discrimination on the example scenarios

Running `python automation_scope_audit/run.py --layers`:

| Scenario                       | Fully-failed layers              | Cycle status              |
|--------------------------------|----------------------------------|---------------------------|
| `kodiak_atlas_permian` (works) | 1 (institutional)                | UNTENABLE_CYCLE_CLOSED    |
| `dispersed_wellsite` (fails)   | 5 (technical, operational, behavioral, institutional, economic) | UNTENABLE_CYCLE_CLOSED |

Both scenarios show the cycle closing — meaning even the "works case"
operates inside an institutional substrate that is structurally
unsustainable. The discrimination between them appears as the
*depth* of failure (1 fully-failed layer vs 5), not as cycle
admissibility.

This is the framework's main structural insight: **autonomous trucking
ROI is not a technical-layer problem.** Both the works case and the
fails case clear layer-1 claims to varying degrees, but neither
escapes the institutional → energy → economic → technical cycle.
Remediating the technical or operational layers in isolation cannot
break the cycle; the institutional and economic layers must be
addressed for any deployment to become structurally tenable.

## Usage

```bash
python automation_scope_audit/run.py --layers              # both scenarios
python automation_scope_audit/run.py --layers --clusters   # add cluster report
python automation_scope_audit/architecture.py              # standalone coverage + reports
```

Cross-references:

- `automation_scope_audit/architecture.py` — the encoded layer map +
  `cycle_status` + `print_layer_report`.
- `automation_scope_audit/correlation.py` — orthogonal cluster
  signatures (cluster ⊥ layer; a cluster can span layers).
- `automation_scope_audit/CLAIM_TABLE.fab.json` — contract-validated
  per-claim metadata.
- `automation_scope_audit/CLAUDE.md` — continuity protocol; references
  this architecture.
- `tests/test_automation_scope_audit.py::ArchitectureTests` —
  coverage + cycle-edge tests.
