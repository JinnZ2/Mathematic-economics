"""governance-physics: same functional fields for every country, labels kept
apart, resource series beside them, one declared lead test.

License: CC0-1.0.  Standard library only.

    python governance_physics/gp.py tables  OWID_CSV   # table/functional.json, table/labels.json
    python governance_physics/gp.py series  OWID_CSV   # series/*.json, events/events.json
    python governance_physics/gp.py test               # the declared lead test
    python governance_physics/gp.py report             # REPORT.md
    python governance_physics/gp.py calibrate          # amendment A1: alpha on 200 noise seeds
    python governance_physics/gp.py                    # self-test (no data needed)

Everything this file does is fixed in DECLARED.json, which was committed
first.  The rules it enforces, in code and not only in prose:

    no recall     a value enters only from the fetched source file, whose
                  sha256 is asserted before a single cell is read
    VOID          an unmeasured cell is VOID with a reason; a blank source
                  cell is VOID, never 0
    labels apart  labels.json is written by its own function and is never
                  read by any function that builds or compares
                  functional.json
    no verdicts   nothing here ranks countries or scores a regime; the
                  similarity matrix compares filled functional fields only

OWID_CSV is owid-energy-data.csv from github.com/owid/energy-data.  It is
not copied into this repository; only derived shares are written, with the
source commit and hash beside them.
"""
import csv
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OWID_REPO = "github.com/owid/energy-data"
OWID_COMMIT = "f8de88a4f6f9cab44f1cf606047cbd6c4414042c"
OWID_SHA = "266f2e2baad7975351bc9bb4aa061d22b1da9fe4c47d51d2ac6071e01e171f76"
FUELS = ["oil", "gas", "coal"]
FIRST_YEAR = 2000


def declared():
    with open(os.path.join(HERE, "DECLARED.json")) as f:
        return json.load(f)


def void(reason):
    return {"value": None, "source": None, "status": "VOID", "reason": reason}


def _num(s):
    try:
        x = float(s)
    except (TypeError, ValueError):
        return None
    return x if x == x else None


def share_and_balance(production, consumption):
    """(net import share, bounded balance) or (None, None).  A missing input
    or a zero denominator gives None, never 0."""
    if production is None or consumption is None:
        return None, None
    share = (consumption - production) / consumption if consumption != 0 else None
    tot = consumption + production
    bal = (consumption - production) / tot if tot != 0 else None
    return share, bal


def read_owid(path):
    raw = open(path, "rb").read()
    got = hashlib.sha256(raw).hexdigest()
    if got != OWID_SHA:
        raise SystemExit("source sha256 mismatch: got %s" % got)
    isos = {c["iso3"] for c in declared()["countries"]}
    out = {}
    for r in csv.DictReader(raw.decode("utf-8").splitlines()):
        if r["iso_code"] in isos and int(r["year"]) >= FIRST_YEAR:
            out.setdefault(r["iso_code"], {})[int(r["year"])] = r
    return out


def energy_series(owid):
    """iso -> year -> fuel -> {production_twh, consumption_twh, net_import_share, balance}"""
    out = {}
    for iso, years in owid.items():
        out[iso] = {}
        for y in sorted(years):
            row = years[y]
            cell = {}
            for f in FUELS:
                p, c = _num(row[f + "_production"]), _num(row[f + "_consumption"])
                s, b = share_and_balance(p, c)
                cell[f] = {"production_twh": p, "consumption_twh": c,
                           "net_import_share": None if s is None else round(s, 6),
                           "balance": None if b is None else round(b, 6)}
            e = _num(row["net_elec_imports_share_demand"])
            cell["electricity"] = {"net_import_share_of_demand": None if e is None else round(e / 100.0, 6)}
            out[iso][str(y)] = cell
    return out


def owid_source():
    return "%s@%s owid-energy-data.csv sha256:%s" % (OWID_REPO, OWID_COMMIT, OWID_SHA)


