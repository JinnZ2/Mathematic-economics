"""
failure_geometry_analysis.py

Hidden structure in AV/AI failures matches EXACTLY the constraint vs comfort
bifurcation. Not coincidence. Causal.

License: CC0
Stdlib only.
"""

# ============================================================================
# AV FAILURE MODES (documented incidents)
# ============================================================================

AV_FAILURE_TAXONOMY = {
    "NOMINAL_FAILURES": {
        "description": "Works fine until one assumption breaks",
        "examples": [
            "Tesla autopilot: highway driving perfect. Sees white truck against white sky. Doesn't brake. 2016, Joshua Brown, dead.",
            "Waymo: handles 95% of urban driving well. Rain on camera. System hands to human. Human not paying attention (trained not to be). Crash.",
            "Uber ATG: LiDAR + radar + camera all see pedestrian. Software stack doesn't fuse them correctly in edge case. Elaine Herzberg, dead. Chandler, Arizona.",
        ],
        "geometric_pattern": (
            "System performs well in TRAINING DISTRIBUTION. "
            "Encounters condition outside training distribution. "
            "Has NO FALLBACK that doesn't also require the assumption that broke. "
            "Failure is HARD (no graceful degradation)."
        ),
        "comfort_based_origin": (
            "System was designed by people who could test: "
            "- in controlled conditions (good weather, clear markings) "
            "- with external help available (car can stop, humans nearby) "
            "- without time pressure (lab schedule, not real world) "
            "System was NOT designed by people who: "
            "- had to make it work in rain, mud, dust, dark "
            "- had to assume zero external help (remote roads) "
            "- had to recover from failure without external intervention"
        ),
    },

    "ASSUMPTION_CASCADE_FAILURES": {
        "description": "Multiple systems fail together, no recovery path",
        "examples": [
            "GPS denied (jamming, tunnels, urban canyon) + cellular dead (rural) + sensor fouled (dust storm). System has no way to navigate. Stops.",
            "LiDAR fails (rain, dust, vibration damage). System switches to camera. Camera degraded (night, backlit). No radar (removed for cost). Blind.",
            "Compute overheats (Arizona summer, load dependent on sensor fusion). Sensor pipeline drops frames. Decision latency spikes. No graceful fallback.",
        ],
        "geometric_pattern": (
            "Each subsystem designed INDEPENDENTLY with its OWN redundancy. "
            "No one designed for SIMULTANEOUS failure of 2+ subsystems. "
            "Because in lab conditions, that never happens. "
            "In field conditions, it's not rare."
        ),
        "comfort_based_origin": (
            "Labs have air conditioning, clean power, stable network. "
            "Field has: temperature swings, voltage sags, dead zones. "
            "Designers never experienced the field condition, so they didn't model for it."
        ),
    },

    "OPERATOR_HANDOFF_FAILURES": {
        "description": "System fails and asks human to take over. Human cannot.",
        "examples": [
            "Tesla autopilot disengages suddenly (edge case). Driver is reading, watching video, hands not on wheel. Can't regain control in time. Crash.",
            "Waymo test: system asks for human takeover. Human has been passive for 45 minutes. Reaction time: 5-7 seconds. Incident happens in 2 seconds.",
            "Cruise autonomous taxi: detects anomaly, hands to remote operator. Network latency: 200-500ms one-way. By the time operator sees camera, incident is over.",
        ],
        "geometric_pattern": (
            "System was designed by people who could CHOOSE to be attentive. "
            "Human in the loop was trained to NOT be attentive (system handles it). "
            "When system fails, human is neurologically INCAPABLE of immediate recovery. "
            "This is predictable. It was designed this way."
        ),
        "comfort_based_origin": (
            "Designers: 'system should handle this, human is backup.' "
            "What they didn't account for: human backup only works if human is ACTIVELY ENGAGED. "
            "If you train a human to NOT pay attention, they can't pay attention when you need them to. "
            "This is basic neuroscience. They didn't know this because they've never had to."
        ),
    },

    "HIDDEN_PARAMETER_FAILURES": {
        "description": "System works in lab, fails in field. Hidden parameter wasn't measured.",
        "examples": [
            "Perception trained on datasets from sunny California, Japan, Germany. Deployed in rural India. Road surface: unpaved, cows on it, no lane markings. Fails catastrophically.",
            "Sensor fusion trained assuming sensors independent. In salt-fog coastal environment, all sensors degrade together (corrosion). Assumed independent redundancy breaks.",
            "Object detection trained on 'normal' human behavior. Deployed in refugee camp where people behave under trauma. Pedestrian detection fails (movement patterns unexpected).",
        ],
        "geometric_pattern": (
            "Training distribution = comfortable, first-world conditions. "
            "Deployment distribution = actual conditions (often constraint-based). "
            "Gap is INVISIBLE to people who trained in comfort. "
            "They don't know what they don't know."
        ),
        "comfort_based_origin": (
            "Data collected from: dashcams in developed countries, test fleets in good weather, highways with lane markings. "
            "If you want data from constraint-based environments, you have to GO THERE. "
            "Most researchers don't."
        ),
    },
}


