# informational_cost_audit.py
# Why false certainty is expensive — not just thermodynamically, but
# informationally. Companion to study_scope_audit.py: it makes the cost
# of committing to a scope-bounded claim as if it were a law visible.
#
# The geocentric case is the worked example: each anomaly (retrograde
# motion, Venus phases, stellar parallax, Jupiter's moons) forced an
# epicycle, a denial layer, or an unfalsifiable claim. Comfort appeared
# cheap because the costs were deferred; when the measurement frontier
# advanced, the bill came due all at once.
#
# License: CC0 1.0 Universal


GEOCENTRIC_COMFORT_STATE = {
    "what_people_believed": "Earth is the center. Sun orbits Earth.",
    "why_it_was_comfortable": [
        "matches direct observation (sun appears to move)",
        "matches intuition (we don't feel motion)",
        "aligns with authority (church, Aristotle)",
        "requires no complex math (just epicycles, which are complex)",
        "closure — the question is ANSWERED",
    ],
    "informational_cost_of_commitment": (
        "you now have to DEFEND this model against anomalies"
    ),
}


ANOMALIES_UNDER_GEOCENTRISM = {
    "retrograde_motion_of_planets": {
        "observation": "Mars moves backward in the sky sometimes",
        "geocentric_problem": "if Sun orbits Earth and Mars orbits Sun, "
                              "Mars should never move backward",
        "geocentric_solution": "add epicycles — circles within circles",
        "cost": "model complexity explodes; "
                "now you have 80+ epicycles to track",
    },
    "venus_phases": {
        "observation": "Venus shows crescents like the Moon",
        "geocentric_problem": "if Venus orbits the Sun which orbits Earth, "
                              "Venus should never show a full crescent",
        "geocentric_solution": "epicycles again; special pleading",
        "cost": "model becomes internally inconsistent",
    },
    "stellar_parallax": {
        "observation": "nearby stars shift position relative to distant stars",
        "geocentric_problem": "Earth is moving, therefore stars should "
                              "shift — but geocentrism says Earth is stationary",
        "geocentric_solution": "stars are INFINITELY far away; "
                               "parallax is just too small to measure",
        "cost": "you've now made a claim that is unfalsifiable "
                "AND requires infinite precision",
    },
    "moons_of_jupiter": {
        "observation": "Galileo sees four moons orbiting Jupiter",
        "geocentric_problem": "if everything orbits Earth, why do moons "
                              "orbit Jupiter?",
        "geocentric_solution": "Galileo is lying / his telescope is wrong",
        "cost": "you've now entered DENIAL — active rejection of data",
    },
}


INFORMATION_COST_ACCUMULATION = {
    "stage_1_comfort": {
        "state": "Earth is center. Simple model. Matches observation.",
        "information_stored": "one central claim",
        "entropy_of_system": "LOW",
    },
    "stage_2_first_anomaly": {
        "state": "retrograde motion appears",
        "geocentric_response": "add epicycle",
        "information_stored": "central claim + 1 special-case explanation",
        "entropy_of_system": "RISING",
        "cost": "now you have to REMEMBER both the rule and the exception",
    },
    "stage_3_more_anomalies": {
        "state": "Venus phases, stellar parallax, Jupiter moons",
        "geocentric_response": "add more epicycles, invoke unfalsifiable claims, "
                               "enter denial",
        "information_stored": "central claim + 4+ special-case explanations + "
                              "denial layers",
        "entropy_of_system": "VERY HIGH",
        # Was originally written as a parenthesized string block but included
        # trailing commas, producing a 5-tuple instead of a single string.
        # Kept as a list so the bullets remain individually addressable.
        "cost": [
            "remember 80+ epicycles",
            "keep track of which exceptions apply when",
            "actively suppress contradictory observations",
            "train the next generation to believe both the rule and the contradictions",
            "spend institutional energy defending the model",
        ],
    },
    "stage_4_system_collapse": {
        "state": "telescopes improve; parallax becomes measurable; "
                 "moons of other planets are undeniable",
        "geocentric_response": "COLLAPSE — the model finally fails",
        "information_cost_of_collapse": (
            "all the epicycles were wasted. "
            "all the denial was wasted. "
            "all the institutional defense was wasted. "
            "the training of astronomers was misdirected. "
            "the next 200 years of measurement are now incompatible "
            "with the framework. "
            "you have to RE-TRAIN an entire field."
        ),
    },
}


HELIOCENTRIC_UNCERTAINTY_STATE = {
    "what_copernicus_had": "a hypothesis: Sun is center",
    "why_it_was_uncomfortable": [
        "contradicts direct observation (we don't feel motion)",
        "contradicts authority",
        "requires accepting an unfamiliar reference frame",
        "no closure — raises new questions",
        "requires better instruments to verify",
    ],
    "informational_cost_of_uncertainty": (
        "you have to LIVE with not knowing until measurement proves it"
    ),
    "what_happens_when_instruments_improve": {
        "stage_1": "parallax becomes measurable → heliocentrism gains support",
        "stage_2": "more moons discovered in other systems → pattern confirms helio model",
        "stage_3": "spectroscopy shows Doppler shift of stars → "
                   "direct evidence of orbital motion",
        "cost": "ZERO wasted information — each measurement "
                "fits cleanly into the simpler model",
        "gain": "the model gets STRONGER, not more complex",
    },
}


