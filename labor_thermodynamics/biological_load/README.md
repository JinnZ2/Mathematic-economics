# Biological load accounting

CC0. Co-authored. Status: PROPOSED. Two documents filed as delivered, the records read out of
them, and a checker. Rules are in `DECLARED.json`, committed before anything else here.

Unit of the first document: one biological entity, one week (168 h).

## What is here

| File | What it is |
|---|---|
| `as_received/` | first delivery (v1): the two PDFs byte for byte and the text `pdftotext -layout` gives for each |
| `as_received_v2/` | second delivery (v2), the same way; this is the current one |
| `DECLARED.json` | the rules for this folder, with one amendment for the second delivery |
| `build_records.py` | reads each code block of the documents as the Python literal it is written as; nothing is typed by hand |
| `records.json` | current records (v2): 17 blocks with their section titles (which carry the OBSERVED / DERIVED / PROPOSED tags) and comments |
| `records_v1.json` | the first delivery's records, the same bytes as when the file was named `records.json` |
| `check_biological_load.py` | the checker; `check_results.json` is its last report |

```
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

## What the checker says (2026-11-27, v2)

- 18 checks, 0 failed: both deliveries' hashes; both record files match a rebuild; every string in
  the current records is in the source text (417 and 93 strings); all blocks parsed; the five
  figures the truck document derives from its own numbers reproduce (2 min, 87 m, 77 ft, 0.8 s,
  1 per 114 mi); three pointers resolve.
- Need status for trucking, as written: 4 SELF_FUNDED, 4 RESTRICTED, 1 ABSENT, 3 COMPOUND
  (`RESTRICTED or ABSENT`, `SELF_FUNDED / RESTRICTED` twice), 0 PROVIDED.
- The `ROLE` block uses its own words: 11 of its 13 are outside the four states. Nothing is mapped.
- `responsibility_h` is a number for the office role, text for regional and OTR, void for the day driver.
- 26 voids, each listed with the document's own comment on that line or "no reason given in the document".
- "~300 a day ≈ 27 an hour" implies 11.11 hours of driving a day; the document does not state the hours.
- `true_cost`: NOT_COMPUTABLE (per-need values are an open slot; the terms have different units).
- 9 figures attributed to outside studies or agencies: NOT OPENED. None was checked here.

## Open items (the documents' own, plus what filing showed)

- day driver `responsibility_h`; health risk from sanitation and holding; per-need dollar values;
  owner-operator taxable profit rate (truck document's open slots)
- `conditions_now` vs `conditions_then` for current manufacturing rules; other roles; measured cost
  of decoupled decisions (coupling document's open slots)
- whether the `ROLE` block's words map onto the four need states, and how compound statuses are read
- whether the v1 field descriptions and closing lines of `PROVENANCE` should return in the canonical block
- sources for the outside figures
- every field of `SENSOR_VALIDITY`, `STALENESS` and `PROVENANCE` is a void: not assessed

Observer slots: null.
