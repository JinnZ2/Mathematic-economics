#!/usr/bin/env python3
"""Build the v3 text of the two documents: the v2 extracted text with the two replacements the
work order names (as_received_v3/WORK_ORDER.md). Stdlib only. Rule: DECLARED.json, amendment
'third delivery (v3)'.

    python3 apply_v3.py            write as_received_v3/*.txt
    python3 apply_v3.py --check    rebuild and compare with the stored files; exit 1 if they differ

The replacement block and the replacement line are read from the work order file; they are not
typed again here. Each target must be found exactly once in the v2 text, or nothing is written.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V2, V3 = os.path.join(HERE, "as_received_v2"), os.path.join(HERE, "as_received_v3")
COUPLING, TRUCK = "decision_exposure_coupling.txt", "biological_load_accounting_for_truck_drivers.txt"


def order_parts():
    lines = open(os.path.join(V3, "WORK_ORDER.md"), encoding="utf-8").read().split("\n")
    a = lines.index("PROVENANCE = {")
    b = next(i for i in range(a, len(lines)) if lines[i].startswith("# CANONICAL:"))
    block = lines[a:b + 1]
    old = next(l for l in lines if l.startswith("Replace:  "))[len("Replace:  "):]
    new = next(l for l in lines if l.startswith("With:     "))[len("With:     "):]
    return block, old, new


def squeeze(s):
    return re.sub(r"\s+", " ", s).strip()


def build():
    block, old_fix, new_fix = order_parts()
    # --- coupling document: the whole PROVENANCE block, with its two trailing comment lines
    c = open(os.path.join(V2, COUPLING), encoding="utf-8").read().split("\n")
    starts = [i for i, l in enumerate(c) if l.strip() == "PROVENANCE = {"]
    if len(starts) != 1:
        raise SystemExit("REFUSED: PROVENANCE block found %d times in the v2 coupling text" % len(starts))
    a = starts[0]
    canon = next(i for i in range(a, len(c)) if c[i].strip().startswith("# CANONICAL:"))
    b = canon
    while b + 1 < len(c) and c[b + 1].strip() and not c[b + 1].strip().startswith("#"):
        b += 1                                    # the rest of that comment, which the PDF wrapped
    margin = " " * (len(c[a]) - len(c[a].lstrip()))
    c3 = c[:a] + [margin + l for l in block] + c[b + 1:]
    # --- truck document: the false_denominator fix line (wrapped over two lines in the v2 text)
    t = open(os.path.join(V2, TRUCK), encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(t) if l.strip().startswith('"fix":')]
    hits = [i for i in hits if squeeze(t[i] + " " + t[i + 1]) == old_fix]
    if len(hits) != 1:
        raise SystemExit("REFUSED: the fix line to replace was found %d times in the v2 truck text" % len(hits))
    i = hits[0]
    indent = " " * (len(t[i]) - len(t[i].lstrip()))
    t3 = t[:i] + [indent + new_fix] + t[i + 2:]
    spans = {COUPLING: {"v2_lines_replaced": [a + 1, b + 1], "v3_lines": len(block)},
             TRUCK: {"v2_lines_replaced": [i + 1, i + 2], "v3_lines": 1}}
    return {COUPLING: "\n".join(c3), TRUCK: "\n".join(t3)}, spans


if __name__ == "__main__":
    texts, spans = build()
    ok = True
    for name, text in texts.items():
        p = os.path.join(V3, name)
        if sys.argv[1:] == ["--check"]:
            same = os.path.exists(p) and open(p, encoding="utf-8").read() == text
            print("%s matches v2 plus the order's replacement: %s" % (name, "yes" if same else "NO"))
            ok = ok and same
        else:
            open(p, "w", encoding="utf-8").write(text)
            print("wrote as_received_v3/%s  %s" % (name, spans[name]))
    sys.exit(0 if ok else 1)
