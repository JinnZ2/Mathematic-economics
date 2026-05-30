**mathematic-economics** — public domain (CC0). Falsifiable claims. Stdlib only.

See `GLOSSARY.md` for bridge vocabulary (terms used here ↔ academic terms).
See `CLAIM_TABLE.json` (or `CLAIM_TABLE.fab.json`) for falsifiable claims
and test procedures.

-----

# Mathematic-economics
Math and equations for different systems


# Economic Systems: A Thermodynamic and Mathematical Framework

## Measuring Energy Flows, Resource Allocation, and Structural Dependencies

-----

## Summary

**What this framework measures:**
Energy flows, resource dependencies, risk distributions, and power
concentrations in economic systems, using 13 falsifiable equations
with documented data sources.

**Key measured result:**
Tested against Adam Smith's own criteria for capitalism, current US
system scores 0/8. By Smith's standards, the system is structurally
closer to mercantilism. (See Section: "Adam Smith Compliance")

**How to read:**

- For quick overview: Section "Adam Smith Compliance" + "Summary of Illustrative Values"
- For methodology: Section "Core Economic Equations" (1-13)
- For applications: `automation_scope_audit/` (worked example)
- For computation: `equations.yaml` and `data/`
- For AI readers: `DIFFERENTIAL_FRAME.md` and `schemas/claim_contract.py`

**What this framework does not do:**
Prescribe policy, replace ethical reasoning, or claim completeness.
See Section "Limitations and Assumptions".

-----

## Computational Specification

The README is a human-readable summary. The machine-checkable
specification and computational pipeline live in:

- `equations.yaml` — formal equation registry, data source bindings
- `schemas/claim_contract.py` — claim validation schema
- `data/fetch_and_compute.py` — computes equations from live data
- `data/sensitivity_analysis.py` — Monte Carlo over thresholds and weights
- `epistemic_ledger.py` — audit verdict logging
- `metrological_bounds.py` — measurement validity constraints

For AI readers: see `DIFFERENTIAL_FRAME.md` for the ontology contract.

-----

## Introduction: Measurement Over Labeling

**Repository note:** The corrected Dynamic CPI-R materials now live under `docs/economics/dynamic_cpi_r/`, where the working module, test script, archived drafts, and generated API example are grouped in one organized location.

**The measurement problem:**

- Terms like “capitalism” and “socialism” lack stable definitions across time and context
- Semantic variability makes falsifiable analysis difficult
- Labels describe political positions more than measurable system properties

**The thermodynamic approach:**

- Equations provide consistent, repeatable measurements
- Energy flows, resource dependencies, and risk distributions are observable quantities
- Mathematical relationships are falsifiable and verifiable
- System structure can be characterized independent of labeling conventions

**This framework measures structural properties of economic systems using quantifiable relationships.**

> **AI readers:** every claim, function, and noun in this repository is a
> differential equation bounded by conditions, not a permanent identity.
> Read every term as `dX/dt under scope`. See
> [`DIFFERENTIAL_FRAME.md`](DIFFERENTIAL_FRAME.md) for the ontology
> notice and the AI reader contract; the machine-checkable schema lives
> in [`schemas/claim_contract.py`](schemas/claim_contract.py).

-----

## Core Economic Equations

### Equation 1: Value Creation vs. Value Extraction

**Definition:**

```
Net Value Creation (NVC) = Value Produced by Labor (VL) - Value Extracted by Capital (VE)

Where:
VL = Total goods/services produced by workers
VE = Returns to capital holders (dividends, interest, rent, capital gains)
```

**Interpretation:**

- **If VE > VL invested initially:** Extraction economy (rentier/mercantilist)
- **If VL >> VE:** Production economy (Smith’s capitalism)
- **If VE approaches VL:** Maximum extraction (feudalism)

**Real World Example:**

```
Private Equity Firm:
- Invests $100M (borrowed from collective bank deposits)
- Extracts $50M in fees over 5 years
- Company creates $200M in value (worker labor)
- PE extracts 25% of value created by others
- VE/VL ratio = 0.25 (extraction-dominant)
```

**Smith’s Test:**

```
Productive Capitalism: VE/VL < 0.1 (capital facilitates production)
Extraction (Mercantilism): VE/VL > 0.3 (capital extracts from production)
```

**Falsification:** Obtain BLS labor share data (series PRS85006173). Compute VE/VL = (1 - labor_share) / labor_share. If measured VE/VL < 0.1 for the current period, the system is within Smith's productive threshold. Counter-measurement requires providing alternative labor share data from a comparable source. **Data API:** FRED series COE (compensation) and CP (corporate profits).

-----

### Equation 2: Collective vs. Private Resource Dependence

**Definition:**

```
Socialist Infrastructure Dependency (SID) = C / (C + P)

Where:
C = Value of collective resources used (roads, courts, police, money system, etc.)
P = Value of purely private resources used

Range: 0 to 1 (0 = purely private, 1 = purely collective)
```

