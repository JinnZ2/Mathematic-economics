# physics_guard — vendored snapshot

This directory is a **vendored snapshot** of the PhysicsGuard logic-verification
framework. Math-Econ treats this as canonical-within-this-repo; the upstream
copy remains the source of truth for the framework itself.

| Field | Value |
|---|---|
| Upstream | https://github.com/JinnZ2/PhysicsGuard |
| License | CC0 1.0 Universal (public domain) |
| Snapshot taken | 2026-04-19 |
| Tests at snapshot | 76 passing (`pytest tests/`) |
| External deps | none (stdlib only); `pytest` for tests |

## Why vendored

PhysicsGuard's pipeline (`premise_parser` → `constraint_mapper` →
`conservation_checker` → `flag_engine`) is the formal physics-grounded version
of the claim-auditing that `audit/ai_delusion_econ_checker.py` and
`audit/efficiency_report_audit.py` do by regex + rule. Keeping a snapshot in
this repo lets those modules call into it without introducing a runtime
dependency on another repository.

## Integration points

All three bridges are wired and covered by `tests/test_bridges.py`:

- **`audit/efficiency_report_audit.py`** — routes each report's headline
  claim through `main.check()` (full parse → constraint → conservation →
  flag pipeline) before the Six Sigma audit. Verdict is attached to the
  audit result as `physics_verdict`.
- **`audit/ai_delusion_econ_checker.py`** — exposes
  `analyze_dataset_with_physics()` which keeps the regex path and adds a
  per-entry PhysicsGuard verdict list.
- **`AI/equation_bridge.py`** —
  `SystemMeasurement.check_organizational_physics()` builds an `OrgClaim`
  from the measured equations (HHI → structure type, ER → enforcement
  ratio, `1 - ER` → adaptive slack) and calls `check_organization()`.

All three use a defensive `_HAS_PHYSICS_GUARD` flag and fall back to
pre-bridge behavior if this directory is not importable.

## Running the tests

```bash
cd physics_guard
pytest tests/
```

Or from the repo root:

```bash
pytest physics_guard/tests/
```

## Updating the snapshot

1. Note the upstream commit SHA being pulled in.
2. Replace the files under `core/`, `domains/`, `tests/`, plus `main.py`,
   `ai_interface.py`, `monoculture_detector.py`, and `pyproject.toml`.
3. Re-run the tests. All 76+ should pass.
4. Update the "Snapshot taken" date above.
5. Note any local adaptations explicitly below.

## Local adaptations

None at this time. Files are verbatim from upstream.

## Invariant: no runtime import of Math-Econ

Nothing under this directory may import a Math-Econ module at runtime.
Math-Econ has no `requirements.txt` and is not pip-installable; if this
snapshot reached back into `audit/`, `AI/`, or `schemas/`, the upstream
PhysicsGuard project (which has its own CI and test expectations) would
inherit a dependency on a repo it cannot install.

The invariant is enforced by
`tests/test_bridges.py::ImportDirectionInvariant`, which AST-scans every
`.py` file under `physics_guard/`, `calibration/`, and `core/` for
imports of Math-Econ module names. CI runs it on every push.

If a future upstream re-sync introduces such an import, the fix is to
move the coupling into a Math-Econ-side bridge (as the three existing
bridges do) rather than modify the vendored file.
