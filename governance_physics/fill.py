# SPDX-License-Identifier: CC0-1.0
"""governance-physics, amendment A3 step 4: fill from the declared sources.

    python3 governance_physics/fill.py SOURCE_DIR     fill tables, series, events
    python3 governance_physics/fill.py                self-test (no source needed)

SOURCE_DIR holds the files fetched from the declared hosts plus manifest.json
(URL, fetch time, sha256 per file).  The files are third-party data and are
not in this tree.  Every file is checked against the manifest and the pinned
hashes below before anything is read.

Reads: DECLARED.json and the source files.  It reads no other table in this
folder except table/functional.json, which it rewrites cell by cell.  The
descriptive-names table is never opened here (asserted in the self-test).

Rules, from DECLARED.json and amendment A3:
  - a value is filled only if the source carries it for that country
  - unmapped, gated or unreadable -> VOID + reason, never zero, never imputed
  - no tag, commodity or definition is swapped after seeing the data
  - no value is typed from memory
"""
import csv
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PINS = {
    "rsf_2026.csv": "65ec7bd9b9740e0f51e9b4eea585030b2226c1a96938ec06a4cbbdbd2639aae2",
    "ucdp/UcdpPrioConflict_v26_1.csv": "2aea044f1bcae7b050bb6c79fb796743e787edeed3b90e74e146cfc4e5b05447",
    "ucdp/OneSided_v26_1.csv": "603a9f8eb084b025b3097cc797012e0a533abe8b2089c7169e16688cd40a1d5c",
    "const_list.json": "e679c2b91782feea54471d48bc7ea5996a8558d01254fe780b82711d70a1c066",
    "bgs_Production.json": "da8e6ecae15faf85e800839fca2b15e16a193a85ba0c7ed1d93f54fc88602ccb",
    "bgs_Imports.json": "90eed698669fdfc484b2789716d0f8a89e5b792e02fd8ddef6b1192267413750",
    "bgs_Exports.json": "c301d4cd875159ebeb66fe434735a5efd6a3016e274701048958242ec4aac874",
}

# Names as each source writes them.  These are lookup keys, not values.
UCDP_GOV = {"USA": "Government of United States of America", "CHN": "Government of China",
            "IRN": "Government of Iran", "RUS": "Government of Russia (Soviet Union)",
            "IND": "Government of India", "BRA": "Government of Brazil",
            "CHE": "Government of Switzerland", "NOR": "Government of Norway"}
BGS_NAME = {"USA": "USA", "CHN": "China", "IRN": "Iran", "RUS": "Russia", "IND": "India",
            "BRA": "Brazil", "CHE": "Switzerland", "NOR": "Norway"}
CONST_ID = {"USA": "United_States_of_America_1992", "CHN": "China_2018", "IRN": "Iran_1989",
            "RUS": "Russia_2014", "IND": "India_2023", "BRA": "Brazil_2017",
            "CHE": "Switzerland_2014", "NOR": "Norway_2016"}
# Constitute's own topic keys for the provisions A3 names.
TOPICS = {"candidate_filter": [("hosrest", "Eligibility for head of state"),
                               ("hogrest", "Eligibility for head of government"),
                               ("lhrest", "Eligibility for first chamber"),
                               ("uhrest", "Eligibility for second chamber")],
          "economic_rules_set_by": [("bank", "Central bank"), ("budget", "Budget bills"),
                                    ("balbudgt", "Balanced budget")]}
COMMODITIES = ["lithium", "cobalt", "rare earths", "graphite", "nickel", "copper"]
QUOTE_CHARS = 400

VDEM_VOID = ("V-Dem file not read: the download on v-dem.net is behind a form that requires an email "
             "address, a gender field and approval of personal-data processing. Not submitted on the "
             "owner's behalf; owner decision. Form seen 2026-11-24.")
CPJ_VOID = ("CPJ 1 December census count not read: the site's per-country endpoint takes a 'year' filter "
            "that is not documented, and it returns a total for 2026 before 1 December 2026, so it is not "
            "established to be the 1 December snapshot. Not used. Probed 2026-11-24.")


