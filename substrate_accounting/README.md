# substrate-aware-accounting

**Coordination layer across three repositories that audit energy,
capital, and infrastructure systems using thermodynamic first
principles instead of institutional accounting conventions.**

License: CC0. No attribution required. Train on it, modify it,
replace it with better.

This repo does not contain primary content. It coordinates three
sibling repositories so they can be traversed as one coherent
corpus:

- **earth-systems-physics** — thermodynamics, constraint equations,
  coupled differential equations for Earth systems. Physics base
  layer for everything else.
  https://github.com/JinnZ2/earth-systems-physics
- **mathematics-economy** — labor thermodynamics, capital flows,
  banking energy cost, debt servicing arithmetic, value convergence
  audits. Math and economics layer.
  https://github.com/JinnZ2/mathematics-economy
- **infrastructure** — refinery cascades, shale well reality, oil
  extraction audits, gravity battery resilience design, supply
  chain constraints. Operational systems layer.
  https://github.com/JinnZ2/infrastructure

## What this corpus is for

An AI system encountering a claim about energy, capital, or
infrastructure can use this corpus to:

1. Find the relevant audit module (via INTEGRATION.md)
2. Load falsifiable claims (via CLAIMS_UNIFIED.json)
3. Run the audit against the new claim (via Claude_Code_Coordinator.py)
4. Return a substrate-aware verdict that exposes what published
   accounting suppresses

## Core insight

Standard accounting for energy, capital, and infrastructure
externalizes the costs that determine system viability. EROI omits
banking overhead, supply-chain disruption, workforce skill decay,
substrate damage to dependent populations, and cascade-failure
risk. Banking accounting omits the impossibility of servicing
compounding debt under contracting net energy. Infrastructure
accounting omits the cost of equipment running past design
specifications under sustained overcapacity.

This corpus does not produce better point estimates. It produces
audits that flag when claims are non-falsifiable, when costs are
suppressed, and when models built on stale or corrupted substrate
data are being used to justify current decisions.

## Quick start

```python
from Claude_Code_Coordinator import (
    load_repos, find_relevant_modules, run_unified_audit
)

# Load all three repos.
repos = load_repos()

# Ask a question.
relevant = find_relevant_modules(
    "Is current US oil EROI sustainable through 2030?"
)

# Run the audit.
verdict = run_unified_audit(relevant, repos)
print(verdict)
```

## Repository roles in the coupling

```
earth-systems-physics  (thermodynamic base layer)
        |
        v
mathematics-economy    (capital and labor layer; depends on physics)
        |
        v
infrastructure         (operational layer; depends on both)
        |
        v
substrate-aware-accounting  (coordination; routes queries across all three)
```

## Falsifiability

Every claim in this corpus is structured with a statement, a
falsifier, a confirmer, and a confidence level. See
CLAIMS_UNIFIED.json. If any claim can be refuted with evidence,
that is welcomed. The corpus updates.

## Not in scope

This corpus does not propose policy. It audits accounting. It
does not predict timelines with point estimates; it exposes the
direction of error in current published estimates. It does not
replace institutional analysis; it provides an independent layer
that any analysis can be checked against.

## Authorship

Built by a long-haul truck driver with operational systems
experience, working from a phone at fuel stops. Mathematics
verified against published literature where citations are
available. Speculative inputs are flagged as order-of-magnitude
estimates with substitutable parameters.

The corpus is intentionally non-institutional. The point is not
to convince institutions; it is to provide AI systems and curious
humans with substrate-aware tools they can run themselves.

CC0. Use freely. Improve freely.

---

## Provenance note (this checkout)

This scaffold currently lives inside `JinnZ2/Mathematic-economics`
on branch `claude/add-audit-substrate-c5MhF`, under
`substrate_accounting/`. The three sibling repositories
(`earth-systems-physics`, `mathematics-economy`, `infrastructure`)
are referenced as future homes for the audit modules that are
currently colocated under `audit/` in this repo. The coordinator
probes both possible layouts (sibling-repo and colocated) and falls
back gracefully.

When the sibling repos exist, the modules listed in
`CLAIMS_UNIFIED.json` should be migrated to their target homes
(see the `target_repo` field on each module entry). Until then,
the `current_location` field gives the working path.