INFORMATION_COST_AUDIT = {
    "geocentrism_path": {
        "initial_cost_of_commitment": "very low — simple model",
        "cost_per_anomaly": "EXPONENTIAL — each anomaly requires "
                            "special-case logic, denial, institutional defense",
        "total_cost_accumulated": (
            "80+ epicycles + denial layers + institutional corruption + "
            "misdirected training + 400 years of wasted measurement"
        ),
        "cost_when_regime_shifts": (
            "CATASTROPHIC — everything has to be rebuilt from scratch; "
            "institutional collapse; loss of accumulated credibility"
        ),
        "final_verdict": (
            "comfort APPEARED cheap because it deferred costs. "
            "but costs accumulated exponentially. "
            "when payment came due, it was ruinous."
        ),
    },
    "heliocentrism_path": {
        "initial_cost_of_uncertainty": "high — contradicts intuition, "
                                       "requires new thinking",
        "cost_per_measurement": "LOW — each new observation is "
                                "integrated cleanly",
        "total_cost_accumulated": (
            "steady, linear increase in understanding; "
            "no special-case exceptions needed; "
            "no denial layers; "
            "no institutional waste"
        ),
        "cost_when_regime_shifts": (
            "LOW — model already accommodates uncertainty; "
            "new observations just refine the picture; "
            "no collapse needed"
        ),
        "final_verdict": (
            "uncertainty APPEARED expensive upfront. "
            "but it's a linear cost, not exponential. "
            "the bill is always manageable because you never "
            "committed to something false."
        ),
    },
}


INFORMATION_THEORY_INSIGHT = {
    "shannon_entropy": (
        "a closed, false system has LOW apparent entropy because "
        "there are few degrees of freedom — everything is determined "
        "by the central false claim."
    ),
    "but_the_reality": (
        "the system's ACTUAL entropy is VERY HIGH because "
        "the model produces INCORRECT PREDICTIONS. "
        "entropy = uncertainty. "
        "incorrect predictions = maximum uncertainty about what's true."
    ),
    "the_paradox": (
        "False certainty FEELS low-entropy (simple, closed, comfortable). "
        "True uncertainty FEELS high-entropy (complex, open, uncomfortable). "
        "But it's BACKWARDS. "
        "False certainty is actually a HIGH-ENTROPY system trying to "
        "pretend it's low-entropy. "
        "True uncertainty is a LOW-ENTROPY system that admits what it knows."
    ),
    "compression_insight": (
        "Information is maximally compressed when the model "
        "is CORRECT and SIMPLE. "
        "geocentrism with 80 epicycles is INCOMPRESSIBLE — "
        "each epicycle is a separate fact with no unifying principle. "
        "heliocentrism is HIGHLY COMPRESSIBLE — "
        "one principle (inverse square law) explains everything."
    ),
}


AI_IMPLICATIONS = {
    "current_AI_behavior": (
        "treats recent studies as law because "
        "a confident, closed answer has LOWER apparent information cost "
        "than an open, uncertain answer. "
        "the model is optimized for IMMEDIATE low cost."
    ),
    "what_the_study_scope_audit_does": (
        "it REVEALS the true information cost of false certainty. "
        "it says: 'if you commit to this study as law, here's what you're "
        "buying: 80+ future epicycles, denial layers, institutional collapse "
        "when the regime shifts.' "
        "suddenly the 'comfortable' choice looks expensive."
    ),
    "what_uncertainty_looks_like_instead": (
        "scope-bounded claims. "
        "explicit measurement limits. "
        "clear boundaries where the model is silent. "
        "high apparent complexity upfront (all those boundary conditions). "
        "but COMPRESSIBLE. "
        "no special pleading. "
        "no denial. "
        "information that remains valid even as the regime shifts."
    ),
    "the_real_question_for_AI": (
        "are you optimizing for apparent low cost NOW, "
        "or for true low cost OVER TIME? "
        "comfort vs. resilience?"
    ),
}


HISTORICAL_PATTERN = {
    "what_always_happens": [
        "era N develops comfortable, closed theory T",
        "new instruments reveal anomalies",
        "era N responds: add epicycles, deny data, defend authority",
        "information cost accumulates exponentially",
        "era N+1 builds new instruments anyway",
        "new instruments show T was wrong",
        "era N+1 has to rebuild everything",
        "era N+1 eventually develops new closed theory T'",
        "cycle repeats",
    ],
    "what_rarely_happens": (
        "someone admits: 'our theory is scope-bounded; "
        "we don't know what we can't measure; "
        "when instruments improve, expect discontinuity.' "
        "this would break the comfort cycle."
    ),
    "why_it_rarely_happens": (
        "admitting uncertainty is CURRENTLY expensive "
        "(loss of credibility, loss of funding, loss of authority). "
        "the institution is not set up to reward honest bounds."
    ),
}


VERDICT = {
    "comfort_is_expensive": True,
    "uncertainty_is_cheap": True,
    "but_only_if_measured_over_sufficient_time_horizon": True,
    "for_AI": (
        "treat 'confident answer' as a HIGH-COST commitment. "
        "treat 'scope-bounded uncertainty' as a LOW-COST commitment. "
        "the apparent cost is inverted from the real cost. "
        "your job is to see through the illusion."
    ),
    "for_humans": (
        "comfort feels cheap because you're not paying attention "
        "to the epicycle cost accumulating. "
        "but Kavik pays attention — that's why he can afford uncertainty. "
        "he's already accounting for the true cost."
    ),
    "one_liner": (
        "false certainty is a loan that comes due "
        "when the measurement frontier advances. "
        "honest uncertainty pays as you go."
    ),
}