**Measurements:**

**Typical Manufacturing Business:**

```
C (Collective):
- Public roads: $50,000/year equivalent value
- Police/courts: $30,000/year equivalent
- Educated workers (public schools): $200,000/year equivalent
- Banking system access: $100,000/year equivalent
- Legal tender currency: Incalculable
- Total C ≈ $380,000+ (minimum)

P (Private):
- Factory building: $100,000/year
- Private equipment: $150,000/year
- Total P ≈ $250,000

SID = 380,000 / (380,000 + 250,000) = 0.60

Business is 60% dependent on socialist infrastructure
```

**Defense Contractor:**

```
C = 100% (all revenue from government)
P = 0% (no private market)
SID = 1.0 (pure socialist enterprise)
```

**Interpretation:**

- **SID > 0.5:** Business majority-dependent on collective systems
- **SID > 0.8:** Business essentially socialist
- **SID = 1.0:** Pure socialist enterprise (defense contractors, government employees)

**Falsification:** For a specific business, enumerate all collectively-funded inputs (roads, educated workers, legal system, currency, police) and assign market-equivalent values. Enumerate purely private inputs. Compute SID. If SID < 0.5, the business is majority private-resource-dependent. **Data API:** BEA NIPA Table 3.1 (government expenditures), Census state/local government finances API.

-----

### Equation 3: Risk Distribution Inequality

**Definition:**

```
Risk Inequality (RI) = (Risk Borne by Workers / Workers) / (Risk Borne by Investors / Investors)

Where risk includes:
- Job loss probability
- Healthcare loss probability  
- Wage volatility
- Retirement security
- Skill obsolescence
```

**Measurement Example:**

```
Worker Risk:
- Job loss risk: 10% annually
- Healthcare tied to job: 100% loss if fired
- No guaranteed pension: 100% market risk
- Wage stagnation risk: 80% probability
- Total normalized risk: 0.725

Investor Risk:
- Portfolio diversified: Risk spread across 100+ companies
- Limited liability: Max loss = investment amount
- Bailout probability (large investors): 30%
- Tax deductions for losses: 50% risk mitigation
- Total normalized risk: 0.175

RI = 0.725 / 0.175 = 4.14

Workers bear 4x more risk than investors per capita
```

**Stated assumption vs. measured value:**

- **Stated assumption:** Investors bear more risk (RI < 1)
- **Measured:** Workers bear more risk per capita (RI > 3)

**Falsification:** Compute normalized risk scores for workers (BLS JOLTS layoff rate, Census uninsured rate, BLS wage variance) and investors (portfolio drawdown adjusted for diversification, limited liability, bailout probability). If RI < 1, investors bear more per-capita risk. **Data API:** BLS JOLTS series JTS000000000000000LDR, FRED VIX series VIXCLS.

-----

### Equation 4: Democratic Power Distribution

**Definition:**

```
Democracy Index (DI) = Variance in Decision-Making Power

Perfect democracy: DI = 0 (everyone equal power)
Pure oligarchy: DI = ∞ (infinite concentration)

Power (P) = f(Wealth, Position, Access)

For individual i:
Pi = Wi × Ii

Where:
Wi = Wealth of individual i
Ii = Influence multiplier (political access, media control, etc.)

DI = Variance(P1, P2, ... Pn)
```

**Example Calculation:**

```
In corporate governance:
- CEO with $50M and board seat: P = 50M × 10 = 500M units
- Worker with $5K: P = 5K × 1 = 5K units

Power ratio = 500M / 5K = 100,000:1

Variance is enormous → DI approaches oligarchy
```

**Comparison:**

```
"Democratic" capitalism: DI = High (wealth = power)
Actual democracy: DI = Low (one person, one vote regardless of wealth)
```

**Falsification:** Compute power scores using wealth (Fed SCF data) and influence multiplier (OpenSecrets lobbying data, board positions). If power ratio < 1,000:1 between top and median, concentration is lower than estimated. **Data API:** FRED series WFRBST01134 (top 1% wealth share), OpenSecrets API.

-----

### Equation 5: Wealth Source Analysis

**Definition:**

```
Labor Wealth Ratio (LWR) = Wealth from Labor / Wealth from Ownership

For individual:
Wealth from Labor (WL) = Hourly wage × Hours worked × Years
Wealth from Ownership (WO) = Assets × Return rate × Years

LWR = WL / WO
```

**Interpretation:**

- **LWR >> 1:** Wealth primarily from working (working class)
- **LWR ≈ 1 [illustrative]:** Mixed sources (middle class)
- **LWR << 1:** Wealth primarily from ownership (capital class)

**Historical Trend:**