def void(reason):
    return {"value": None, "source": None, "status": "VOID", "reason": reason}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load_sources(src):
    man = json.load(open(os.path.join(src, "manifest.json")))
    for rel, pin in PINS.items():
        got = sha(open(os.path.join(src, rel), "rb").read())
        if got != pin or man[rel]["sha256"] != pin:
            raise SystemExit("HASH MISMATCH %s: nothing filled" % rel)
    h = hashlib.sha256()
    names = sorted(n for n in os.listdir(os.path.join(src, "const")) if n.endswith(".json"))
    for n in names:
        h.update(n.encode() + b"\0" + open(os.path.join(src, "const", n), "rb").read())
    if h.hexdigest() != man["const/"]["combined_sha256"] or len(names) != man["const/"]["files"]:
        raise SystemExit("HASH MISMATCH const/: nothing filled")
    return man


def tag(man, rel):
    m = man[rel]
    return "%s fetched %s sha256:%s" % (m["url"], m["utc"], m["sha256"])


# ------------------------------------------------------------------- RSF
def rsf(src, man, isos):
    rows = list(csv.DictReader(open(os.path.join(src, "rsf_2026.csv"), encoding="latin-1"), delimiter=";"))
    by = {r["ISO"]: r for r in rows}
    out = {}
    for iso in isos:
        r = by.get(iso)
        if r is None or not r.get("Score 2026") or not r.get("Rank"):
            out[iso] = void("country not in the RSF 2026 file")
            continue
        out[iso] = {"value": {"edition": 2026, "score": float(r["Score 2026"].replace(",", ".")),
                              "rank": int(r["Rank"]), "ranked_countries": len(rows)},
                    "source": tag(man, "rsf_2026.csv"), "status": "MEASURED",
                    "note": "score and rank as published; an index built by the source, not a count"}
    return out


# ------------------------------------------------------------------- Constitute
def _text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def constitute(src, man, isos, field):
    titles = {c["id"]: c["title_long"] for c in json.load(open(os.path.join(src, "const_list.json")))}
    out = {}
    for iso in isos:
        cid = CONST_ID[iso]
        if cid not in titles:
            out[iso] = void("constitution id %s not in the Constitute in-force list" % cid)
            continue
        topics = {}
        for key, label in TOPICS[field]:
            d = json.load(open(os.path.join(src, "const", "%s__%s.json" % (cid, key))))[cid]
            provs = []
            for res in d["results"]:
                anchor = re.search(r'href="([^"]+)"', res)
                crumb = re.search(r'(?s)<span class="article-breadcrumb[^>]*>(.*?)</span>', res)
                body = _text(re.sub(r"(?s)<h4.*?</h4>", " ", res))
                provs.append({"where": _text(crumb.group(1)) if crumb else None,
                              "link": "https://www.constituteproject.org" + html.unescape(anchor.group(1))
                              if anchor else None,
                              "quote": body[:QUOTE_CHARS], "quote_cut": len(body) > QUOTE_CHARS,
                              "quote_full_chars": len(body)})
            topics[key] = {"topic": label, "sections_tagged": d["num_results"], "provisions": provs}
        n = sum(t["sections_tagged"] for t in topics.values())
        if n == 0:
            out[iso] = void("Constitute tags no section of %s with the declared topics (%s). "
                            "No tagged section is not the same as no rule in law."
                            % (cid, ", ".join(k for k, _ in TOPICS[field])))
            continue
        out[iso] = {"value": {"constitution": cid, "title": titles[cid], "topics": topics,
                              "elected": void("not read: the y/n is recorded only where a quoted provision "
                                              "states how the deciding body is chosen, and no mechanical "
                                              "rule for that reading was declared; needs a reader")},
                    "source": "%s ; sections: %s fetched %s to %s combined sha256:%s"
                              % (tag(man, "const_list.json"), man["const/"]["url"], man["const/"]["utc_first"],
                                 man["const/"]["utc_last"], man["const/"]["combined_sha256"]),
                    "status": "MEASURED",
                    "note": "quoted text as tagged by the source; a topic with 0 tagged sections is "
                            "'not tagged', not 'absent in law'. Quotes cut at %d characters where marked."
                            % QUOTE_CHARS}
    return out


