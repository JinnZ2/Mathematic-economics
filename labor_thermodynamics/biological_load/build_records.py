#!/usr/bin/env python3
"""Build records.json from the two documents in as_received/. Stdlib only.

    python3 build_records.py            write records.json (current delivery) and check the earlier ones
    python3 build_records.py --check    rebuild both and compare with the stored files; exit 1 if either differs

Two deliveries (DECLARED.json, amendment 'second delivery'): v1 in as_received/, v2 in
as_received_v2/. The v1 record file keeps the bytes it had when it was named records.json.
Third delivery (amendment 'third delivery (v3)'): text only, no PDF; as_received_v3/*.txt is the v2
text with the work order's two replacements (apply_v3.py). records_v2.json keeps the v2 bytes.

Rule (DECLARED.json): every value comes from the extracted text. Each code block is rebuilt as the
Python literal it is written as (lines the PDF wrapped are joined again) and read with
ast.literal_eval. Nothing is typed by hand. A block that does not read is listed NOT_PARSED.
Comments are kept beside each block as text. Section titles carry the documents' status tags.
"""
import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = [("biological_load_accounting_for_truck_drivers", "Biological Load Accounting for Truck Drivers"),
        ("decision_exposure_coupling", "Decision-Exposure Coupling")]
VERSIONS = {"v1": ("as_received", "records_v1.json"), "v2": ("as_received_v2", "records_v2.json"),
            "v3": ("as_received_v3", "records.json")}
CURRENT = "v3"
# what each delivery's record file says about itself; v1 and v2 keep the words they were written with
SUPERSEDES = {"v2": "records_v1.json (first delivery, kept unchanged)",
              "v3": "records_v2.json (second delivery, kept unchanged)"}
OPEN = re.compile(r'^\s*(?:([A-Za-z_]+) = ([{\[])(?:\s*(#.*)?$|")|"([a-z_]+)": \{\s*(#.*)?$)')
KEYLINE = re.compile(r'^\s*("[^"]*":|[}\]\[]|"|#)')


def clean_lines(name, title, folder="as_received"):
    out = []
    for raw in open(os.path.join(HERE, folder, name + ".txt"), encoding="utf-8").read().replace("\f", "\n").split("\n"):
        s = raw.strip()
        if s == title or re.fullmatch(r"Page \d+ of \d+", s):
            continue          # running header and footer of the PDF pages
        out.append(raw)
    return out


def split_comment(line):
    """Return (code, comment). A # inside a string is not a comment."""
    quote = False
    for i, ch in enumerate(line):
        if ch == '"':
            quote = not quote
        elif ch == "#" and not quote:
            return line[:i].rstrip(), line[i + 1:].strip()
    return line.rstrip(), None


def read_block(lines, start):
    """Read one block starting at lines[start]. Returns (name, value or None, comments, end, reason)."""
    m = OPEN.match(lines[start])
    name = m.group(1) or m.group(4)
    margin = len(lines[start]) - len(lines[start].lstrip())
    code, comments, depth, last_was_comment, in_string = [], [], 0, False, False
    i = start
    while i < len(lines):
        raw = lines[i]
        if not raw.strip():
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip())
        continuation = i > start and indent <= margin and not re.match(r"^\s*[}\]]", raw) and depth > 0
        if continuation and last_was_comment and not in_string:
            comments[-1] = comments[-1] + " " + raw.strip()      # a comment the PDF wrapped
            i += 1
            continue
        c, com = split_comment(raw) if not in_string else (raw.rstrip(), None)
        if in_string or continuation:
            # a string the PDF wrapped: join with one space, unless the break came after a hyphen
            if in_string and '"' in raw:
                c, com = split_comment('"' + raw.lstrip())
                c = c[1:]
            joiner = "" if code and code[-1].endswith("-") else " "
            code[-1] = code[-1] + joiner + c.strip()
        else:
            code.append(c.strip())
        if com is not None:
            comments.append(com)
        last_was_comment = com is not None
        in_string = code[-1].count('"') % 2 == 1
        if not in_string:
            depth = sum(x.count("{") + x.count("[") - x.count("}") - x.count("]") for x in map(strip_strings, code))
            if depth == 0:
                break
        i += 1
    src = " ".join(code)
    src = re.sub(r"^[A-Za-z_]+ = ", "", src) if m.group(1) else "{" + src + "}"
    try:
        value = ast.literal_eval(src.rstrip(","))
        if not m.group(1):
            value = value[name]
        return name, value, comments, i, None
    except (SyntaxError, ValueError) as exc:
        return name, None, comments, i, "%s: %s" % (type(exc).__name__, exc)


