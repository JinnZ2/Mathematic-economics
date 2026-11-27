#!/usr/bin/env python3
"""Build records.json from the two documents in as_received/. Stdlib only.

    python3 build_records.py            write records.json (current delivery) and check the earlier ones
    python3 build_records.py --check    rebuild both and compare with the stored files; exit 1 if either differs

Two deliveries (DECLARED.json, amendment 'second delivery'): v1 in as_received/, v2 in
as_received_v2/. The v1 record file keeps the bytes it had when it was named records.json.
Third delivery (amendment 'third delivery (v3)'): text only, no PDF; as_received_v3/*.txt is the v2
text with the work order's two replacements (apply_v3.py). records_v2.json keeps the v2 bytes.
Fourth delivery (amendment 'fourth delivery (v4)'): text only; as_received_v4/*.txt is the v3 text
with one line replaced in the coupling document (apply_v4.py). records_v3.json keeps the v3 bytes.
Fifth delivery (amendment 'fifth delivery (v5)'): the two documents are unchanged (v5 text = v4 text);
the third document gains three sections, read from the order (apply_v5.py). records_v4.json and
records_engineered_stability_v1.json keep their bytes.

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
            "v3": ("as_received_v3", "records_v3.json"), "v4": ("as_received_v4", "records_v4.json"), "v5": ("as_received_v5", "records.json")}
CURRENT = "v5"
# text-only deliveries: what the stored text is (v3 keeps the words it was written with)
TEXT_IS = {"v3": "the v2 extracted text with the replacements of %s/WORK_ORDER.md (apply_v3.py)",
           "v4": "the v3 text with the one-line replacement of %s/WORK_ORDER.md (apply_v4.py); "
                 "the truck document's text is the v3 text unchanged",
           "v5": "the v4 text unchanged, byte for byte; %s/WORK_ORDER.md changes only the third document (apply_v5.py)"}
# what each delivery's record file says about itself; v1 and v2 keep the words they were written with
SUPERSEDES = {"v2": "records_v1.json (first delivery, kept unchanged)",
              "v3": "records_v2.json (second delivery, kept unchanged)",
              "v4": "records_v3.json (third delivery, kept unchanged)",
              "v5": "records_v4.json (fourth delivery, kept unchanged)"}
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
            ar["text_is"] = TEXT_IS[version] % folder
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


# A third document, delivered once (DECLARED.json, amendment 'third document'). Its own record file.
STABILITY = ("engineered_stability", "Engineered Stability: Overshoot, Coupling and Buffer Visibility",
             "as_received_stability", "records_engineered_stability_v1.json")


def build_stability():
    name, title, folder, _ = STABILITY
    return {"record": "ENGINEERED_STABILITY", "date": "2026-11-27", "status": "PROPOSED", "license": "CC0",
            "co_authored": True, "observer_slots": None, "delivery": "v1",
            "note": "Built by build_records.py from the extracted text of the document. Values are the "
                    "document's; null is a void, never zero and never 'safe'.",
            "companions": "records.json (Decision-Exposure Coupling; Biological Load Accounting for Truck Drivers)",
            "documents": [{"document": title,
                           "as_received": {"pdf": "%s/%s.pdf" % (folder, name), "pdf_sha256": sha("%s/%s.pdf" % (folder, name)),
                                           "text": "%s/%s.txt" % (folder, name), "text_sha256": sha("%s/%s.txt" % (folder, name))},
                           "blocks": read_doc(name, title, folder)}]}


STABILITY_CURRENT = "records_engineered_stability.json"
STABILITY_V3 = "records_engineered_stability_v3.json"      # second PDF alone; kept unchanged
STABILITY_V2 = "records_engineered_stability_v2.json"      # first PDF + v5 order; kept unchanged
STABILITY_PDF2 = "as_received_stability_v2"                 # second PDF (amendment 'third document, second PDF')
SCALAR = re.compile(r'^     ([A-Z_]+) = ("|None\b)')


def read_scalars(lines):
    """One-line assignments (NAME = "..." / NAME = None  # ...), with lines the PDF wrapped joined."""
    out, section = [], None
    for i, raw in enumerate(lines):
        if raw.strip() and len(raw) - len(raw.lstrip()) == 2 and re.match(r"^[A-Z]", raw.strip()) and "(" in raw \
                and not lines[i - 1].strip() and not raw.strip().endswith((".", ":")):
            section = raw.strip()
            if section.count("(") > section.count(")"):
                section += " " + lines[i + 1].strip()
        m = SCALAR.match(raw)
        if not m:
            continue
        code, com = split_comment(raw)
        j = i + 1
        while j < len(lines) and lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) == 5 \
                and not SCALAR.match(lines[j]) and not OPEN.match(lines[j]):
            if com is None:
                code += " " + lines[j].strip()
            else:
                com += " " + lines[j].strip()
            j += 1
        try:
            value, reason = ast.literal_eval(code.split(" = ", 1)[1]), None
        except (SyntaxError, ValueError) as exc:
            value, reason = None, "%s: %s" % (type(exc).__name__, exc)
        out.append((i, {"block": m.group(1), "section": section, "state": "PARSED" if reason is None else "NOT_PARSED",
                        "reason": reason, "value": value, "comments": [com] if com is not None else [], "comments_after": []}))
    return out