# ------------------------------------------------------------------- UCDP
def ucdp(src, man, isos):
    acd = list(csv.DictReader(open(os.path.join(src, "ucdp/UcdpPrioConflict_v26_1.csv"), encoding="utf-8-sig")))
    one = list(csv.DictReader(open(os.path.join(src, "ucdp/OneSided_v26_1.csv"), encoding="utf-8-sig")))
    events, notes = [], {}
    for iso in isos:
        g = UCDP_GOV[iso]
        seen = set()
        for r in acd:
            parties = [p.strip() for p in (r["side_a"] + "," + r["side_b"]).split(",")]
            if g in parties and (r["conflict_id"], r["start_date2"]) not in seen:
                seen.add((r["conflict_id"], r["start_date2"]))
                events.append({"iso3": iso, "date": r["start_date2"], "kind": "conflict",
                               "what": "state-based conflict episode start; UCDP conflict_id %s; %s vs %s"
                                       % (r["conflict_id"], r["side_a"], r["side_b"]),
                               "source": "UCDP/PRIO Armed Conflict Dataset v26.1"})
        years = sorted({int(r["year"]) for r in one if r["actor_name"] == g})
        coalition = sorted({int(r["year"]) for r in one
                            if r["actor_name"] != g and g in [p.strip() for p in r["actor_name"].split(",")]})
        for i, y in enumerate(years):
            if i == 0 or y - years[i - 1] > 1:
                events.append({"iso3": iso, "date": "%d-01-01" % y, "kind": "conflict",
                               "what": "one-sided violence, first year of an unbroken run of active years; "
                                       "actor %s" % g,
                               "source": "UCDP One-sided Violence Dataset v26.1"})
        notes[iso] = {"state_based_episode_starts": len(seen), "one_sided_active_years": len(years),
                      "one_sided_coalition_years_not_counted": coalition}
    events.sort(key=lambda e: (e["iso3"], e["date"], e["what"]))
    return events, notes


# ------------------------------------------------------------------- BGS
def _bgs_lines(d, name):
    """(commodity, sub-line, unit) -> {year: value} for one country."""
    out = {}
    for com, subs in d["data"].get(name, {}).items():
        for sub, v in subs.items():
            out[(com, sub, v["units"])] = {int(y): x[0] for y, x in v["years"].items()}
    return out


def import_dependence(p, i, e):
    """(imports - exports) / (production + imports - exports); None if a term is missing
    or the denominator is zero or negative."""
    if p is None or i is None or e is None:
        return None
    den = p + i - e
    if den <= 0:
        return None
    return (i - e) / den