def strip_strings(s):
    return re.sub(r'"[^"]*"', '""', s)


def read_doc(name, title, folder="as_received"):
    lines = clean_lines(name, title, folder)
    blocks, section, i = [], None, 0
    prose = []
    while i < len(lines):
        raw = lines[i]
        indent = len(raw) - len(raw.lstrip())
        if raw.strip() and indent == 2 and not raw.strip().startswith(("#", "•")) and len(raw.strip()) < 90 \
                and i + 1 < len(lines) and (not lines[i - 1].strip()) and re.match(r"^[A-Z]", raw.strip()) \
                and not raw.strip().endswith((".", ":")):
            section = raw.strip()
            # a title the PDF wrapped onto a second line
            if i + 1 < len(lines) and lines[i + 1].strip() and len(lines[i + 1]) - len(lines[i + 1].lstrip()) == 2 \
                    and (section.endswith(",") or section.count("(") > section.count(")")):
                section += " " + lines[i + 1].strip()
                i += 1
        if OPEN.match(raw) and indent >= 5:
            bname, value, comments, end, reason = read_block(lines, i)
            tail = []
            j = end + 1
            while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith("#") or
                                      (tail and len(lines[j]) - len(lines[j].lstrip()) == 5 and not OPEN.match(lines[j])
                                       and not re.match(r'^\s*"', lines[j]))):
                if lines[j].strip().startswith("#"):
                    tail.append(lines[j].strip()[1:].strip())
                elif lines[j].strip() and tail:
                    tail[-1] += " " + lines[j].strip()
                j += 1
            blocks.append({"block": bname, "section": section, "state": "PARSED" if reason is None else "NOT_PARSED",
                           "reason": reason, "value": value, "comments": comments, "comments_after": tail})
            i = end + 1
            continue
        i += 1
    return blocks


def sha(rel):
    return hashlib.sha256(open(os.path.join(HERE, rel), "rb").read()).hexdigest()


def build(version="v1"):
    folder = VERSIONS[version][0]
    docs = []
    for name, title in DOCS:
        has_pdf = os.path.exists(os.path.join(HERE, folder, name + ".pdf"))
        ar = {"pdf": "%s/%s.pdf" % (folder, name) if has_pdf else None,
              "pdf_sha256": sha("%s/%s.pdf" % (folder, name)) if has_pdf else None,
              "text": "%s/%s.txt" % (folder, name), "text_sha256": sha("%s/%s.txt" % (folder, name))}
        if not has_pdf:
            ar["pdf_reason"] = "no PDF was delivered for this version"
            ar["text_is"] = "the v2 extracted text with the replacements of %s/WORK_ORDER.md (apply_v3.py)" % folder
            ar["order_sha256"] = sha("%s/WORK_ORDER.md" % folder)
        docs.append({"document": title, "as_received": ar, "blocks": read_doc(name, title, folder)})
    rec = {"record": "BIOLOGICAL_LOAD_ACCOUNTING", "date": "2026-11-27", "status": "PROPOSED", "license": "CC0",
           "co_authored": True, "observer_slots": None,
           "note": "Built by build_records.py from the extracted text of the two documents. Values are the "
                   "documents'; null is a void, not False and not zero. Section titles carry the documents' "
                   "own status tags.",
           "documents": docs}
    if version != "v1":       # the v1 file keeps exactly the keys it was first written with
        rec = dict(rec, delivery=version, supersedes=SUPERSEDES[version])
    return rec


def dump(o):
    return json.dumps(o, indent=2, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    ok = True
    for version, (folder, fname) in VERSIONS.items():
        rec = build(version)
        out = os.path.join(HERE, fname)
        if sys.argv[1:] == ["--check"]:
            same = os.path.exists(out) and open(out, encoding="utf-8").read() == dump(rec)
            print("%s matches a rebuild from %s/: %s" % (fname, folder, "yes" if same else "NO"))
            ok = ok and same
            continue
        if version != CURRENT and os.path.exists(out) and open(out, encoding="utf-8").read() != dump(rec):
            print("REFUSED: %s exists and differs from a rebuild; an earlier delivery's records are not rewritten" % fname)
            ok = False
            continue
        open(out, "w", encoding="utf-8").write(dump(rec))
        for d in rec["documents"]:
            for b in d["blocks"]:
                print("%-3s %-10s %-18s %-48s %s" % (version, b["state"], b["block"], (b["section"] or "")[:48], b["reason"] or ""))
    sys.exit(0 if ok else 1)
