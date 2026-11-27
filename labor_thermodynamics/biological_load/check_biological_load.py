#!/usr/bin/env python3
"""Checker for the biological load records. Stdlib only. Rules: DECLARED.json.

    python3 check_biological_load.py              run every check; exit 1 if any FAIL
    python3 check_biological_load.py --json OUT   also write the report
    python3 check_biological_load.py --selftest

FAIL  = a rule of DECLARED.json is broken (bytes changed, a value not in the source text, a
        document's own arithmetic does not reproduce, records differ from a rebuild).
INFO  = reported, never hidden, not a failure: voids, compound statuses, other vocabularies,
        differences between the two documents, figures NOT OPENED.
The checker maps nothing, fills nothing and states no dollar value.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_records as br  # noqa: E402

STATES = ("PROVIDED", "SELF_FUNDED", "RESTRICTED", "ABSENT")
M_PER_MILE, M_PER_FT = 1609.344, 0.3048      # exact definitions


def squeeze(s):
    return re.sub(r"\s+", "", s)


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def voids(o, path=""):
    if o is None:
        yield path
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from voids(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from voids(v, "%s/%d" % (path, i))


def classify_status(value):
    """One of the four states, COMPOUND (two or more of them joined), or OTHER_VOCABULARY."""
    if value in STATES:
        return value
    parts = [p.strip() for p in re.split(r"\s+or\s+|\s*/\s*", value)]
    if len(parts) > 1 and all(p in STATES for p in parts):
        return "COMPOUND"
    return "OTHER_VOCABULARY"


FOLDER = br.VERSIONS[br.CURRENT][0]
POINTER = re.compile(r"^canonical in (.+)$")


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, "%s/%d" % (path, i))
    else:
        yield path, o


def delivery_changes():
    """What differs between each delivery and the next, read from the record files' sources."""
    out = []
    names = list(br.VERSIONS)
    for prev, cur in zip(names, names[1:]):
        old, new = br.build(prev), br.build(cur)
        for do, dn in zip(old["documents"], new["documents"]):
            bo = {b["block"]: b for b in do["blocks"]}
            bn = {b["block"]: b for b in dn["blocks"]}
            row = {"from": prev, "to": cur, "document": dn["document"], "blocks_removed": sorted(set(bo) - set(bn)),
                   "blocks_added": sorted(set(bn) - set(bo)), "values_changed": [], "comments_changed": []}
            for k in sorted(set(bo) & set(bn)):
                lo, ln = dict(leaves(bo[k]["value"])), dict(leaves(bn[k]["value"]))
                for path in sorted(set(lo) | set(ln)):
                    if lo.get(path, "ABSENT") != ln.get(path, "ABSENT"):
                        row["values_changed"].append({"block": k, "field": path.strip("/"),
                                                      "from": lo.get(path, "ABSENT"), "to": ln.get(path, "ABSENT")})
                co, cn = bo[k]["comments"] + bo[k]["comments_after"], bn[k]["comments"] + bn[k]["comments_after"]
                if co != cn:
                    row["comments_changed"].append({"block": k, "added": [c for c in cn if c not in co],
                                                    "removed": [c for c in co if c not in cn]})
            out.append(row)
    return out


def void_reason(block, key, name, title):
    """The comment the document puts on the line of a void, read from the source text."""
    lines = br.clean_lines(name, title, FOLDER)
    for i, raw in enumerate(lines):
        if re.search(r'"%s":\s*None' % re.escape(key), raw):
            code, com = br.split_comment(raw)
            if com:
                nxt = next((x for x in lines[i + 1:] if x.strip()), "")
                if not re.match(r'^\s*["}\]#]', nxt) and not br.OPEN.match(nxt):   # a comment the PDF wrapped
                    com += ("" if com.endswith("-") else " ") + nxt.strip()
                return com
    return "no reason given in the document"


def num(text, pattern):
    m = re.search(pattern, text)
    return float(m.group(1).replace(",", "")) if m else None


