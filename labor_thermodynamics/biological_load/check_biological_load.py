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
    """What differs between the two deliveries, read from the two record files."""
    old, new = br.build("v1"), br.build("v2")
    out = []
    for do, dn in zip(old["documents"], new["documents"]):
        bo = {b["block"]: b for b in do["blocks"]}
        bn = {b["block"]: b for b in dn["blocks"]}
        row = {"document": dn["document"], "blocks_removed": sorted(set(bo) - set(bn)),
               "blocks_added": sorted(set(bn) - set(bo)), "values_changed": [], "comments_changed": []}
        for k in sorted(set(bo) & set(bn)):
            lo, ln = dict(leaves(bo[k]["value"])), dict(leaves(bn[k]["value"]))
            for path in sorted(set(lo) | set(ln)):
                if lo.get(path, "ABSENT") != ln.get(path, "ABSENT"):
                    row["values_changed"].append({"block": k, "field": path.strip("/"),
                                                  "v1": lo.get(path, "ABSENT"), "v2": ln.get(path, "ABSENT")})
            if bo[k]["comments"] + bo[k]["comments_after"] != bn[k]["comments"] + bn[k]["comments_after"]:
                row["comments_changed"].append({"block": k,
                                                "added": [c for c in bn[k]["comments"] + bn[k]["comments_after"]
                                                          if c not in bo[k]["comments"] + bo[k]["comments_after"]]})
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
                check("%s delivery, %s: PDF and text hashes as recorded" % (version, d["document"]),
                      json.load(open(os.path.join(HERE, fname), encoding="utf-8"))["documents"][built["documents"].index(d)]["as_received"] == ar)
    out["info"]["changes_v1_to_v2"] = delivery_changes()
    blocks = {}
    all_voids = []
    for (name, title), d in zip(br.DOCS, rec["documents"]):
        ar = d["as_received"]
        check("%s: PDF and text hashes unchanged" % name,
              br.sha(ar["pdf"]) == ar["pdf_sha256"] and br.sha(ar["text"]) == ar["text_sha256"])
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
    for row in i["changes_v1_to_v2"]:
        print("INFO v1 -> v2, %s: blocks removed %s, added %s, values changed %d, blocks with new comments %d" % (
            row["document"], row["blocks_removed"], row["blocks_added"], len(row["values_changed"]), len(row["comments_changed"])))
    print("checks: %d   failed: %d" % (rep["summary"]["checks"], rep["summary"]["failed"]))
    if "--json" in sys.argv:
        p = sys.argv[sys.argv.index("--json") + 1]
        open(p, "w", encoding="utf-8").write(json.dumps(rep, indent=2, ensure_ascii=False) + "\n")
    sys.exit(1 if rep["summary"]["failed"] else 0)
