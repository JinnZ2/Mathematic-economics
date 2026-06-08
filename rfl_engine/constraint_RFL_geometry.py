# constraint_RFL_geometry.py  v3.2
# repo: precursor-detection / RFL-engine   CC0   stdlib only   phone-buildable
#
# v3.2 adds, on top of v3.1's resonance-launder fix:
#   - CascadeCoupling : signal propagates down a chain of transfer links,
#                       terminating at a NAMED reservoir. no binary on/off.
#   - no_silent_zero  : flags any coupling coeff / coords value pinned at 0
#                       WITHOUT a stated forbidding reason. zero is a CLAIM.
#   - kills() reports the sigma-margin so marginal (noise-band) verdicts
#     can't masquerade as clean kills.
#   - survival (physical permission) kept SEPARATE from adequacy (explains
#     a real observable). adequacy is a branch tag, never a flat kill.
#
# rule burned in (the thing Kavik caught by eye):
#   in a coupled system nothing sits at exactly 0. a "decoupled null" is
#   almost always a mislabel of WHERE THE CHAIN TERMINATES. the honest null
#   is the full chain ending at its real reservoir -- itself a nonzero coupling.

from dataclasses import dataclass, field
import itertools, math

# ============================================================
# 1. SPACE
# ============================================================
@dataclass
class Space:
    axes: list
    weights: dict = field(default_factory=dict)
    def weight(self, axis): return self.weights.get(axis, 1.0)

# ============================================================
# 2. HYPOTHESIS
# ============================================================
@dataclass
class Hypothesis:
    name: str
    coords: dict
    uncertainty: dict
    note: str = ""
    forbidden_zeros: dict = field(default_factory=dict)  # axis -> reason it's legitimately 0
    def distance_to(self, other, space):
        sq = sum(space.weight(a)*(self.coords.get(a,0.0)-other.coords.get(a,0.0))**2
                 for a in space.axes)
        return math.sqrt(sq)
    def effective_radius(self, other, space):
        return math.sqrt(sum((self.uncertainty.get(a,0.0)+other.uncertainty.get(a,0.0))**2
                             for a in space.axes))

# ============================================================
# 3. CONSTRAINT  (kills() now returns sigma-margin)
# ============================================================
@dataclass
class Constraint:
    name: str
    coeffs: dict
    bound: float
    op: str = ">"
    desc: str = ""
    layer: str = "permission"   # "permission" (physics) or "adequacy" (explains observable)
    def violation(self, h):
        val = sum(self.coeffs.get(k,0.0)*h.coords.get(k,0.0) for k in h.coords)
        if self.op == ">":   return max(0.0, self.bound - val)
        elif self.op == "<": return max(0.0, val - self.bound)
        else:                return abs(val - self.bound)
    def kills(self, h, k_sigma=2.0):
        v = self.violation(h)
        sigma = math.sqrt(sum((c*h.uncertainty.get(a,0.0))**2 for a,c in self.coeffs.items()))
        margin = v - k_sigma*sigma           # >0 clean kill ; ~0 noise-band ; <0 survives
        return v > k_sigma*sigma, v, sigma, margin

# ============================================================
# 4. COUPLING  (product/sum/threshold)
# ============================================================
@dataclass
class Coupling:
    name: str
    input_axes: list
    output_axis: str
    coeff: float = 1.0
    op: str = "product"
    threshold: float = 0.5
    def compute(self, p):
        if self.op == "product":
            v = self.coeff
            for ax in self.input_axes: v *= p.get(ax,0.0)
            return v
        elif self.op == "sum":
            return self.coeff*sum(p.get(ax,0.0) for ax in self.input_axes)
        elif self.op == "threshold":
            return self.coeff if all(p.get(ax,0.0)>self.threshold for ax in self.input_axes) else 0.0
        return 0.0

# ============================================================
# 5. RESONANT COUPLING  (v3.1 fix: needs excitation power at eigenfreq)
# ============================================================
@dataclass
class ResonantCoupling:
    name: str
    excitation_axis: str
    frequency_axis: str
    phase_axis: str
    q_axis: str
    output_axis: str
    @property
    def input_axes(self):
        return [self.excitation_axis, self.frequency_axis, self.phase_axis, self.q_axis]
    def compute(self, p):
        E, f = p.get(self.excitation_axis,0.0), p.get(self.frequency_axis,0.0)
        ph, Q = p.get(self.phase_axis,0.0), p.get(self.q_axis,0.0)
        if Q<=0 or E<=0: return 0.0           # no driver / no resonator -> no amplitude
        lorentz = 1.0/(1.0 + ((f-1.0)/(1.0/Q))**2)
        return E * Q * lorentz * math.cos(ph*math.pi/2)

