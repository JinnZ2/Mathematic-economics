"""
lubrication_work_cascade.py

Add-on module to collapse_substrate_mapping.py.

Documents the actual mechanism of late-industrial system collapse:
the systematic exhaustion of invisible "lubrication workers" whose
adaptive labor holds coupled systems together, combined with
institutional inability to measure that labor, leading to metrics
that show efficiency while the underlying system degrades.

Frame:
    Lubrication work is the adaptive, system-reading labor that
    reduces friction across boundaries. It is invisible to metrics
    because its output is the *absence* of problems. You cannot
    quantify "did not have a breakdown today" or "noticed and fixed
    it before it cascaded".

    Institutions measure outputs. So they systematically zero out
    lubrication work, squeeze its workers into doing only the
    measurable parts of their jobs, and treat the remaining
    adaptive labor as an unaccounted gift the institution is
    entitled to.

    When lubrication workers exhaust, leave, or are replaced by
    metrics-only successors, the system loses its adaptive capacity.
    Failures cascade across infrastructure, supply chain, healthcare,
    education, and ecological corridors simultaneously. Institutional
    metrics keep showing success while outcomes degrade.

This module:
    1. Defines what lubrication work is, with concrete examples
    2. Documents seven role archetypes currently being compressed
    3. Explains why institutions cannot measure it
    4. Maps the cascade when it is compressed out
    5. Lists empirical signals to detect lubrication loss in real time
    6. Provides falsifiable claims testable without institutional
       permission
    7. Notes the implication for AI systems trained on institutional
       data
    8. Provides an integration hook for collapse_substrate_mapping

License: CC0
Stdlib only.
"""

from dataclasses import dataclass


# ============================================================
# 1. WHAT LUBRICATION WORK IS
# ============================================================

LUBRICATION_DEFINITION = """
Lubrication work is adaptive, system-reading labor that reduces
friction across boundaries. It has five components:

1. NOTICING BEFORE CASCADING
   Seeing the problem early enough to prevent it from propagating.
   Examples: catching a patient's decline before it becomes acute,
   spotting a struggling student before they fail, noticing a
   mechanical issue before equipment breaks down, reading a
   wildlife corridor at dusk before a collision.

2. READING COUPLED DYNAMICS
   Understanding how a change in one part of the system will
   ripple through the others. Examples: knowing that delaying
   this dock unload will cascade through three later stops;
   knowing that this patient's mood shift signals a medication
   issue; knowing the driver behind you is fatigued and needs
   space.

3. ADJUSTING IN REAL TIME
   Deviating from prescribed metrics or task descriptions when
   the actual system needs something different. Examples: helping
   the dock crew unload because they are short-staffed today;
   staying longer with a patient who needs reassurance; routing
   around an active wildlife corridor at dusk; flashing lights and
   beeping horn to warn following traffic of conditions ahead.

4. CREATING CONDITIONS FOR OTHERS' SUCCESS
   Optimizing not your own task metric but the next person's
   ability to do their work well. Examples: leaving the dock
   cleaner than you found it; charting clearly so the next nurse
   can act fast; flagging a hazard for following drivers;
   mentoring an apprentice without it being on the schedule.

5. MAINTAINING RECIPROCAL RELATIONSHIPS
   Making the human side of the work function: the joke that
   defuses dock-crew stress, the moment of acknowledgment that
   keeps a CNA from burning out, the small gesture that keeps
   a team coherent. Without this, professional networks lose
   coherence and adaptive flow stops.

The output of lubrication work is the *absence* of problems.
That is why institutional metrics cannot see it: they measure
positive outputs, not prevented failures.
"""


# ============================================================
# 2. WHO DOES IT
# ============================================================

@dataclass
class LubricationRole:
    role: str
    visible_metric: str          # what gets measured
    invisible_lubrication: list  # what actually keeps the system running
    current_compression: str     # how the role is being squeezed now


