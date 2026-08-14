# legacy/

License: CC0 1.0 Universal.

**This is not an attic. It is the prior state of the record, and it
still carries precedence.**

Every other directory in this repository holds the framework's *current*
claims. This one holds the claims those replaced, and the reason each
was replaced. Nothing here is maintained, imported, or executed by CI.
Everything here is citable.

---

## Why a repository that runs on falsification needs this folder

The method this repo applies to the world is the one it has to apply to
itself:

```
    hypothesize  ->  run  ->  result
                                |
                   falsified <--+--> survives
                        |                |
                   edit the claim     keep it
                        |
                search for unknowns
                        |
                      rerun
```

The failure mode is at the *edit the claim* step. When a claim is
revised, the natural move is to delete the old version — the code is
superseded, the file is dead, `git rm`. But that deletes the evidence
that the revision was made, and with it:

- **what the previous claim was**, so a later reader can tell whether
  the current one is a refinement or a drift;
- **what the revision assumed but never checked**, which is where the
  unexamined assumptions accumulate;
- **the fallback position**, if the successor is itself falsified.

That last one is the reason for the word *precedence*. A superseded
claim is not a disproven claim. Usually it was replaced because
something sharper came along — and if the sharper thing breaks, the
coarser thing is where you land, not zero. A repository that deletes
its precedents cannot fall back; it can only start over.

This folder is the falsification cycle's memory. `LEDGER.jsonl` is that
memory in machine-readable form, and `ledger.py` is the check that keeps
it honest.

## What this folder is *not*

- **Not a graveyard for bad code.** Code retired for being wrong is
  recorded with a verdict saying so, but the folder's purpose is
  continuity, not shame.
- **Not maintained.** Files here are frozen at their retirement state.
  They will not be updated to track their successors, and several are
  not runnable by construction. There is deliberately no `__init__.py`.
- **Not in the import graph.** No live module imports anything here, and
  no CI job collects it. If you find a live import pointing into
  `legacy/`, that is a bug in the live module.
- **Not a substitute for git.** Git has every byte. Git does not have
  the *reasoning*, and reasoning is what erodes — it lives in a commit
  message that no one will find because they do not know the file ever
  existed. This folder makes the retirement discoverable without knowing
  what to search for.

---

## The ledger

`LEDGER.jsonl` — one JSON object per line, one line per retirement.

| Field | Meaning |
|---|---|
| `record_id` | Stable id (`L001`, …). Cite this. |
| `artifact` | Original repo-relative path at retirement time. |
| `also_retired` | Sibling paths retired in the same event. |
| `retained_at` | Where the bytes live now, or `null` if not kept. |
| `retired_at` | ISO date. |
| `retired_in` | 40-hex commit sha, or `"pending"` before landing. |
| `verdict` | One of six, below. |
| `hypothesis` | What the artifact asserted or was for. |
| `run` | What was actually done that tested it. |
| `result` | What that run showed. |
| `successor` | Path(s) carrying the function now. |
| **`precedence`** | **What still carries forward. The load-bearing field.** |
| `unknowns_surfaced` | Questions the retirement raised, with status. |
| `rerun` | Command that re-executes the comparison today. |
| `reversible` | Whether the artifact could be resurrected. |

### The six verdicts

They are epistemically distinct, not stylistic. The verdict determines
what a future reader owes the retired artifact.

| Verdict | What happened | What you owe it |
|---|---|---|
| `SUPERSEDED` | A better implementation of the **same** claim replaced it. | The claim stands; only the code retired. Check the successor implements all of it. |
| `ABSORBED` | Its distinctive contribution was merged elsewhere. | Know where that feature came from and what else came with it. |
| `REFRAMED` | **The claim itself changed.** | The most weight. The old framing is the live fallback if the new one fails. |
| `EXTRACTED` | Content was promoted out of a container that was dropped. | Check what in the container was *not* promoted. |
| `RELOCATED` | Address changed, content did not. | Nothing epistemic. Path resolution only. |
| `DISCARDED` | No content, therefore no precedence. | Nothing. Recorded so the deletion is not mistaken for a loss. |

`REFRAMED` is the one to read carefully. `SUPERSEDED` says *we built it
better*; `REFRAMED` says *we were measuring the wrong thing*. Only the
second changes what the framework asserts about the world.

### Unknowns carry status

Each entry in `unknowns_surfaced` is an object, not a string:

```json
{"question": "...", "status": "open", "resolution": null, "resolved_at": null}
```

A retirement almost always raises questions it does not answer — an
assumption the successor inherited without re-deriving, a delta asserted
but never enumerated. Those are the *search for unknowns* step, and
writing them down is what makes them survivable. An unknown that is
never recorded is indistinguishable from one that was never noticed.

Marking one `resolved` **requires** stating how (gate G9). The cycle
cannot be closed by assertion.

