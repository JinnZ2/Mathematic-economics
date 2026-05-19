# INTEGRATION.md

How the substrate-aware-accounting corpus is traversed.

## Three layers, one bus

```
+-------------------------------+
|  earth-systems-physics        |   constraint equations,
|  (thermodynamic base)         |   coupled diff-eqs for Earth systems
+-------------------------------+
              |
              v
+-------------------------------+
|  mathematics-economy          |   capital, labor, banking,
|  (capital and labor layer)    |   substrate damage accounting
+-------------------------------+
              |
              v
+-------------------------------+
|  infrastructure               |   oil extraction, refinery cascade,
|  (operational systems layer)  |   shale wells, EROI real-time
+-------------------------------+
              |
              v
+-------------------------------+
|  substrate-aware-accounting   |   coordination, routing, unified
|  (this corpus)                |   claim index, demo coordinator
+-------------------------------+
```

The arrow direction is dependency, not data flow. A claim about
banking depends on physics (energy is finite, entropy increases)
and feeds into infrastructure (extraction continues because debt
requires growth). Routing through the corpus respects this order.

## What lives where

`Claude_Code_Coordinator.py` is the entry point for query routing.
It knows about the three sibling repos and their modules by name,
matches keywords from a query against per-repo keyword sets, and
orders the resulting workflow by layer (physics first, then
economy, then infrastructure).

`CLAIMS_UNIFIED.json` is the corpus belief set. Every claim has
`id`, `statement`, `falsifier`, `confirmer`, `confidence`,
`module`, `repo`, and (for the current scaffold) `current_location`
so the actual file can be loaded even though the sibling repos do
not yet exist as separate GitHub repos.

`README.md` is the AI-parseable entry point describing what the
corpus is and what it is for.

Each `audit/*.py` module in the current scaffold carries a
**See also** header listing the other corpus modules and what
they audit. Following those headers builds the full picture
without consulting a central index.

## Routing flow

1. **Query in.** Any natural-language claim or question about
   energy, capital, infrastructure, or substrate.

2. **Keyword match.** `find_relevant_modules(query)` lowercases
   the query and checks each repo's keyword list for substring
   presence. Each match expands to every module in that repo;
   matched keywords are carried as metadata so the caller can
   audit *why* a module was selected.

3. **Claim match.** `find_relevant_claims(query, claims_data)`
   splits the query into words and checks each claim's statement,
   module, and repo for any of those words.

4. **Layer ordering.** `plan_audit` orders the resulting modules
   by layer (physics -> economy -> infrastructure). This matches
   the dependency direction: a physics constraint binds an
   economy claim binds an infrastructure claim.

5. **Workflow out.** The output is a list of module paths in
   ranked order plus the matching claims. A downstream caller —
   an AI agent, a human auditor, or another tool — decides how
   to consume them. For example: load the first module, run its
   `audit()` function against the question's inputs, check whether
   any of the matching claims are falsified by the inputs, then
   move to the next module.

## Current scaffold vs. target architecture

The corpus is currently colocated inside
`JinnZ2/Mathematic-economics`:

| Claimed home (`repo`)     | Current scaffold (`current_location`)        |
|---------------------------|----------------------------------------------|
| `mathematics-economy`     | `audit/substrate_damage_audit.py`             |
| `mathematics-economy`     | `audit/banking_thermodynamic_audit.py`        |
| `infrastructure`          | `audit/oil_extraction_thermodynamic_cascade_audit.py` |
| `infrastructure`          | `audit/refinery_stress_cascade_module.py`     |
| `infrastructure`          | `audit/shale_well_thermodynamic_reality_module.py`    |
| `infrastructure`          | `audit/eroi_real_time_audit.py`               |

When the sibling repos exist as separate GitHub repos under
`JinnZ2/`, each module migrates to its `repo` home and the
`current_location` field is dropped from `CLAIMS_UNIFIED.json`.

## Adding a new module

1. Write the module under the appropriate sibling repo (or in
   `audit/` if you are still in the scaffold).
2. Append an entry to `CLAIMS_UNIFIED.json` `modules` block with
   `id`, `repo`, `current_location`, `domain`, `summary`.
3. Append each falsifiable claim from the module to the `claims`
   block with `id`, `module`, `repo`, `domain`, `statement`,
   `falsifier`, `confirmer`, `confidence`.
4. Add the module name to the appropriate `Repository.modules`
   list in `Claude_Code_Coordinator.py`, plus any new domain
   keywords to `Repository.keywords`.
5. Add a `See also` header to the new module that lists the
   other corpus modules.

That is the entire onboarding path. No CI, no schemas to bump,
no version negotiation.

## Falsification path

A new observation can refute a claim by matching its `falsifier`
field. The corpus does not silently overwrite; the suggested flow:

1. Open an issue referencing the claim `id` and the contradicting
   observation.
2. Either downgrade the claim's `confidence` (`HIGH -> MODERATE
   -> LOW`) or remove it from `CLAIMS_UNIFIED.json` with a note
   in the commit message.
3. If the contradicting observation rises to a positive claim,
   add it as a new claim entry.

CC0 means anyone can fork and refute. The corpus is supposed to
update.