# ------------------------------------------------------------------- tables
def build_functional(series):
    d = declared()
    table = {}
    for c in d["countries"]:
        iso = c["iso3"]
        row = {}
        for field, spec in d["fields"].items():
            if field == "energy_base":
                continue
            row[field] = void("source not read in this run (%s); no value typed from memory%s"
                              % (spec["source_state"], "; " + spec["note"] if spec.get("note") else ""))
        val = {}
        for f in FUELS:
            best = None
            for y in sorted(series.get(iso, {}), key=int, reverse=True):
                k = series[iso][y][f]
                if k["net_import_share"] is not None and k["balance"] is not None:
                    best = {"year": int(y), "net_import_share": k["net_import_share"], "balance": k["balance"]}
                    break
            val[f] = best if best else {"year": None, "net_import_share": None, "balance": None,
                                         "void_reason": "no year with both production and consumption in the source"}
        if any(v["year"] is not None for v in val.values()):
            row["energy_base"] = {"value": val, "source": owid_source(), "status": "DERIVED",
                                  "formula": d["fields"]["energy_base"]["formula"]}
        else:
            row["energy_base"] = void("no fuel has both production and consumption in the source")
        table[iso] = row
    return {"record": "governance-physics functional table", "license": "CC0-1.0",
            "note": "energy_base is derived from Our World in Data (CC BY 4.0), built on the Energy Institute "
                    "Statistical Review; those terms apply to the underlying figures.",
            "countries": table}


def build_labels():
    """Written with no access to the functional table, by construction."""
    d = declared()
    reason = "no label source read in this run (%s); no label typed from memory" % d["labels_table"]["source_state"]
    return {"record": "governance-physics labels table", "license": "CC0-1.0",
            "rule": d["rules"]["labels"],
            "countries": {c["iso3"]: {"self_labels": void(reason), "labels_by_others": void(reason)}
                          for c in d["countries"]}}


# --------------------------------------------------------------------- test
def stress_changes(series_iso):
    """year -> largest year-on-year rise in balance across fuels (None if no fuel has both years)."""
    out = {}
    years = sorted(int(y) for y in series_iso)
    for y in years[1:]:
        rises = []
        for f in FUELS:
            a = series_iso.get(str(y - 1), {}).get(f, {}).get("balance")
            b = series_iso[str(y)][f]["balance"]
            if a is not None and b is not None:
                rises.append(b - a)
        out[y] = max(rises) if rises else None
    return out


def lead_stat(stress, event_years, window):
    vals = []
    for e in event_years:
        w = [stress.get(y) for y in range(e - window, e)]
        if any(v is None for v in w):
            return None
        vals.append(sum(w) / window)
    return sum(vals) / len(vals) if vals else None


def lead_test(stress, event_years, window=3, draws=1000, seed=20261124, min_events=3):
    eligible = [y for y in stress if all(stress.get(k) is not None for k in range(y - window, y))]
    ev = sorted(e for e in event_years if e in eligible)
    if len(ev) < min_events:
        return {"state": "NOT RUN", "reason": "fewer than %d dated events with a full lead window (%d)"
                % (min_events, len(ev)), "n_events": len(ev)}
    obs = lead_stat(stress, ev, window)
    rng = random.Random(seed)
    null = sorted(lead_stat(stress, rng.sample(eligible, len(ev)), window) for _ in range(draws))
    return {"state": "RUN", "n_events": len(ev), "observed": obs, "null_mean": sum(null) / len(null),
            "null_p05": null[int(0.05 * (len(null) - 1))], "null_p95": null[int(0.95 * (len(null) - 1))],
            "share_null_ge_observed": sum(x >= obs for x in null) / len(null),
            "effect": obs - sum(null) / len(null)}