def build_stability_v3():
    """Built from the second PDF's text alone. To do item boundaries come from the v5 order (see DECLARED.json)."""
    import apply_v5
    name, title, _, _ = STABILITY
    lines = clean_lines(name, title, STABILITY_PDF2)
    blocks = read_doc(name, title, STABILITY_PDF2)
    where = {b["block"]: next(i for i, l in enumerate(lines) if re.match(r"^\s*%s = " % b["block"], l)) for b in blocks}
    ordered = sorted([(where[b["block"]], b) for b in blocks] + read_scalars(lines), key=lambda t: t[0])
    start = next(i for i, l in enumerate(lines) if l.strip() == "To do (amendments)")
    todo = " ".join(" ".join(lines[start + 1:]).split()).replace("supply- chain", "supply-chain")
    items, rest, found = [], todo, True
    for it in apply_v5.read_additions()[1][-1]["items"]:
        if it["state"] != "AS_RECEIVED":
            continue
        if rest.startswith(it["text"]):
            items.append({"text": it["text"], "state": "IN_PDF", "boundary_from": "v5 order"})
            rest = rest[len(it["text"]):].lstrip()
        else:
            found = False
            items.append({"text": it["text"], "state": "NOT_FOUND_IN_PDF", "boundary_from": "v5 order"})
    if rest:
        items.append({"text": rest, "state": "IN_PDF", "boundary_from": "what remains after the items above" if found else None})
    pdf, txt = "%s/%s.pdf" % (STABILITY_PDF2, name), "%s/%s.txt" % (STABILITY_PDF2, name)
    return {"record": "ENGINEERED_STABILITY", "date": "2026-11-27", "status": "PROPOSED", "license": "CC0",
            "co_authored": True, "observer_slots": None, "delivery": "v3 (second PDF, six pages)",
            "supersedes": "%s (first PDF plus the v5 order's sections, kept unchanged)" % STABILITY_V2,
            "note": "Built by build_records.py from the extracted text of the second PDF. Values are the document's; "
                    "null is a void, never zero and never 'safe'. The PDF text has no bullet marks: To do item "
                    "boundaries are taken from the v5 order, and the last item is what remains.",
            "companions": "records.json (Decision-Exposure Coupling; Biological Load Accounting for Truck Drivers)",
            "documents": [{"document": title,
                           "as_received": {"pdf": pdf, "pdf_sha256": sha(pdf), "text": txt, "text_sha256": sha(txt)},
                           "blocks": [b for _, b in ordered],
                           "lists": [{"section": "To do (amendments)", "text": todo, "items": items}]}]}