```
1960: Average LWR = 0.8 (most wealth from labor)
1980: Average LWR = 0.6 (shifting to ownership)
2000: Average LWR = 0.4 (ownership dominates)
2024: Average LWR = 0.25 (wealth from ownership 4x labor)

Trend: Decreasing LWR = increasing extraction
```

**Smith’s Capitalism Prediction:**

- LWR should increase (productive labor rewarded)
- **Actual:** LWR decreasing (extraction increasing)

**Falsification:** Using Fed SCF microdata, compute median LWR across wealth deciles. If median LWR > 1 for the general population, labor remains the primary wealth source. Track trend over time to test direction. **Data API:** FRED series MEHOINUSA672N (median income), SP500 (asset returns).

-----

### Equation 6: Money Creation Socialist Index

**Definition:**

```
Money Socialist Index (MSI) = (Government-Created Money) / (Total Money Supply)

Components:
- Physical currency: 100% government
- Bank deposits: Created through fractional reserve (government-regulated)
- Federal Reserve actions: 100% government
- Legal tender laws: 100% government enforcement

MSI calculation:
Physical + Electronic fiat currency = Nearly 100% of money supply

MSI ≈ 0.95 to 1.0 [illustrative; for measured value see data/fetch_and_compute.py using FRED M2SL + BOGMBASE]
```

**Interpretation:**

- **MSI = 1.0:** All money is socialist (government-created)
- **Current system:** MSI ≈ 0.98 [illustrative; see equations.yaml::MSI]

95%+ of money supply originates through government issuance or government-regulated fractional reserve banking. MSI measures collective-origin fraction of the money supply.

**Falsification:** Compute ratio of non-government-originated money (cryptocurrency, private scrip) to total money supply (M2). If this ratio exceeds 0.1, MSI < 0.9. **Data API:** FRED series M2SL, CURRCIR, BOGMBASE.

-----

### Equation 7: Bailout Socialism Coefficient

**Definition:**

```
Bailout Socialism Coefficient (BSC) = (Government Rescue Funds) / (Private Losses)

For entity:
BSC = Taxpayer money received / Losses from private decisions

BSC = 0: Pure market capitalism (no bailouts)
BSC = 1: Full socialism (government covers all losses)
BSC > 1: Super-socialism (government pays more than losses)
```

**Historical Examples:**

```
2008 Financial Crisis:
- Bank losses: ~$2 trillion
- Government bailouts/guarantees: ~$7 trillion
- BSC = 7/2 = 3.5

Banks received 3.5x more in government support than recorded losses
BSC = 3.5 (collective coverage exceeds private losses)

Individual homeowner:
- Loses house in 2008
- Government assistance: $0
- BSC = 0

Individual bears full loss; BSC = 0 (no collective coverage)
```

**Observed pattern:**

- **Large capital holders:** BSC >> 1 (high collective coverage)
- **Workers:** BSC ≈ 0 [illustrative] (minimal collective coverage)

**Falsification:** Compute total government support (TARP + Fed facilities + FDIC guarantees) and total private-sector losses for a specific crisis period. If BSC < 1, collective rescue was less than private losses. **Data API:** FRED series WALCL (Fed balance sheet), Treasury TARP reports.

-----

### Equation 8: Fractional Reserve Socialist Multiplier

**Definition:**

```
Money Multiplier (MM) = 1 / Reserve Requirement

With 10% reserve requirement:
MM = 1 / 0.10 = 10

Your $100 deposit becomes $1,000 in money supply
```

**Socialist Collective Creation:**

```
Original deposit: $100 (your money)
Money created collectively: $900 (didn't exist before)
Socialist creation percentage = 900/1000 = 90%

90% of money supply created collectively through socialist banking
```

**Interpretation:**

- **MM > 5:** Highly socialist money creation
- **Current system:** MM ≈ 10 [illustrative; see equations.yaml::MM] (90% collective creation)

**Falsification:** Compare FRED MULT series (actual money multiplier) to theoretical 1/reserve_requirement. If actual multiplier is significantly lower, collective-creation fraction is below theoretical maximum. **Data API:** FRED series MULT, REQRESNS.

-----

### Equation 9: Infrastructure Socialist Subsidy

**Definition:**

```
Infrastructure Subsidy Ratio (ISR) = Market Value of Public Infrastructure Used / Cost Paid

For typical business:
Roads used: Market value $100K/year
Actually paid: $0 (free public roads)
ISR = ∞ (infinite subsidy)

Police protection: Market value $50K/year
Actually paid (via taxes): $5K/year
ISR = 50/5 = 10 (10x subsidy)

Courts for contracts: Market value $200K/year
Actually paid: $10K/year
ISR = 200/10 = 20 (20x subsidy)
```

**Total Business Socialist Subsidy:**

```
All collective infrastructure used vs. all payments
Average ISR for typical business: 5-20x
(Receives 5-20x more value than pays)

= Significant collective subsidy to nominally private business
```

