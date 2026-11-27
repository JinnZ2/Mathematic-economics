#!/usr/bin/env python3
"""Fifth delivery. Stdlib only. Rule: DECLARED.json, amendment 'fifth delivery (v5)'.

    python3 apply_v5.py            write the v5 files in as_received_v5/
    python3 apply_v5.py --check    rebuild and compare with the stored files; exit 1 if they differ

The order changes neither of the first two documents: their v5 text is the v4 text, byte for byte.
For the third document it carries three sections. additions() cuts them out of the order file
(from '## Full-boundary EROI' to the end); read_additions() reads their code blocks as the Python
literals they are written as, and the To do list as lines. Nothing is retyped.
"""
import ast
import os
import re
import sys

import build_records as br

HERE = os.path.dirname(os.path.abspath(__file__))
V4, V5 = os.path.join(HERE, "as_received_v4"), os.path.join(HERE, "as_received_v5")
CARRIED = ["decision_exposure_coupling.txt", "biological_load_accounting_for_truck_drivers.txt"]
ADDITIONS = "engineered_stability_additions.txt"
FIRST = "## Full-boundary EROI"


def order_text():
    return open(os.path.join(V5, "WORK_ORDER.md"), encoding="utf-8").read()


def additions():
    t = order_text()
    if t.count("\n" + FIRST) != 1:
        raise SystemExit("REFUSED: '%s' is not in the order exactly once" % FIRST)
    return t[t.index("\n" + FIRST) + 1:]


def build():
    out = {n: open(os.path.join(V4, n), encoding="utf-8").read() for n in CARRIED}
    out[ADDITIONS] = additions()
    return out


def read_additions(text=None):
    """Returns (blocks, lists, sections). Blocks have the same shape as build_records' blocks."""
    lines = (additions() if text is None else text).split("\n")
    blocks, lists, sections, section, i = [], [], [], None, 0
    while i < len(lines):
        raw = lines[i]
        if raw.startswith("## "):
            section = raw[3:].strip()
            sections.append(section)
        m = re.match(r"^([A-Z_]+) = (.*)$", raw)
        if m:
            name, j = m.group(1), i
            if m.group(2).lstrip()[:1] in "{[":
                close = "}" if m.group(2).lstrip()[0] == "{" else "]"
                while lines[j] != close:
                    j += 1
            code, comments = [], []
            for l in lines[i:j + 1]:
                c, com = br.split_comment(l)
                code.append(c.strip())
                if com is not None:
                    comments.append(com)
            src = re.sub(r"^[A-Z_]+ = ", "", " ".join(code))
            try:
                value, reason = ast.literal_eval(src), None
            except (SyntaxError, ValueError) as exc:
                value, reason = None, "%s: %s" % (type(exc).__name__, exc)
            blocks.append({"block": name, "section": section, "state": "PARSED" if reason is None else "NOT_PARSED",
                           "reason": reason, "value": value, "comments": comments, "comments_after": []})
            i = j
        elif raw.startswith("- "):
            if not lists or lists[-1]["section"] != section:
                lists.append({"section": section, "items": []})
            lists[-1]["items"].append({"text": raw[2:], "state": "AS_RECEIVED"})
        i += 1
    # the order arrived cut off: if the text does not end with a newline-terminated full line that is
    # followed by nothing, the last item is where the cut fell
    last = lists[-1]["items"][-1] if lists else None
    if last is not None and lines[-1] == "" and lines[-2] == "- " + last["text"] and not re.search(r"[\s:;,]", last["text"]):
        last["state"] = "TRUNCATED"
        last["reason"] = "the order ends here, mid-word; what followed was not received"
    return blocks, lists, sections


if __name__ == "__main__":
    ok = True
    for name, text in build().items():
        p = os.path.join(V5, name)
        if sys.argv[1:] == ["--check"]:
            same = os.path.exists(p) and open(p, encoding="utf-8").read() == text
            print("%s as built from %s: %s" % (name, "the order" if name == ADDITIONS else "v4 (unchanged)", "yes" if same else "NO"))
            ok = ok and same
        else:
            open(p, "w", encoding="utf-8").write(text)
            print("wrote as_received_v5/%s" % name)
    sys.exit(0 if ok else 1)