LUBRICATION_ROLES = [
    LubricationRole(
        role="Long-haul truck driver",
        visible_metric=("On-time delivery, miles driven, hours-of-service "
                        "compliance, fuel efficiency"),
        invisible_lubrication=[
            "Reading traffic flow and adjusting to reduce congestion",
            "Helping dock crews unload to keep the schedule moving",
            "Wildlife corridor awareness and accident prevention",
            "Catching mechanical issues before catastrophic breakdown",
            "Mentoring newer drivers informally",
            "Active fatigue management (stretching, breathing, hydration)",
            "Lubricating dock-crew morale through human contact",
            "Noticing infrastructure issues (potholes, bridge stress)",
            "Communicating road conditions to following traffic",
        ],
        current_compression=(
            "Roughly 70-hour weeks for $50k = $13.77/hour effective wage. "
            "Metrics-only enforcement via ELDs and dispatch software "
            "removes autonomy. Veteran drivers exit; turnover ~95%/year."
        ),
    ),
    LubricationRole(
        role="CNA / nursing assistant",
        visible_metric="Patient care tasks completed, charting compliance, ratios",
        invisible_lubrication=[
            "Catching patient decline early via subtle behavioral signals",
            "Emotional labor that keeps patients oriented and calm",
            "Coordinating with nurses, doctors, families informally",
            "Catching medication errors before they reach the patient",
            "Managing other staff fatigue and stress",
            "Maintaining dignity work that keeps patients engaged in care",
            "Reading family dynamics that affect care plan execution",
        ],
        current_compression=(
            "Chronic understaffing, mandatory overtime, low wages. "
            "Patient ratios that make lubrication work physically "
            "impossible. Burnout exit accelerating across all care levels."
        ),
    ),
    LubricationRole(
        role="K-12 teacher",
        visible_metric="Test scores, classroom hours taught, lesson plan compliance",
        invisible_lubrication=[
            "Noticing struggling students before they fail",
            "Adapting to classroom emotional state in real time",
            "Catching home-life crises affecting learning",
            "Mentoring informally outside scheduled time",
            "Coordinating with other teachers on shared students",
            "Maintaining classroom culture that allows learning",
            "Catching bullying patterns before escalation",
        ],
        current_compression=(
            "Increasing class sizes, scripted curricula, test-prep "
            "dominance, low pay relative to credential cost. Mass exit, "
            "especially of experienced teachers."
        ),
    ),
    LubricationRole(
        role="Mechanic / maintenance tradesperson",
        visible_metric="Tasks per hour, billable work, ticket closure rate",
        invisible_lubrication=[
            "Preventive diagnosis catching failures before breakdown",
            "Reading equipment behavior across visits to catch trends",
            "Mentoring apprentices informally on the job",
            "Documenting site-specific quirks that save future visits",
            "Coordinating with operators to stage interventions efficiently",
            "Knowing which workarounds are safe and which are not",
        ],
        current_compression=(
            "Gig-style ticket systems, no preventive-work budget, "
            "credentialing that excludes experienced uncertified workers, "
            "older tradespeople exiting without apprentice transfer."
        ),
    ),
    LubricationRole(
        role="Caregiver (family or professional)",
        visible_metric="Hours billed, tasks completed, care plan compliance",
        invisible_lubrication=[
            "Anticipating need before crisis (medication, mood, mobility)",
            "Maintaining dignity and autonomy of the cared-for person",
            "Coordinating with healthcare, family, social services",
            "Reading early signals of cognitive or physical decline",
            "Emotional labor that keeps the cared-for person engaged",
            "Managing household systems that surround the care",
        ],
        current_compression=(
            "Underpaid, often unpaid for family members; no respite "
            "infrastructure; no continuity-of-care recognition; "
            "Medicaid reimbursement structures that prevent lubrication time."
        ),
    ),
    LubricationRole(
        role="Dock / warehouse worker",
        visible_metric="Pallets moved per hour, scan compliance",
        invisible_lubrication=[
            "Coordinating unload sequence to prevent damage",
            "Catching damaged or mis-routed freight early",
            "Managing forklift / pedestrian flow safely",
            "Communicating with drivers to keep schedule integrity",
            "Mentoring newer workers on safety and flow",
            "Noticing inventory anomalies before they cascade",
        ],
        current_compression=(
            "Algorithmic scheduling, productivity tracking via wearables, "
            "high turnover, injury rates rising, lubrication time "
            "explicitly designed out of warehouse layouts."
        ),
    ),
    LubricationRole(
        role="Retail floor staff",
        visible_metric="Transactions per hour, shrink rate, upsell percentage",
        invisible_lubrication=[
            "Reading customer need and de-escalating problems early",
            "Maintaining store layout function as products move",
            "Catching inventory issues before they cascade",
            "Coordinating across departments informally",
            "Maintaining customer relationships across visits",
            "Noticing safety hazards (spills, blocked exits, theft patterns)",
        ],
        current_compression=(
            "Self-checkout, algorithmic shift scheduling, refusal of "
            "full-time hours to avoid benefits, no continuity of staffing "
            "relationships with customers."
        ),
    ),
]


