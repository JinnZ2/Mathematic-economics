<!-- SPDX-License-Identifier: CC0-1.0 -->
# governance-physics

CC0, except `table/third_party/` (see the licence split below).
Co-authored (Kavik + Claude). Observer slots: null.

A functional table and a labels table for eight countries, an energy series,
dated conflict events, and one declared test: do resource-stress changes lead
events beyond a shuffled-date null. No verdict on any regime. No ranking.
`DECLARED.json` is the declaration; each amendment (A1 to A4) was committed
before the work it declares was run. `REPORT.md` is generated, never typed.

## Run

```text
python governance_physics/gp.py build OWID_CSV SOURCE_DIR   whole chain:
        tables -> series -> fill -> tests -> report
python governance_physics/gp.py                             self-test
python governance_physics/fill.py                           self-test
python governance_physics/gp.py calibrate | calibrate 2000 | calibrate fresh | calibrate tied
```

`tables` and `series` never overwrite a filled cell or a filled file.
OWID_CSV and SOURCE_DIR are third-party files and are not in this tree;
their URL, fetch time and sha256 are pinned in the code and in
`series/fill_sources.json`. Calibration is not part of `build`.

## Licence split

```text
CC0 (structure, code, own-derived numbers)
  DECLARED.json  gp.py  fill.py  REPORT.md  README.md
  table/functional.json      pointers, statuses, own counts; energy shares computed here
  table/labels.json
  series/energy.json         shares and balances computed here from Our World in Data
                             (CC BY 4.0, attribution in the file)
  series/minerals.json       rule and counts only
  series/calibration*.json   series/test_result*.json   series/fill_sources.json
  events/events.json         rule and counts only

NOT CC0: table/third_party/   each file has its own license field
  constitute.json   quoted constitutional provisions      CC BY-NC 3.0 Unported
  bgs.json          ratios derived from BGS tables        BGS terms: non-commercial academic
                                                          and research use; third-party or
                                                          commercial use needs permission
                                                          (not asked; note in the file)
  rsf.json          index score and rank                  not stated on the page read
  ucdp.json         conflict event rows                   CC BY 4.0
```

The order for this split named Constitute and BGS. RSF and UCDP were moved
under the same rule (CC0 files hold only CC0 or own-derived content); that
choice is recorded in amendment A4 and is the owner's to reverse.

## Provenance

Declaration and amendments: `DECLARED.json`. Sources, with URL, fetch time and
sha256: `series/fill_sources.json` and the `source` field of each cell.
Source origins (who funds each source): `DECLARED.json`, VERIFIED or
NOT_VERIFIED per entry. Unknowns are VOID with a reason, never zero.
