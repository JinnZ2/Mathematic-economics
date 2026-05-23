# mathematic-economics — Architecture

License: CC0 1.0 Universal.

## Position in the ecosystem

This repository implements the *structural-economics* layer of the
JinnZ2 substrate-primary toolchain. It provides 13 canonical
falsifiable equations measuring energy flows, resource dependencies,
risk distributions, and power concentrations in economic systems,
plus an 84-claim `automation_scope_audit/` layer (C000-C083) covering
autonomous-deployment ROI, substrate care, credential inversion,
adoption-curve thermodynamics, lifecycle design, training-corpus
dynamics, and cross-domain empirical validation.

The foundational ontology — every claim a `dX/dt under scope`, no
permanent identities — is documented in the repo-local
[`DIFFERENTIAL_FRAME.md`](DIFFERENTIAL_FRAME.md) (mirrored from the
sister `differential-frame-core` repository).

## Two architectural views

This repo carries **two distinct ARCHITECTURE documents** at different
scopes:

- **This file** (`ARCHITECTURE.md`, repo root) — high-level position
  in the JinnZ2 ecosystem and corpus-hardening metadata.
- **`automation_scope_audit/ARCHITECTURE.md`** — the 6-layer
  coupling cycle (technical → operational → behavioral →
  institutional → energy → economic → technical) the audit's 84
  claims sit inside. That document is the load-bearing structural
  diagram for the audit framework.

## Sister repositories

This repo couples to (via shared ontology, vendored bridges, or
explicit fieldlinks):

- `differential-frame-core` — ontology: every noun is `dX/dt`.
- `energy_english` — constraint-grammar / formal-semantics tool that
  resists projection error in claim text.
- `calibration-audit` — falsifiable-diagnostic suite (5 dimensions,
  GREEN/YELLOW/RED/EXTINCT bands) — vendored into `calibration/`.
- `labor-thermodynamics` — five compounding labor-measurement failure
  modes — vendored into `labor_thermodynamics/`.
- `projection_error_modes` — failure-mode catalog for AI projection
  errors; informs C065-C069 credential-inversion claims.
- `physics_guard` — physics-grounded claim verification (CC0 vendored
  snapshot in `physics_guard/`).
- `metabolic-accounting` — fieldlinked via
  `audit/metabolic_bridge.py` for the GlucoseFlow basin-trajectory
  computation; *not* vendored.

See [`automation_scope_audit/RELATION.md`](automation_scope_audit/RELATION.md)
for the distinction between `automation_scope_audit/` and the
older-architecture `vehicle_audit/` folder.

## Key constraint / assumption

The single load-bearing constraint that distinguishes this repo from
sister repos: **every claim must be falsifiable through measurement
of energy / resource / time, not through redefinition of terms.**

Operationally this means:

- A claim with no falsifier is inadmissible (enforced by C000 +
  `semantic_coherence_check` + `scope_gate`).
- A claim whose threshold can be reached only by redefining the
  measurement unit is inadmissible (enforced by `metrological_bounds.py`).
- Every measured number in published documents must be tagged as
  `[illustrative]` or with a primary-source citation (enforced by
  the H1.3 hardening pass; see `AUDIT_TASKS_HARDENING.md`).

## Vendored-subtree import invariant

`physics_guard/`, `calibration/`, `core/`, and `labor_thermodynamics/`
are vendored snapshots. They must not import from Math-Econ; the
import direction flows Math-Econ → vendored, never the reverse.
Enforced by `tests/test_bridges.py::ImportDirectionInvariant`.

## License

CC0 1.0 Universal.