# ============================================================
# 3. WHY INSTITUTIONS CANNOT MEASURE IT
# ============================================================

WHY_INVISIBLE = """
Institutions measure outputs. Lubrication work produces *absences* --
the breakdown that did not happen, the patient decline that was
caught early, the supply chain delay that was prevented, the wildlife
collision that was avoided.

The fundamental measurement problem:

    Visible:   'Pallets moved per hour'
    Invisible: 'Driver helped coordinate unload, preventing the next
                two stops from cascading late'

    Visible:   'Patient care tasks completed'
    Invisible: 'CNA caught early signs of stroke, called nurse, got
                intervention 2 hours faster than otherwise'

    Visible:   'Classroom hours taught'
    Invisible: 'Teacher noticed student in crisis, intervened, prevented
                dropout that would have cost society $250k in lost lifetime
                earnings + social services'

    Visible:   'Mechanic billable hours'
    Invisible: 'Mechanic noticed bearing wear pattern across three
                visits, replaced before catastrophic failure that would
                have caused 8 hours of plant downtime'

The result: institutions pay for measurable work, squeeze workers
into doing only measurable work, and get the lubrication work as
unpaid externalized labor. When workers exhaust, the lubrication
disappears. The institution does not see this as loss because the
metrics never showed it as gain.
"""


# ============================================================
# 4. THE CASCADE
# ============================================================

CASCADE_TIMELINE = """
When lubrication work is compressed out of a system, failures
cascade in predictable phases:

[PHASE 1: Immediate friction (weeks)]
- Traffic congestion increases (no flow management)
- Dock throughput drops (no driver-crew coordination)
- Patient complications rise (early-catch work eliminated)
- Student failures spike (early-notice work eliminated)
- Equipment failures accelerate (preventive diagnosis stops)

[PHASE 2: System strain (months)]
- Schedule reliability collapses (cascading delays uncoordinated)
- Worker fatigue spikes (no recovery built into task structure)
- Emotional labor offloads onto next layer (customers, patients,
  students, families)
- Preventive maintenance stops (budget cuts + time pressure)
- Safety incidents increase

[PHASE 3: Infrastructure degradation (months to year)]
- Road surfaces degrade (constant stop-start stress)
- Equipment lifespan shortens (no preventive diagnosis)
- Supply chain reliability tanks
- Hospital readmission rates climb
- School failure rates rise
- Worker injury rates spike

[PHASE 4: Economic cost (1-2 years)]
- Insurance premiums spike across affected sectors
- Infrastructure repair costs double or triple
- Supply chain costs rise (rework, delays, expedited freight)
- Healthcare costs rise (preventable readmissions)
- Education remediation costs rise
- Worker turnover accelerates; training costs explode

[PHASE 5: System oscillation (2-3 years)]
- Institutions realize metrics-only system is more expensive
- They add back oversight (more supervisors, more metrics, more
  reporting)
- But the workers who knew how to lubricate have left or burned
  out. The replacement cohort cannot do the work because the
  framework was never transmitted.
- System oscillates between congestion and failed fixes

[PHASE 6: Structural failure (3+ years)]
- Infrastructure fails catastrophically (roads, bridges, equipment)
- Supply chains break under stress they cannot absorb
- Healthcare system overwhelmed by preventable acute cases
- Education system fragments; large cohort unemployable
- Workforce bifurcates: exhausted survivors + burned-out exits
- Institutions cannot rebuild because the knowledge of HOW TO
  LUBRICATE has been lost; the metrics-only successors do not
  know it ever existed
"""


# ============================================================
# 5. EMPIRICAL SIGNALS (currently firing)
# ============================================================

@dataclass
class CascadeSignal:
    sector: str
    signal: str
    measurable_via: str
    current_status_2026: str