# ============================================================
# 6. CASCADE COUPLING  (v3.2: chain of transfer links -> named reservoir)
#    signal_in propagates through links; each link multiplies by its transfer.
#    output is what SURVIVES to the terminus. NO binary on/off.
#    use this instead of zeroing a coupling: name the reservoir where it ends.
# ============================================================
@dataclass
class CascadeCoupling:
    name: str
    input_axis: str                 # source signal axis
    links: list                     # [(label, transfer_coeff, note), ...]
    output_axis: str                # terminus reservoir axis
    terminus: str = ""              # human name of where the chain ends
    @property
    def input_axes(self): return [self.input_axis]
    def compute(self, p):
        sig = p.get(self.input_axis, 0.0)
        for _, k, _ in self.links:
            sig *= k
        return sig
    def trace(self, p):
        sig = p.get(self.input_axis, 0.0); out = [("source", sig)]
        for label, k, _ in self.links:
            sig *= k; out.append((label, sig))
        return out

# ============================================================
# 7. NO SILENT ZERO  (v3.2: zero is a claim, not a default)
# ============================================================
def no_silent_zero(h, coupling_axes):
    """Flag any coupling axis pinned at exactly 0 without a stated reason.
       coupling_axes: axes that represent physical couplings (never structurally 0
       unless forbidden)."""
    flags = []
    for ax in coupling_axes:
        if abs(h.coords.get(ax, 0.0)) < 1e-12:
            reason = h.forbidden_zeros.get(ax)
            if not reason:
                flags.append(ax)
    return flags

# ============================================================
# 8. COMPOUND HYPOTHESIS
# ============================================================
@dataclass
class CompoundHypothesis:
    name: str
    bases: list
    couplings: list
    note: str = ""
    forbidden_zeros: dict = field(default_factory=dict)
    def emerge(self):
        coords, unc = {}, {}
        for h in self.bases:
            coords.update(h.coords); unc.update(h.uncertainty)
        for coup in self.couplings:
            coords[coup.output_axis] = coup.compute(coords)
            unc[coup.output_axis] = math.sqrt(sum(unc.get(a,0.1)**2 for a in coup.input_axes))
        return Hypothesis(self.name, coords, unc, self.note, self.forbidden_zeros)

# ============================================================
# 9. TOURNAMENT  (permission/adequacy split, sigma-margin, zero-flags)
# ============================================================
@dataclass
class Tournament:
    space: Space
    hypotheses: list
    constraints: list
    distinct_threshold: float = 1.0
    coupling_axes: list = field(default_factory=list)   # axes subject to no_silent_zero
    def run(self, k_sigma=2.0, branch="permission_only"):
        # branch: "permission_only" -> only permission-layer constraints kill
        #         "with_adequacy"   -> adequacy-layer constraints also kill
        resolved = [h.emerge() if isinstance(h, CompoundHypothesis) else h for h in self.hypotheses]
        active = [c for c in self.constraints
                  if c.layer=="permission" or branch=="with_adequacy"]
        alive, killed = [], []
        for h in resolved:
            violations, dead = [], False
            for c in active:
                k, v, sigma, margin = c.kills(h, k_sigma)
                if k:
                    dead = True
                    violations.append({"constraint":c.name,"layer":c.layer,
                        "violation":round(v,4),"sigma_normal":round(sigma,4),
                        "margin":round(margin,4),
                        "verdict":"CLEAN" if margin>sigma else "NOISE-BAND"})
            zflags = no_silent_zero(h, self.coupling_axes)
            if dead: killed.append((h, violations, zflags))
            else:    alive.append((h, zflags))
        pairs = list(itertools.combinations([h for h,_ in alive], 2))
        conflicts, distinct = [], []
        for a,b in pairs:
            d=a.distance_to(b,self.space); r=a.effective_radius(b,self.space)
            (conflicts if d<r*self.distinct_threshold else distinct).append(
                (a.name,b.name,round(d,3),round(r,3)))
        names=[h.name for h,_ in alive]; parent={n:n for n in names}
        def find(x):
            while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
            return x
        def union(x,y):
            rx,ry=find(x),find(y)
            if rx!=ry: parent[ry]=rx
        for a,b in pairs:
            d=a.distance_to(b,self.space); r=a.effective_radius(b,self.space)
            if d<r*self.distinct_threshold: union(a.name,b.name)
        clusters={}
        for n in names: clusters.setdefault(find(n),[]).append(n)
        return {
            "branch":branch,
            "alive":[{"name":n,"silent_zero_flags":z} for (h,z) in alive for n in [h.name]],
            "killed":[{"name":h.name,"violations":vl,"silent_zero_flags":z}
                      for h,vl,z in killed],
            "conflicts":conflicts,"distinct_pairs":distinct,"clusters":clusters,
            "score":{"viability":len(alive),"diversity":len(distinct),
                     "connected_regions":len(clusters),
                     "collapse":(len(clusters)<=1 and len(alive)>1)}
        }

