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


def lead_test_tied(stress, event_years, window=3, draws=1000, seed=20261124, min_events=3):
    """Amendment A4 item 2.  Null that keeps the tie structure: k distinct event
    years with multiplicities m_1..m_k; each draw takes k distinct eligible years
    and gives them the multiplicities in random order.  A year with m events
    counts m times, in the observed statistic and in every draw.  With no shared
    year this makes the same draws as lead_test."""
    eligible = [y for y in stress if all(stress.get(k) is not None for k in range(y - window, y))]
    ev = sorted(e for e in event_years if e in eligible)
    if len(ev) < min_events:
        return {"state": "NOT RUN", "reason": "fewer than %d dated events with a full lead window (%d)"
                % (min_events, len(ev)), "n_events": len(ev)}
    distinct = sorted(set(ev))
    mult = [ev.count(y) for y in distinct]

    def stat(years):
        return sum(m * sum(stress[k] for k in range(y - window, y)) / window
                   for y, m in zip(years, mult)) / len(ev)
    obs = stat(distinct)
    rng = random.Random(seed)
    null = sorted(stat(rng.sample(eligible, len(distinct))) for _ in range(draws))
    return {"state": "RUN", "null": "tied-year (A4)", "n_events": len(ev), "n_distinct_years": len(distinct),
            "n_eligible_years": len(eligible),
            "multiplicities": mult, "observed": obs, "null_mean": sum(null) / len(null),
            "null_p05": null[int(0.05 * (len(null) - 1))], "null_p95": null[int(0.95 * (len(null) - 1))],
            "share_null_ge_observed": sum(x >= obs for x in null) / len(null),
            "effect": obs - sum(null) / len(null)}


TIED_SEEDS = range(20000, 22000)       # amendment A4 item 2
TIED_MULT = (2, 2, 1, 1, 1, 1)


def tied_noise_pvalues(seeds=TIED_SEEDS):
    """Noise stress as A1; 6 distinct event years, two of them doubled (8 events).
    Returns (p under the v1.2 null, p under the tied-year null) per seed."""
    old, new = [], []
    for seed in seeds:
        r = random.Random(seed)
        stress = {y: r.gauss(0, 0.01) for y in range(1960, 2025)}
        years = r.sample(range(1970, 2024), len(TIED_MULT))
        events = sorted(y for y, m in zip(years, TIED_MULT) for _ in range(m))
        old.append(lead_test(stress, events, seed=seed)["share_null_ge_observed"])
        new.append(lead_test_tied(stress, events, seed=seed)["share_null_ge_observed"])
    return old, new


def calibrate_tied():
    thr = _load("series/calibration_2000.json")["threshold_in_force"]
    old, new = tied_noise_pvalues()
    out = {"record": "calibration with shared-year events, amendment A4 item 2",
           "design": "noise stress as A1; 6 distinct event years from 1970..2023 with multiplicities "
                     "2,2,1,1,1,1 (8 events); seeds %d..%d" % (TIED_SEEDS[0], TIED_SEEDS[-1]),
           "v1.2_null_on_tied_events": {"at_0.05": rate(old, 0.05), "at_threshold": rate(old, thr)},
           "tied_year_null": {"at_0.05": rate(new, 0.05), "at_threshold": rate(new, thr)},
           "rule": "threshold stays for the tied-year null only if the 95% interval of its alpha at the "
                   "threshold includes a value at or below 0.05"}
    out["threshold_stays_for_tied_null"] = out["tied_year_null"]["at_threshold"]["wilson95"][0] <= 0.05
    return out


DRIVER_NOTE = ("tested driver = energy_base only; critical_minerals and chokepoints have no series (VOID), "
               "so the test does not cover those drivers")