def noise_pvalues(seeds):
    out = []
    for seed in range(seeds):
        r = random.Random(seed)
        stress = {y: r.gauss(0, 0.01) for y in range(1960, 2025)}
        events = sorted(r.sample(range(1970, 2024), 8))
        out.append(lead_test(stress, events, seed=seed)["share_null_ge_observed"])
    return out


def calibrated_threshold(pvals, target=0.05):
    """Amendment A2 step 2: the largest threshold on share_null_ge_observed
    whose false-flag rate on the calibration seeds is at most target."""
    best = None
    for t in sorted(set(pvals)):
        if sum(p <= t for p in pvals) / len(pvals) <= target:
            best = t
    return best


def flag_threshold():
    """The threshold in force: 0.05 as first declared, or the calibrated one
    once series/calibration_2000.json records it (amendment A2)."""
    try:
        return _load("series/calibration_2000.json")["threshold_in_force"]
    except (IOError, OSError, KeyError):
        return 0.05


def calibrate(seeds=200):
    """Amendment A1: false-flag rate of the lead test on pure noise."""
    flags = [p <= 0.05 for p in noise_pvalues(seeds)]
    k, n, z = sum(flags), seeds, 1.96
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return {"seeds": n, "flagged": k, "alpha": p, "wilson95": [round(centre - half, 4), round(centre + half, 4)],
            "nominal": 0.05, "above_nominal": p > 0.05,
            "interval_excludes_nominal": centre - half > 0.05 or centre + half < 0.05}


# --------------------------------------------------------------- similarity
def similarity(functional, series):
    """Functional fields only.  This function is never given the labels table.
    energy_base is compared per fuel at the latest year where BOTH countries
    have a balance, as declared; a fuel with no common year is left out."""
    isos = sorted(functional["countries"])
    out = {}
    for i in isos:
        for j in isos:
            if i >= j:
                continue
            dists = {}
            a, b = functional["countries"][i], functional["countries"][j]
            for field in a:
                if a[field]["status"] == "VOID" or b[field]["status"] == "VOID":
                    continue
                if field == "energy_base":
                    ds, yrs = [], {}
                    for f in FUELS:
                        common = [y for y in series[i] if y in series[j]
                                  and series[i][y][f]["balance"] is not None
                                  and series[j][y][f]["balance"] is not None]
                        if common:
                            y = max(common, key=int)
                            ds.append(abs(series[i][y][f]["balance"] - series[j][y][f]["balance"]) / 2.0)
                            yrs[f] = int(y)
                    if ds:
                        dists[field] = sum(ds) / len(ds)
                        years_used = yrs
            out["%s-%s" % (i, j)] = ({"similarity": round(1 - sum(dists.values()) / len(dists), 4),
                                      "fields_used": sorted(dists), "energy_years": years_used} if dists else
                                     {"similarity": None, "fields_used": [], "reason": "no shared filled field"})
    return out


# ------------------------------------------------------------------- output
def _write(rel, obj):
    p = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def _load(rel):
    with open(os.path.join(HERE, rel)) as f:
        return json.load(f)


def cmd_tables(path):
    series = energy_series(read_owid(path))
    _write("table/functional.json", build_functional(series))
    _write("table/labels.json", build_labels())
    print("wrote table/functional.json and table/labels.json")


def cmd_series(path):
    d = declared()
    series = energy_series(read_owid(path))
    _write("series/energy.json", {"record": "annual energy net import share and balance by fuel",
                                   "source": owid_source(), "units": "TWh; shares and balances are fractions",
                                   "formula": d["fields"]["energy_base"]["formula"],
                                   "licence_note": "derived from Our World in Data (CC BY 4.0), built on the Energy "
                                                   "Institute Statistical Review; a null is a blank in the source",
                                   "countries": series})
    _write("series/minerals.json", {"record": "annual mineral import dependence",
                                     "countries": {c["iso3"]: void("no minerals source declared or read: %s"
                                                                   % d["fields"]["critical_minerals"]["source"])
                                                   for c in d["countries"]}})
    _write("events/events.json", {"record": "dated policy / conflict events; no causal tags",
                                   "rule": "each event: {iso3, date, kind: policy|conflict, what, source}. "
                                           "No cause, no effect, no label.",
                                   "events": [],
                                   "status": "VOID",
                                   "reason": "no event source read in this run (%s); no event typed from memory; %s"
                                             % (d["events"]["source_state"], d["events"]["note"])})
    print("wrote series/energy.json, series/minerals.json, events/events.json")


