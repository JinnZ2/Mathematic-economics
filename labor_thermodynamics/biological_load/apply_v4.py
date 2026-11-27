#!/usr/bin/env python3
"""Build the v4 text of the two documents from the v3 text and the work order in
as_received_v4/WORK_ORDER.md. Stdlib only. Rule: DECLARED.json, amendment 'fourth delivery (v4)'.

    python3 apply_v4.py            write as_received_v4/*.txt
    python3 apply_v4.py --check    rebuild and compare with the stored files; exit 1 if they differ

Coupling document: one line replaced; the line and its replacement are read from the order file.
Truck document: not changed by the order; its v4 text is the v3 text byte for byte.
Also reads the third document's code blocks out of the order (order_blocks), for the checker.
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
V3, V4 = os.path.join(HERE, "as_received_v3"), os.path.join(HERE, "as_received_v4")
COUPLING, TRUCK = "decision_exposure_coupling.txt", "biological_load_accounting_for_truck_drivers.txt"


def order_lines():
    return open(os.path.join(V4, "WORK_ORDER.md"), encoding="utf-8").read().split("\n")


def build():
    lines = order_lines()
    old = next(l for l in lines if l.startswith("Replace:  "))[len("Replace:  "):]
    new = next(l for l in lines if l.startswith("With:     "))[len("With:     "):]
    c = open(os.path.join(V3, COUPLING), encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(c) if l.strip() == old]
    if len(hits) != 1:
        raise SystemExit("REFUSED: the line to replace was found %d times in the v3 coupling text" % len(hits))
    i = hits[0]
    c4 = c[:i] + [c[i][:len(c[i]) - len(c[i].lstrip())] + new] + c[i + 1:]
    truck = open(os.path.join(V3, TRUCK), encoding="utf-8").read()
    return {COUPLING: "\n".join(c4), TRUCK: truck}, {COUPLING: {"v3_line_replaced": i + 1}, TRUCK: {"changed": False}}


def order_blocks():
    """The third document's code blocks as written in the order: {name: value}. Comments dropped."""
    lines = order_lines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Title: "))
    out, i = {}, start
    while i < len(lines):
        m = re.match(r"^([A-Z_]+) = ([{\[])\s*$", lines[i])
        if m:
            close = "}" if m.group(2) == "{" else "]"
            j = next(k for k in range(i + 1, len(lines)) if lines[k] == close)
            src = m.group(2) + " ".join(re.sub(r'\s+#[^"]*$', "", l) for l in lines[i + 1:j]) + close
            out[m.group(1)] = ast.literal_eval(src)
            i = j
        i += 1
    return out


if __name__ == "__main__":
    texts, spans = build()
    ok = True
    for name, text in texts.items():
        p = os.path.join(V4, name)
        if sys.argv[1:] == ["--check"]:
            same = os.path.exists(p) and open(p, encoding="utf-8").read() == text
            print("%s matches v3 plus the order's replacement: %s" % (name, "yes" if same else "NO"))
            ok = ok and same
        else:
            open(p, "w", encoding="utf-8").write(text)
            print("wrote as_received_v4/%s  %s" % (name, spans[name]))
    sys.exit(0 if ok else 1)