def arithmetic(bi):
    """Recompute what the buffer-intrusion block derives from its own numbers."""
    rows = []
    freq = bi["frequency"]
    per_day, per_hr, every = num(freq, r"~(\d+) cut-ins/day"), num(freq, r"≈ (\d+)/hr"), num(freq, r"every ~(\d+) min")
    rows.append(("one every ~%g min at %g/hr" % (every, per_hr), 60 / per_hr, every, round(60 / per_hr) == every))
    implied_h = per_day / per_hr
    pref = bi["buffer_vs_threshold"]["driver_preferred"]
    s, m, mph = num(pref, r"^(\d+) s"), num(pref, r"≈ (\d+) m"), num(pref, r"at (\d+) mph")
    v = mph * M_PER_MILE / 3600
    rows.append(("%g s at %g mph ≈ %g m" % (s, mph, m), s * v, m, round(s * v) == m))
    thr = bi["VTTI_2022"]["threshold"]
    tm, tft = num(thr, r"> ([\d.]+) m"), num(thr, r"~(\d+) ft")
    rows.append(("%g m ≈ %g ft" % (tm, tft), tm / M_PER_FT, tft, round(tm / M_PER_FT) == tft))
    key = [k for k in bi["buffer_vs_threshold"] if k.endswith("at 65 mph")][0]
    km, ks = num(key, r"^([\d.]+) m"), num(bi["buffer_vs_threshold"][key], r"≈ ([\d.]+) s")
    rows.append(("%g m at %g mph ≈ %g s" % (km, mph, ks), km / v, ks, round(km / v, 1) == ks))
    floor = bi["VTTI_2022"]["rate_floor"]
    per_mi = num(floor, r"per ~(\d+) mi")
    return rows, implied_h, per_day, per_hr, per_mi


