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

The natural bridges into the rest of Math-Econ are:

- `audit/efficiency_report_audit.py` — route headline efficiency claims
  (e.g., "300% gain") through `core.conservation_checker` before running them
  through `field_system`.
- `audit/ai_delusion_econ_checker.py` — replace or augment regex detection
  with `core.premise_parser` + `core.constraint_mapper`.
- `AI/equation_bridge.py` — `domains/organizational.py`'s 5 structural
  constraints (resilience, enforcement ratio, adaptive slack, interdependency
  load) are direct cousins of the OSDI sub-indices (HHI, SD, RI).

None of those bridges are wired up yet — this snapshot simply makes them
possible.

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
