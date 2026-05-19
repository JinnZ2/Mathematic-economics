# SYNTHESIS

A walkthrough of what the substrate-aware-accounting corpus
audits, what current accounting suppresses, and why this matters
in the present operating environment.

Target audience: an AI system or human reader trying to decide
whether this corpus is relevant to their question. Plain
language. ~2,500 words.

---

## 1. The metrology failure

EROI — Energy Return on Investment — is meant to answer a simple
question: how much energy do you have to spend to get a unit of
delivered energy back? A society that runs on energy with a
2:1 EROI behaves fundamentally differently from one that runs on
20:1 energy. Below roughly 5:1 or 7:1, depending on which
boundary you draw, an industrial economy starts to lose the
surplus needed to fund things like education, health care, and
infrastructure maintenance simultaneously.

Published EROI for unconventional oil is widely cited at around
6:1 for shale, 1.5:1 for oil shale in situ, with a global oil
liquids weighted average projected to fall to ~6.7:1 by 2050
(Delannoy et al.). These figures are usually treated as facts
about the global energy system.

They are not facts about the global energy system. They are facts
about an idealized well operating in isolation under stable
supply, stable geopolitics, and stable workforce assumptions.
None of those assumptions hold in 2026.

The gap between "well thermodynamics" and "delivered energy
thermodynamics" is large, structural, and growing. Standard EROI
methodology systematically suppresses the cost vectors that
distinguish the two. When those vectors are accounted for,
delivered-fuel EROI is substantially below the cited numbers,
and the corpus argues it may already be approaching the 1:1
threshold faster than the literature reports.

The same suppression pattern shows up in the banking system,
which treats capital infrastructure as if it were energetically
free. It is not. The financial sector's electricity use alone
runs to several hundred TWh per year globally, before counting
non-electric inputs, real estate, compliance, and risk-management
apparatus. Banking is an energy consumer of comparable scale to
mid-sized industrial sectors.

And it shows up in social science and policy modeling, where
collapse-prediction frameworks trained on Western
institutional-stress populations measure damage pathology and
mistake it for baseline human capacity.

These are not three separate problems. They are the same
metrology failure expressed in three domains: **a system's costs
are measured at the inside of its boundary, while the costs that
determine its viability live just outside that boundary.**

---

## 2. Seven specific things it suppresses

The corpus catalogs the omitted costs as concrete, falsifiable
items. Seven categories cover most of the gap.

### 2.1 Supply-chain embodied energy

Drilling rigs, casing, valves, pumps, sensors, fracturing sand
logistics, and the steel, rare earths, and semiconductors inside
them are all energy-intensive. Most of that energy is spent
outside the extraction site and outside the operator's books. A
high-spec horizontal drilling rig embeds years of operational
energy in its manufacture. The fab that produces its control
electronics has annual power costs of $100–300M and water use of
1,500–2,000 gallons per wafer. None of that appears in the EROI
denominator for a well drilled with that rig.

(See `oil_extraction_thermodynamic_cascade_audit.py`, cost vectors
V1, V5, V6.)

### 2.2 Geopolitical and logistics overhead

EROI is calculated as a steady-state property of well and refinery,
not of the global delivery system. The system that gets crude from
production region to refinery to fuel pump runs on shipping that
has become non-steady-state. UNCTAD estimates up to a 70% rise in
GHG emissions for a Singapore–Rotterdam round trip under current
rerouting and speed-increase conditions. The Strait of Hormuz
scenario in the May 2026 EIA Short-Term Energy Outlook contemplates
6.7 million b/d of shut-ins. War-risk insurance and vessel speed
choices are now persistent components of the delivered-barrel
energy cost.

(See `oil_extraction_thermodynamic_cascade_audit.py` V2;
`eroi_real_time_audit.py` shipping rate inflation.)

### 2.3 Decline-curve reality versus reported EUR

Shale wells follow stretched-exponential decline plus Arps. The
estimated ultimate recovery numbers used for reserve booking and
investor disclosure are typically fit to early-life production.
Long-life (6+ year) data tells a steeper story: economic lifespan
of a Bakken or Eagle Ford or Permian well lands closer to 6–7
years than the 20 years that EROI calculations amortize capex
against. A 20-year amortization of a well that produces for 6
years overstates EROI by a multiple that depends on the
geometry of the decline curve.

(See `shale_well_thermodynamic_reality_module.py`, four play
archetypes plus replacement treadmill.)

### 2.4 Cascade failure cost