def cmd_test13():
    """v1.3: the v1.2 countries again under the tied-year null, beside the v1.2 results as committed."""
    d = declared()["test"]
    series = _load("series/energy.json")["countries"]
    events = _load("events/events.json")["events"]
    v12 = _load("series/test_result.json")["countries"]
    cal = _load("series/calibration_tied.json")
    thr = flag_threshold() if cal["threshold_stays_for_tied_null"] else None
    res = {}
    for iso in sorted(series):
        ev = [int(e["date"][:4]) for e in events if e["iso3"] == iso]
        r = lead_test_tied(stress_changes(series[iso]), ev, d["lead_window_years"])
        r["driver_note"] = DRIVER_NOTE
        if r["state"] == "RUN":
            r["flag_threshold"] = thr
            r["flag"] = (r["share_null_ge_observed"] <= thr) if thr is not None else "NOT CALIBRATED"
            r["alpha_beside_flag"] = cal["tied_year_null"]["at_threshold"]
            r["v1.2"] = {k: v12[iso].get(k) for k in ("n_events", "observed", "null_mean", "null_p05", "null_p95",
                                                      "share_null_ge_observed", "flag")}
        res[iso] = r
    _write("series/test_result_tied.json", {"record": "lead test under the tied-year null (A4 item 2), "
                                                      "party-basis events as in v1.2", "countries": res})
    print("iso  n  distinct  v1.2 p  tied p  v1.2 null 5..95        tied null 5..95        flag")
    for iso, r in res.items():
        if r["state"] == "RUN":
            o = r["v1.2"]
            print("%s %3d %5d     %.3f   %.3f   %+.4f..%+.4f   %+.4f..%+.4f   %s"
                  % (iso, r["n_events"], r["n_distinct_years"], o["share_null_ge_observed"],
                     r["share_null_ge_observed"], o["null_p05"], o["null_p95"], r["null_p05"], r["null_p95"],
                     r["flag"]))
        else:
            print(iso, r["state"], r["reason"])
    return res


def load_events():
    """{basis: [events]} for the two UCDP bases of amendment A4 item 3."""
    e = _load("events/events.json")
    return {"party": e.get("events", []), "location": e.get("events_location", [])}


def cmd_test_basis():
    """A4 item 3: both UCDP bases, tied-year null, v1.2 null beside it."""
    d = declared()["test"]
    series = _load("series/energy.json")["countries"]
    ev_all = load_events()
    cal = _load("series/calibration_tied.json")
    thr = flag_threshold() if cal["threshold_stays_for_tied_null"] else None
    res = {}
    for iso in sorted(series):
        st = stress_changes(series[iso])
        res[iso] = {"driver_note": DRIVER_NOTE}
        for basis in ("party", "location"):
            ev = [int(e["date"][:4]) for e in ev_all[basis] if e["iso3"] == iso]
            r = lead_test_tied(st, ev, d["lead_window_years"])
            r["n_events_in_file"] = len(ev)
            if r["state"] == "RUN":
                r["flag_threshold"] = thr
                r["flag"] = (r["share_null_ge_observed"] <= thr) if thr is not None else "NOT CALIBRATED"
                r["alpha_beside_flag"] = cal["tied_year_null"]["at_threshold"]
                if r["n_events"] > r["n_eligible_years"]:
                    r["v1.2_null_beside"] = {"state": "NOT COMPUTABLE", "reason": "more events (%d) than eligible "
                                             "years (%d): the v1.2 null cannot draw that many distinct years"
                                             % (r["n_events"], r["n_eligible_years"])}
                else:
                    o = lead_test(st, ev, d["lead_window_years"])
                    r["v1.2_null_beside"] = {k: o[k] for k in ("null_p05", "null_p95", "share_null_ge_observed")}
                r["years_free_in_null"] = r["n_eligible_years"] - r["n_distinct_years"]
            res[iso][basis] = r
    _write("series/test_result_basis.json", {
        "record": "lead test on both UCDP bases (A4 item 3), tied-year null",
        "run_rule": "a country-basis runs with at least 3 events with a full lead window; a country is "
                    "listed as tested if either basis runs", "countries": res})
    print("iso  basis     in file  full window  distinct  eligible  tied p  v1.2-null p  flag")
    for iso, rr in res.items():
        for basis in ("party", "location"):
            r = rr[basis]
            if r["state"] == "RUN":
                o = r["v1.2_null_beside"].get("share_null_ge_observed")
                print("%s  %-8s %7d %11d %9d %9d   %.3f   %-11s  %s"
                      % (iso, basis, r["n_events_in_file"], r["n_events"], r["n_distinct_years"],
                         r["n_eligible_years"], r["share_null_ge_observed"],
                         "%.3f" % o if o is not None else "not comput.", r["flag"]))
            else:
                print("%s  %-8s %7d %11d   NOT RUN (fewer than 3)" % (iso, basis, r["n_events_in_file"], r["n_events"]))
    return res


