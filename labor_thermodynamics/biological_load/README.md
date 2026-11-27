# Biological load accounting

CC0. Co-authored. Status: PROPOSED. Two documents filed as delivered, the records read out of
them, and a checker. Rules are in `DECLARED.json`, committed before anything else here.

Unit of the first document: one biological entity, one week (168 h).

## What is here

| File | What it is |
|---|---|
| `as_received/*.pdf` | the two documents, byte for byte: *Biological Load Accounting for Truck Drivers* and *Decision-Exposure Coupling* |
| `as_received/*.txt` | the text `pdftotext -layout` gives for each; not edited |
| `DECLARED.json` | the rules for this folder |
| `build_records.py` | reads each code block of the documents as the Python literal it is written as, and writes `records.json`; nothing is typed by hand |
| `records.json` | 18 blocks (9 per document) with their section titles (which carry the OBSERVED / DERIVED / PROPOSED tags) and comments |
| `check_biological_load.py` | the checker; `check_results.json` is its last report |

```
python3 build_records.py --check
python3 check_biological_load.py
python3 check_biological_load.py --selftest
```

Standard library only. Re-extracting the text needs `pdftotext`; the checker does not.

## What the checker says (2026-11-27)

- 12 checks, 0 failed: hashes unchanged; every string in the records is in the source text
  (427 and 92 strings); all blocks parsed; the five figures the first document derives from its
  own numbers reproduce (2 min, 87 m, 77 ft, 0.8 s, 1 per 114 mi).
- Need status for trucking, as written: 4 SELF_FUNDED, 4 RESTRICTED, 1 ABSENT, 3 COMPOUND
  (`RESTRICTED or ABSENT`, `SELF_FUNDED / RESTRICTED` twice), 0 PROVIDED.
- The `ROLE` block uses its own words: 11 of its 13 are outside the four states. Nothing is mapped.
- `responsibility_h` is a number for the office role, text for regional and OTR, void for the day driver.
- 35 voids, each listed with the document's own comment or "no reason given in the document".
- "~300 a day ≈ 27 an hour" implies 11.11 hours of driving a day; the document does not state the hours.
- `true_cost`: NOT_COMPUTABLE (per-need values are an open slot; the terms have different units).
- 9 figures attributed to outside studies or agencies: NOT OPENED. None was checked here.
- The two documents both carry `PROVENANCE` and a false-denominator definition, and they differ;
  both are kept as written.

## Open items (the documents' own, plus what filing showed)

- day driver `responsibility_h`; health risk from sanitation and holding; per-need dollar values;
  owner-operator taxable profit rate (first document's open slots)
- `conditions_now` vs `conditions_then` for current manufacturing rules; other roles; measured cost
  of decoupled decisions (second document's open slots; `ROLES_TO_AUDIT` also lists teaching)
- which document owns the shared `PROVENANCE` and false-denominator blocks
- whether the `ROLE` block's words map onto the four need states, and how compound statuses are read
- sources for the outside figures
- every field of `SENSOR_VALIDITY`, `STALENESS` and both `PROVENANCE` blocks is a void: not assessed

Observer slots: null.