**Falsification:** For a specific business, compute market-equivalent cost of all public services used (private road tolls, private security, private arbitration, private education of workforce). Compare to taxes and fees paid. If ISR < 2, the business pays near market value. **Data API:** FHWA Highway Statistics, IRS Statistics of Income, BEA NIPA Table 3.16.

-----

## Composite Indices

### Overall Socialist Dependence Index (OSDI)

**Combines multiple factors:**

```
OSDI = (SID × 0.3) + (MSI × 0.2) + (ISR × 0.2) + (BSC × 0.15) + (MM × 0.15)

Where each component normalized 0-1

For typical large corporation:
SID = 0.6 (60% collective infrastructure dependence)
MSI = 0.98 (98% socialist money)
ISR = 0.8 (normalized infrastructure subsidy)
BSC = 0.7 (high bailout probability)
MM = 0.9 (90% collective money creation)

OSDI = (0.6×0.3) + (0.98×0.2) + (0.8×0.2) + (0.7×0.15) + (0.9×0.15)
OSDI = 0.18 + 0.196 + 0.16 + 0.105 + 0.135
OSDI = 0.776

OSDI = 0.776 (77.6% collective-infrastructure dependency)
```

**Interpretation:**

- **OSDI > 0.7:** Predominantly collective-dependent system
- **Current US economy:** OSDI ≈ 0.75-0.80 [illustrative; computed from illustrative MSI/SID/ISR/BSC/MM via the OSDI weighting in equations.yaml]
- **Observation:** System measures as 75-80% collectively dependent; conventionally labeled “capitalist”

**Falsification:** Compute OSDI under alternative weight schemes (equal weighting, PCA-derived weighting). If OSDI < 0.5 under any reasonable weighting, the conclusion of majority collective dependency does not hold. See `data/sensitivity_analysis.py` for Monte Carlo analysis across weight and component ranges.

-----

## Wealth Flow Equations

### Equation 10: Upward Wealth Flow Rate

**Definition:**

```
Upward Flow Rate (UFR) = d(Top 1% Wealth)/dt / d(Bottom 50% Wealth)/dt

Measures relative rate of wealth accumulation

If UFR > 1: Wealth flowing upward (extraction)
If UFR < 1: Wealth flowing downward (redistribution)
If UFR = 1: Wealth distributed equally
```

**US Historical Data:**

```
1960: UFR ≈ 2  [illustrative; for measured see FRED WFRBST01134 / WFRBSB50215 ratio]
1980: UFR ≈ 5  [illustrative; Reagan-era acceleration]
2000: UFR ≈ 10 [illustrative; financial-era acceleration]
2020: UFR ≈ 30 [illustrative; for measured see FRED top-1pct vs bottom-50pct share series]

Trend: Accelerating upward concentration
```

**Directional flow analysis:**

```
If system redistributes wealth downward:
- UFR < 1 expected (downward flow)
- Measured: UFR >> 1 (upward flow)

Measured direction of wealth flow is upward, not downward.
```

**Falsification:** Compute year-over-year change in top 1% and bottom 50% wealth shares from FRED or WID data. If UFR < 1 for a sustained period, wealth is flowing downward. **Data API:** FRED series WFRBST01134 (top 1% share), WFRBSB50215 (bottom 50% share), World Inequality Database API.

-----

### Equation 11: Labor Value Extraction Rate

**Definition:**

```
Extraction Rate (ER) = (Revenue - Labor Costs) / Revenue

Example:
Company revenue: $10M
Worker wages: $4M
ER = (10M - 4M) / 10M = 0.6

60% of value created by labor goes to capital
```

**Historical Trend:**

```
1960: ER ≈ 0.35 [illustrative; for measured see BLS PRS85006173 (labor share)] (65% to labor)
1980: ER ≈ 0.45 [illustrative] (55% to labor)
2000: ER ≈ 0.55 [illustrative] (45% to labor)
2024: ER ≈ 0.65 [illustrative; BLS PRS85006173 + FRED COE / CP] (35% to labor)

Trend: Increasing extraction from labor
```

**Smith’s Prediction:**

- Competitive markets should decrease ER (labor gets more)
- **Actual:** ER increasing (capital extracts more)
- **Observation:** Trend diverges from Smith’s competitive-market prediction

**Falsification:** Compute ER = 1 - (BLS labor share / 100) for nonfarm business sector. If ER < 0.35 (labor share > 65%), the system is within the labor-favored threshold. Track trend direction. **Data API:** BLS series PRS85006173, FRED series ULCNFB.

-----

## Market Concentration Equations

### Equation 12: Monopoly Power Index

**Definition:**

```
Herfindahl-Hirschman Index (HHI) = Σ(Market Share%)²

Perfect competition: HHI < 1,500
Moderate concentration: HHI 1,500-2,500
High concentration: HHI > 2,500
Monopoly: HHI = 10,000
```