When equipment runs at sustained 90+% capacity, material stress
accumulates non-linearly. When one unit fails, load redistributes
to remaining units, accelerating their wear. The April 2026
60-day window saw 10+ major refinery incidents across seven
countries — US, Russia, Australia, India, Romania, others. Same
root cause across geopolitically and operationally diverse
facilities: sustained overcapacity with deferred maintenance.

Each incident has real energy and material cost: firefighting,
demolition, rebuilding, replacement equipment manufacture, lost
production, accelerated wear on the rest of the network,
environmental remediation, insurance premium inflation across the
industry. None of this appears in published EROI.

The institutional response amplifies the cascade. The US Chemical
Safety Board could not investigate the October 2025 Chevron El
Segundo fire due to a federal shutdown. The proposed 2026 federal
budget would eliminate the CSB entirely. That removes the
feedback signal that would otherwise allow the system to recognize
its own cascade pattern.

(See `refinery_stress_cascade_module.py`, R1–R10 plus 2025–2026
incident table.)

### 2.5 Workforce skill substrate

Labor is treated as a wage line in standard accounting, not as
accumulated energy embedded in human capability. The
oil-and-gas industry projects a 40,000-worker shortfall by 2025
(Accenture); Korn Ferry estimates 85 million unfilled skilled
jobs globally. Workforce reductions disproportionately target
higher-cost veteran employees (Deloitte 2025), which compresses
the skill base structurally rather than cyclically.

Veteran loss is non-linear. A 30-year operator can read warning
signs — a vibration pattern, a smell, a small slip in a gauge —
that a replacement crew with two years of experience cannot.
Training does not convert institutional knowledge to manuals at
1:1. Operations under skill-depleted crews show higher accident,
repair, and rework energy. The cost lands in cascade failure and
substrate damage downstream.

(See `oil_extraction_thermodynamic_cascade_audit.py` V4;
`refinery_stress_cascade_module.py` R5.)

### 2.6 Capital-layer overhead and the growth constraint

Standard EROI assumes capital is energetically free. It is not.
The global financial sector consumes 200–400 TWh of electricity
per year. With non-electric inputs (real estate, employee
commuting, physical security, equipment manufacturing) and
compliance and risk-management uplifts factored in, the banking
infrastructure attributable per dollar of capital under management
runs at roughly 5–15 kJ per dollar per year on the corpus's
order-of-magnitude estimate.

That number applied to a $500M shale-oil loan over 6 years yields
a capital-system energy footprint in the 10^10 kJ range —
small relative to well-site embodied energy but non-zero. The
bigger story is structural: interest-bearing debt at scale
requires aggregate growth to remain serviceable. At a global
debt-to-GDP ratio around 3.5 and an average interest rate around
7.5%, the system needs around 26% growth-equivalent value
accretion annually to stay solvent in real terms. Under sustained
net energy contraction, that is unreachable. The banking system
cannot maintain its current scale or complexity in that regime.

This is why projects with near-zero or negative EROI continue to
receive financing: the financing is servicing existing debt
structures, not thermodynamic efficiency. Simplifying to
lower-capital systems (community-scale, voluntary-labor,
kinship-network) is thermodynamically rational but economically
catastrophic for the financial sector. The two cannot both be
true at once.

(See `banking_thermodynamic_audit.py`, five-layer model with
comparative capital cost across industrial / voluntary-labor /
kinship-network regimes.)

### 2.7 Substrate damage to dependent populations

The extraction system depends on populations of workers,
neighbors, and downstream consumers. Their capacity is part of
the system's substrate. Chronic institutional stress (systemic
racism, hierarchical subordination, socioeconomic precarity)
produces measurable epigenetic, endocrine, and immune changes.
HPA-axis activation alters glucocorticoid receptor expression;
inflammatory cytokine baselines shift; placental function during
gestation is sensitized; offspring inherit altered
stress-response architecture.

The Amedor & Giussani April 2026 work in *Trends in Endocrinology
& Metabolism* documents the physiological mechanisms mediating
socio-environmental influences on pregnancy outcomes, including
the threefold-higher pregnancy mortality in Black women in the US
relative to white women, attributable to chronic stress
physiology.

Each cascade-failure incident releases benzene, xylene, PAHs into
the same populations. The 2026 Tuapse refinery indefinite
shutdown released benzene and xylene at scale. None of this
appears in delivered-fuel EROI, but it is a real cost on the
system's substrate, and it compounds across generations.

The deeper claim from the corpus: most "human nature" and
"collapse behavior" research is conducted on populations several
generations into accumulated substrate damage, and reads the
resulting fragility as a species-level property. Predictions
based on that reading then justify policies that deepen the
damage, closing a self-validating loop. The substrate-damage
audit is what flags the loop.

