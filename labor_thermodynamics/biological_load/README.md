# Biological load accounting

CC0. Co-authored. Status: PROPOSED. Two documents filed as delivered, the records read out of
them, and a checker. Rules are in `DECLARED.json`, committed before anything else here.

Unit of the first document: one biological entity, one week (168 h).

## What is here

| File | What it is |
|---|---|
| `as_received/` | first delivery (v1): the two PDFs byte for byte and the text `pdftotext -layout` gives for each |
| `as_received_v2/` | second delivery (v2), the same way |
| `as_received_v3/` | third delivery (v3): the work order that carried it, verbatim, and the text of each document. No PDF was delivered for v3 |
| `as_received_v4/` | fourth delivery (v4), the current one: the work order, verbatim, and the text of each document. No PDF. The order also carries the third document's text |
| `apply_v3.py` | builds the v3 text: the v2 text with the work order's two replacements, read from the order file |
| `apply_v4.py` | builds the v4 text: the v3 text with the order's one-line replacement in the coupling document; the truck document's text is carried over unchanged. Also reads the third document's code blocks out of the order |
| `DECLARED.json` | the rules for this folder, with one amendment per later delivery |
| `build_records.py` | reads each code block of the documents as the Python literal it is written as; nothing is typed by hand |
| `records.json` | current records (v4): 17 blocks with their section titles (which carry the OBSERVED / DERIVED / PROPOSED tags) and comments |
| `records_v3.json`, `records_v2.json`, `records_v1.json` | the earlier deliveries' records, each the same bytes as when it was named `records.json` |
| `as_received_stability/` | a third document, *Engineered Stability: Overshoot, Coupling and Buffer Visibility*: its PDF byte for byte and the extracted text (first delivery) |
| `records_engineered_stability.json` | that document's records: 5 blocks |
| `check_biological_load.py` | the checker; `check_results.json` is its last report |

```
python3 apply_v3.py --check
python3 apply_v4.py --check
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

## What changed from v3 to v4 (one line)

- Coupling document, the comment line after the `PROVENANCE` block's closing brace:
  - v3: "office seat writing about the floor = DERIVED at best, never OBSERVED"
  - v4: "office, media or academic seat writing about the floor / cab = DERIVED at best, never OBSERVED"

  This puts v1's media seat back and adds an academic seat, matching the `current_seat` options.
- Truck document: not changed. Its v4 text is the v3 text byte for byte.
- No block's values changed; one block's comments changed (`PROVENANCE`).

### v1 to v3 wording differences in `PROVENANCE`: ACCEPTED

The other five differences between the v1 block and the current one are intentional (generalized
across roles), accepted by the v4 work order on 2026-11-27. They stay as they are:

| Field / line | v1 | now |
|---|---|---|
| `conditions` | "real routes" | "real routes/shifts" |
| `role_type` | "day / regional / OTR / custody / owner-op" | "cab / floor / ward / classroom / field, with sub-role" |
| `recency` | "years since last doing it" | "years since exposure" |
| `current_seat` | without "floor" | includes "floor" |
| closing line on time | DIFFERENT in capitals, with a dash | "time measures different things; no single years threshold" |

## What the checker says (2026-11-27, v4)

- 36 checks, 0 failed (28 on the first two documents, 8 on the third); selftest 9, 0 failed.
  Hashes for v1 to v4; all four record files and the third document's match a rebuild; v3 text is
  v2 plus exactly its two replacements; v4 text is v3 plus exactly its one; every string in the
  current records is in the source text (417, 93 and 48 strings, 0 not found); all blocks parsed;
  the five figures the truck document derives from its own numbers reproduce (2 min, 87 m, 77 ft,
  0.8 s, 1 per 114 mi); four pointers resolve.
- 37 voids: 26 in the first two documents (unchanged since v2) and the 11 fields of `BUFFER_RECORD`.
  Each is listed with the document's own comment on that line or "no reason given in the document".
  None is read as zero or as safe.
- 11 outside figures NOT OPENED: the 9 in the truck document, plus Meadows et al. and Tainter.

## Third document: Engineered Stability (filed 2026-11-27)

A companion that sets the other two inside a stability frame: overshoot needs growth, a limit and
delayed feedback; delay and noise are the part that can be engineered; buffers are the stability
margin and are invisible by design. It names the coupling document as canonical for `PROVENANCE`,
`FALSE_DENOMINATOR` and `SENSOR_VALIDITY`.

- 8 checks of the 36 are its own, all pass: its records match a rebuild; every string is in the
  source text; all 5 blocks parsed; the three blocks it calls canonical exist in the coupling
  records; the two figures it shares with the truck document agree (3 s following distance,
  ~300 cut-ins a day).
- `BUFFER_RECORD` is a template: all 11 fields are voids, and the document says so ("None = void
  (unassessed), never treated as zero or as safe"). No buffer has been recorded yet.
  `BUFFER_EXAMPLES` lists 6 candidates.
- The v4 work order carried this document's text. It is not filed a second time: the PDF stays
  the source. The checker reads the five code blocks out of the order's text and they equal the
  blocks read from the PDF, value for value.
- Two framings are attributed by name (Meadows et al.; Tainter): outside figures, NOT OPENED.
- Its research program is open and nothing in it is started here: common denominators across
  domains; measured feedback delay per decision chain; buffer inventory per domain with trend;
  historical cases; small simulations of sensor latency against overshoot; thresholds.

## Open

- `ROLE` vocabulary: 11 of its 13 words are outside the four need states; 3 compound statuses
  (`RESTRICTED or ABSENT`, `SELF_FUNDED / RESTRICTED` twice) are unmapped.
- `responsibility_h` has mixed types: a number for the office role, text for regional and OTR, void
  for the day driver.
- `true_cost`: NOT_COMPUTABLE (per-need values are an open slot; the terms have different units).
- 11 figures or framings attributed to outside studies, agencies or authors: NOT OPENED (9 in the
  truck document; Meadows et al. and Tainter in the third).
- The documents' own open slots: day driver `responsibility_h`; health risk from sanitation and
  holding; per-need dollar values; owner-operator taxable profit rate; `conditions_now` vs
  `conditions_then` for current manufacturing rules; other roles; measured cost of decoupled decisions.
- Every field of `SENSOR_VALIDITY`, `STALENESS` and `PROVENANCE` is a void: not assessed.
- "~300 a day ≈ 27 an hour" implies 11.11 hours of driving a day; the document does not state the hours.

Observer slots: null.