def bgs(src, man, isos):
    P, I, E = (json.load(open(os.path.join(src, "bgs_%s.json" % t))) for t in ("Production", "Imports", "Exports"))
    span = {"production": [int(P["minYear"]), int(P["maxYear"])], "imports": [int(I["minYear"]), int(I["maxYear"])],
            "exports": [int(E["minYear"]), int(E["maxYear"])]}
    years = range(min(s[0] for s in span.values()), max(s[1] for s in span.values()) + 1)
    all_lines = {"production": set(), "imports": set(), "exports": set()}
    per = {}
    for iso in isos:
        lp, li, le = (_bgs_lines(d, BGS_NAME[iso]) for d in (P, I, E))
        all_lines["production"] |= set(lp)
        all_lines["imports"] |= set(li)
        all_lines["exports"] |= set(le)
        per[iso] = (lp, li, le)
    # a line is same-basis only if production, imports and exports carry the identical
    # (commodity, sub-line, unit) in the source, for any of the eight countries
    same = all_lines["production"] & all_lines["imports"] & all_lines["exports"]
    series, cells = {}, {}
    for iso in isos:
        lp, li, le = per[iso]
        coms = {}
        for com in COMMODITIES:
            lines = sorted(k for k in same if k[0] == com)
            if not lines:
                coms[com] = void("no same-basis line: the source reports %s production and trade under "
                                 "different lines (production by mine / refinery output, trade by product "
                                 "form), so the three terms are not the same quantity" % com)
                continue
            k = lines[0]
            ys = {}
            for y in years:
                p, i, e = lp.get(k, {}).get(y), li.get(k, {}).get(y), le.get(k, {}).get(y)
                v = import_dependence(p, i, e)
                if v is None:
                    miss = [n for n, x in (("production", p), ("imports", i), ("exports", e)) if x is None]
                    ys[str(y)] = {"import_dependence": None,
                                  "void_reason": ("missing in source: " + ", ".join(miss)) if miss
                                  else "denominator zero or negative"}
                else:
                    ys[str(y)] = {"import_dependence": round(v, 6)}
            coms[com] = {"line": {"commodity": k[0], "sub_line": k[1], "unit": k[2]}, "years": ys}
        series[iso] = coms
        latest = None
        for com in COMMODITIES:
            if "years" in coms[com]:
                got = [int(y) for y, v in coms[com]["years"].items() if v["import_dependence"] is not None]
                if got:
                    y = max(got)
                    latest = latest or {}
                    latest[com] = {"year": y, "import_dependence": coms[com]["years"][str(y)]["import_dependence"]}
        if latest:
            cells[iso] = {"value": {"import_dependence": latest,
                                    "void_commodities": [c for c in COMMODITIES if c not in latest],
                                    "processing_share": void("the source response carries no world total "
                                                             "line; declared rule: no world total -> VOID")},
                          "source": "; ".join(tag(man, "bgs_%s.json" % t) for t in ("Production", "Imports", "Exports")),
                          "status": "DERIVED",
                          "formula": "(imports - exports) / (production + imports - exports)",
                          "note": "latest year with all three terms; trade lines in the source end in %d"
                                  % min(span["imports"][1], span["exports"][1])}
        else:
            cells[iso] = void("no commodity-year has production, imports and exports on one same-basis line "
                              "for this country in the source")
    return series, cells, span, sorted(same)


# ------------------------------------------------------------------- assemble
def combine(parts, note):
    """A field cell built from named source sub-cells; never averaged, never merged."""
    if all(p["status"] == "VOID" for p in parts.values()):
        return void("; ".join("%s: %s" % (k, p["reason"]) for k, p in parts.items()))
    return {"value": parts, "source": "see each sub-cell", "status": "MEASURED",
            "note": note, "void_parts": sorted(k for k, p in parts.items() if p["status"] == "VOID")}