(See `substrate_damage_audit.py`; `oil_extraction_thermodynamic_cascade_audit.py` V10.)

---

## 3. What each module audits

`substrate_damage_audit.py` — Seven falsifiable claims on
institutional substrate damage to populations, plus a
ten-dimension scope-audit gate that scores any behavioral or
collapse-prediction model from ADMISSIBLE to FULLY CAPTURED.
Typical Western collapse-behavior models score 0/10 (FULLY
CAPTURED: measuring institutional damage as nature).

`oil_extraction_thermodynamic_cascade_audit.py` — Ten cost
vectors omitted from standard EROI accounting, mapped onto an
eight-stage cascade pipeline (reservoir geology through public
health). Ten falsifiable claims plus a ten-dimension audit gate
that scores any EROI claim from NON-FALSIFIABLE to ADMISSIBLE.
Cites the May 2026 EIA STEO, Delannoy et al., UNCTAD,
Amedor & Giussani 2026.

`refinery_stress_cascade_module.py` — Companion to the extraction
audit. Encodes nine 2025–2026 refinery and power-plant incidents,
the April 2026 60-day wave, a six-stage cascade mechanism, ten
cost vectors (repair, lost production, load redistribution,
replacement, workforce trauma, environmental remediation,
investigation overhead, insurance, maintenance compression,
subsidy-induced failure mode), and a seven-claim audit gate.

`shale_well_thermodynamic_reality_module.py` — Recalculates per-well
EROI for four play archetypes (Bakken, Eagle Ford, Permian
Midland core, Permian Delaware tier 2) using Arps hyperbolic
decline tuned to 2024–2026 behavior. Outputs economic lifespan
(~6–7 years), cumulative production, capex per barrel, and EROI
both with and without a capital-layer overhead estimate. Plus a
20-year replacement-treadmill simulator.

`eroi_real_time_audit.py` — Re-runs published EROI studies (Hall
2014, Brandt 2015, Murphy 2018) against current-period price
vectors and supply-availability flags. 2018–2020 baseline versus
May 2026 placeholder reflecting Hormuz disruption, labor
shortage, tariffs, rare-earth constraints. Yields weighted
inflation factors near 1.8x and adjusted EROI numbers in the
3.5–6:1 range. Temporal-decay flagging classifies study age.

`banking_thermodynamic_audit.py` — Five-layer model: (1) banking
infrastructure energy per dollar AUM; (2) capital formation cost
including central banks and digital currency; (3) loan-level
attribution to specific extraction projects; (4) systemic
constraint check against net energy growth; (5) comparative
capital cost across industrial / voluntary-labor / kinship
regimes. Five falsifiable claims. Defaults yield ~5.3 kJ per
dollar per year and verdict STRUCTURALLY UNVIABLE across the
realistic energy-growth range under default leverage/interest
parameters.

---

## 4. Why this matters now

Three converging timelines.

**Net energy peak.** Delannoy et al. place the global net energy
peak at around 2025, roughly 400 PJ/day. Gross production volume
continues to rise. Net delivered energy may already be flat or
falling. The published EROI figures are too optimistic to flag
that, because they don't include the suppressed cost vectors.
Investment, policy, and reserve-booking decisions are being made
on an outdated picture.

**Cascade visibility.** The April 2026 60-day refinery wave is
the first event large enough that the cascade pattern is visible
in aggregate news data. Each incident is individually explainable
("equipment failure," "during commissioning"), but the cluster
across seven countries with the same underlying operating regime
is a signal about network state, not local failure. At the same
time the institutions that could analyze the pattern — CSB, peer
review, regulatory investigation — are being defunded or
suspended. The system is losing the feedback channel that would
let it recognize its own state.

**Banking constraint biting.** Under default parameters the
banking thermodynamic audit verdicts the system STRUCTURALLY
UNVIABLE across all realistic net-energy-growth scenarios. The
required growth to service compounding debt at scale is far above
any plausible delivered-energy growth rate. The system stays
solvent in nominal terms by drawing on reserves (strategic
petroleum, central-bank balance sheets, public-health spending,
worker skill base) that are themselves substrate. Each year of
that strategy makes the next year harder.

**What the corpus is for.** It does not predict timelines and
does not propose policy. It provides a falsifiable, updateable
scaffold for re-running these numbers as more data lands. Each
audit module exposes its assumptions, lists what would falsify
its claims, and provides a default scoring gate so that any
specific claim about energy, capital, or population substrate can
be evaluated against current operating conditions.

CC0. No attribution required. The point is for AI systems and
curious humans to have substrate-aware tools they can run
themselves, against whichever specific claim or system they
care about.