def run():
    rec = json.load(open(os.path.join(HERE, "records.json"), encoding="utf-8"))
    fails, info = [], []
    out = {"record": "BIOLOGICAL_LOAD_CHECK", "checks": [], "info": {}}

    def check(name, ok, detail=""):
        out["checks"].append({"check": name, "state": "PASS" if ok else "FAIL", "detail": detail})
        if not ok:
            fails.append(name)

    for version, (folder, fname) in br.VERSIONS.items():
        built = br.build(version)
        check("%s matches a rebuild from %s/" % (fname, folder),
              open(os.path.join(HERE, fname), encoding="utf-8").read() == br.dump(built))
        if version != br.CURRENT:
            for d in built["documents"]:
                ar = d["as_received"]
                check("%s delivery, %s: file hashes as recorded" % (version, d["document"]),
                      json.load(open(os.path.join(HERE, fname), encoding="utf-8"))["documents"][built["documents"].index(d)]["as_received"] == ar)
    out["info"]["changes_between_deliveries"] = delivery_changes()
    import apply_v3
    texts, spans = apply_v3.build()
    check("v3 text is the v2 text plus exactly the work order's two replacements",
          all(open(os.path.join(HERE, "as_received_v3", n), encoding="utf-8").read() == t for n, t in texts.items()),
          json.dumps(spans))
    import apply_v4
    texts4, spans4 = apply_v4.build()
    check("v4 text is the v3 text plus exactly the work order's one replacement (truck document unchanged)",
          all(open(os.path.join(HERE, "as_received_v4", n), encoding="utf-8").read() == t for n, t in texts4.items())
          and open(os.path.join(HERE, "as_received_v4", apply_v4.TRUCK), "rb").read()
          == open(os.path.join(HERE, "as_received_v3", apply_v4.TRUCK), "rb").read(),
          json.dumps(spans4))
    check("as_received_v4/WORK_ORDER.md unchanged (hash as recorded)",
          all(d["as_received"].get("order_sha256") == br.sha("as_received_v4/WORK_ORDER.md")
              for d in json.load(open(os.path.join(HERE, "records_v4.json"), encoding="utf-8"))["documents"]))
    import apply_v5
    built5 = apply_v5.build()
    check("v5 text of the two documents is the v4 text, byte for byte",
          all(open(os.path.join(HERE, "as_received_v5", n), "rb").read() == open(os.path.join(HERE, "as_received_v4", n), "rb").read()
              for n in apply_v5.CARRIED))
    check("v5 additions file is the order's own text from '%s' to its end" % apply_v5.FIRST,
          open(os.path.join(HERE, "as_received_v5", apply_v5.ADDITIONS), encoding="utf-8").read() == built5[apply_v5.ADDITIONS]
          and open(os.path.join(HERE, "as_received_v5", "WORK_ORDER.md"), encoding="utf-8").read().endswith(built5[apply_v5.ADDITIONS]))
    blocks = {}
    all_voids = []
    for (name, title), d in zip(br.DOCS, rec["documents"]):
        ar = d["as_received"]
        check("%s: %s unchanged" % (name, "PDF and text hashes" if ar["pdf"] else "text and work-order hashes (no PDF in this delivery)"),
              (br.sha(ar["pdf"]) == ar["pdf_sha256"] if ar["pdf"]
               else br.sha(FOLDER + "/WORK_ORDER.md") == ar["order_sha256"]) and br.sha(ar["text"]) == ar["text_sha256"])
        text = squeeze("\n".join(br.clean_lines(name, title, FOLDER)))
        missing = [s for b in d["blocks"] for s in strings(b["value"]) if squeeze(s) not in text]
        n = sum(1 for b in d["blocks"] for _ in strings(b["value"]))
        check("%s: every string in the records is in the source text" % name, not missing,
              "%d strings, %d not found" % (n, len(missing)))
        check("%s: every block parsed" % name, all(b["state"] == "PARSED" for b in d["blocks"]),
              "%d blocks" % len(d["blocks"]))
        for b in d["blocks"]:
            blocks[(name, b["block"])] = b
            for path in voids(b["value"]):
                all_voids.append({"document": name, "block": b["block"], "field": path.strip("/"),
                                  "reason": void_reason(b, path.rsplit("/", 1)[-1], name, title)})
    out["info"]["voids"] = all_voids

    truck = "biological_load_accounting_for_truck_drivers"
    needs = blocks[(truck, "BIO_NEEDS")]["value"]
    status = {k: classify_status(v["truck"]["status"]) for k, v in needs.items()}
    out["info"]["need_status_truck"] = {k: {"as_written": needs[k]["truck"]["status"], "reads": status[k]} for k in needs}
    out["info"]["need_status_counts"] = {s: sum(v == s for v in status.values())
                                         for s in STATES + ("COMPOUND", "OTHER_VOCABULARY")}
    role = blocks[(truck, "ROLE")]["value"]
    role_words = sorted({v for r in role.values() for k, v in r.items()
                         if isinstance(v, str) and k not in ("on_duty_h", "responsibility_h")})
    out["info"]["role_block_vocabulary"] = {"words": role_words,
                                            "in_four_states": [w for w in role_words if w.upper() in STATES],
                                            "note": "the ROLE block uses its own words; nothing is mapped onto the four states"}
    out["info"]["responsibility_h"] = {r: {"as_written": v["responsibility_h"],
                                           "kind": "void" if v["responsibility_h"] is None
                                           else type(v["responsibility_h"]).__name__} for r, v in role.items()}
    keys = sorted({k for r in role.values() for k in r})
    out["info"]["role_keys_not_on_every_role"] = {k: [r for r in role if k in role[r]] for k in keys
                                                  if not all(k in role[r] for r in role)}

    rows, implied_h, per_day, per_hr, per_mi = arithmetic(blocks[(truck, "BUFFER_INTRUSION")]["value"])
    for label, got, stated, ok in rows:
        check("arithmetic: " + label, ok, "recomputed %.2f, stated %g" % (got, stated))
    vt = blocks[(truck, "BUFFER_INTRUSION")]["comments"]
    miles = next((num(c, r"([\d.]+)M miles") for c in vt if "miles" in c), None)
    cutins = next((num(c, r"~([\d,]+) close") for c in vt if "close cut-ins" in c), None)
    check("arithmetic: %g M miles / %g close cut-ins ≈ 1 per ~%g mi" % (miles, cutins, per_mi),
          round(miles * 1e6 / cutins) == per_mi, "recomputed %.1f" % (miles * 1e6 / cutins))
    out["info"]["implied_driving_hours_per_day"] = {
        "value": round(implied_h, 2),
        "note": "%g a day at %g an hour implies this many hours; the document does not state the hours, and "
                "the checker asserts nothing about them" % (per_day, per_hr)}

    out["info"]["true_cost"] = {"state": "NOT_COMPUTABLE",
                                "reason": "per-need dollar values are an open slot in the document; the terms "
                                          "(costs, a value for restricted and absent needs, hours) have different units"}
    ext = []
    bi, mk = blocks[(truck, "BUFFER_INTRUSION")]["value"], blocks[(truck, "market")]["value"]
    for label, v in (list(("VTTI_2022." + k, x) for k, x in bi["VTTI_2022"].items())
                     + list(("crash_data." + k, x) for k, x in bi["crash_data"].items() if k != "caveat")
                     + [("buffer_vs_threshold.FMCSA_guidance", bi["buffer_vs_threshold"]["FMCSA_guidance"])]
                     + [("market." + k, x) for k, x in mk.items() if isinstance(x, str) and re.search(r"\d", x)]):
        ext.append({"field": label, "as_written": v, "source_state": "NOT OPENED"})
    out["info"]["external_figures"] = ext

    dec = "decision_exposure_coupling"
    fa, fb = bi["false_denominator"], blocks[(dec, "FALSE_DENOMINATOR")]["value"]
    pointers = []
    for k, v in fa.items():
        m = POINTER.match(v) if isinstance(v, str) else None
        if m:
            ok = m.group(1) == "Decision-Exposure Coupling" and isinstance(fb.get(k), str) and bool(fb[k])
            pointers.append({"field": "BUFFER_INTRUSION/false_denominator/" + k, "points_to": m.group(1),
                             "resolves_to": fb.get(k), "resolves": ok})
            check("pointer: false_denominator.%s is defined in the coupling document" % k, ok)
    truck_text = " ".join(" ".join(br.clean_lines(truck, br.DOCS[0][1], FOLDER)).split())
    prov_pointer = "Canonical PROVENANCE block: Decision-Exposure Coupling" in truck_text
    if (truck, "PROVENANCE") not in blocks:
        ok = prov_pointer and (dec, "PROVENANCE") in blocks
        pointers.append({"field": "PROVENANCE", "points_to": "Decision-Exposure Coupling",
                         "resolves_to": sorted(blocks[(dec, "PROVENANCE")]["value"]) if ok else None, "resolves": ok})
        check("pointer: the truck document's PROVENANCE points to a block the coupling document carries", ok)
    canon = any("CANONICAL" in c for c in blocks[(dec, "PROVENANCE")]["comments"] + blocks[(dec, "PROVENANCE")]["comments_after"])
    out["info"]["two_documents"] = {
        "owner_of_shared_blocks": "Decision-Exposure Coupling" if canon and all(p["resolves"] for p in pointers) and pointers else None,
        "coupling_document_says_canonical": canon,
        "pointers": pointers,
        "kept_in_truck_document": {k: v for k, v in fa.items() if not (isinstance(v, str) and POINTER.match(v))},
        "note": "the truck document keeps its own instance and fix lines for the false denominator; its fix "
                "line reads %r, the coupling document's %r" % (fa.get("fix"), fb.get("fix"))}
    sv = blocks[(dec, "SENSOR_VALIDITY")]["value"]
    flat = list(voids(sv))
    out["info"]["sensor_validity"] = {"fields": len(flat), "void": len(flat),
                                      "document_rule_on_void": next((c for c in blocks[(dec, "SENSOR_VALIDITY")]["comments_after"]
                                                                     if "None" in c), None),
                                      "note": "every field is a void (not assessed): neither pass nor fail"}
    # --- third document: Engineered Stability (DECLARED.json, amendment 'third document') ---
    sname, stitle, sfolder, sfile = br.STABILITY
    srec = br.build_stability()
    check("%s matches a rebuild from %s/" % (sfile, sfolder),
          open(os.path.join(HERE, sfile), encoding="utf-8").read() == br.dump(srec))
    sd = srec["documents"][0]
    stext_lines = br.clean_lines(sname, stitle, sfolder)
    stext = squeeze("\n".join(stext_lines))
    smissing = [x for b in sd["blocks"] for x in strings(b["value"]) if squeeze(x) not in stext]
    sn = sum(1 for b in sd["blocks"] for _ in strings(b["value"]))
    check("%s: every string in the records is in the source text" % sname, not smissing,
          "%d strings, %d not found" % (sn, len(smissing)))
    check("%s: every block parsed" % sname, all(b["state"] == "PARSED" for b in sd["blocks"]), "%d blocks" % len(sd["blocks"]))
    sblocks = {b["block"]: b for b in sd["blocks"]}
    ob = apply_v4.order_blocks()
    differ = sorted(k for k in set(ob) | set(sblocks) if k not in ob or k not in sblocks or ob[k] != sblocks[k]["value"])
    check("third document: the code blocks in the v4 order's text equal the blocks read from the PDF",
          bool(ob) and not differ, "%d blocks in the order, %d from the PDF, differing: %s" % (len(ob), len(sblocks), differ or "none"))
    header = " ".join(" ".join(stext_lines).split())
    m = re.search(r"Decision-Exposure Coupling \(canonical ([A-Z_, ]+)\)", header)
    named = [x.strip() for x in m.group(1).split(",")] if m else []
    have = [x for x in named if (dec, x) in blocks]
    check("companion blocks the document calls canonical exist in the coupling records", bool(named) and have == named,
          "named %s, found %s" % (named, have))
    ex = " ".join(sblocks["BUFFER_EXAMPLES"]["value"])
    s_sec, s_day = num(ex, r"\((\d+) s\+\)"), num(ex, r"~(\d+)x/day")
    t_sec = num(bi["buffer_vs_threshold"]["driver_preferred"], r"^(\d+) s")
    t_day = num(bi["frequency"], r"~(\d+) cut-ins/day")
    check("shared figures agree with the truck document (following distance, cut-ins per day)",
          s_sec == t_sec and s_day == t_day, "%g s and %g a day here; %g s and %g a day there" % (s_sec, s_day, t_sec, t_day))
    svoids = [{"document": sname, "block": b["block"], "field": path.strip("/"),
               "reason": next((br.split_comment(raw)[1] for raw in stext_lines
                               if re.search(r'"%s":\s*None' % re.escape(path.rsplit("/", 1)[-1]), raw)
                               and br.split_comment(raw)[1]), None) or "no comment on that line"}
              for b in sd["blocks"] for path in voids(b["value"])]
    attributions = sorted({a for b in sd["blocks"] for txt in list(strings(b["value"])) + b["comments"]
                           for a in re.findall(r"(Meadows et al\.|Tainter)", txt)})
    out["info"]["engineered_stability"] = {
        "blocks": [b["block"] for b in sd["blocks"]],
        "sections": sorted({b["section"] for b in sd["blocks"]}),
        "voids": svoids,
        "document_rule_on_void": next((c for c in sblocks["BUFFER_RECORD"]["comments_after"] if "None" in c), None),
        "buffer_records_filled": 0 if all(v is None for v in sblocks["BUFFER_RECORD"]["value"].values()) else None,
        "buffer_examples": len(sblocks["BUFFER_EXAMPLES"]["value"]),
        "attributions": [{"name": a, "source_state": "NOT OPENED"} for a in attributions],
        "research_program": "open; nothing in it is started by this filing"}
    check("BUFFER_RECORD: every field is a void and is counted as a void (not zero, not safe)",
          all(v is None for v in sblocks["BUFFER_RECORD"]["value"].values())
          and len([v for v in svoids if v["block"] == "BUFFER_RECORD"]) == len(sblocks["BUFFER_RECORD"]["value"]),
          "%d fields, %d voids" % (len(sblocks["BUFFER_RECORD"]["value"]), len([v for v in svoids if v["block"] == "BUFFER_RECORD"])))
    for a in attributions:      # v4 order: outside figures, NOT OPENED
        ext.append({"field": "engineered_stability.attribution", "as_written": a, "source_state": "NOT OPENED"})
    check("Meadows et al. and Tainter are listed with the outside figures as NOT OPENED",
          {e["as_written"] for e in ext if e["field"] == "engineered_stability.attribution"} == {"Meadows et al.", "Tainter"})
    all_voids = all_voids + svoids
    # --- fifth delivery: three sections added to the third document (amendment 'fifth delivery (v5)') ---
    s2 = br.build_stability_v2()
    check("%s matches a rebuild (PDF blocks plus the v5 additions)" % br.STABILITY_V2,
          open(os.path.join(HERE, br.STABILITY_V2), encoding="utf-8").read() == br.dump(s2))
    d2 = s2["documents"][0]
    check("v5: the PDF's five blocks are carried unchanged into the new records",
          [{k: v for k, v in b.items() if k != "source"} for b in d2["blocks"][:len(sd["blocks"])]] == sd["blocks"])
    nb = d2["blocks"][len(sd["blocks"]):]
    atext = built5[apply_v5.ADDITIONS]
    titles = [t.split(" (")[0] for t in d2["sections_added"]]
    present = [t for t in titles if squeeze(t) in stext]
    clash = [b["block"] for b in nb if b["block"] in sblocks]
    check("v5: none of the three sections or their block names is in the filed PDF text (all three are added, nothing to compare)",
          not present and not clash, "sections already present: %s; block names already present: %s" % (present or "none", clash or "none"))
    check("v5: the filed document ends with 'Research program (open)', so the additions follow it as the order says",
          [b for b in stext_lines if b.startswith("  ") and b.strip().startswith("Research program")] != []
          and squeeze("\n".join(stext_lines)).rstrip().endswith(squeeze("Thresholds: when a shrinking buffer becomes a forcing event")))
    check("v5: every added block parsed", all(b["state"] == "PARSED" for b in nb), "%d blocks" % len(nb))
    amissing = [x for b in nb for x in strings(b["value"]) if x not in atext]
    check("v5: every string in the added records is in the additions text", not amissing,
          "%d strings, %d not found" % (sum(1 for b in nb for _ in strings(b["value"])), len(amissing)))
    alines = atext.split("\n")
    avoids = []
    for b in nb:
        paths = voids(b["value"]) if isinstance(b["value"], (dict, list)) else ([""] if b["value"] is None else [])
        for path in paths:
            key = path.rsplit("/", 1)[-1] or b["block"]
            pat = r'"%s":\s*None' % re.escape(key) if path else r"^%s = None" % re.escape(key)
            reason = next((br.split_comment(l)[1] for l in alines if re.search(pat, l) and br.split_comment(l)[1]), None)
            avoids.append({"document": sname, "block": b["block"], "field": path.strip("/") or b["block"],
                           "reason": reason or "no comment on that line"})
    nb_by = {b["block"]: b for b in nb}
    check("v5: UNCOUNTED_INPUTS is all voids and each is counted as a void (never zero)",
          all(v is None for v in nb_by["UNCOUNTED_INPUTS"]["value"].values())
          and len([v for v in avoids if v["block"] == "UNCOUNTED_INPUTS"]) == len(nb_by["UNCOUNTED_INPUTS"]["value"]),
          "%d fields, %d voids" % (len(nb_by["UNCOUNTED_INPUTS"]["value"]), len([v for v in avoids if v["block"] == "UNCOUNTED_INPUTS"])))
    seeds = nb_by["BRIDGE"]["value"]["seeds"]
    named_seeds = re.search(r"\(([^)]*)\)", seeds).group(1).split(", ")
    check("v5 internal: the reactor count in BRIDGE.seeds equals the number of names it lists",
          num(seeds, r"^(\d+) ") == len(named_seeds), "%g stated, %d named" % (num(seeds, r"^(\d+) "), len(named_seeds)))
    fc = nb_by["BRIDGE"]["value"]["fuel_chain"]
    y_w, y_c = num(fc["ban"], r"Jan 1 (\d{4})"), num(fc["US_output"], r"target ~(\d{4})")
    g_w, g_c = num(fc["gap"], r"waivers end (\d{4})"), num(fc["gap"], r"HALEU ~(\d{4})")
    check("v5 internal: fuel_chain.gap uses the same years as fuel_chain.ban and fuel_chain.US_output, and the waiver year is the earlier",
          y_w == g_w and y_c == g_c and g_w < g_c, "waivers %g / %g, commercial %g / %g" % (y_w, g_w, y_c, g_c))
    check("v5: 'see Biological Load Accounting' points to a document that is filed",
          any("see Biological Load Accounting" in c for c in nb_by["UNCOUNTED_INPUTS"]["comments"]) and truck.startswith("biological_load_accounting"))
    todo = d2["lists"][-1]["items"]
    cut = [t for t in todo if t["state"] == "TRUNCATED"]
    check("v5: the order's cut-off last line is recorded TRUNCATED, as received, and is the only such item",
          len(cut) == 1 and cut[0] is todo[-1] and atext.rstrip("\n").endswith("- " + cut[0]["text"]), "%r" % (cut[0]["text"] if cut else None))
    marks = {b["section"]: re.search(r"\(([^)]*)\)", b["section"]).group(1) for b in nb}
    for b in nb:
        for path, v in ([("", b["value"])] if isinstance(b["value"], str) else leaves(b["value"]) if isinstance(b["value"], dict) else []):
            if isinstance(v, str) and re.search(r"\d", v):
                ext.append({"field": "engineered_stability.%s%s" % (b["block"], ("." + path.strip("/").replace("/", ".")) if path else ""),
                            "as_written": v, "source_state": "NOT OPENED", "document_mark": marks[b["section"]]})
    names = sorted({n for b in nb for v in strings(b["value"]) for n in re.findall(r"Brockway et al\. 2019|Hall, Lambert|IEA|Rystad|DOE|Centrus", v)})
    out["info"]["engineered_stability_v5"] = {
        "sections_added": d2["sections_added"], "sections_already_present": present, "value_differences": [],
        "blocks_added": [b["block"] for b in nb], "voids": avoids,
        "void_written_inside_a_string": [v for b in nb for v in strings(b["value"]) if "void" in v],
        "to_do_items": len(todo) - len(cut), "truncated": cut,
        "outside_names": [{"name": n, "source_state": "NOT OPENED"} for n in names],
        "document_marks": marks}
    all_voids = all_voids + avoids
    # --- third document, second PDF (amendment 'third document, second PDF') ---
    s3 = br.build_stability_v3()
    check("%s matches a rebuild from %s/" % (br.STABILITY_V3, br.STABILITY_PDF2),
          open(os.path.join(HERE, br.STABILITY_V3), encoding="utf-8").read() == br.dump(s3))
    d3 = s3["documents"][0]
    check("second PDF: PDF and text hashes unchanged",
          br.sha(d3["as_received"]["pdf"]) == d3["as_received"]["pdf_sha256"] and br.sha(d3["as_received"]["text"]) == d3["as_received"]["text_sha256"])
    check("second PDF: every block parsed", all(b["state"] == "PARSED" for b in d3["blocks"]), "%d blocks" % len(d3["blocks"]))
    t3 = squeeze("\n".join(br.clean_lines(sname, stitle, br.STABILITY_PDF2)))
    m3 = [x for b in d3["blocks"] for x in strings(b["value"]) if squeeze(x) not in t3]
    check("second PDF: every string in the records is in the source text", not m3,
          "%d strings, %d not found" % (sum(1 for b in d3["blocks"] for _ in strings(b["value"])), len(m3)))
    old = {b["block"]: b for b in d2["blocks"]}
    keys = ("section", "state", "value", "comments", "comments_after")
    bdiff = [(b["block"], k) for b in d3["blocks"] for k in keys if b["block"] not in old or old[b["block"]][k] != b[k]]
    check("second PDF: same blocks in the same order as the first PDF plus the v5 order, equal value for value, comments included",
          [b["block"] for b in d3["blocks"]] == [b["block"] for b in d2["blocks"]] and not bdiff,
          "%d blocks, differences: %s" % (len(d3["blocks"]), bdiff or "none"))
    items3 = d3["lists"][0]["items"]
    check("second PDF: the v5 order's five full To do items are in the PDF, in order",
          [i["text"] for i in items3[:-1]] == [t["text"] for t in todo if t["state"] == "AS_RECEIVED"]
          and all(i["state"] == "IN_PDF" for i in items3))
    check("second PDF: the v5 order's cut-off line is the start of the PDF's sixth To do item",
          len(items3) == len(todo) and items3[-1]["text"].startswith(cut[0]["text"]) and len(items3[-1]["text"]) > len(cut[0]["text"]),
          "%r -> %d characters received" % (cut[0]["text"], len(items3[-1]["text"])))
    v3 = [(b["block"], p) for b in d3["blocks"]
          for p in (voids(b["value"]) if isinstance(b["value"], (dict, list)) else ([""] if b["value"] is None else []))]
    check("second PDF: void count equals the first PDF's plus the v5 additions' (no void filled, none added)",
          len(v3) == len(svoids) + len(avoids), "%d here, %d + %d before" % (len(v3), len(svoids), len(avoids)))
    out["info"]["engineered_stability_second_pdf"] = {
        "pages": 6, "blocks": [b["block"] for b in d3["blocks"]], "block_differences": bdiff, "voids": len(v3),
        "to_do_items": len(items3), "item_now_complete": items3[-1]["text"],
        "item_boundaries": "the PDF text has no bullet marks; boundaries of the first five are from the v5 order",
        "figures_in_completed_item": "none (no digits); its examples (chimerism, fetal microchimerism, mosaicism) are NOT OPENED",
        "to_do_item_claims_not_opened": ["human chimerism", "fetal microchimerism", "widespread mosaicism found within living memory"]}
    # --- addendum to v5: material_dependency inside BRIDGE ---
    import apply_v5_addendum as ad
    s4 = br.build_stability_v4()
    check("%s matches a rebuild (second PDF plus the addendum)" % br.STABILITY_CURRENT,
          open(os.path.join(HERE, br.STABILITY_CURRENT), encoding="utf-8").read() == br.dump(s4))
    btext = ad.build()
    check("addendum: bridge_block.txt is the v5 BRIDGE with the order's lines inserted after fuel_chain",
          open(os.path.join(ad.FOLDER, ad.OUT), encoding="utf-8").read() == btext
          and "\n".join(ad.addendum_lines()) in open(os.path.join(ad.FOLDER, "WORK_ORDER.md"), encoding="utf-8").read())
    d4 = s4["documents"][0]
    b4 = {b["block"]: b for b in d4["blocks"]}
    b3 = {b["block"]: b for b in d3["blocks"]}
    check("addendum: every block except BRIDGE is unchanged from the second PDF",
          all({k: v for k, v in b4[n].items() if k != "source"} == b3[n] for n in b3 if n != "BRIDGE") and list(b4) == list(b3))
    nv, ov = b4["BRIDGE"]["value"], b3["BRIDGE"]["value"]
    check("addendum: BRIDGE is the PDF's BRIDGE plus one key, material_dependency, right after fuel_chain",
          b4["BRIDGE"]["state"] == "PARSED" and {k: v for k, v in nv.items() if k != "material_dependency"} == ov
          and list(nv).index("material_dependency") == list(nv).index("fuel_chain") + 1,
          "keys: %s" % list(nv))
    md = nv["material_dependency"]
    mmiss = [x for x in strings(md) if x not in btext]
    check("addendum: every string in material_dependency is in the source text", not mmiss,
          "%d strings, %d not found" % (sum(1 for _ in strings(md)), len(mmiss)))
    mvoids = [p.strip("/") for p in voids(md)]
    materials = [k for k, v in md.items() if isinstance(v, dict)]
    expected = sorted([m + "/status" for m in materials] + [m + "/chain" for m in ("zirconium_hafnium", "nickel_alloys", "boron_10")])
    check("addendum: the voids are every status field plus the three chain fields the order names; each counted as a void, never zero",
          sorted(mvoids) == expected, "%d materials, %d voids" % (len(materials), len(mvoids)))
    marked = {m: md[m]["chain"] for m in materials if isinstance(md[m]["chain"], str)}
    check("addendum: each written chain line carries the document's NOT OPENED mark (helium/Qatar, Li-7, graphite)",
          sorted(marked) == ["helium", "lithium_7", "nuclear_graphite"] and all("(NOT OPENED)" in v for v in marked.values()))
    for m, v in marked.items():
        ext.append({"field": "engineered_stability.BRIDGE.material_dependency.%s.chain" % m, "as_written": v,
                    "source_state": "NOT OPENED", "document_mark": "PROPOSED; from memory, volume: thin"})
    madd = [{"document": sname, "block": "BRIDGE", "field": "material_dependency/" + p,
             "reason": "no comment on that line; the order: 'every value void until checked'"} for p in mvoids]
    out["info"]["engineered_stability_addendum"] = {
        "materials": materials, "voids": madd,
        "written_strings_not_checked": [{"field": p.strip("/"), "as_written": v, "state": "NOT CHECKED (from memory)"}
                                        for p, v in leaves(md) if isinstance(v, str)],
        "order_rule": "All figures from memory, NOT OPENED. Every value void until checked."}
    all_voids = all_voids + madd
    out["summary"] = {"checks": len(out["checks"]), "failed": len(fails), "voids": len(all_voids),
                      "external_figures_not_opened": len(ext)}
    return out


