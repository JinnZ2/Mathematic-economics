#!/usr/bin/env python3
# forensic_eroi.py
# CC0-1.0. stdlib-only. phone-buildable.
#
# a normal EROI stops at the wellhead and divides. this one refuses to.
# it walks the whole exploration funnel -- desk pre-select, aerial survey,
# seismic, land, capital machinery, rig-up, drill -- and counts the energy
# spent on every candidate that ENTERED a stage, whether or not it advanced.
# the rejected candidates are the graveyard. they consumed energy and
# produced no well, and the industry ledger does not carry them.
#
# the numbers here are DECLARED PLACEHOLDER BOUNDS. the company keeps the
# real ones dark by design. so the tool does not fake a point value -- it
# carries lo/hi bounds and marks disclosure state. the GAP between the
# reported figure and the forensic floor is the output. empty space = signal.
#
# refutation protocol: replace a bound when a real record contradicts it.
# never retune the funnel to make an EROI pass.
#
# energy_english: disclosure carried as measured state, not moral label.
#   DISCLOSED   company reports this cost
#   UNDISCLOSED structurally required, not in the books
#   INFERRED    reconstructed from adjacent records

from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class Stage:
    id: str
    does: str                # verb-first: what work happens here
    entering: int            # candidates that enter (all consume energy)
    advancing: int           # candidates that pass to next stage
    e_lo: float              # energy per entering candidate, low bound  (GJ)
    e_hi: float              # energy per entering candidate, high bound (GJ)
    counted: float           # fraction of this cost standard EROI includes 0..1
    disclosure: str          # DISCLOSED | UNDISCLOSED | INFERRED

    @property
    def rejected(self) -> int:
        return self.entering - self.advancing

    @property
    def total(self) -> Tuple[float, float]:
        return self.entering * self.e_lo, self.entering * self.e_hi

    @property
    def reported(self) -> Tuple[float, float]:
        lo, hi = self.total
        return lo * self.counted, hi * self.counted

    @property
    def opacity(self) -> float:
        return self.e_hi / self.e_lo if self.e_lo > 0 else float("inf")


def funnel_energy(funnel: List[Stage], reported_only: bool) -> Tuple[float, float]:
    lo = hi = 0.0
    for s in funnel:
        a, b = s.reported if reported_only else s.total
        lo += a
        hi += b
    return lo, hi


def failure_ledger(funnel: List[Stage]) -> dict:
    drill = funnel[-1]
    selection = sum(s.rejected for s in funnel[:-1])   # rejected before a well ever drilled
    wells = drill.rejected                              # drilled, produced nothing
    reported_failures = wells                           # what the spreadsheet admits
    true_failures = selection + wells                   # every dead node in the funnel
    return {
        "reported_failures": reported_failures,
        "true_failures": true_failures,
        "hidden_failures": true_failures - reported_failures,
        "per_stage": [(s.id, s.rejected) for s in funnel if s.rejected],
    }


def eroi_band(funnel: List[Stage], yield_lo: float, yield_hi: float) -> dict:
    producing = funnel[-1].advancing
    ret_lo, ret_hi = producing * yield_lo, producing * yield_hi

    rep_lo, rep_hi = funnel_energy(funnel, reported_only=True)
    for_lo, for_hi = funnel_energy(funnel, reported_only=False)

    def band(ret_l, ret_h, den_l, den_h):
        return (ret_l / den_h if den_h else 0.0,
                ret_h / den_l if den_l else float("inf"))

    reported = band(ret_lo, ret_hi, rep_lo, rep_hi)
    forensic = band(ret_lo, ret_hi, for_lo, for_hi)
    return {
        "producing_wells": producing,
        "returned_GJ": (round(ret_lo), round(ret_hi)),
        "reported_cost_GJ": (round(rep_lo), round(rep_hi)),
        "forensic_cost_GJ": (round(for_lo), round(for_hi)),
        "hidden_cost_GJ": (round(for_lo - rep_lo), round(for_hi - rep_hi)),
        "reported_eroi": (round(reported[0], 2), round(reported[1], 2)),
        "forensic_eroi": (round(forensic[0], 2), round(forensic[1], 2)),
    }


def forensic_markers(funnel: List[Stage], e: dict) -> Tuple[str, List[str]]:
    marks = []
    for s in funnel:
        if s.counted < 1.0 and s.total[1] > 0:
            share = round((1 - s.counted) * 100)
            marks.append(f"disclosure_gap  {s.id:<14} {share}% of cost uncounted "
                         f"[{s.disclosure}]")
        if s.disclosure == "UNDISCLOSED" and s.opacity > 3:
            marks.append(f"opacity_flag    {s.id:<14} bound spread x{s.opacity:.1f} "
                         f"-- undisclosed by design")

    reported_floor = e["reported_eroi"][0]
    reported_best = e["reported_eroi"][1]
    forensic_floor = e["forensic_eroi"][0]

    if forensic_floor < 1.0 and reported_best >= 5.0:
        verdict = "ENERGY_SINK_HIDDEN"     # reported profitable, forensic floor is a sink
    elif any(m.startswith("disclosure_gap") for m in marks):
        verdict = "DISCLOSURE_GAP"          # cost structurally present, not carried
    else:
        verdict = "TRACES_CLEAN"
    return verdict, marks