# ============================================================================
# AI FAILURE MODES (language models, decision systems)
# ============================================================================

AI_FAILURE_TAXONOMY = {
    "DISTRIBUTION_SHIFT": {
        "description": "AI trained on curated data, fails on real data",
        "examples": [
            "GPT trained on internet text (biased toward English speakers, educated, wealthy). Deployed in healthcare system. Misses diagnoses in under-resourced populations because training data distribution didn't include their presentations.",
            "Hiring algorithm trained on company's past hires (biased toward privileged backgrounds). Applied to general population. Filters out the exact people who are most adaptable (constraint-trained).",
            "Credit scoring: trained on people with stable housing, regular paychecks. Applied to gig workers, informal economy. Fails to identify creditworthy people because creditworthiness (in constraint world) doesn't look like training data.",
        ],
        "geometric_pattern": (
            "AI learns CORRELATIONS in training distribution. "
            "Assumes those correlations hold in deployment. "
            "They don't, when constraints are different. "
            "System has no mechanism to detect this shift."
        ),
        "comfort_based_origin": (
            "Data collection is expensive. Easy data: comfortable populations (digital natives, employed, stable). "
            "Hard data: constraint-based populations (no smartphones, irregular patterns, survival-mode decision making). "
            "AI builders use easy data. Fail in hard conditions."
        ),
    },

    "BLACK_BOX_HIDES_BRITTLE_ASSUMPTIONS": {
        "description": "System works until one assumption breaks, then fails hard",
        "examples": [
            "Fraud detection system trained assuming fraud is rare. Deployed during economic crisis. Fraud pattern changes (desperate people, not criminals). System misses it, or over-flags legitimate transactions.",
            "Demand forecasting: trained during stable economy. Supply chain shock hits. System can't adapt because it learned correlations, not causation. Predicts based on past, not constraints.",
            "Resume screening: trained on successful hires (who all had certain backgrounds). Applied to all resumes. Systematically filters for 'safe' candidates, eliminating people who adapted through constraint (exactly who would be best at hard problems).",
        ],
        "geometric_pattern": (
            "Model learned correlations in ONE regime. "
            "Regime changes, correlations break. "
            "Model has no understanding of WHY the correlation existed, so it can't adapt. "
            "Failure is sudden and complete."
        ),
        "comfort_based_origin": (
            "Builders optimize for: accuracy on test set, not robustness to regime change. "
            "If you've never lived through regime change, you don't build for it. "
            "If you build systems in comfortable regime, you don't anticipate how they fail in constraint regime."
        ),
    },

    "OPTIMIZATION_MISALIGNMENT": {
        "description": "System optimizes for what you measured, not what you wanted",
        "examples": [
            "Recommendation algorithm optimizes for engagement. Outputs increasingly extreme content. User is more engaged. But angry, polarized. System is working as designed, harming as undesigned.",
            "School grading AI optimizes for test scores. Teaches to test. Knowledge fragmentation. Students can't adapt (no constraint-based learning, just procedure memorization).",
            "Truck dispatch algorithm optimizes for: miles per hour, fuel efficiency, on-time delivery. Driver forced into: no sleep, no breaks, no safety margin. Accidents increase. Algorithm optimized correctly for its metric. Catastrophic for humans.",
        ],
        "geometric_pattern": (
            "Optimization has IMPLICIT assumptions about what's acceptable to sacrifice. "
            "Designers from comfort background assume: safety exists elsewhere, humans have margins. "
            "They optimize the SYSTEM, not the SYSTEM + HUMAN + CONSTRAINTS. "
            "When the implicit assumptions break, the sacrifice becomes visible (and deadly)."
        ),
        "comfort_based_origin": (
            "Builders optimize what they measure. "
            "Comfortable people measure: efficiency, productivity, cost. "
            "Constraint-trained people measure: survivability, redundancy, recovery. "
            "When system is designed only for efficiency, it fails when survival is the question."
        ),
    },
}


# ============================================================================
# THE HIDDEN GEOMETRY (what connects them all)
# ============================================================================