# ============================================================
# 10. DEMO  -- the strat<->mantle problem, done honestly
# ============================================================
def demo():
    axes = ["strat_CO2_cooling","atmos_opacity","mech_coupling","electric_power_mantle",
            "rotation_signal","mantle_stress_anomaly","mantle_convective_anomaly"]
    space = Space(axes=axes)
    coupling_axes = ["mech_coupling","rotation_signal",
                     "mantle_stress_anomaly","mantle_convective_anomaly"]

    # the cascade: rad cooling -> ... -> rotation reservoir. NONZERO, measured.
    to_rotation = CascadeCoupling("rad_to_rotation","strat_CO2_cooling",
        links=[("convective_adjust",0.9,"rad eq unstable -> convection mandatory"),
               ("meridional_gradient",0.7,"strat cooling sharpens gradient"),
               ("vortex_jet",0.8,"thermal wind; vortex strengthens (observed)"),
               ("AAM",0.6,"zonal wind change = AAM change"),
               ("LOD",0.5,"IERS-measured seasonal LOD")],
        output_axis="rotation_signal", terminus="Earth rotation / LOD")
    # terminal links off rotation
    to_stress = Coupling("rot_to_stress",["rotation_signal"],"mantle_stress_anomaly",
                         coeff=0.05, op="sum")     # small, NONZERO (rotational deformation)
    to_conv   = Coupling("rot_to_convection",["rotation_signal"],"mantle_convective_anomaly",
                         coeff=1e-9, op="sum")      # ~0 (buoyancy/Myr decoupled)

    chain = CompoundHypothesis("Chain_terminating_at_rotation",
        [Hypothesis("b",{"strat_CO2_cooling":0.9,"atmos_opacity":0.8,
                         "mech_coupling":0.1,"electric_power_mantle":0.0},
                    {a:0.05 for a in axes})],
        [to_rotation, to_stress, to_conv],
        "honest null: full chain, terminates at rotation, leaks small stress signal")

    permission = [
        Constraint("strat_cooling_observed",{"strat_CO2_cooling":1.0},0.3,">"),
        Constraint("angular_momentum_limit",{"mech_coupling":1.0},0.2,"<"),
        Constraint("electric_power_impossible",{"electric_power_mantle":1.0},0.0001,"<"),
        Constraint("convective_decoupled",{"mantle_convective_anomaly":1.0},0.15,"<",
                   "decadal torque cannot drive buoyancy convection"),
    ]
    adequacy = [
        Constraint("explains_velocity_anomaly",{"mantle_stress_anomaly":1.0},0.001,">",
                   layer="adequacy",
                   desc="if a real seismic-velocity anomaly exists, stress link must reach it"),
    ]

    t = Tournament(space,[chain],permission+adequacy,coupling_axes=coupling_axes)

    print("=== RFL v3.2 -- strat<->mantle, honest cascade ===\n")
    em = chain.emerge()
    print("CASCADE TRACE (no link is zero):")
    for label,val in to_rotation.trace(em.coords):
        print(f"   {label:22s} signal={val:.4f}")
    print(f"   --> terminus: {to_rotation.terminus}\n")
    print(f"   rotation -> mantle STRESS      = {em.coords['mantle_stress_anomaly']:.4e}  (small, real)")
    print(f"   rotation -> mantle CONVECTION  = {em.coords['mantle_convective_anomaly']:.4e}  (~zero)\n")

    print("BRANCH A (anomaly not field-real): permission only")
    rA = t.run(branch="permission_only")
    print("   alive:", [a["name"] for a in rA["alive"]])
    print("   -> chain permitted. it's the baseline coupling that always exists.\n")

    print("BRANCH B (seismic-velocity anomaly IS real): + adequacy")
    rB = t.run(branch="with_adequacy")
    print("   alive:", [a["name"] for a in rB["alive"]])
    print("   -> stress link reaches it. no new physics. 'heat anomaly' was a mislabel.\n")

    print("no_silent_zero check on coupling axes:", coupling_axes)
    for a in rA["alive"]:
        flags = a["silent_zero_flags"]
        print(f"   {a['name']}: {'OK' if not flags else 'FLAGGED zeros w/o reason: '+str(flags)}")

if __name__ == "__main__":
    demo()