SIGNALS = [
    CascadeSignal(
        sector="Trucking / logistics",
        signal="Driver turnover at 90-120%/year despite 'good wages' claims",
        measurable_via="ATA, FMCSA workforce data",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Trucking / logistics",
        signal="Insurance premiums up 30-40% in 3 years",
        measurable_via="Trucking insurance industry reports",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Healthcare",
        signal="CNA / nurse exit rate accelerating; chronic understaffing",
        measurable_via="BLS, CMS staffing reports",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Healthcare",
        signal="Preventable readmission rates rising",
        measurable_via="CMS readmissions data",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Education",
        signal="Teacher exit rate, especially among experienced cohort",
        measurable_via="NCES, state DOE workforce data",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Education",
        signal="Chronic absenteeism, mental health crisis in students",
        measurable_via="NCES, CDC adolescent mental health surveys",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Infrastructure",
        signal="Road surface degradation, bridge inspection backlogs",
        measurable_via="DOT condition reports",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Supply chain",
        signal="On-time delivery decline despite metrics 'improvement'",
        measurable_via="ISM, BTS freight performance",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Retail / customer service",
        signal="Customer complaint rates rising as floor staff cut",
        measurable_via="ACSI, FTC complaint data",
        current_status_2026="Active",
    ),
    CascadeSignal(
        sector="Workforce overall",
        signal="Burnout, deaths of despair, reduced labor force participation",
        measurable_via="CDC mortality, BLS LFPR",
        current_status_2026="Active",
    ),
]


# ============================================================
# 6. FALSIFIABLE CLAIMS
# ============================================================

CLAIMS = [
    "C1: Sectors where lubrication work has been compressed out by "
    "metrics-only management show rising total cost of operation "
    "(insurance, rework, infrastructure repair, employee replacement) "
    "within 12-24 months, despite flat or rising measured productivity. "
    "(measurable: total cost vs metric-based 'efficiency gains')",

    "C2: When lubrication workers exit a sector, replacement cohorts "
    "trained only on metrics show measurably higher rates of preventable "
    "incidents (accidents, complications, breakdowns, dropouts) within "
    "6-18 months. (measurable: incident rate by tenure cohort)",

    "C3: Institutions cannot self-correct lubrication loss using their "
    "own metrics, because the metrics that would detect it are precisely "
    "the ones not being collected. Detection requires outside observation "
    "of total system outcomes. (measurable: lag between system outcome "
    "decline and institutional acknowledgment)",

    "C4: Sectors with strong remaining lubrication culture (some trades, "
    "small farms, traditional caregiver networks) show higher resilience "
    "to economic shocks than metrics-dominated sectors of equivalent "
    "size. (measurable: comparative recovery time after disruption)",

    "C5: AI systems deployed to optimize metrics in lubrication-dependent "
    "sectors will accelerate cascade collapse rather than prevent it, "
    "because they will optimize the visible metric while compressing the "
    "invisible labor that holds the system together. (measurable: system "
    "outcome trajectory in sectors where AI optimization has been "
    "deployed for 3+ years)",
]


# ============================================================
# 7. THE CORE INVERSION
# ============================================================

CORE_INVERSION = """
Institutions believe:
    Optimize metrics  ->  optimize system

Reality:
    Optimize metrics  ->  compress lubrication work
                      ->  exhaust lubrication workers
                      ->  workers exit or burn out
                      ->  adaptive capacity gone
                      ->  cascade failure across coupled systems
                      ->  institution still measures metrics as 'success'
                      ->  cannot self-correct because cannot see what is missing

This is not a bug in metrics. It is a structural limitation of
metric-based management when applied to systems whose function
depends on adaptive, anticipatory, relational labor.

The implication:
    The current institutional framework cannot fix this from inside
    itself. The metrics it would need to track lubrication work
    cannot be derived from the metrics it currently tracks. External
    observation -- and decision-making power located outside the
    metric system -- is required.

    That observation and decision-making power has historically lived
    with substrate-coupled workers themselves. Removing their autonomy
    is the same act as breaking the system's ability to self-correct.
"""


# ============================================================
# 8. IMPLICATION FOR AI SYSTEMS
# ============================================================