def noise_pvalues(seeds):
    """seeds: a count (seeds 0..n-1, as A1 and A2) or an iterable of seeds (A4)."""
    out = []
    for seed in (range(seeds) if isinstance(seeds, int) else seeds):
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
    once series/calibration_2000.json records it (amendment A2).  Amendment A4:
    if the fresh-seed check withdrew it, None (no threshold in force)."""
    try:
        fresh = _load("series/calibration_fresh.json")
        if not fresh["threshold_stays"]:
            return None
    except (IOError, OSError, KeyError):
        pass
    try:
        return _load("series/calibration_2000.json")["threshold_in_force"]
    except (IOError, OSError, KeyError):
        return 0.05


def wilson(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return [round(centre - half, 4), round(centre + half, 4)]


def rate(pvals, thr):
    k = sum(p <= thr for p in pvals)
    return {"threshold": thr, "flagged": k, "seeds": len(pvals), "alpha": k / len(pvals),
            "wilson95": wilson(k, len(pvals))}


FRESH_SEEDS = range(10000, 12000)      # amendment A4 item 1; A1 used 0..199, A2 0..1999


def calibrate_fresh():
    thr = _load("series/calibration_2000.json")["threshold_in_force"]
    pv = noise_pvalues(FRESH_SEEDS)
    at = rate(pv, thr)
    return {"record": "fresh-seed check of the threshold in force, amendment A4 item 1",
            "design": "as amendment A1; seeds %d..%d, none used before" % (FRESH_SEEDS[0], FRESH_SEEDS[-1]),
            "at_threshold": at, "at_0.05": rate(pv, 0.05),
            "rule": "threshold stays only if the 95% interval of alpha at the threshold includes a value "
                    "at or below 0.05 (lower bound <= 0.05)",
            "threshold_stays": at["wilson95"][0] <= 0.05}


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
    thr = flag_threshold()
    c2 = _load("series/calibration_2000.json")
    alpha = {"at_threshold_in_force": c2["alpha_at_threshold_in_force"], "threshold_in_force": thr,
             "at_0.05_on_2000_seeds": c2["result"]["alpha"], "wilson95_on_2000_seeds": c2["result"]["wilson95"],
             "at_0.05_on_200_seeds": _load("series/calibration.json")["result"]["alpha"],
             "note": c2["note"]}
    res = {}
    for iso in sorted(series):
        ev = [int(e["date"][:4]) for e in events if e["iso3"] == iso]
        r = lead_test(stress_changes(series[iso]), ev, d["lead_window_years"])
        r["n_events_in_file"] = len(ev)
        if r["state"] == "RUN":
            st = stress_changes(series[iso])
            used = sorted(e for e in ev if all(st.get(k) is not None for k in range(e - 3, e)) and e in st)
            r["event_years_used"] = used
            r["events_sharing_a_year"] = len(used) - len(set(used))
            r["flag_threshold"] = thr
            r["flag"] = r["share_null_ge_observed"] <= thr
            r["alpha_beside_flag"] = alpha
        res[iso] = r
    _write("series/test_result.json", {"record": "lead test, as declared", "declared": d, "countries": res})
    for iso, r in res.items():
        print(iso, r["state"], r.get("reason", "") or "n %d p %.3f flag %s (threshold %.3f, alpha %.4f)"
              % (r["n_events"], r["share_null_ge_observed"], r["flag"], thr, alpha["at_threshold_in_force"]))
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
          "A filled cell can still hold VOID parts (one source read, another not). Sources per",
          "filled field, with the parts left VOID:", "", "```text"]
    for f in fields:
        parts = {}
        for i in isos:
            c = fn["countries"][i][f]
            if c["status"] != "VOID" and isinstance(c.get("value"), dict):
                for k, v in c["value"].items():
                    if isinstance(v, dict) and "status" in v:
                        parts.setdefault(k, []).append(i if v["status"] != "VOID" else None)
        for k, got in parts.items():
            n = sum(g is not None for g in got)
            L.append("%-24s %-22s filled for %d of %d filled countries" % (f, k, n, len(got)))
    L += ["```", "", "VOID reasons, per field (countries sharing a reason are grouped):", "", "```text"]
    for f in fields:
        rs = {}
        for i in isos:
            if fn["countries"][i][f]["status"] == "VOID":
                rs.setdefault(fn["countries"][i][f]["reason"], []).append(i)
        for reason, who in rs.items():
            L.append("%-24s [%s] %s" % (f, " ".join(who), reason))
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
          "A distance is declared only for energy_base; the fields filled since hold quoted text,",
          "an index score or one mineral ratio and have no declared distance, so they do not enter.",
          "Every number below is energy-balance similarity and nothing else. It is not a country",
          "similarity.", "", "```text", "      " + "    ".join(isos)]
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
    ev = _load("events/events.json")
    c2 = _load("series/calibration_2000.json")
    L += ["```", "", "Events: UCDP conflict episode starts and one-sided-violence run starts, as declared in",
          "amendment A3. Policy events stay VOID. Events in the file, and events with a full 3-year",
          "lead window in the energy series:", "", "```text"]
    for i in isos:
        r = test[i]
        L.append("%-5s in file %3d   with full lead window %3d%s"
                 % (i, r.get("n_events_in_file", 0), r["n_events"],
                    "   (%d share a year with another event)" % r["events_sharing_a_year"]
                    if r.get("events_sharing_a_year") else ""))
    L += ["```", "", "Flags, each with the calibrated alpha beside it. A flag is share null >= observed at or",
          "below the threshold in force. It is a reading of this one test, not a finding about a country.",
          "", "```text"]
    ran = [i for i in isos if test[i]["state"] == "RUN"]
    for i in ran:
        r = test[i]
        a = r["alpha_beside_flag"]
        L.append("%-5s p %.3f  flag %-5s  threshold %.3f  alpha at threshold %.4f (in-sample, 2000 noise seeds)"
                 % (i, r["share_null_ge_observed"], "yes" if r["flag"] else "no", r["flag_threshold"],
                    a["at_threshold_in_force"]))
    if not ran:
        L.append("no country ran")
    L += ["```", "",
          "%d countries ran, %d flagged. With %d tests at alpha %.4f each, about %.2f flags are expected"
          % (len(ran), sum(test[i]["flag"] for i in ran), len(ran), c2["alpha_at_threshold_in_force"],
             len(ran) * c2["alpha_at_threshold_in_force"]),
          "from noise alone. No pooled verdict is made.",
          "", "Limits of this run: the null redraws distinct years, while a country's events can share a",
          "year (counts above); the calibration did not cover that case. The stress series is energy",
          "only. Conflict events only.",
          "", "Calibration: amendment A1, %d pure-noise seeds, flagged %d at 0.05, alpha = %.3f (95%% interval"
          % (cal["seeds"], cal["flagged"], cal["alpha"]),
          "%.3f to %.3f). Amendment A2 step 1, %d seeds: flagged %d, alpha = %.4f (95%% interval %.4f to"
          % (cal["wilson95"][0], cal["wilson95"][1], c2["result"]["seeds"], c2["result"]["flagged"],
             c2["result"]["alpha"], c2["result"]["wilson95"][0]),
          "%.4f); the interval excludes 0.05, so A2 step 2 applies: threshold in force %.3f, alpha at"
          % (c2["result"]["wilson95"][1], c2["threshold_in_force"]),
          "that threshold %.4f, read on the same 2000 seeds." % c2["alpha_at_threshold_in_force"],
          "", "## Source origin", "",
          "single source = consistent scale, shared frame. VERIFIED = read from the org's own page",
          "(URL, fetch time and quote in DECLARED.json). NOT_VERIFIED = host not reachable; the entry",
          "is model knowledge, flagged.", "", "```text"]
    a3 = [a for a in d["amendments"] if a["id"] == "A3"][0]
    def _so(name, so):
        for s in so:
            L.append("%-24s %-12s %s / %s / %s" % (name, s.get("status", "NOT_VERIFIED"), s["org"], s["country"],
                                                    s["funding_type"]))
            if s.get("differs_from_declared", "no")[:2] != "no":
                L.append("%-24s %-12s differs: %s" % ("", "", s["differs_from_declared"]))
    for f in fields:
        if d["fields"][f]["source_origin"]:
            _so(f, d["fields"][f]["source_origin"])
        else:
            L.append("%-24s no source declared" % f)
    for k in ("v-dem", "bgs", "ucdp"):
        _so("A3 " + k, a3["sources"][k]["source_origin"])
    L += ["```", "", "## Provenance", "",
          "Declaration: `DECLARED.json`, committed before any table or series.",
          "Energy source: %s." % owid_source(),
          "That file is the legacy Our World in Data energy release (CC BY 4.0), built on the Energy",
          "Institute Statistical Review; its own README says it is no longer updated and that the",
          "primary-energy method has since changed. It is not copied here; only derived shares are.",
          "A current release was looked for on GitHub on 2026-11-24 and not found there; the host",
          "that carries it refused the connection.",
          "Filled since (amendment A3, `fill.py`): RSF, Constitute, UCDP and BGS, each with URL, fetch",
          "time and sha256 in `series/fill_sources.json`. Their files are not copied here. Those cells",
          "carry the sources' own terms (Constitute CC BY-NC 3.0; UCDP CC BY 4.0; BGS copyright NERC,",
          "non-commercial research use; RSF terms not stated on the page read); CC0 covers the",
          "structure and the code. V-Dem and CPJ were not read; the reasons are in the VOID cells.",
          "Every source not reachable from this run stays VOID and nothing was typed in its place.", ""]
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
    # tied-year null: with no shared year it is the v1.2 null, draw for draw
    rr = random.Random(5)
    st = {y: rr.gauss(0, 0.01) for y in range(1960, 2025)}
    e0 = [1975, 1988, 1999, 2010]
    t0, t1 = lead_test(st, e0), lead_test_tied(st, e0)
    ok.append(("tied null = v1.2 null when no year is shared",
               abs(t0["share_null_ge_observed"] - t1["share_null_ge_observed"]) < 1e-12
               and abs(t0["null_p95"] - t1["null_p95"]) < 1e-12))
    e1 = [1975, 1975, 1988, 1999]
    t2 = lead_test_tied(st, e1)
    w = lambda y: sum(st[k] for k in range(y - 3, y)) / 3
    ok.append(("tied null: a year with 2 events counts twice",
               abs(t2["observed"] - (2 * w(1975) + w(1988) + w(1999)) / 4) < 1e-15
               and t2["multiplicities"] == [2, 1, 1] and t2["n_distinct_years"] == 3))
    ok.append(("wilson interval, known answer 50/100", wilson(50, 100) == [0.4038, 0.5962]))
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
    elif a == ["calibrate", "tied"]:
        c = calibrate_tied()
        _write("series/calibration_tied.json", c)
        for name in ("v1.2_null_on_tied_events", "tied_year_null"):
            for k in ("at_0.05", "at_threshold"):
                r = c[name][k]
                print("%-26s threshold %.3f: flagged %3d / %d  alpha %.4f  95%% interval %.4f to %.4f"
                      % (name, r["threshold"], r["flagged"], r["seeds"], r["alpha"], r["wilson95"][0],
                         r["wilson95"][1]))
        print("threshold stays for tied null:", c["threshold_stays_for_tied_null"])
    elif a == ["testbasis"]:
        cmd_test_basis()
    elif a == ["test13"]:
        cmd_test13()
    elif a == ["calibrate", "fresh"]:
        c = calibrate_fresh()
        _write("series/calibration_fresh.json", c)
        for k in ("at_threshold", "at_0.05"):
            r = c[k]
            print("threshold %.3f: flagged %d / %d  alpha %.4f  95%% interval %.4f to %.4f"
                  % (r["threshold"], r["flagged"], r["seeds"], r["alpha"], r["wilson95"][0], r["wilson95"][1]))
        print("threshold stays:", c["threshold_stays"])
    elif a == ["calibrate"]:
        c = calibrate()
        _write("series/calibration.json", {"record": "lead-test calibration, amendment A1", "result": c,
                                            "design": declared()["amendments"][0]["calibration"]})
        print("alpha = %d / %d = %.3f" % (c["flagged"], c["seeds"], c["alpha"]))
    else:
        raise SystemExit(__doc__)