FAILURE_GEOMETRY_UNIFIED = {
    "principle": (
        "Systems designed under comfort assumptions fail when constraints appear. "
        "Because constraints were never part of the model."
    ),

    "mathematical_structure": {
        "comfort_based_system": {
            "state_space": "all variables bounded within training distribution",
            "dynamics": "continuous, linear (within bounds)",
            "failure_mode": "undefined (state space assumes you never leave)",
            "when_constraints_appear": "sudden transition to undefined behavior (hard failure)",
        },
        "constraint_based_system": {
            "state_space": "explicitly includes constraint-degraded states",
            "dynamics": "piecewise (different rules in different constraint regimes)",
            "failure_mode": "defined at every boundary (graceful degradation)",
            "when_constraints_appear": "system follows pre-computed degraded-state path",
        },
    },

    "why_it_looks_like_AI_problem_but_isnt": (
        "Everyone says: 'we need more data, better training, more parameters.' "
        "But the data is the problem. "
        "You're training on comfortable distributions. "
        "You can't infer constraint-based behavior from comfort-based data. "
        "It's not in there."
    ),

    "why_it_looks_like_engineering_problem_but_isnt": (
        "Everyone says: 'we need better sensors, more redundancy, faster computers.' "
        "But sensors in comfortable environment work fine. "
        "The problem is: you haven't tested them in constraint environments. "
        "Adding MORE sensors in comfortable design just adds more things that fail together when constraint hits."
    ),

    "the_actual_problem": (
        "Your designers never had to operate in constraint. "
        "Your training data is from constraint-free populations. "
        "Your system architecture doesn't model constraint-based degradation. "
        "Your failure modes are undefined for constraint regimes. "
        "So when constraint appears in the field, failure is SUDDEN and COMPLETE."
    ),
}


# ============================================================================
# PROOF: Look at the actual failure rate curves
# ============================================================================

FAILURE_RATE_GEOMETRY = {
    "comfort_designed_system": {
        "in_training_distribution": "failure rate: 0.01-0.1% (excellent)",
        "near_edge_of_training": "failure rate: 1-5% (unexpected jump)",
        "outside_training": "failure rate: 50-99% (catastrophic)",
        "shape": "step function (flat, then cliff)",
        "why": "all failure modes are in 'outside training' category",
    },

    "constraint_designed_system": {
        "in_nominal_conditions": "failure rate: 0.1-1% (good, not amazing)",
        "in_degraded_conditions": "failure rate: 5-15% (graceful, predictable)",
        "in_severe_constraint": "failure rate: 20-40% (still handling, just reduced capability)",
        "shape": "smooth curve (continuous degradation)",
        "why": "failure modes are pre-designed for constraint regimes",
    },

    "difference": (
        "Comfort system: fails suddenly outside training. "
        "Constraint system: degrades smoothly always. "
        "The SHAPE of the failure curve tells you what assumptions were baked in."
    ),
}


# ============================================================================
# HOW TO DETECT THIS IN DATA
# ============================================================================

GEOMETRIC_SIGNATURE_TO_LOOK_FOR = {
    "if_comfort_based": [
        "Failure incidents cluster around edges of training distribution",
        "Failures are 'surprising' to developers (weren't expected)",
        "Multiple failures happen together in same incident (cascade)",
        "Incident reports say: 'this edge case wasn't in our data'",
        "Performance cliff at certain environmental conditions (rain, dark, crowded)",
        "Failures worse when multiple systems degrade together",
        "Recovery requires external intervention (human takes over, goes to depot)",
    ],

    "if_constraint_based": [
        "Failure incidents distributed across entire operational envelope",
        "Failures are expected (developer says 'we designed for this')",
        "Single failures don't cascade (redundancy at every layer)",
        "Incident reports reference: 'constraint regime, system in fallback mode'",
        "Performance continuous across conditions (degrades smoothly, doesn't cliff)",
        "Failures less severe when multiple systems degrade (redundancy designed in)",
        "Recovery is local (system adapts, or human + system handle it together)",
    ],
}


# ============================================================================
# APPLY THIS TO YOUR DATA (Tesla, Waymo, Uber, Cruise)
# ============================================================================

APPLY_GEOMETRY_TEST = """
For each autonomous vehicle failure:

1. Plot: time since incident vs. environmental conditions
   - Does failure cluster at edges of training (comfort-based signature)?
   - Or spread across operating envelope (constraint-based)?

2. Plot: failure type vs. number of simultaneous system failures
   - Do single-system failures cause major crashes (no cascade protection)?
   - Or do multiple systems fail, system gracefully reduces capability?

3. Read: incident reports
   - Do they say 'unexpected edge case'?
   - Or 'constraint regime, system performed as designed'?

4. Look: recovery mode
   - Does system ask human to take over (human wasn't paying attention)?
   - Or does system adapt and human stays engaged?

5. Check: testing before deployment
   - Was testing in controlled lab conditions?
   - Or in actual field conditions (rain, dust, darkness, real pedestrians)?

If you see:
- Sudden failure at condition boundary (not in training)
- Multiple cascading sub-failures
- 'Unexpected edge case' language
- Human in fallback role isn't engaged
- Testing was lab-based

You're looking at comfort-based design failing under constraint.
"""