def cmd_test():
    d = declared()["test"]
    series = _load("series/energy.json")["countries"]
    events = _load("events/events.json")["events"]
    res = {}
    for iso in sorted(series):
        ev = [int(e["date"][:4]) for e in events if e["iso3"] == iso]
        res[iso] = lead_test(stress_changes(series[iso]), ev, d["lead_window_years"])
    _write("series/test_result.json", {"record": "lead test, as declared", "declared": d, "countries": res})
    for iso, r in res.items():
        print(iso, r["state"], r.get("reason", ""))
    return res


def cmd_report():
    d = declared()
    fn = _load("table/functional.json")
    lb = _load("table/labels.json")
    test = _load("series/test_result.json")["countries"]
    series = _load("series/energy.json")["countries"]
    cal = _load("series/calibration.json")["result"]
    isos = [c["iso3"] for c in d["countries"]]
    fields = list(d["fields"])
    L = ["# governance-physics: report", "",
         "CC0. Co-authored (Kavik + Claude). Generated by `python governance_physics/gp.py report`;",
         "no number below was typed. Observer slots: null.", "",
         "No verdict on any regime is made here and no country is ranked.", "",
         "## Filled vs VOID, per field per country", "", "```text",
         "%-24s %s" % ("field", "  ".join(isos))]
    for f in fields:
        L.append("%-24s %s" % (f, "  ".join("%-3s" % ("ok" if fn["countries"][i][f]["status"] != "VOID" else "V")
                                             for i in isos)))
    filled = sum(fn["countries"][i][f]["status"] != "VOID" for i in isos for f in fields)
    L += ["", "ok = filled, V = VOID.  filled %d of %d cells." % (filled, len(isos) * len(fields)),
          "labels table: %d of %d label cells filled."
          % (sum(lb["countries"][i][k]["status"] != "VOID" for i in isos for k in lb["countries"][i]),
             2 * len(isos)), "```", "",
          "VOID reasons, one per field (the same for every country):", "", "```text"]
    for f in fields:
        if fn["countries"][isos[0]][f]["status"] == "VOID":
            L.append("%-24s %s" % (f, fn["countries"][isos[0]][f]["reason"]))
    L += ["```", "", "## energy_base: latest year with both production and consumption in the source", "",
          "net import share = (consumption - production) / consumption; positive = net importer.",
          "balance = (consumption - production) / (consumption + production), bounded -1..1.", "", "```text",
          "iso   " + "   ".join("%-28s" % (f + " (year share balance)") for f in FUELS)]
    for i in isos:
        v = fn["countries"][i]["energy_base"]["value"]
        cells = []
        for f in FUELS:
            k = v[f]
            cells.append("%-28s" % ("VOID" if k["year"] is None else
                                     "%d %+9.3f %+7.3f" % (k["year"], k["net_import_share"], k["balance"])))
        L.append("%-5s %s" % (i, "   ".join(cells)))
    L += ["```", "", "Series coverage (years with a balance, of %d to latest):" % FIRST_YEAR, "", "```text"]
    for i in isos:
        ys = sorted(int(y) for y in series[i])
        L.append("%-5s %d-%d   " % (i, ys[0], ys[-1]) + "   ".join(
            "%s %d of %d" % (f, sum(series[i][str(y)][f]["balance"] is not None for y in ys), len(ys)) for f in FUELS))
    L += ["```", "", "## Similarity on functional fields only", "",
          "Labels never enter. A pair's similarity is taken over the fields filled for both.",
          "Only energy_base is filled, so every number below is energy-balance similarity and",
          "nothing else. It is not a country similarity.", "", "```text", "      " + "    ".join(isos)]
    sim = similarity(fn, series)
    for i in isos:
        row = []
        for j in isos:
            if i == j:
                row.append("   -  ")
            else:
                k = sim["%s-%s" % tuple(sorted((i, j)))]
                row.append("%6s" % ("VOID" if k["similarity"] is None else "%.3f" % k["similarity"]))
        L.append("%-5s %s" % (i, " ".join(row)))
    old = sorted({"%s %d" % (f, y) for k in sim.values() if k["similarity"] is not None
                  for f, y in k["energy_years"].items() if y < max(int(x) for x in series[isos[0]]) - 1})
    L += ["", "Each fuel is compared at the latest year both countries have a balance.",
          "Comparisons that fall back to an older year: %s." % (", ".join(old) or "none")]
    L += ["```", "", "## Lead test (declared before any run)", "", d["test"]["question"], "", "```text"]
    for i in isos:
        r = test[i]
        L.append("%-5s %s" % (i, r["state"] + ("  " + r["reason"] if r["state"] != "RUN" else
                 "  n %d  observed %+.4f  null mean %+.4f  null 5..95 %+.4f..%+.4f  share null >= obs %.3f"
                 % (r["n_events"], r["observed"], r["null_mean"], r["null_p05"], r["null_p95"],
                    r["share_null_ge_observed"]))))
    L += ["```", "", "The events file is empty (no event source was read), so the test did not run for any",
          "country. Its code was checked on synthetic series only: a planted three-year lead is",
          "flagged (self-test); the pure-noise flag rate is the calibration below.",
          "", "Calibration (amendment A1): on %d pure-noise seeds the test flagged %d, alpha = %.3f"
          % (cal["seeds"], cal["flagged"], cal["alpha"]),
          "(95%% interval %.3f to %.3f; nominal 0.05). alpha is above nominal: %s. The interval"
          % (cal["wilson95"][0], cal["wilson95"][1], "yes" if cal["above_nominal"] else "no"),
          "excludes nominal: %s. A fix is PROPOSED as amendment A2 in DECLARED.json and is not applied."
          % ("yes" if cal["interval_excludes_nominal"] else "no"),
          "", "## Source origin", "",
          "single source = consistent scale, shared frame. Origins are declaration metadata,",
          "marked in DECLARED.json as model knowledge, not fetched.", "", "```text"]
    for f in fields:
        so = d["fields"][f]["source_origin"]
        L.append("%-24s %s" % (f, "; ".join("%s / %s / %s" % (s["org"], s["country"], s["funding_type"])
                                             for s in so) or "no source declared"))
    L.append("%-24s %s" % ("events", "; ".join("%s / %s / %s" % (s["org"], s["country"], s["funding_type"])
                                                for s in d["events"]["source_origin"])))
    L += ["```", "", "## Provenance", "",
          "Declaration: `DECLARED.json`, committed before any table or series.",
          "Energy source: %s." % owid_source(),
          "That file is the legacy Our World in Data energy release (CC BY 4.0), built on the Energy",
          "Institute Statistical Review; its own README says it is no longer updated and that the",
          "primary-energy method has since changed. It is not copied here; only derived shares are.",
          "A current release was looked for on GitHub on 2026-11-24 and not found there; the host",
          "that carries it refused the connection.",
          "Every other source named in the declaration was not reachable from this run and nothing",
          "was typed in its place.", ""]
    with open(os.path.join(HERE, "REPORT.md"), "w") as f:
        f.write("\n".join(L))
    print("wrote REPORT.md: filled %d of %d" % (filled, len(isos) * len(fields)))


