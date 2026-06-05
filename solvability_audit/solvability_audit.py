"""
solvability_audit.py  --  CC0, stdlib only, mobile-runnable
Weighted latent scoring. Domain-silence (L0) decoupled from asserted-unbounded (L1).

Contract: do not forecast. Audit whether the model CAN forecast.
Pipeline: ingest -> inventory -> count_dof -> detect_latent
          -> classify -> bound_scope -> emit_confidence
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ----------------------------------------------------------------------
# 1. CLASSES + TUNABLES  (all falsifiable; tune against real failures)
# ----------------------------------------------------------------------

class Solvability(Enum):
    OVERDETERMINED  = "DOF<0   redundant/conflicting constraints"
    DETERMINED      = "DOF=0   uniquely solvable"
    UNDERDETERMINED = "DOF>0   infinite/empty solution space"
    UNKNOWN         = "latent load over kill threshold"

UNBOUNDED   = "UNBOUNDED"   # sentinel: extent asserted infinite (vs None = silence)
DOF_WARN    = 1
LATENT_KILL = 1.0           # latent_score >= this -> UNKNOWN / near-impossible

SEVERITY = {                # per-signature weight; sums to latent_score
    "L0": 0.1,   # domain silence -- informational, never kills alone
    "L1": 0.6,   # asserted-unbounded free var
    "L2": 1.0,   # stationarity assumed on coupled system (single hit kills)
    "L3": 0.8,   # cross-domain claim, NO coupling constraint
    "L3w": 0.3,  # cross-domain, co-mention only (NL weak bridge, unverified)
    "L4": 0.8,   # multi-scale claim, constraint count flat
    "L5": 0.2,   # per optimism marker
}
L5_CAP = 0.4                # cap noisy optimism-marker contribution

# ----------------------------------------------------------------------
# 2. LEXICONS  (edit per domain; fork per community)
# ----------------------------------------------------------------------

DOMAIN_LEX = {
    "thermal":    {"temperature","heat","thermal","entropy","cooling","warming","energy"},
    "fluid":      {"flow","pressure","viscosity","velocity","discharge","hydraulic"},
    "economic":   {"price","cost","money","capital","wage","demand","supply","market","growth"},
    "biological": {"population","species","mortality","biomass","reproduction","insect","yield"},
    "mechanical": {"force","load","stress","strain","torque","friction"},
    "electrical": {"voltage","current","resistance","charge","field"},
    "climate":    {"climate","emission","carbon","albedo","forcing","precipitation"},
}
SCALE_LEX = {
    "micro": {"molecular","cellular","cell","micro","local","individual","node"},
    "meso":  {"organism","community","regional","meso","population"},
    "macro": {"global","planetary","macro","systemic","ecosystem","continental"},
}
OPTIMISM = ("negligible","assume","assumed","ignore","ignored","hold constant",
            "held constant","all else equal","ceteris paribus","approximately",
            "roughly","should","expected to","stable","steady","constant","fixed")
CAUSAL = {"because","causes","cause","drives","drive","depends","affect","affects",
          "determines","controls","increases","decreases","reduces","raises",
          "leads","results"}
STATIONARY = {"constant","fixed","steady","unchanging","stationary"}
STOP = {"the","a","an","of","to","in","is","are","be","and","or","with","for","on",
        "as","at","by","that","this","it","its","than","then","when","will","can",
        "we","i","you","they","model","system","predict","forecast","over","into"}
_QTY = re.compile(r"\d|\b\d+\.?\d*\s*(kg|g|m|km|s|hr|c|k|pa|w|j|%)\b", re.I)
_OPS = set("=*/+-")

# ----------------------------------------------------------------------
# 3. DATA STRUCTURES
# ----------------------------------------------------------------------

@dataclass
class Variable:
    name: str
    known: bool
    domain: Optional[str] = None        # range str | UNBOUNDED | None(silence)

@dataclass
class Constraint:
    expr: str
    independent: bool = True

@dataclass
class ModelRegime:
    variables:   list = field(default_factory=list)
    constraints: list = field(default_factory=list)
    claim: str = ""
    stationarity_assumed: bool = False
    source_text: str = ""

@dataclass
class Flag:
    code: str
    severity: float
    reason: str

@dataclass
class AuditResult:
    solvability: Solvability
    dof: Optional[int]
    n_unknowns: int
    n_independent: int
    latent_score: float
    flags: list
    scope_in: str
    scope_out: str
    forecast_probability: str

# ----------------------------------------------------------------------
# 4. INGEST
# ----------------------------------------------------------------------

def ingest_formal(variables, constraints, claim="", stationarity=False, source_text=""):
    return ModelRegime(variables, constraints, claim, stationarity, source_text or claim)

def _tok(text):
    return [w for w in re.findall(r"[a-zA-Z]+", text.lower()) if len(w) >= 3]

def _sing(w):
    return w[:-1] if w.endswith("s") and not w.endswith("ss") else w

def ingest_language(text):
    sents = [s.strip() for s in re.split(r"[.;\n]", text) if s.strip()]
    constraints, seen = [], []
    for s in sents:
        toks = set(_tok(s))
        if toks & CAUSAL:
            content = frozenset(_sing(w) for w in toks if w not in STOP and w not in CAUSAL)
            constraints.append(Constraint(expr=s, independent=(content not in seen)))
            seen.append(content)
    quantified = set()
    for s in sents:
        if _QTY.search(s):
            quantified |= {_sing(w) for w in _tok(s)}
    names, vars_ = set(), []
    for w in _tok(text):
        lw = _sing(w)
        if lw in STOP or lw in CAUSAL or lw in names:
            continue
        names.add(lw)
        vars_.append(Variable(lw, known=(lw in quantified), domain=None))
    stationary = bool(set(_tok(text)) & STATIONARY)
    return ModelRegime(vars_, constraints, claim=text, stationarity_assumed=stationary, source_text=text)

# ----------------------------------------------------------------------
# 5. INVENTORY + DOF
# ----------------------------------------------------------------------

def inventory(m):
    return (sum(1 for v in m.variables if not v.known),
            sum(1 for c in m.constraints if c.independent))

def count_dof(n_unknowns, n_independent):
    return n_unknowns - n_independent

# ----------------------------------------------------------------------
# 6. LATENT DETECTION  -> list[Flag]
# ----------------------------------------------------------------------

def _domains_in(words):
    return {d for d, lex in DOMAIN_LEX.items() if words & lex}

def _scales_in(words):
    return {s for s, lex in SCALE_LEX.items() if words & lex}

def detect_latent(m):
    flags = []
    free = [v for v in m.variables if not v.known]

    silent = [v.name for v in free if v.domain is None]
    if silent:
        flags.append(Flag("L0", SEVERITY["L0"], f"domain unspecified (not asserted, just silent): {silent[:6]}"))

    asserted = [v.name for v in free if v.domain == UNBOUNDED]
    if asserted:
        flags.append(Flag("L1", SEVERITY["L1"], f"asserted-unbounded free var(s): {asserted[:6]}"))

    if m.stationarity_assumed and len(free) >= 2:
        flags.append(Flag("L2", SEVERITY["L2"], f"stationarity on {len(free)}-var coupled system (regime-shift risk)"))

    words = set()
    for v in m.variables: words |= set(_tok(v.name))
    words |= set(_tok(m.claim)) | set(_tok(m.source_text))
    doms = _domains_in(words)
    if len(doms) >= 2:
        formal = any(len(_domains_in(set(_tok(c.expr)))) >= 2 and (set(c.expr) & _OPS) for c in m.constraints)
        comention = any(len(_domains_in(set(_tok(c.expr)))) >= 2 for c in m.constraints)
        if formal:
            pass
        elif comention:
            flags.append(Flag("L3w", SEVERITY["L3w"], f"spans {sorted(doms)}; co-mention only, coupling unverified"))
        else:
            flags.append(Flag("L3", SEVERITY["L3"], f"spans {sorted(doms)} but NO constraint couples them"))

    scales = _scales_in(set(_tok(m.claim)) | set(_tok(m.source_text)))
    n_ind = sum(1 for c in m.constraints if c.independent)
    if len(scales) >= 2 and n_ind < len(scales):
        flags.append(Flag("L4", SEVERITY["L4"], f"scales {sorted(scales)} w/ only {n_ind} independent constraint(s)"))

    blob = (m.source_text + " " + m.claim + " " + " ".join(c.expr for c in m.constraints)).lower()
    hits = sorted({mk for mk in OPTIMISM if mk in blob})
    if hits:
        sev = min(L5_CAP, SEVERITY["L5"] * len(hits))
        flags.append(Flag("L5", sev, f"assumed-away terms ({sev:.1f}): {hits}"))

    return flags

def latent_score(flags):
    return round(sum(f.severity for f in flags), 2)

# ----------------------------------------------------------------------
# 7. CLASSIFY  (weighted)
# ----------------------------------------------------------------------

def classify(dof, score):
    if score >= LATENT_KILL: return Solvability.UNKNOWN
    if dof < 0:  return Solvability.OVERDETERMINED
    if dof == 0: return Solvability.DETERMINED
    return Solvability.UNDERDETERMINED

# ----------------------------------------------------------------------
# 8. SCOPE + CONFIDENCE
# ----------------------------------------------------------------------

def bound_scope(m, flags):
    bounded   = [v.name for v in m.variables if v.domain not in (None, UNBOUNDED)]
    open_axes = [v.name for v in m.variables if v.domain == UNBOUNDED and not v.known]
    scope_in  = ("within: " + ", ".join(bounded)) if bounded else "no stated domain -> scope undefined"
    out = open_axes + [f.code for f in flags if f.code != "L0"]
    scope_out = "beyond: " + "; ".join(out) if out else "none flagged"
    return scope_in, scope_out

def emit_confidence(sol, dof, score):
    if sol is Solvability.UNKNOWN:
        return f"near-impossible (latent {score} >= {LATENT_KILL}): name drivers first"
    base = {Solvability.DETERMINED: "high",
            Solvability.UNDERDETERMINED: f"low: {dof} free dimension(s)",
            Solvability.OVERDETERMINED: "check consistency: constraints may conflict"}[sol]
    if score > 0:
        base += f" | latent {score} below kill -- degraded, scope-bound"
    return base + " (within stated scope)"

# ----------------------------------------------------------------------
# 9. ORCHESTRATOR
# ----------------------------------------------------------------------

def audit(m):
    n_unk, n_ind = inventory(m)
    dof   = count_dof(n_unk, n_ind)
    flags = detect_latent(m)
    score = latent_score(flags)
    sol   = classify(dof, score)
    s_in, s_out = bound_scope(m, flags)
    return AuditResult(sol, dof, n_unk, n_ind, score, flags, s_in, s_out,
                       emit_confidence(sol, dof, score))

# ----------------------------------------------------------------------
# 10. SMOKE TEST
# ----------------------------------------------------------------------

def _show(tag, r):
    print(f"== {tag} ==")
    print(r.solvability.name, "| dof", r.dof, "| latent", r.latent_score, "|", r.forecast_probability)
    for f in r.flags: print(f"   {f.code} {f.severity:>4} {f.reason}")
    print()

if __name__ == "__main__":
    # A) silent domains must NOT kill (P1 fixed): -> UNDERDETERMINED, low
    vs = [Variable(n, known=False) for n in ("a","b","c","d")]
    _show("formal 3eq/4unk, domains silent",
          audit(ingest_formal(vs, [Constraint(f"eq{i}") for i in range(3)], claim="predict d")))

    # B) one var asserted unbounded -> L1+L0, still sub-kill
    vs2 = [Variable("a", False, UNBOUNDED), Variable("b", False), Variable("c", False), Variable("d", False)]
    _show("formal w/ 1 asserted-unbounded",
          audit(ingest_formal(vs2, [Constraint(f"eq{i}") for i in range(3)], claim="predict d")))

    # C) stationarity on coupled system -> L2 single-hit kill
    txt = ("Global insect population growth drives crop yield because temperature "
           "is held constant and emission effects are negligible.")
    _show("language: stationary coupled cross-domain", audit(ingest_language(txt)))