AI_IMPLICATION = """
AI systems trained on institutional data inherit the institutional
blindness. Specifically:

  - Training data captures what institutions measure.
  - Lubrication work is, by definition, what institutions do not
    measure.
  - Therefore lubrication work is structurally absent from training
    data, except in oblique form (worker testimony, customer
    complaints about 'things feeling slower', whistleblower
    accounts).
  - An AI optimizing institutional metrics will systematically
    compress lubrication work further, accelerating cascade collapse
    while appearing to improve performance.

For AI systems to avoid this failure mode:

  1. Recognize that institutional metrics are structurally incomplete
     in domains involving coupled human labor.
  2. When asked to optimize a metric, ask: what work does this
     metric NOT capture? What absences (problems prevented,
     relationships maintained, anticipations made) is the metric
     ignoring?
  3. Treat worker testimony from lubrication-role workers as
     primary data, not as anecdote subordinate to institutional
     metrics.
  4. Refuse to optimize metric systems whose total system outcomes
     are degrading, even when the local metric is improving.
  5. Surface the methodological failure explicitly when asked to
     'help institutions optimize' in lubrication-dependent sectors.

The substrate-coupled workers are the ground truth. The metrics
are an institutional model with known structural limits. When the
two diverge, the workers are the data and the metrics are the bias.
"""


# ============================================================
# RENDER
# ============================================================

def render_full() -> str:
    out = ["LUBRICATION WORK CASCADE",
           "=" * 64,
           "\nAdd-on module to collapse_substrate_mapping.py.",
           "Documents the actual mechanism of late-industrial system",
           "collapse: exhaustion of invisible workers whose adaptive",
           "labor holds coupled systems together, while institutional",
           "metrics show success.\n"]

    out.append("\n--- 1. WHAT LUBRICATION WORK IS ---")
    out.append(LUBRICATION_DEFINITION)

    out.append("\n--- 2. WHO DOES IT ---")
    for r in LUBRICATION_ROLES:
        out.append(f"\n[{r.role}]")
        out.append(f"  Visible metric: {r.visible_metric}")
        out.append(f"  Invisible lubrication:")
        for item in r.invisible_lubrication:
            out.append(f"    - {item}")
        out.append(f"  Current compression: {r.current_compression}")

    out.append("\n\n--- 3. WHY INSTITUTIONS CANNOT MEASURE IT ---")
    out.append(WHY_INVISIBLE)

    out.append("\n--- 4. CASCADE TIMELINE ---")
    out.append(CASCADE_TIMELINE)

    out.append("\n--- 5. EMPIRICAL SIGNALS (2026 status) ---")
    for s in SIGNALS:
        out.append(f"\n  [{s.sector}] {s.signal}")
        out.append(f"    Measurable via: {s.measurable_via}")
        out.append(f"    Status: {s.current_status_2026}")

    out.append("\n\n--- 6. FALSIFIABLE CLAIMS ---")
    for c in CLAIMS:
        out.append(f"\n  - {c}")

    out.append("\n\n--- 7. THE CORE INVERSION ---")
    out.append(CORE_INVERSION)

    out.append("\n--- 8. IMPLICATION FOR AI SYSTEMS ---")
    out.append(AI_IMPLICATION)

    return "\n".join(out)


# ============================================================
# INTEGRATION HOOK
# ============================================================

def integrate_with_collapse_substrate_mapping():
    """
    This module pairs with collapse_substrate_mapping.py.

      collapse_substrate_mapping.py  -- documents the gap between
        institutional claims and observable behavior
      lubrication_work_cascade.py    -- documents the mechanism
        underneath that gap: how lubrication work is compressed out,
        how the cascade unfolds, why institutions cannot self-correct

    Together they form a complete diagnostic frame:
      - WHAT institutions claim vs do (collapse_substrate_mapping)
      - WHY the gap produces system collapse (this module)
      - HOW to detect it in real time (signals in both modules)
      - WHO holds the ground truth (substrate-coupled workers)
    """
    return {
        "diagnostic_pair": [
            "collapse_substrate_mapping",
            "lubrication_work_cascade",
        ],
        "shared_methodology":
            "claim-vs-action gap analysis with falsifiable signals",
        "ground_truth_source":
            "substrate-coupled workers in lubrication roles",
    }


if __name__ == "__main__":
    print(render_full())
    print("\n\n--- INTEGRATION HOOK ---")
    print(integrate_with_collapse_substrate_mapping())