def report(name: str, funnel: List[Stage], yield_lo: float, yield_hi: float) -> str:
    e = eroi_band(funnel, yield_lo, yield_hi)
    f = failure_ledger(funnel)
    verdict, marks = forensic_markers(funnel, e)
    L = [
        "=" * 64,
        f"{name}",
        "=" * 64,
        f"producing wells      {e['producing_wells']}",
        f"energy returned      {e['returned_GJ'][0]:,} .. {e['returned_GJ'][1]:,} GJ",
        "",
        f"reported cost        {e['reported_cost_GJ'][0]:,} .. {e['reported_cost_GJ'][1]:,} GJ   (wellhead ledger)",
        f"forensic cost        {e['forensic_cost_GJ'][0]:,} .. {e['forensic_cost_GJ'][1]:,} GJ   (full funnel)",
        f"hidden cost          {e['hidden_cost_GJ'][0]:,} .. {e['hidden_cost_GJ'][1]:,} GJ   (never on the books)",
        "",
        f"reported EROI        {e['reported_eroi'][0]} .. {e['reported_eroi'][1]}   <- the story",
        f"forensic EROI        {e['forensic_eroi'][0]} .. {e['forensic_eroi'][1]}   <- the floor",
        "",
        f"failures reported    {f['reported_failures']}   (dry / collapsed wells)",
        f"failures actual      {f['true_failures']}   (+{f['hidden_failures']} rejected before a well ever drilled)",
        f"  per stage          " + ", ".join(f"{sid}:{n}" for sid, n in f["per_stage"]),
        "",
        f"VERDICT              {verdict}",
    ]
    for m in marks:
        L.append(f"  {m}")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# funnel: 500 candidate basins in, 12 producing wells out.
# every `entering` count consumed that stage's energy. bounds are placeholders
# to be replaced from real records; the STRUCTURE is the deliverable.
# ---------------------------------------------------------------------------

CONVENTIONAL: List[Stage] = [
    Stage("desk_preselect", "screen basins on desk + compute",
          entering=500, advancing=120, e_lo=50,     e_hi=300,    counted=0.0, disclosure="UNDISCLOSED"),
    Stage("aerial_survey",  "fly and image candidates",
          entering=120, advancing=60,  e_lo=800,    e_hi=3000,   counted=0.0, disclosure="UNDISCLOSED"),
    Stage("seismic_survey", "sound the ground, echolocate",
          entering=60,  advancing=30,  e_lo=5000,   e_hi=20000,  counted=0.1, disclosure="INFERRED"),
    Stage("land_acquire",   "acquire rights, run legal",
          entering=30,  advancing=25,  e_lo=2000,   e_hi=15000,  counted=0.0, disclosure="UNDISCLOSED"),
    Stage("capital_stage",  "accumulate capital, hold positions",
          entering=25,  advancing=25,  e_lo=3000,   e_hi=30000,  counted=0.0, disclosure="UNDISCLOSED"),
    Stage("rig_stage",      "mobilize and stage rigs",
          entering=25,  advancing=18,  e_lo=20000,  e_hi=60000,  counted=0.5, disclosure="INFERRED"),
    Stage("drill_stage",    "drill and complete",
          entering=18,  advancing=12,  e_lo=150000, e_hi=400000, counted=1.0, disclosure="DISCLOSED"),
]

# laundered play: the visible ledger is kept small and cheap (low drill cost,
# high claimed yield) so the reported EROI looks excellent -- while the true
# cost is dumped into uncounted upstream stages. reported story is clean,
# forensic floor is a sink. this is the pattern the tool exists to catch.
LAUNDERED: List[Stage] = [
    Stage("desk_preselect", "screen basins on desk + compute",
          entering=500, advancing=120, e_lo=50,      e_hi=300,     counted=0.0, disclosure="UNDISCLOSED"),
    Stage("aerial_survey",  "fly and image candidates",
          entering=120, advancing=60,  e_lo=800,     e_hi=3000,    counted=0.0, disclosure="UNDISCLOSED"),
    Stage("seismic_survey", "sound the ground, echolocate",
          entering=60,  advancing=30,  e_lo=5000,    e_hi=20000,   counted=0.1, disclosure="INFERRED"),
    Stage("land_acquire",   "acquire rights, run legal",
          entering=30,  advancing=25,  e_lo=10000,   e_hi=80000,   counted=0.0, disclosure="UNDISCLOSED"),
    Stage("capital_stage",  "accumulate capital, hold positions",
          entering=25,  advancing=25,  e_lo=500000,  e_hi=3000000, counted=0.0, disclosure="UNDISCLOSED"),
    Stage("rig_stage",      "mobilize and stage rigs",
          entering=25,  advancing=18,  e_lo=30000,   e_hi=90000,   counted=0.3, disclosure="INFERRED"),
    Stage("drill_stage",    "drill and complete",
          entering=18,  advancing=12,  e_lo=80000,   e_hi=150000,  counted=1.0, disclosure="DISCLOSED"),
]

if __name__ == "__main__":
    # conventional: well yields 1.5M .. 4M GJ over life
    print(report("CONVENTIONAL PLAY", CONVENTIONAL, yield_lo=1_500_000, yield_hi=4_000_000))
    print()
    # laundered: high claimed yield 1M .. 3M GJ, cheap visible drill, huge hidden capital
    print(report("LAUNDERED PLAY", LAUNDERED, yield_lo=1_000_000, yield_hi=3_000_000))