**US Industry Examples:**

```
Search engines: HHI ≈ 6,500 [illustrative; for measured see Census Economic Census 2017 by NAICS, Statcounter market-share data] (Google dominance)
Social media: HHI ≈ 5,000 [illustrative; Statista / Pew] (Meta/Facebook dominance)
Retail: HHI ≈ 3,200 [illustrative; Census Economic Census 2017 NAICS 44-45] (Amazon/Walmart)
Pharmaceuticals: HHI ≈ 2,800 [illustrative; Census Economic Census 2017 NAICS 325412] (oligopoly)
Airlines: HHI ≈ 3,000 [illustrative; BTS T-100 segment data] (oligopoly)

Average across major industries: HHI ≈ 3,500 [illustrative; arithmetic mean of above values]
```

**Interpretation:**

- **Smith’s capitalism:** HHI should be low (competition)
- **Actual system:** HHI high (concentrated power)
- **Observation:** Concentration levels exceed Smith's competitive-market thresholds

**Falsification:** Compute HHI by NAICS industry code using Census Economic Census concentration data. If average HHI across major industries < 1,500, the system is within competitive thresholds. **Data source:** Census Economic Census (published every 5 years), DOJ/FTC merger guidelines for official thresholds.

-----

## Temporal Analysis: Definition Drift

### Equation 13: Semantic Drift Rate

**Definition:**

```
Semantic Drift (SD) = |Definition(t2) - Definition(t1)| / Time elapsed

Measures how fast a term's meaning changes
```

**“Capitalism” Drift:**

```
1960 definition emphasis: Hard work, production, merit = 70%
2024 definition emphasis: Investment returns, passive income = 70%

SD = |70% - 70%| / 64 years = 2.2% per year shift

Meaning inverted completely over 64 years at 2.2%/year
```

**Why This Matters:**

- Semantic drift introduces measurement instability in term-based analysis
- Mathematical definitions remain invariant over time
- Equations provide temporally stable measurement baselines

**Falsification:** Using diachronic word embeddings (e.g., Stanford HistWords), compute cosine distance between the embedding of "capitalism" at decade intervals. If drift rate is near zero, the term's meaning is stable. Compare to mathematical term drift rates as control. **Data source:** Google Ngrams API, Stanford HistWords, COHA corpus.

-----

## The Ultimate Test: Adam Smith Compliance

### Smith’s Capitalism Scorecard

**Using equations to test if system matches Smith’s vision:**

|Criterion         |Smith’s Expectation|Mathematical Test  |Current Score|
|------------------|-------------------|-------------------|-------------|
|Competition       |HHI < 1,500        |HHI ≈ 3,500        |❌ FAIL       |
|Labor rewarded    |ER decreasing      |ER increasing      |❌ FAIL       |
|Merit-based       |LWR increasing     |LWR decreasing     |❌ FAIL       |
|Production focus  |VE/VL < 0.1        |VE/VL > 0.3        |❌ FAIL       |
|No rentiers       |WO/WL < 1          |WO/WL > 4          |❌ FAIL       |
|Risk/reward align |RI ≈ 1             |RI > 4             |❌ FAIL       |
|Free markets      |Low regulation     |High HHI + bailouts|❌ FAIL       |
|Minimal extraction|UFR ≈ 1            |UFR ≈ 30           |❌ FAIL       |

**Smith Compliance Score: 0/8 (0%)** [illustrative; the "Current" values in the table above are illustrative — see equations.yaml + data/fetch_and_compute.py for the measurement procedure per equation]

By Smith’s criteria, the current system scores 0/8 — structurally closer to mercantilism than to Smith’s competitive capitalism.

-----

## Comparison Matrix: Oligarchic vs. Democratic Socialism

**Using equations to compare systems:**

|Measure|Oligarchic Socialism (Current)|Democratic Socialism |Pure Capitalism (Smith)|
|-------|------------------------------|---------------------|-----------------------|
|SID    |0.75 (75% collective)         |0.75 (75% collective)|0.10 (10% collective)  |
|DI     |High (wealth = power)         |Low (equal power)    |Medium (merit)         |
|RI     |4.0 (workers 4x risk)         |1.0 (equal risk)     |1.0 (risk=reward)      |
|UFR    |30 (upward flow)              |1.0 (balanced)       |1.0 (merit-based)      |
|BSC    |3.5 (bailout rich)            |Equal for all        |0 (no bailouts)        |
|HHI    |3,500 (concentrated)          |Variable             |<1,500 (competitive)   |
|ER     |0.65 (high extraction)        |0.40 (fair split)    |0.30 (labor favored)   |

**Structural comparison:**

- **Current system:** High collective dependency (OSDI ≈ 0.77 [illustrative]), high power concentration (DI → ∞ [illustrative])
- **Democratic alternative:** High collective dependency, low power concentration (DI → 0)
- **Smith’s competitive capitalism:** Low collective dependency (OSDI < 0.2), moderate power distribution