def build_stability_v2():
    """The PDF's blocks unchanged, plus the blocks of the v5 order's three sections."""
    import apply_v5
    v1 = build_stability()
    blocks, lists, sections = apply_v5.read_additions()
    d1 = v1["documents"][0]
    src1, src2 = d1["as_received"]["text"], "as_received_v5/" + apply_v5.ADDITIONS
    return {"record": "ENGINEERED_STABILITY", "date": "2026-11-27", "status": "PROPOSED", "license": "CC0",
            "co_authored": True, "observer_slots": None, "delivery": "v2 (with the fifth delivery, v5)",
            "supersedes": "records_engineered_stability_v1.json (first delivery, kept unchanged)",
            "note": "The first five blocks are read from the PDF's extracted text; the rest from the three sections "
                    "the v5 work order carried. Values are the document's; null is a void, never zero and never "
                    "'safe'. The order arrived cut off: the last To do item is TRUNCATED.",
            "companions": "records.json (Decision-Exposure Coupling; Biological Load Accounting for Truck Drivers)",
            "documents": [{"document": d1["document"],
                           "as_received": dict(d1["as_received"], additions=src2, additions_sha256=sha(src2),
                                               additions_pdf=None, additions_pdf_reason="no PDF was delivered for the additions",
                                               order_sha256=sha("as_received_v5/WORK_ORDER.md")),
                           "sections_added": sections,
                           "blocks": [dict(b, source=src1) for b in d1["blocks"]] + [dict(b, source=src2) for b in blocks],
                           "lists": [dict(l, source=src2) for l in lists]}]}


def build_stability_v4():
    """The second PDF's blocks, with BRIDGE read from the v5 addendum's combined block."""
    import apply_v5_addendum as ad
    rec = build_stability_v3()
    d = rec["documents"][0]
    src1, src2 = d["as_received"]["text"], "as_received_v5_addendum/" + ad.OUT
    new = ad.read()
    d["blocks"] = [dict(new if b["block"] == "BRIDGE" else b, source=src2 if b["block"] == "BRIDGE" else src1) for b in d["blocks"]]
    d["as_received"] = dict(d["as_received"], addendum=src2, addendum_sha256=sha(src2), addendum_pdf=None,
                            addendum_pdf_reason="no PDF was delivered for the addendum",
                            order_sha256=sha("as_received_v5_addendum/WORK_ORDER.md"))
    rec["delivery"] = "v4 (second PDF plus the addendum to v5)"
    rec["supersedes"] = "%s (second PDF alone, kept unchanged)" % STABILITY_V3
    rec["note"] = ("Built by build_records.py: every block from the second PDF's text except BRIDGE, which is the v5 order's "
                   "BRIDGE with the addendum's material_dependency inserted after fuel_chain. Values are the document's; "
                   "null is a void, never zero. The addendum's written strings are from memory and NOT CHECKED.")
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
    for rec, fname, src, frozen in ((build_stability(), STABILITY[3], STABILITY[2], True),
                                    (build_stability_v2(), STABILITY_V2, STABILITY[2] + "/ and as_received_v5", True),
                                    (build_stability_v3(), STABILITY_V3, STABILITY_PDF2, True),
                                    (build_stability_v4(), STABILITY_CURRENT, STABILITY_PDF2 + "/ and as_received_v5_addendum", False)):
        out = os.path.join(HERE, fname)
        same = os.path.exists(out) and open(out, encoding="utf-8").read() == dump(rec)
        if sys.argv[1:] == ["--check"]:
            print("%s matches a rebuild from %s/: %s" % (fname, src, "yes" if same else "NO"))
            ok = ok and same
        elif frozen and not same:
            print("REFUSED: %s differs from a rebuild; an earlier delivery's records are not rewritten" % fname)
            ok = False
        else:
            open(out, "w", encoding="utf-8").write(dump(rec))
            for b in rec["documents"][0]["blocks"]:
                print("st  %-10s %-18s %-48s %s" % (b["state"], b["block"], (b["section"] or "")[:48], b["reason"] or ""))
    sys.exit(0 if ok else 1)