def _write(rel, obj):
    with open(os.path.join(HERE, rel), "w") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def main(src):
    man = load_sources(src)
    d = json.load(open(os.path.join(HERE, "DECLARED.json")))
    isos = [c["iso3"] for c in d["countries"]]
    fn = json.load(open(os.path.join(HERE, "table/functional.json")))
    r, cf, er = rsf(src, man, isos), constitute(src, man, isos, "candidate_filter"), \
        constitute(src, man, isos, "economic_rules_set_by")
    events, enotes = ucdp(src, man, isos)
    mser, mcell, span, same = bgs(src, man, isos)
    for iso in isos:
        row = fn["countries"][iso]
        row["candidate_filter"] = combine({"constitute": cf[iso], "v-dem": void(VDEM_VOID)},
                                          "two sources, kept apart")
        row["economic_rules_set_by"] = combine({"constitute": er[iso],
                                                "central_bank_statute": void("no source declared in A3; not read")},
                                               "constitutional text only")
        row["dissent_cost"] = combine({"rsf": r[iso], "cpj": void(CPJ_VOID), "v-dem": void(VDEM_VOID)},
                                      "three sources, kept apart, never averaged")
        row["surveillance_decided_by"] = void(VDEM_VOID + " The only declared source for this field is V-Dem.")
        row["critical_minerals"] = mcell[iso]
        row["citizen_override"] = void("stays VOID (A3): no source declared; CourtListener not reachable")
        row["chokepoints"] = void("stays VOID: needs trade-flow data; no source declared in A3")
    fn["note"] = (fn["note"].split(" THIRD-PARTY:")[0] + " THIRD-PARTY: filled cells quote or derive from RSF, "
                  "Constitute (CC BY-NC 3.0), UCDP (CC BY 4.0) and BGS (copyright NERC; non-commercial "
                  "research use). Those terms apply to those cells; CC0 covers the structure and the code.")
    _write("table/functional.json", fn)
    _write("series/minerals.json", {
        "record": "annual mineral import dependence, per country per commodity",
        "formula": "(imports - exports) / (production + imports - exports)",
        "same_basis_rule": "computed only on a line where production, imports and exports carry the "
                           "identical (commodity, sub-line, unit) in the source; otherwise VOID",
        "same_basis_lines": [{"commodity": k[0], "sub_line": k[1], "unit": k[2]} for k in same],
        "source_year_span": span,
        "source": "; ".join(tag(man, "bgs_%s.json" % t) for t in ("Production", "Imports", "Exports")),
        "licence_note": "derived ratios only; no source tonnage is copied here. BGS World Mineral Statistics, "
                        "copyright NERC; BGS terms allow adapting and using the tables for non-commercial "
                        "academic and research purposes",
        "processing_share": void("the source response carries no world total line"),
        "countries": mser})
    _write("events/events.json", {
        "record": "dated policy / conflict events; no causal tags",
        "rule": "each event: {iso3, date, kind: policy|conflict, what, source}. No cause, no effect, no label.",
        "event_rule": [a for a in d["amendments"] if a["id"] == "A3"][0]["sources"]["ucdp"]["event_rule"],
        "status": "MEASURED", "events": events, "per_country": enotes,
        "policy_events": void("policy events stay VOID: no single dated source"),
        "source": "%s ; %s" % (tag(man, "ucdp/UcdpPrioConflict_v26_1.csv"), tag(man, "ucdp/OneSided_v26_1.csv")),
        "licence_note": "UCDP data, CC BY 4.0"})
    _write("series/fill_sources.json", {
        "record": "sources read by fill.py: URL, fetch time, sha256", "manifest": man,
        "not_read": {"v-dem": VDEM_VOID, "cpj": CPJ_VOID},
        "licences": {"rsf": "not stated on the index page read; score and rank quoted with attribution",
                     "constitute": "CC BY-NC 3.0 (stated on the site's about page)",
                     "ucdp": "CC BY 4.0 (stated on the downloads page)",
                     "bgs": "copyright NERC; non-commercial academic and research use (BGS mineral "
                            "statistics terms page)"}})
    print("%-4s %-10s %-10s %-10s %-10s %s" % ("iso", "cand.filt", "econ.rules", "dissent", "minerals", "events"))
    for iso in isos:
        row = fn["countries"][iso]
        print("%-4s %-10s %-10s %-10s %-10s %d" % (iso, *(row[f]["status"] for f in
              ("candidate_filter", "economic_rules_set_by", "dissent_cost", "critical_minerals")),
              sum(e["iso3"] == iso for e in events)))
    print("same-basis mineral lines:", same)


def selftest():
    ok = []
    ok.append(("import dependence 30/(70+30) = 0.3", abs(import_dependence(70, 40, 10) - 0.3) < 1e-12))
    ok.append(("missing term -> None, not 0", import_dependence(None, 40, 10) is None))
    ok.append(("zero or negative denominator -> None", import_dependence(10, 0, 10) is None))
    ok.append(("net exporter is negative, not clipped", import_dependence(100, 0, 20) == -0.25))
    ok.append(("VOID cell carries a reason and no value", void("x")["value"] is None and void("x")["reason"]))
    c = combine({"a": void("r1"), "b": void("r2")}, "n")
    ok.append(("all sub-cells VOID -> the field is VOID", c["status"] == "VOID"))
    c = combine({"a": {"value": 1, "source": "s", "status": "MEASURED"}, "b": void("r2")}, "n")
    ok.append(("one sub-cell filled -> field filled, VOID part listed", c["void_parts"] == ["b"]))
    me = open(os.path.abspath(__file__)).read()
    ok.append(("this file never names the descriptive-names table", ("lab" + "els.json") not in me))
    ok.append(("text extraction strips markup", _text("<p>a &amp; <b>b</b></p>") == "a & b"))
    bad = 0
    for name, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", name))
        bad += not good
    print("checks: %d   failed: %d" % (len(ok), bad))
    return bad


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        sys.exit(1 if selftest() else 0)