# ---------------------------------------------------------------- self-test
def selftest():
    ok = []
    ok.append(("share: importer", share_and_balance(25.0, 100.0) == (0.75, 0.6)))
    ok.append(("share: blank production is VOID, not 0", share_and_balance(None, 100.0) == (None, None)))
    ok.append(("share: zero consumption has no share", share_and_balance(10.0, 0.0)[0] is None))
    ok.append(("balance bounded for an exporter", share_and_balance(1800.0, 100.0)[1] > -1))
    # lead test, known answer: stress rises in the 3 years before each event
    rng = random.Random(1)
    hit = miss = 0
    for seed in range(20):
        r = random.Random(seed)
        stress = {y: r.gauss(0, 0.01) for y in range(1960, 2025)}
        events = sorted(r.sample(range(1970, 2024), 8))
        planted = dict(stress)
        for e in events:
            for y in range(e - 3, e):
                planted[y] += 0.05
        hit += lead_test(planted, events, seed=seed)["share_null_ge_observed"] <= 0.05
        miss += lead_test(stress, events, seed=seed)["share_null_ge_observed"] <= 0.05
    ok.append(("lead test flags a planted lead on %d of 20 seeds (need >= 18)" % hit, hit >= 18))
    ok.append(("lead test flags pure noise on %d of 20 seeds (need <= 3)" % miss, miss <= 3))
    ok.append(("lead test refuses under 3 events", lead_test({y: 0.0 for y in range(2000, 2025)}, [2010])["state"] == "NOT RUN"))
    lab = build_labels()
    ok.append(("labels table holds no functional field",
               not any(f in json.dumps(lab["countries"]) for f in declared()["fields"])))
    src = open(os.path.abspath(__file__)).read()
    body = src[src.index("def similarity("):src.index("# ------------------------------------------------------------------- output")]
    ok.append(("similarity() never names the labels table", "labels" not in body.split('"""')[2]))
    ok.append(("VOID cell carries a reason and no value", void("x") == {"value": None, "source": None, "status": "VOID", "reason": "x"}))
    for name, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", name))
    print("checks: %d   failed: %d" % (len(ok), sum(not g for _, g in ok)))
    return all(g for _, g in ok)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(0 if selftest() else 1)
    if a[0] == "tables" and len(a) == 2:
        cmd_tables(a[1])
    elif a[0] == "series" and len(a) == 2:
        cmd_series(a[1])
    elif a == ["test"]:
        cmd_test()
    elif a == ["report"]:
        cmd_report()
    elif a == ["calibrate", "2000"]:
        c = calibrate(2000)
        pv = noise_pvalues(2000)
        thr = calibrated_threshold(pv) if c["interval_excludes_nominal"] and c["above_nominal"] else 0.05
        _write("series/calibration_2000.json", {
            "record": "lead-test calibration, amendment A2", "result": c,
            "design": "as amendment A1, 2000 seeds (0..1999)",
            "step_2_applies": bool(c["interval_excludes_nominal"] and c["above_nominal"]),
            "threshold_in_force": thr,
            "alpha_at_threshold_in_force": sum(p <= thr for p in pv) / len(pv),
            "note": "threshold and its alpha are read on the same 2000 seeds (in-sample)"})
        print("threshold in force %.3f ; alpha at that threshold %.4f" % (thr, sum(p <= thr for p in pv) / len(pv)))
        print("alpha = %d / %d = %.4f   95%% interval %.4f to %.4f   excludes 0.05: %s"
              % (c["flagged"], c["seeds"], c["alpha"], c["wilson95"][0], c["wilson95"][1],
                 c["interval_excludes_nominal"]))
    elif a == ["calibrate"]:
        c = calibrate()
        _write("series/calibration.json", {"record": "lead-test calibration, amendment A1", "result": c,
                                            "design": declared()["amendments"][0]["calibration"]})
        print("alpha = %d / %d = %.3f" % (c["flagged"], c["seeds"], c["alpha"]))
    else:
        raise SystemExit(__doc__)
