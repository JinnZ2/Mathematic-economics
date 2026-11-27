# Biological load accounting

CC0. Co-authored. Status: PROPOSED. Two documents filed as delivered, the records read out of
them, and a checker. Rules are in `DECLARED.json`, committed before anything else here.

Unit of the first document: one biological entity, one week (168 h).

## What is here

| File | What it is |
|---|---|
| `as_received/` | first delivery (v1): the two PDFs byte for byte and the text `pdftotext -layout` gives for each |
| `as_received_v2/` | second delivery (v2), the same way |
| `as_received_v3/` | third delivery (v3), the current one: the work order that carried it, verbatim, and the text of each document. No PDF was delivered for v3 |
| `apply_v3.py` | builds the v3 text: the v2 text with the work order's two replacements, read from the order file |
| `DECLARED.json` | the rules for this folder, with one amendment per later delivery |
| `build_records.py` | reads each code block of the documents as the Python literal it is written as; nothing is typed by hand |
| `records.json` | current records (v3): 17 blocks with their section titles (which carry the OBSERVED / DERIVED / PROPOSED tags) and comments |
| `records_v2.json`, `records_v1.json` | the earlier deliveries' records, each the same bytes as when it was named `records.json` |
| `check_biological_load.py` | the checker; `check_results.json` is its last report |

```
python3 apply_v3.py --check
python3 build_records.py --check
python3 check_biological_load.py
python3 check_biological_load.py --selftest
```

Standard library only. Re-extracting the text needs `pdftotext`; the checker does not.

## What changed from v1 to v2 (read from the two extracted texts)

- The coupling document is now the stated owner of `PROVENANCE` and `FALSE_DENOMINATOR`
  ("CANONICAL ... companion docs point here"). The truck document's own `PROVENANCE` block is gone;
  its false-denominator definition and status read "canonical in Decision-Exposure Coupling". The
  checker treats these as pointers and all three resolve.
- Coupling `PROVENANCE`: `role_and_conditions` is split into `role_type` and `conditions`.
- `SENSOR_VALIDITY` now states: "None = unassessed (void): neither pass nor fail" and "all True -> valid sensor".
- The coupling document's open slots now list teaching.
- Not carried over: the v1 truck `PROVENANCE` block held a line of description for each field (what
  learning, endurance, maintenance and diversity measure; exposed vs sheltered spelled out) and three
  closing lines ("years != experience ...", "authority judged per dimension, not as one score"). v2
  does not have them in either document. They remain in `as_received/` and `records_v1.json`.
- The truck document keeps its own false-denominator `instance` and `fix` lines; its `fix` wording
  still differs slightly from the coupling document's.

## What changed from v2 to v3 (the work order's two changes, nothing else)

- Coupling document, canonical `PROVENANCE`: the per-field descriptions and the closing lines that v2
  had not carried over from v1 are back ("years != experience (20 yrs in school != a PhD's work)",
  "authority judged per dimension, not as one score"). The open item about them is closed.
- Wording note: v1's "exposed (real routes, own needs)" is now "exposed (real routes/shifts, own
  needs)", to cover all roles. `recency` reads "years since exposure" (v1: "years since last doing
  it") and `current_seat` includes "floor", both as in v2.
- Truck document: `false_denominator.fix` now reads "canonical in Decision-Exposure Coupling".
  Definition, status and fix all point to the coupling document and all resolve.
- v3 was delivered as text in a work order, not as PDFs: the two documents are Claude Docs edited
  live. The v3 text here is the v2 extracted text with those two replacements, and the checker
  confirms nothing else differs.

## What the checker says (2026-11-27, v3)

- 23 checks, 0 failed: hashes for v1, v2 and v3; all three record files match a rebuild; the v3 text
  is v2 plus exactly the two replacements; every string in the current records is in the source
  text (417 and 93 strings, 0 not found); all blocks parsed; the five figures the truck document
  derives from its own numbers reproduce (2 min, 87 m, 77 ft, 0.8 s, 1 per 114 mi); four pointers
  resolve (false-denominator definition, status and fix, and `PROVENANCE`).
- 26 voids (unchanged from v2), each listed with the document's own comment on that line or "no
  reason given in the document".

## Open

- `ROLE` vocabulary: 11 of its 13 words are outside the four need states; 3 compound statuses
  (`RESTRICTED or ABSENT`, `SELF_FUNDED / RESTRICTED` twice) are unmapped.
- `responsibility_h` has mixed types: a number for the office role, text for regional and OTR, void
  for the day driver.
- `true_cost`: NOT_COMPUTABLE (per-need values are an open slot; the terms have different units).
- 9 figures attributed to outside studies or agencies: NOT OPENED.
- The documents' own open slots: day driver `responsibility_h`; health risk from sanitation and
  holding; per-need dollar values; owner-operator taxable profit rate; `conditions_now` vs
  `conditions_then` for current manufacturing rules; other roles; measured cost of decoupled decisions.
- Every field of `SENSOR_VALIDITY`, `STALENESS` and `PROVENANCE` is a void: not assessed.
- "~300 a day ≈ 27 an hour" implies 11.11 hours of driving a day; the document does not state the hours.

Observer slots: null.
