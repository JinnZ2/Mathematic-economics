#!/usr/bin/env python3
# electron_accounting.py — TAF add-on module
# CC0 1.0 Universal. No rights reserved.
#
# Sits BESIDE atomicaccounting, resolves BELOW it.
# Dormant by default (lazy layer). Activates only when an energy
# or quantum-precision load demands per-carrier granularity.
#
# Why electron, not atom, as the bridge unit:
#   same conserved carrier in classical drift current and in
#   quantum tunneling — ledger crosses the boundary with no
#   unit change. Atomic tops out before the boundary.
#
# stdlib-only. phone-buildable. run: python3 electron_accounting.py

import json
import time

# ---------------------------------------------------------------
# constants (CODATA exact, SI 2019 redefinition)
# ---------------------------------------------------------------
E_CHARGE = 1.602176634e-19      # C per electron (exact)
AVOGADRO = 6.02214076e23        # per mol (exact)
FARADAY = E_CHARGE * AVOGADRO   # C per mol electrons (derived, exact)

JOULE_PER_EV = E_CHARGE         # numerically identical, semantically distinct

# ---------------------------------------------------------------
# CLAIM_TABLE — falsifiable. refute -> update claim, never retune.
# ---------------------------------------------------------------
CLAIM_TABLE = [
    {
        "id": "EA-1",
        "claim": "electron count closes in every ledger window: "
                 "sum(in) - sum(out) - sum(stored) == 0 within tolerance",
        "test": "Ledger.close_window()",
        "refuted_by": "nonzero residual exceeding tolerance on real data",
        "status": "open",
    },
    {
        "id": "EA-2",
        "claim": "atomic-layer energy entries resolve to electron entries "
                 "with no information loss (round-trip within tolerance)",
        "test": "resolve_down() then roll_up() round-trip",
        "refuted_by": "round-trip residual exceeding tolerance",
        "status": "open",
    },
    {
        "id": "EA-3",
        "claim": "dormant carrying cost is near zero: module imported but "
                 "inactive performs no per-carrier work",
        "test": "Ledger(active=False).post() defers resolution",
        "refuted_by": "measured work scaling with entry count while inactive",
        "status": "open",
    },
    {
        "id": "EA-4",
        "claim": "the ledger grammar is valid unchanged at quantum "
                 "granularity (per-carrier, per-event posting)",
        "test": "quantum_hook posting path (stub — not yet built)",
        "refuted_by": "any quantum posting requiring a unit change",
        "status": "stub",
    },
]

TOLERANCE = 1e-9  # relative residual tolerance for window closure


# ---------------------------------------------------------------
# unit moves — verb-first, no stored verdicts
# ---------------------------------------------------------------
def coulombs_to_electrons(coulombs):
    return coulombs / E_CHARGE

def electrons_to_coulombs(n_electrons):
    return n_electrons * E_CHARGE

def amps_to_electron_rate(amps):
    """A -> electrons per second."""
    return amps / E_CHARGE

def mol_e_to_electrons(mol_e):
    return mol_e * AVOGADRO

def joules_to_ev(joules):
    return joules / JOULE_PER_EV


# ---------------------------------------------------------------
# ledger
# ---------------------------------------------------------------
class Ledger:
    """Electron-count ledger. Posts flows, closes windows on
    charge conservation. Output is trajectory (window residual
    series), not a stored verdict."""

    def __init__(self, active=False, tolerance=TOLERANCE):
        self.active = active          # dormant by default
        self.tolerance = tolerance
        self.entries = []             # raw postings, always cheap
        self.residual_trajectory = [] # per-window residuals over time

    def post(self, direction, n_electrons, source, t=None):
        """direction: 'in' | 'out' | 'stored'
        Posting is always allowed and always cheap. Resolution to
        per-carrier work happens only at close_window when active."""
        if direction not in ("in", "out", "stored"):
            raise ValueError("direction must be in|out|stored")
        self.entries.append({
            "t": t if t is not None else time.time(),
            "dir": direction,
            "n_e": float(n_electrons),
            "src": source,
        })

    def close_window(self):
        """Close current window: conservation check.
        Returns residual and appends to trajectory. Clears entries."""
        s_in = sum(e["n_e"] for e in self.entries if e["dir"] == "in")
        s_out = sum(e["n_e"] for e in self.entries if e["dir"] == "out")
        s_sto = sum(e["n_e"] for e in self.entries if e["dir"] == "stored")
        residual = s_in - s_out - s_sto
        scale = max(abs(s_in), abs(s_out), abs(s_sto), 1.0)
        rel = residual / scale
        record = {
            "t": time.time(),
            "in": s_in, "out": s_out, "stored": s_sto,
            "residual": residual,
            "rel_residual": rel,
            "closes": abs(rel) <= self.tolerance,
        }
        self.residual_trajectory.append(record)
        self.entries = []
        return record


# ---------------------------------------------------------------
# bridge: atomic layer <-> electron layer
# ---------------------------------------------------------------
def resolve_down(atomic_entry):
    """Atomic-layer energy entry -> electron-layer posting.
    atomic_entry: {"energy_j": float, "volts": float, "dir": str, "src": str}
    Only call when the load demands it (lazy layer)."""
    q = atomic_entry["energy_j"] / atomic_entry["volts"]  # C
    return {
        "dir": atomic_entry["dir"],
        "n_e": coulombs_to_electrons(q),
        "src": atomic_entry["src"],
        "volts": atomic_entry["volts"],
    }

def roll_up(electron_entry):
    """Electron-layer posting -> atomic-layer energy entry.
    Round-trip partner of resolve_down for claim EA-2."""
    q = electrons_to_coulombs(electron_entry["n_e"])
    return {
        "energy_j": q * electron_entry["volts"],
        "volts": electron_entry["volts"],
        "dir": electron_entry["dir"],
        "src": electron_entry["src"],
    }

def quantum_hook(event):
    """STUB (claim EA-4). Per-carrier, per-event posting path for
    quantum loads (tunneling counts, single-carrier devices).
    Grammar must hold unchanged: dir, n_e, src. n_e may be 1."""
    raise NotImplementedError("build when a quantum load arrives")


# ---------------------------------------------------------------
# self-test — one-finger runnable
# ---------------------------------------------------------------
def _selftest():
    out = {}

    # EA-1: window closes on synthetic balanced flow
    led = Ledger(active=True)
    led.post("in", 1.0e20, "grid_feed")
    led.post("out", 6.0e19, "traction_load")
    led.post("stored", 4.0e19, "pack")
    w = led.close_window()
    out["EA-1_closes"] = w["closes"]
    out["EA-1_rel_residual"] = w["rel_residual"]

    # EA-2: resolve_down / roll_up round-trip
    a = {"energy_j": 3.6e6, "volts": 400.0, "dir": "in", "src": "charger"}
    rt = roll_up(resolve_down(a))
    rel = abs(rt["energy_j"] - a["energy_j"]) / a["energy_j"]
    out["EA-2_roundtrip_rel"] = rel
    out["EA-2_closes"] = rel <= TOLERANCE

    # EA-3: dormant posting stays cheap (structural check only here;
    # timing refutation belongs on real hardware)
    d = Ledger(active=False)
    d.post("in", 1.0, "idle_check")
    out["EA-3_dormant_entries"] = len(d.entries)

    # sanity anchors
    out["faraday_C_per_mol"] = FARADAY
    out["electrons_per_amp_second"] = amps_to_electron_rate(1.0)

    return out


if __name__ == "__main__":
    print(json.dumps(_selftest(), indent=2))