## Checking the trail

```bash
python legacy/ledger.py
```

Prints the retirement summary, the open-unknown work queue, and the
resolved ones with their resolutions. Then it runs nine gates — the ones
that matter:

- every `successor` path exists in the working tree (a retirement note
  pointing at a vanished successor is a broken trail);
- every `retained_at` file is actually present;
- `precedence` is non-empty — a record that cannot say what carries
  forward is a deletion with extra steps;
- a `resolved` unknown states its resolution.

Exit 0 means the audit trail holds. It runs in
`scripts/validate_claims.py` and in CI, so the trail cannot rot
silently: delete a successor module without updating the ledger and the
build goes red.

Programmatic use:

```python
from legacy.ledger import load, unknowns, by_verdict

records = load()
for rid, u in unknowns(records, status="open"):
    print(rid, u.question)

for record in by_verdict(records, "REFRAMED"):
    print(record.artifact, "->", record.successor)
    print(record.precedence)   # the fallback position
```

---

## Retiring something

1. **Do the work first.** Run the comparison. Record what you actually
   ran in `run`, and what it showed in `result` — not what you expected.
2. **Pick the verdict honestly.** If the claim changed, it is
   `REFRAMED`, even when the new code looks like a refactor.
3. **Move the file** to `legacy/<original path>`, mirroring where it
   lived. Use `git mv` so rename history survives. Skip this only when
   the content genuinely survives elsewhere unchanged (`RELOCATED`) or
   there was no content (`DISCARDED`) — then set `retained_at` to
   `null`.
4. **Write `precedence` last, and write it for a stranger.** Not "old
   version of X" — that is the `artifact` field. Say what a future
   reader must still honor: which defaults are the original measurement
   basis, which feature originated here, what you fall back to if the
   successor fails.
5. **List the unknowns.** What did this retirement assume without
   checking? Every entry is a real question someone can pick up.
6. **Append the record** to `LEDGER.jsonl`, run `python
   legacy/ledger.py`, and set `retired_in` to the sha once it lands.

Deleting an artifact outright, with no ledger record, is the one move
this folder exists to prevent.

## Relationship to the claim registry

Distinct mechanisms, same doctrine.

| Mechanism | Governs | Defined in |
|---|---|---|
| Claim versioning (`Cnnn_v2`, `superseded_by`) | Claims in `CLAIM_TABLE.fab.json` | `CLAIM_TABLE_VERSIONING.md`, `CLAIM_UPDATE_PROCEDURE.md` |
| `ClaimState` state machine (`SUPERSEDED`, `RETIRED`, `superseded_by`) | The lifecycle of an individual claim | `inquiry_engine/claim_lifecycle.py` |
| `predictions_registry.jsonl` | Forward-looking predictions and their resolution | `PREDICTION_PROTOCOL.md` |
| **This ledger** | **Retired files and modules** | this README |

The layering is deliberate. `claim_lifecycle.py` already encodes the
cycle for a *claim* — including the transition
`FALSIFIED -> PROPOSED`, which is the "edit the claim and rerun" arrow
made explicit. This ledger is the same doctrine one level up, for the
*files* that carry claims. A module can be retired while the claim it
implemented stays `ACTIVE` (that is `SUPERSEDED` here), and a claim can
be falsified while its module lives on to serve a narrower scope.

`CLAIM_UPDATE_PROCEDURE.md` step 8 already says it: *"Resolve via an
issue + PR, not by deleting the older version."* That rule governed
claims inside a table. This folder extends the same rule to whole files.

Where a retirement also changes a claim, do both: bump the claim per
`CLAIM_UPDATE_PROCEDURE.md`, and record the file retirement here.
`L004` is that case — the C011/C012/C013 reframe.

## Contents

```
legacy/
├── README.md                     # this file -- the doctrine
├── LEDGER.jsonl                  # the retirement records
├── ledger.py                     # reader + validator (stdlib only)
├── Md.md, Md1.md                 # L002  narrative dumps, code extracted out
├── Study_scope_audit.py          # L005  superseded by audit/study_scope_audit.py
├── accounting/
│   └── generic.py                # L006  CLI absorbed into HVAC_gradient.py
├── automation_scope_audit/modules/
│   └── interface_labor_audit.py  # L004  REFRAMED -- fallback for C011-C013
└── docs/economics/dynamic_cpi_r/drafts/
    ├── dynamic_inflation_weight.py   # L007  pseudocode; method outlived the code
    └── iteration_module.py           # L007  five unevaluated mechanisms
```

Five of the seven records were recovered from deletions in git history
(2026-04 through 2026-07) that predate this folder. Their rationale was
reconstructed from the commit messages that performed the deletions, and
is quoted rather than invented. `L005`'s open unknown was resolved in
the course of that reconstruction — the check its original retirement
asserted but never ran now exists in the record.