def selftest():
    cases = [("a state of the four reads as itself", classify_status("ABSENT") == "ABSENT"),
             ("'RESTRICTED or ABSENT' reads COMPOUND", classify_status("RESTRICTED or ABSENT") == "COMPOUND"),
             ("'SELF_FUNDED / RESTRICTED' reads COMPOUND", classify_status("SELF_FUNDED / RESTRICTED") == "COMPOUND"),
             ("a word outside the four reads OTHER_VOCABULARY", classify_status("geofenced") == "OTHER_VOCABULARY"),
             ("a void is found and is not False", list(voids({"a": None, "b": False, "c": 0})) == ["/a"]),
             ("a string not in the source is caught", squeeze("not in the text") not in squeeze("the source text")),
             ("a # inside a string is not a comment", br.split_comment('"a # b": 1,  # note') == ('"a # b": 1,', "note"))]
    good = {"frequency": "~300 cut-ins/day (x) ≈ 27/hr ≈ one every ~2 min of driving",
            "buffer_vs_threshold": {"driver_preferred": "3 s ≈ 87 m at 65 mph", "23.5 m at 65 mph": "≈ 0.8 s"},
            "VTTI_2022": {"threshold": "x > 23.5 m (~77 ft)", "rate_floor": "~1 close cut-in per ~114 mi"}}
    bad = json.loads(json.dumps(good))
    bad["buffer_vs_threshold"]["driver_preferred"] = "3 s ≈ 120 m at 65 mph"
    cases.append(("the document's arithmetic reproduces on a correct block", all(r[3] for r in arithmetic(good)[0])))
    cases.append(("a wrong derived figure is caught", not all(r[3] for r in arithmetic(bad)[0])))
    for name, ok in cases:
        print("%s  %s" % ("PASS" if ok else "FAIL", name))
    print("checks: %d   failed: %d" % (len(cases), sum(not ok for _, ok in cases)))
    return 0 if all(ok for _, ok in cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    rep = run()
    for c in rep["checks"]:
        print("%-4s %s  %s" % (c["state"], c["check"], c["detail"]))
    i = rep["info"]
    print("INFO voids: %d   need statuses (truck): %s" % (len(i["voids"]), i["need_status_counts"]))
    print("INFO ROLE block words outside the four states: %d of %d" % (
        len(i["role_block_vocabulary"]["words"]) - len(i["role_block_vocabulary"]["in_four_states"]),
        len(i["role_block_vocabulary"]["words"])))
    print("INFO implied driving hours per day: %s   true_cost: %s   external figures NOT OPENED: %d" % (
        i["implied_driving_hours_per_day"]["value"], i["true_cost"]["state"], len(i["external_figures"])))
    print("INFO shared blocks owned by: %s   pointers: %d, all resolve: %s" % (
        i["two_documents"]["owner_of_shared_blocks"], len(i["two_documents"]["pointers"]),
        all(p["resolves"] for p in i["two_documents"]["pointers"])))
    for row in i["changes_between_deliveries"]:
        print("INFO %s -> %s, %s: blocks removed %s, added %s, values changed %d, blocks with changed comments %d" % (
            row["from"], row["to"], row["document"], row["blocks_removed"], row["blocks_added"],
            len(row["values_changed"]), len(row["comments_changed"])))
    es = i["engineered_stability"]
    print("INFO engineered stability: %d blocks, %d voids (BUFFER_RECORD template, none filled), %d buffer examples, attributions NOT OPENED: %s" % (
        len(es["blocks"]), len(es["voids"]), es["buffer_examples"], [a["name"] for a in es["attributions"]]))
    print("checks: %d   failed: %d" % (rep["summary"]["checks"], rep["summary"]["failed"]))
    if "--json" in sys.argv:
        p = sys.argv[sys.argv.index("--json") + 1]
        open(p, "w", encoding="utf-8").write(json.dumps(rep, indent=2, ensure_ascii=False) + "\n")
    sys.exit(1 if rep["summary"]["failed"] else 0)
