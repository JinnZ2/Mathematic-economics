"""
claim_ledger.py  -- CC0, stdlib-only

Metrological skin + self-falsifying claim registry for the
ringwoodite -> earth-systems coupling model.

Every quantity that crosses a module boundary must carry a unit and a
sanity range, or it is rejected. Every claim must carry a falsifier and an
evidence_class, or it is rejected. This is upstream of the physics: a model
that cannot state what would prove it wrong is not a model, it is a story.

evidence_class:
  MEASURED    -- direct lab / field measurement (mineral physics, seismology)
  DERIVED     -- computed from MEASURED inputs via stated equations
  SPECULATIVE -- coupling hypothesis; the part that earns the falsifier
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import math


class Evidence(str, Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    SPECULATIVE = "SPECULATIVE"


class Status(str, Enum):
    OPEN = "OPEN"            # not yet tested against data
    SUPPORTED = "SUPPORTED"  # passed its falsifier with current data
    FALSIFIED = "FALSIFIED"  # failed its falsifier


@dataclass
class Quantity:
    """A number that is not allowed to travel naked."""
    value: float
    unit: str
    lo: float          # sanity range low (same unit)
    hi: float          # sanity range high (same unit)

    def __post_init__(self):
        if not self.unit or self.unit.strip() == "":
            raise ValueError("Quantity rejected: missing unit (metrological skin).")
        if not (self.lo <= self.hi):
            raise ValueError(f"Quantity rejected: bad range [{self.lo},{self.hi}].")

    def in_range(self) -> bool:
        return self.lo <= self.value <= self.hi

    def assert_sane(self, name: str = "quantity"):
        if not self.in_range():
            raise ValueError(
                f"{name} = {self.value} {self.unit} outside sanity "
                f"[{self.lo},{self.hi}] {self.unit}"
            )
        return self.value


@dataclass
class Claim:
    cid: str
    statement: str
    evidence: Evidence
    unit: str                       # unit of the predicted observable
    sanity: tuple                   # (lo, hi) in `unit`
    falsifier: str                  # observation that would kill this claim
    references: list = field(default_factory=list)
    status: Status = Status.OPEN
    note: str = ""

    def __post_init__(self):
        if not self.falsifier.strip():
            raise ValueError(f"Claim {self.cid} rejected: no falsifier.")
        if not self.unit.strip():
            raise ValueError(f"Claim {self.cid} rejected: no unit.")


LEDGER = [
    Claim(
        cid="RW-01",
        statement="Ringwoodite stores 0-3 wt% structural water across the "
                  "lower transition zone (~525-660 km, ~18-23 GPa).",
        evidence=Evidence.MEASURED,
        unit="wt_percent_H2O",
        sanity=(0.0, 3.0),
        falsifier="Hydrous ringwoodite inclusions / electrical conductivity "
                  "show storage capacity outside 0-3 wt% under TZ P-T.",
        references=["Pearson et al. 2014 (diamond inclusion, ~1.4 wt%)",
                    "Schmandt et al. 2014 (dehydration melting atop 660)"],
        status=Status.SUPPORTED,
    ),
    Claim(
        cid="RW-02",
        statement="Hydrous ringwoodite descending across the 660 km boundary "
                  "(rw -> bridgmanite + ferropericlase) sheds water because "
                  "the lower-mantle assemblage stores far less.",
        evidence=Evidence.MEASURED,
        unit="kg_H2O_per_kg_rock",
        sanity=(0.0, 0.03),
        falsifier="Lower-mantle phases shown to retain ~rw-level water, "
                  "erasing the dehydration contrast at 660.",
        references=["Schmandt et al. 2014"],
        status=Status.SUPPORTED,
    ),
    Claim(
        cid="CPL-01",
        statement="Mantle water content lowers effective viscosity "
                  "(hydrolytic weakening), modulating heat delivered to the base "
                  "of the crust on >10 kyr timescales.",
        evidence=Evidence.DERIVED,
        unit="dimensionless_log10_eta_drop_per_wt_percent",
        sanity=(0.5, 2.5),
        falsifier="Olivine/ringwoodite rheology shows <0.5 decade viscosity "
                  "drop per wt% water at TZ conditions.",
        references=["Mei & Kohlstedt 2000 (hydrolytic weakening)"],
        status=Status.OPEN,
    ),
    Claim(
        cid="CPL-02",
        statement="Deep-water boundary state sets a SLOW background sensitivity; "
                  "it does NOT trigger human-timescale floods directly. "
                  "Mantle overturn ~1e8-1e9 yr >> narrative window ~1e4-1e5 yr.",
        evidence=Evidence.DERIVED,
        unit="years_mantle_overturn",
        sanity=(1.0e8, 2.0e9),
        falsifier="Demonstrated regional deep-water pulse with surface "
                  "expression on <1e4 yr timescale.",
        references=["whole-mantle convection overturn estimates"],
        status=Status.SUPPORTED,
        note="This is the honesty spine. Ringwoodite is the dimmer switch, "
             "not the trigger. The trigger is fast forcing on a sensitive base.",
    ),
    Claim(
        cid="EVT-01",
        statement="Surface water-emergence/flood events cluster where FAST "
                  "forcings (orbital insolation, glacial unloading, solar, "
                  "Chandler/annual wobble) constructively align ON TOP OF a "
                  "high deep-water sensitivity baseline.",
        evidence=Evidence.SPECULATIVE,
        unit="event_probability",
        sanity=(0.0, 1.0),
        falsifier="Adding the deep-water baseline term does NOT improve "
                  "hit-rate of predicted windows vs fast-forcing-only model "
                  "above a random-shuffle baseline.",
        references=[],
        status=Status.OPEN,
        note="The whole model lives or dies here. If the baseline term is "
             "inert, drop it and keep the fast-forcing model.",
    ),
    Claim(
        cid="NAR-01",
        statement="Geographic/temporal clustering of flood & island-subsidence "
                  "narratives correlates with predicted high-probability windows "
                  "better than chance.",
        evidence=Evidence.SPECULATIVE,
        unit="hit_rate_minus_random",
        sanity=(-1.0, 1.0),
        falsifier="Narrative-cluster dates show no excess overlap with "
                  "predicted windows beyond a Monte-Carlo shuffle null.",
        references=[],
        status=Status.OPEN,
        note="Requires a real, dated narrative dataset. Placeholder shipped.",
    ),
    Claim(
        cid="AQ-01",
        statement="Coseismic / crustal-stress change drives pore-pressure "
                  "change in saturated aquifers via undrained poroelastic "
                  "(Skempton) coupling, dp = B * d_sigma_mean.",
        evidence=Evidence.MEASURED,
        unit="Pa_pore_pressure_change",
        sanity=(0.0, 5.0e6),
        falsifier="Observed water-level/spring response to known coseismic "
                  "strain departs from poroelastic prediction with B in 0.4-0.9.",
        references=["Skempton 1954", "Roeloffs 1996", "Manga & Wang 2010"],
        status=Status.SUPPORTED,
    ),
    Claim(
        cid="AQ-02",
        statement="Liquefaction / forced upwelling ('water from the ground') "
                  "occurs above a seismic-energy-density threshold "
                  "(~0.1 J/m^3); milder hydrologic response (spring/level) "
                  "extends to ~1e-3 J/m^3. e(M,r) per Wang 2007.",
        evidence=Evidence.MEASURED,
        unit="J_per_m3_energy_density",
        sanity=(1.0e-4, 1.0e4),
        falsifier="Documented liquefaction at e well below 1e-2 J/m^3, or "
                  "no liquefaction well above 1 J/m^3 in saturated loose soil.",
        references=["Wang 2007 GRL (seismic energy density)",
                    "Wang & Manga 2010"],
        status=Status.SUPPORTED,
    ),
    Claim(
        cid="AQ-03",
        statement="A primed deep-water baseline (low effective stress / "
                  "pre-overpressured aquifers) lowers the energy-density "
                  "threshold for forced emergence, linking the SLOW mantle "
                  "state to FAST seismic triggering.",
        evidence=Evidence.SPECULATIVE,
        unit="dimensionless_threshold_scale",
        sanity=(0.3, 1.0),
        falsifier="Sites over high-sensitivity zones show no lower emergence "
                  "threshold than matched control sites at equal M and r.",
        references=[],
        status=Status.OPEN,
        note="The bridge between the mantle model and the seismic mechanism.",
    ),
    Claim(
        cid="SYN-01",
        statement="Emergence narratives in disconnected cultures co-date with "
                  "regional paleoseismic markers (turbidites, liquefaction "
                  "features, tsunami deposits) better than chance.",
        evidence=Evidence.SPECULATIVE,
        unit="hit_rate_minus_random",
        sanity=(-1.0, 1.0),
        falsifier="Emergence-narrative dates show no excess overlap with "
                  "paleoseismic-marker dates beyond a shuffle null.",
        references=[],
        status=Status.OPEN,
        note="Each region triggers LOCALLY. Apparent cross-continental "
             "synchrony is a SEPARATE claim (SYN-02): test it against dating "
             "resolution and a Poisson clustering null before believing it.",
    ),
    Claim(
        cid="SYN-02",
        statement="Cross-continental TEMPORAL synchrony of emergence events "
                  "exceeds what independent regional seismicity produces by "
                  "chance (i.e. there is a common pacing, not coincidence).",
        evidence=Evidence.SPECULATIVE,
        unit="synchrony_excess_over_poisson",
        sanity=(-1.0, 1.0),
        falsifier="Observed cross-region clustering is consistent with "
                  "independent Poisson seismicity once dating uncertainty is "
                  "convolved in. Then synchrony is an artifact, drop it.",
        references=[],
        status=Status.OPEN,
        note="The seductive claim. Most likely to be a dating-resolution "
             "illusion. Built to be killed unless the data is overwhelming.",
    ),
]


def dump_ledger(path: str = "CLAIM_TABLE.earth.json") -> str:
    payload = []
    for c in LEDGER:
        d = asdict(c)
        d["evidence"] = c.evidence.value
        d["status"] = c.status.value
        payload.append(d)
    text = json.dumps(payload, indent=2)
    with open(path, "w") as f:
        f.write(text)
    return path


def gate(q: Quantity, name: str) -> float:
    """Boundary gate: nothing passes without a unit and an in-range value."""
    return q.assert_sane(name)


if __name__ == "__main__":
    p = dump_ledger()
    n_spec = sum(1 for c in LEDGER if c.evidence == Evidence.SPECULATIVE)
    print(f"ledger written -> {p}")
    print(f"claims: {len(LEDGER)}  speculative(load-bearing): {n_spec}")
    # demo of the skin rejecting a naked number:
    try:
        Quantity(value=5.0, unit="", lo=0, hi=10)
    except ValueError as e:
        print("skin works ->", e)