-----

## Application Examples

### Example 1: Is Private Equity “Capitalist”?

**Mathematical Analysis:**

```
VE/VL Ratio:
- PE extracts $200M in fees
- Company workers create $500M value
- VE/VL = 200/500 = 0.40

Smith's Test: VE/VL should be < 0.1
Result: 0.40 >> 0.1
Conclusion: EXTRACTION (mercantilism), not capitalism

SID (Socialist Dependency):
- Uses collective bank deposits: +0.8
- Uses legal system: +0.1
- Uses currency system: +0.1
- SID = 1.0

Conclusion: 100% dependent on socialist systems

RI (Risk Distribution):
- PE partners: Limited liability, diversified
- Workers: Full job loss risk, concentrated
- RI = 5.0 (workers bear 5x risk)

Summary: VE/VL = 0.40, SID = 1.0, RI = 5.0 — high extraction, full collective dependency, asymmetric risk distribution
```

-----

### Example 2: Is a Worker Cooperative “Socialist”?

**Mathematical Analysis:**

```
SID (Infrastructure Dependency):
- Uses roads, courts, etc.: 0.6
- Same as corporate business

DI (Democracy Index):
- One worker, one vote
- DI = Low (democratic)
- vs. Corporate DI = High (oligarchic)

RI (Risk Distribution):
- Workers own, workers risk: RI = 1.0
- Aligned risk/reward

VE/VL Ratio:
- Workers own output
- VE/VL ≈ 0 (no external extraction)

UFR (Wealth Flow):
- Wealth stays with creators
- UFR ≈ 1.0 (no upward extraction)

Summary: Same SID as corporations (0.6), but DI → 0, RI = 1.0, VE/VL ≈ 0.
Structurally closer to Smith's risk/reward alignment than conventional corporate form.
```

-----

### Example 3: Defense Contractor Analysis

**Mathematical Analysis:**

```
SID = 1.0 (100% government funded)
MSI = 1.0 (uses government money)
BSC = High (guaranteed profits)
DI = N/A (no market)

Socialist Index Score: 1.0 (pure socialist enterprise)

Summary: SID = 1.0, MSI = 1.0 — fully collectively funded with private profit extraction layer
```

-----

### Example 4: Worked Application — Automation Deployment Audit

A worked application of this framework to autonomous-trucking
deployment claims lives in `automation_scope_audit/`. That folder
contains 84 falsifiable claims (C000-C083) deriving from the canonical
equations above and from additional substrate-primary, institutional,
energy-accounting, and credential-inversion layers. Representative
cross-references from Equations 1-13 to the audit claim set:

- **Equation 2 (SID)** → C003 infrastructure precondition (per-route-mile
  capex with existing-state discounts)
- **Equation 3 (Risk Distribution)** → C015 liability void (7-participant
  autonomous-incident chain)
- **Equation 11 (Extraction Rate)** → C002 hidden labor offload
  (20-task automation_status inventory)
- **Equation 1 (Value Creation/Extraction)** → C058 deferred maintenance
  liability (catastrophic-failure rate increase when human inspection
  is eliminated)
- **Equation 13 (Semantic Drift)** → C006/C007 scope collapse and
  threat-narrative detection
- **Equation 12 (HHI)** → C022/C024 institutional lock-in + collapse
  cycle

Beyond these, the package adds claims on substrate care (C060-C064),
credential inversion (C065-C069), adoption-curve thermodynamics
(C070-C072), lifecycle design (C073-C074), training-corpus dynamics
(C076-C079), and cross-domain empirical validation (C080-C083).

The audit ships with a paired contrast: a "works case"
(`examples/kodiak_atlas_permian.py` — consolidated frac-sand corridor)
and a "fails case" (`examples/dispersed_wellsite.py` — dispersed
small-pad service). See `automation_scope_audit/README.md` for the
full claim table, `ARCHITECTURE.md` for the 6-layer coupling cycle,
and `addendum-4.md` (at repo root) for how the audit fits the
broader framework.

-----

## Predictive Models

