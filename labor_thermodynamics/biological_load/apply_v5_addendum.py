#!/usr/bin/env python3
"""Addendum to v5. Stdlib only. Rule: DECLARED.json, amendment 'addendum to v5: material_dependency inside BRIDGE'.

    python3 apply_v5_addendum.py            write as_received_v5_addendum/bridge_block.txt
    python3 apply_v5_addendum.py --check    rebuild and compare; exit 1 if it differs

The BRIDGE block as the v5 order wrote it, with the addendum's lines (cut from the addendum's
order file) inserted after the closing line of "fuel_chain". Nothing is retyped.
"""
import os
import sys

import apply_v5

HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = os.path.join(HERE, "as_received_v5_addendum")
OUT = "bridge_block.txt"
SECTION = "## Bridge window (DERIVED; figures via search, Nov 2026)"


def addendum_lines():
    lines = open(os.path.join(FOLDER, "WORK_ORDER.md"), encoding="utf-8").read().split("\n")
    a = [i for i, l in enumerate(lines) if l.startswith('  "material_dependency": {')]
    if len(a) != 1:
        raise SystemExit("REFUSED: the addendum's opening line was found %d times" % len(a))
    b = next(i for i in range(a[0] + 1, len(lines)) if lines[i] == "  },")
    return lines[a[0]:b + 1]


def build():
    lines = apply_v5.additions().split("\n")
    s = lines.index("BRIDGE = {")
    e = next(i for i in range(s, len(lines)) if lines[i] == "}")
    block = lines[s:e + 1]
    f = [i for i, l in enumerate(block) if l.startswith('  "fuel_chain": {')]
    if len(f) != 1:
        raise SystemExit("REFUSED: \"fuel_chain\" was found %d times in BRIDGE" % len(f))
    close = next(i for i in range(f[0] + 1, len(block)) if block[i] == "  },")
    return "\n".join([SECTION, ""] + block[:close + 1] + addendum_lines() + block[close + 1:]) + "\n"


def read():
    blocks, _, _ = apply_v5.read_additions(build())
    return blocks[0]


if __name__ == "__main__":
    p, text = os.path.join(FOLDER, OUT), build()
    if sys.argv[1:] == ["--check"]:
        same = os.path.exists(p) and open(p, encoding="utf-8").read() == text
        print("%s as built from the v5 BRIDGE plus the addendum: %s" % (OUT, "yes" if same else "NO"))
        sys.exit(0 if same else 1)
    open(p, "w", encoding="utf-8").write(text)
    print("wrote as_received_v5_addendum/%s" % OUT)