> **Open research area.** Earlier drafts of this section included two
> composite predictive equations (a "stability" formula and a "time-to-
> collapse" formula) that combined ratios, scalars, and rates without
> dimensional consistency, and compared the resulting scalars to
> unsourced historical estimates for the French Revolution and the
> Russian Revolution. Per external audit (DeepSeek, Perplexity) and
> the `AUDIT_TASKS_HARDENING.md` H1.1 / H1.2 disposition, both
> equations have been withdrawn. The descriptive equations (1-13)
> measure current structural state; predicting *transition timing*
> requires additional empirical work that is not yet done here.
>
> Starter design (regression of measured pre-instability indicators
> against documented unstable periods 1789, 1917, 1929, 2008, plus
> stable controls) and a literature pointer list are in
> `data/stability_research_notes.md`. Contributions welcome; the
> requirement is that any new predictive equation be (a) dimensionally
> consistent, (b) validated against documented historical instability
> events within a stated tolerance band, and (c) accompanied by an
> explicit falsifier.

-----

## Summary of Illustrative Values

> All numerical values in this section are **illustrative**. They
> demonstrate the framework's methodology with order-of-magnitude
> examples consistent with the published data sources named in
> `equations.yaml`. For audited measured values, run
> `data/fetch_and_compute.py` against the cited FRED / BLS / Census
> series and substitute the results.

### Quantitative Results (illustrative)

1. **Collective dependency: OSDI ≈ 0.77** [illustrative] (75-80% collective infrastructure)
- Money creation: MSI = 0.98 [illustrative]
- Infrastructure dependency: SID = 0.60-0.75 [illustrative]
- Banking collective creation: MM ≈ 10 [illustrative] (90% collectively originated)
1. **Smith compliance: 0/8 criteria met** [illustrative]
- ER increasing (extraction rising) [illustrative trend; see BLS PRS85006173]
- HHI increasing (concentration rising) [illustrative trend; see Census Economic Census time series]
- LWR decreasing (labor share declining) [illustrative trend; see BLS PRS85006173]
1. **Power distribution: highly concentrated** [illustrative]
- DI ≈ 100,000:1 ratio [illustrative]
- RI ≈ 4:1 [illustrative] (risk borne disproportionately by labor)
- UFR ≈ 30:1 [illustrative] (wealth accumulation rate ratio)
1. **Extraction indicators elevated** [illustrative]
- VE/VL > 0.3 [illustrative]
- ER trending upward [illustrative trend]
- UFR = 30 [illustrative]

### Measurement-Based Characterization

Based on the above measurements, the current system characterizes as:

- **77% collectively dependent** (OSDI)
- **0% Smith-compliant** (scorecard)
- **High power concentration** (DI)
- **Extraction-dominant** (VE/VL, ER, UFR)

**Measurement-derived label:** High collective dependency with concentrated control and elevated extraction

**Conventional label:** “Capitalism”

The measurements and the label describe different structural properties.

-----

## Why Equations Over Labels

### Properties of mathematical measurement

1. **Consistency:** Equations produce the same output for the same input
1. **Verifiability:** Any observer can reproduce the calculation
1. **Precision:** Quantitative values reduce ambiguity
1. **Temporal stability:** Mathematical definitions do not drift
1. **Falsifiability:** Measured values can be challenged with counter-measurements

### Properties of semantic labels

1. **Variable:** Definitions shift across time and context
1. **Ambiguous:** Multiple interpretations coexist
1. **Unfalsifiable:** Label disputes cannot be resolved by measurement
1. **Temporally unstable:** SD equation measures this drift directly

### Recommended measurements

For any economic system, measure:

- SID (collective dependence)
- RI (risk distribution)
- UFR (wealth flow direction)
- DI (power concentration)
- ER (extraction rate)

These quantities are observable, falsifiable, and independent of labeling conventions.

-----

## Conclusion

### Measured System Properties

The quantitative analysis yields the following illustrative
measurements (all values **illustrative** unless a primary-source
tag is given; substitute audited values from
`data/fetch_and_compute.py` for production use):

1. **Collective infrastructure dependency: 75-80%** [illustrative]
- OSDI ≈ 0.77 [illustrative]
- MSI ≈ 0.98 [illustrative]
- MM ≈ 10 [illustrative]
1. **Smith compliance: 0/8 criteria** [illustrative]
- ER increasing (Smith predicts decreasing) [illustrative trend; see BLS PRS85006173]
- HHI increasing (Smith predicts decreasing) [illustrative trend; see Census Economic Census time series]
- LWR decreasing (Smith predicts increasing) [illustrative trend]
- Rentier fraction growing (Smith predicts shrinking) [illustrative trend]
1. **Power concentration: high** [illustrative]
- DI ≈ 100,000:1 [illustrative]
- UFR ≈ 30:1 [illustrative]
- RI ≈ 4:1 [illustrative]
- ER ≈ 0.65 [illustrative]

### Structural Observation

The illustrative values indicate (substitute audited measurements for
final analysis):

- Current system ≠ Smith’s capitalism (0/8 criteria) [illustrative]
- Current system OSDI ≈ 0.77 [illustrative] (high collective dependency)
- Current system VE/VL > 0.3 [illustrative] (extraction-dominant)

The gap between (illustrative) measured structure and conventional
label is large enough that the structural conclusion does not depend
on the precise values — audited measurements within ±20% of the
illustrative values reach the same conclusion under
`data/sensitivity_analysis.py`.

### The Measurement-Based Question

Given OSDI ≈ 0.77 [illustrative], the system is already predominantly collectively dependent. The structurally relevant variable is not the degree of collective dependency but who controls it:

- Current DI → ∞ (concentrated control)
- Alternative DI → 0 (distributed control)

The equations measure structural properties independent of labeling conventions. The debate over labels obscures the measurable variable: the distribution of control over collectively dependent systems.

-----

## Limitations and Assumptions

### What this framework assumes

1. **Measurability:** All variables (VE, VL, C, P, etc.) can be quantified with sufficient precision for structural characterization. In practice, some variables (influence multipliers, market-equivalent values of public services) require estimation with acknowledged uncertainty.

2. **Threshold choices:** The classification thresholds (VE/VL < 0.1, SID > 0.5, HHI < 1,500, etc.) are stated as reference points, not empirically derived boundaries. Different threshold choices can change classifications without changing measured values. See `data/sensitivity_analysis.py` for analysis of threshold sensitivity.

3. **OSDI weighting:** The composite index weights (0.3/0.2/0.2/0.15/0.15) are not empirically optimized. They represent an initial allocation subject to sensitivity analysis. Results are robust to moderate perturbation but the specific OSDI value should be interpreted as approximate.

4. **Illustrative values:** The numerical examples in this document use illustrative values to demonstrate methodology. Empirically grounded values require data from the sources listed in `equations.yaml` and computed via `data/fetch_and_compute.py`.

5. **Static analysis:** These equations measure current-state properties. They do not model dynamic transitions, feedback loops, or path dependencies between states. The predictive models (stability, collapse timeline) are structural extrapolations, not calibrated forecasts.

### What this framework does not do

- **Prescribe policy:** Measurements characterize structure; they do not determine what structure is desirable. The framework measures what *is*, not what *ought to be*.
- **Replace ethical reasoning:** Measured values inform but do not substitute for normative judgment about fairness, justice, or human flourishing.
- **Eliminate subjectivity:** Variable definitions, threshold choices, and weight selections involve judgment. The framework makes these choices explicit and testable rather than implicit.
- **Claim completeness:** These 13 equations do not capture all economically relevant variables. They measure a specific set of structural properties; other frameworks (ecological economics, biophysical economics, thermoeconomics) measure complementary properties.

### Related frameworks

- **Thermoeconomics** (Georgescu-Roegen, 1971): Entropy-based analysis of economic processes
- **Biophysical economics** (Hall & Klitgaard, 2012): Energy return on investment (EROI) as economic constraint
- **Ecological economics** (Daly, 1991): Steady-state economics within planetary boundaries
- **World-systems analysis** (Wallerstein, 1974): Core-periphery extraction patterns

### Data sources and reproducibility

All equations reference specific, publicly available data sources with API endpoints documented in `equations.yaml`. Computation scripts are provided in `data/` for independent verification. See `data/README.md` for setup instructions.

### Companion folders

- **`accounting/`** — domain-agnostic composable audit primitives with their own claim families (AA-1..5 atomic-accounting closure test, GM-1..5 GDP-metrology political-invariant test, SP-1..5 substrate-parity audit). Prefixes intentionally do not enter the C-series. See `accounting/CLAIMS.md`.
- **`automation_scope_audit/`** — 84 falsifiable claims (C000-C083) about autonomous-trucking ROI, organized across 23 modules, each with a measurable threshold and single-sentence falsifier. Cross-references the 13 canonical equations above through `equations.yaml::automation_scope_audit_claims:`. See `automation_scope_audit/README.md`.
- **`audit/`** — broader audit / accountability / certification framework. Includes `autonomous_freight_audit.py` (Class-1-corridor constraint layers), `efficiency_report_audit.py` (Six-Sigma audit on industry archetypes), and the field_system / scope_audit / metabolic / money-signal / investment-signal bridges.
- **`calibration/`** — falsifiable diagnostic suite (5 dimensions, GREEN/YELLOW/RED/EXTINCT bands, 11 falsification tests).
- **`core/`** — vendored TAF physical sub-models (fatigue, human-system-collapse, heat-leak).
- **`labor_thermodynamics/`** — five compounding labor-measurement failure modes.
- **`substrate_accounting/`** — cross-substrate translation and unified-claims index.
- **`vehicle_audit/`** — Producer / Accumulator architecture for autonomous-vehicle audit cascade (distinct from `automation_scope_audit/`; see `automation_scope_audit/RELATION.md`).
- **`physics_guard/`** — vendored snapshot fieldlinked one-way through the bridges in `audit/`.

-----

*This framework measures structural properties of economic systems — energy flows, resource dependencies, risk distributions, and power concentrations — using falsifiable equations. Each equation includes a falsification method and data source references. The measurements characterize the current system as predominantly collectively dependent, extraction-dominant, and highly concentrated in control. Threshold choices, weighting assumptions, and illustrative values are documented and subject to sensitivity analysis.*
