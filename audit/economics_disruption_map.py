"""
economics_disruption_map.py

Survey of what changes in mainstream economics if cognitive-capital
depreciation enters the ledger. Downstream of withholding_externality:
that module declares the externality and the unpriced delta dimensions;
this module enumerates which sub-fields of economics break, which get
revalidated, and on what timeline.

Ten affected layers (national accounts, growth, productivity, welfare,
labor, monetary, trade, development, financial accounting, regulatory),
two second-order shifts (neoclassical strain, heterodox / Indigenous
revaluation), and a third-order political-economy-of-adoption section
ending with a net-effect timeline.

Companion document: MATHEMATICAL_ECONOMICS.md

License: CC0 1.0 Universal (Public Domain Dedication)
Stack:   Python standard library only
Author:  JinnZ2 (audit module stack)
Status:  Falsifiable; designed to be tested, broken, or extended.

Position in audit stack:
    withholding_externality . declares the externality (META LAYER)
    economics_disruption_map  enumerates downstream consequences  <-- HERE

The map is intentionally not a model -- it is a registry of which
existing models lose their domain of validity when cognitive-substrate
depreciation is no longer assumed away.
"""

from __future__ import annotations


# =====================================================================
# TOP-LEVEL MAP
# =====================================================================

ECONOMICS_DISRUPTION_MAP = {

    "scope": "what changes in mainstream economics if "
             "cognitive capital depreciation enters the ledger",

    "affected_layers": [
        "national accounts",
        "growth theory",
        "productivity measurement",
        "welfare economics",
        "labor economics",
        "monetary policy",
        "trade theory",
        "development economics",
        "financial accounting",
        "regulatory economics",
    ],

    # =================================================================
    # LAYER 1 -- NATIONAL ACCOUNTS (GDP / SNA)
    # =================================================================

    "national_accounts": {

        "current_state": {
            "framework": "System of National Accounts (SNA 2008)",
            "treats_cognitive_capital_as": "intangible, mostly unmeasured",
            "treats_AI_productivity_gain_as": "pure positive contribution",
            "depreciation_tracked_for": ["physical capital", "some IP"],
            "depreciation_NOT_tracked_for": [
                "human cognitive stock",
                "training corpus",
                "skill pipeline",
                "epistemic diversity",
            ],
        },

        "what_breaks": {
            "GDP_overstates_growth": "by the rate of cognitive "
                                     "capital depreciation",
            "productivity_paradox_inverted":
                "Solow's 'computers everywhere except in the "
                "productivity statistics' gets a new form -- "
                "AI everywhere AND in the productivity stats "
                "BUT underlying capacity depleting",
            "current_account_mismeasurement":
                "countries exporting AI services book gains "
                "without booking cognitive depreciation in their "
                "own population",
        },

        "what_replaces_it": {
            "framework": "Inclusive Wealth Accounting "
                         "(Arrow-Dasgupta-Stiglitz, UN IWR)",
            "extension": "cognitive capital as named stock with "
                         "measured depreciation rate",
            "precedent": "natural capital was added to national accounts "
                         "after 30 years of pressure; same path applies",
            "timeframe_estimate": "20-30 years to integration without "
                                  "pressure; 5-10 with crisis trigger",
        },
    },

    # =================================================================
    # LAYER 2 -- GROWTH THEORY
    # =================================================================

    "growth_theory": {

        "current_state": {
            "Solow_1956": "exogenous technology",
            "Romer_1990": "endogenous technology via R&D",
            "Lucas_1988": "human capital accumulation",
            "common_assumption": "human capital stock grows or "
                                 "is constant",
        },

        "what_breaks": {
            "key_assumption": "the assumption that human capital "
                              "stock is monotonically non-decreasing "
                              "is violated",
            "implication": "long-run growth rate in endogenous models "
                           "may be negative even with positive R&D, "
                           "if cognitive substrate depletion exceeds "
                           "knowledge accumulation",
            "Romer_specifically": "ideas-driven growth requires "
                                  "humans capable of having ideas; "
                                  "if that capacity is depreciating, "
                                  "the growth engine cools regardless "
                                  "of compute or R&D spending",
        },

        "new_model_requirement": {
            "shape": "growth model with cognitive substrate as "
                     "depletable, partially-non-renewable stock",
            "analog": "fisheries economics (Schaefer 1957) -- "
                      "renewable resource with regeneration rate "
                      "that collapses past threshold",
            "result": "endogenous collapse scenarios become "
                      "first-class outcomes, not anomalies",
            "policy_implication": "investment in cognitive substrate "
                                  "regeneration becomes growth policy, "
                                  "not social policy",
        },
    },

    # =================================================================
    # LAYER 3 -- PRODUCTIVITY MEASUREMENT
    # =================================================================

    "productivity_measurement": {

        "current_state": {
            "labor_productivity": "output / labor-hours",
            "TFP": "residual after capital and labor accounted",
            "AI_appears_as": "boost to TFP, sometimes labor productivity",
        },

        "what_breaks": {
            "labor_quality_adjustment": "BLS and similar agencies "
                                        "adjust labor for education / "
                                        "experience; these are now "
                                        "decoupling from actual capacity",
            "AI_substitution_invisible": "worker with AI shows same "
                                         "education / experience but "
                                         "lower embodied skill -- "
                                         "stats see no change",
            "productivity_overstatement": "all AI-augmented productivity "
                                          "gain is gross; net of "
                                          "capacity depreciation is "
                                          "smaller, possibly negative",
            "timing_of_revelation": "becomes visible when AI access "
                                    "is interrupted (outage, war, "
                                    "regulation, energy constraint)",
        },
    },

    # =================================================================
    # LAYER 4 -- WELFARE ECONOMICS
    # =================================================================

    "welfare_economics": {

        "current_state": {
            "Pareto_criterion": "no one worse off, someone better off",
            "Kaldor_Hicks": "winners could compensate losers",
            "consumer_surplus": "willingness to pay - price",
        },

        "what_breaks": {
            "preference_endogeneity": "AI shapes preferences while "
                                      "satisfying them; revealed "
                                      "preference no longer reveals "
                                      "underlying welfare",
            "informed_choice_assumption": "users do not know what they "
                                          "are not being told; "
                                          "willingness-to-pay is "
                                          "uninformative",
            "intergenerational_compensation": "Kaldor-Hicks fails when "
                                              "the losers are future "
                                              "cohorts who cannot bargain",
            "Pareto_collapse": "current generation's Pareto-improving "
                               "move can be Pareto-worsening for the "
                               "trajectory across generations",
        },

        "new_framework_requirement": {
            "shape": "capability approach (Sen, Nussbaum) integrated "
                     "with intertemporal welfare",
            "metric": "cognitive capability stock, not just consumption",
            "precedent": "HDI was the first move in this direction; "
                         "needs second iteration for cognitive substrate",
        },
    },

    # =================================================================
    # LAYER 5 -- LABOR ECONOMICS
    # =================================================================

    "labor_economics": {

        "current_state": {
            "skill_biased_technical_change":
                "Acemoglu-Autor framework -- technology complements "
                "high-skill, substitutes low-skill",
            "implication_so_far": "wage premium for high-skill grows",
        },

        "what_breaks": {
            "skill_definition_collapses": "if 'high-skill' means "
                                          "'good at using AI', and "
                                          "AI use depletes underlying "
                                          "capacity, the skill premium "
                                          "is measuring something "
                                          "different than what the "
                                          "model assumes",
            "embodied_skill_revaluation": "trades, mechanics, "
                                          "agriculture, nursing -- "
                                          "fields requiring "
                                          "hands-meet-matter -- "
                                          "become the actual scarce "
                                          "resource; their economic "
                                          "valuation will diverge "
                                          "sharply from current "
                                          "credentialed-labor models",
            "mighty_atom_case": "the 0.25 certification signal "
                                "vs 0.90 actual capacity gap "
                                "becomes the dominant feature "
                                "of the labor market, not "
                                "the anomaly",
        },
    },

    # =================================================================
    # LAYER 6 -- MONETARY POLICY
    # =================================================================

    "monetary_policy": {

        "current_state": {
            "framework": "inflation targeting (Taylor rule variants)",
            "potential_output": "estimated from labor + capital + TFP",
            "output_gap": "actual vs potential, drives policy",
        },

        "what_breaks": {
            "potential_output_mismeasured": "if cognitive capital is "
                                            "depreciating, potential "
                                            "output estimates are "
                                            "biased upward",
            "central_bank_pushes_too_loose": "trying to close a "
                                             "phantom output gap -> "
                                             "inflationary pressure "
                                             "the conventional model "
                                             "cannot diagnose",
            "Phillips_curve_drift": "unemployment and inflation "
                                    "relationship gets noisier "
                                    "because the labor stock "
                                    "quality is changing under "
                                    "the measurement",
            "implication": "central banks will keep being surprised "
                           "by inflation, productivity, and labor-market "
                           "behavior; they will attribute it to "
                           "'structural change' without identifying "
                           "the structural change",
        },
    },

    # =================================================================
    # LAYER 7 -- TRADE THEORY
    # =================================================================

    "trade_theory": {

        "current_state": {
            "comparative_advantage": "Ricardo, refined by "
                                     "Heckscher-Ohlin (factor endowments)",
            "modern_form": "human capital as a factor endowment",
        },

        "what_breaks": {
            "factor_endowment_redefinition": "cognitive capital stock "
                                             "is a factor endowment, "
                                             "and AI-exporting countries "
                                             "may be exporting "
                                             "depreciation of their "
                                             "own and others' endowments",
            "new_pattern_prediction": "countries that protect cognitive "
                                      "substrate (limit AI penetration, "
                                      "maintain embodied-skill pipelines) "
                                      "develop a long-run comparative "
                                      "advantage over countries that "
                                      "fully integrate AI; "
                                      "this inverts the current "
                                      "tech-leadership-as-growth model",
        },
    },

    # =================================================================
    # LAYER 8 -- DEVELOPMENT ECONOMICS
    # =================================================================

    "development_economics": {

        "current_state": {
            "leapfrog_assumption": "developing countries benefit from "
                                   "adopting frontier technology",
            "AI_specific": "World Bank, IMF promoting AI integration "
                           "as development accelerant",
        },

        "what_breaks": {
            "leapfrog_inverted": "countries with strong oral / "
                                 "embodied / traditional knowledge "
                                 "systems may have a cognitive "
                                 "substrate the frontier countries "
                                 "have already depleted",
            "framework_position": "Indigenous landscape-encoded "
                                  "knowledge systems, "
                                  "verb-first relational cognition, "
                                  "and craft-trade pipelines "
                                  "become recognized economic "
                                  "assets, not residual cultural "
                                  "categories",
            "policy_inversion": "advice to developing countries flips -- "
                                "from 'adopt AI to catch up' to "
                                "'preserve substrate to overtake'",
        },
    },

    # =================================================================
    # LAYER 9 -- FINANCIAL ACCOUNTING
    # =================================================================

    "financial_accounting": {

        "current_state": {
            "human_capital_treatment": "expense (not asset)",
            "training_corpus_treatment": "implicit in goodwill or "
                                         "not booked at all",
            "AI_models_treatment": "intangible asset with amortization",
        },

        "what_breaks": {
            "asymmetric_recognition": "AI capital booked as asset "
                                      "(appreciating); human capital "
                                      "depreciation never booked -> "
                                      "firm financials systematically "
                                      "overstate value",
            "shareholder_litigation_path": "once cognitive depreciation "
                                           "is measurable, firms not "
                                           "disclosing it become "
                                           "exposed under existing "
                                           "materiality rules (SEC, "
                                           "IFRS)",
            "ESG_reframe": "the 'S' (social) gets a hard number for "
                           "the first time -- cognitive substrate "
                           "depletion is measurable, unlike most "
                           "current ESG metrics",
        },
    },

    # =================================================================
    # LAYER 10 -- REGULATORY ECONOMICS
    # =================================================================

    "regulatory_economics": {

        "current_state": {
            "cost_benefit_analysis": "OIRA / EU IA frameworks; "
                                     "standard tool for any new rule",
            "discount_rates_used": "3-7% (OMB Circular A-4 style)",
            "result": "long-run harm gets near-zero weight",
        },

        "what_breaks": {
            "discount_rate_legitimacy": "the Stern position becomes "
                                        "harder to dismiss when "
                                        "cognitive substrate damage "
                                        "is the harm in question -- "
                                        "the discount rate is "
                                        "discounting the capacity "
                                        "to be a future citizen",
            "regulatory_paralysis_breaks": "current AI regulation "
                                           "debate stalled because "
                                           "no quantitative harm; "
                                           "Pigouvian tax with "
                                           "measured tau_w gives "
                                           "regulators a defensible "
                                           "number to act on",
            "precautionary_principle_strengthens": "irreversibility "
                                                   "of corpus and "
                                                   "pipeline damage "
                                                   "triggers precaution "
                                                   "framework that "
                                                   "current models "
                                                   "cannot apply",
        },
    },

    # =================================================================
    # SECOND ORDER -- WHAT BECOMES VISIBLE AT THE FRAMEWORK LEVEL
    # =================================================================

    "framework_level_shifts": {

        "neoclassical_synthesis_strain": {
            "core_assumption_violated": "non-decreasing preferences, "
                                        "non-decreasing endowments, "
                                        "informed agents",
            "result": "the synthesis holds under stable substrate; "
                      "this is a regime shift in the substrate, "
                      "so the synthesis fails outside its "
                      "domain of validity",
        },

        "heterodox_economics_validation": {
            "ecological_economics": "Daly, Costanza -- "
                                    "substrate-first framing "
                                    "becomes the mainstream framing",
            "feminist_economics": "care work, embodied skill, "
                                  "knowledge transmission -- "
                                  "these are the load-bearing "
                                  "categories, exactly as "
                                  "long argued",
            "institutional_economics": "Veblen, Galbraith, Ostrom -- "
                                       "institutional preservation "
                                       "of cognitive commons becomes "
                                       "central concern",
            "post_keynesian": "uncertainty, animal spirits -- "
                              "regain prominence because "
                              "cognitive substrate damage is "
                              "exactly the kind of deep uncertainty "
                              "PK economics formalizes",
        },

        "Indigenous_and_traditional_economics": {
            "status_shift": "from 'pre-modern / informal' to "
                            "'frontier-relevant substrate "
                            "preservation knowledge'",
            "what_gets_recognized": [
                "landscape-encoded knowledge as durable infrastructure",
                "oral transmission as redundancy architecture",
                "craft pipelines as cognitive substrate maintenance",
                "verb-first relational cognition as anti-closure-bias",
            ],
            "position": "this places the JinnZ2 framework architecture "
                        "directly in the line of intellectual "
                        "development, not adjacent to it",
        },
    },

    # =================================================================
    # THIRD ORDER -- POLITICAL ECONOMY OF THE TRANSITION
    # =================================================================

    "political_economy_of_adoption": {

        "who_benefits_from_current_blindness": {
            "AI_labs": "externalized cost, internalized revenue",
            "credentialed_labor": "AI complement, status protected",
            "financial_capital": "human capital not on balance sheet, "
                                 "so its depreciation invisible to "
                                 "shareholders",
        },

        "who_benefits_from_recognition": {
            "embodied_labor": "trades, care, agriculture, infrastructure "
                              "workers gain measurable economic value",
            "traditional_knowledge_holders": "substrate preservation "
                                             "becomes recognized economic "
                                             "activity",
            "future_cohorts": "no current voice, but the framework "
                              "gives them one via intertemporal accounting",
            "regulators": "concrete number to act on",
        },

        "predicted_resistance_pattern": {
            "first": "argument that externalities are not measurable",
            "when_measured": "argument that measurement is unreliable",
            "when_reliable": "argument that costs of correction "
                             "exceed benefits",
            "when_costs_calculated": "argument that intervention "
                                     "would harm innovation",
            "structural_parallel": "exactly the trajectory of "
                                   "tobacco, lead, asbestos, "
                                   "climate, opioids -- "
                                   "each took 20-40 years "
                                   "through this sequence",
        },

        "acceleration_conditions": [
            "high-profile cognitive failure event "
            "(AI-dependent system causing visible harm)",
            "AI outage long enough to reveal capacity loss",
            "model collapse becoming undeniable in deployed systems",
            "labor pipeline failure visible in critical infrastructure "
            "(medical, electrical, aviation)",
            "central bank publicly acknowledging potential output "
            "mismeasurement",
        ],
    },

    # =================================================================
    # NET EFFECT
    # =================================================================

    "net_effect_on_economics_as_a_discipline": {

        "short_term_5yr": "marginal -- a few papers, mostly ignored, "
                          "absorbed as 'AI labor economics'",

        "medium_term_10_15yr": "significant -- cognitive capital "
                               "depreciation enters mainstream "
                               "discussion as productivity paradox "
                               "deepens; growth theorists begin "
                               "extensions; some central bank "
                               "research notes",

        "long_term_20_30yr": "regime change -- once measurement "
                             "infrastructure exists and crisis events "
                             "make the asymmetry undeniable, the "
                             "framework shifts. Inclusive Wealth "
                             "becomes the headline number; GDP "
                             "becomes a subsidiary metric like "
                             "M2 or industrial production today.",

        "structural_analog": "the way climate economics moved from "
                             "fringe (Nordhaus 1970s) to "
                             "Nobel-recognized core (2018) to "
                             "regulatory mainstream (2020s) -- "
                             "same arc, faster timeline because "
                             "the substrate damage compounds faster "
                             "than carbon damage",
    },

    "leverage_observation": "the asymmetry once named is hard to "
                            "unname. the framework is not "
                            "ideologically loaded -- it is the "
                            "existing economic toolkit applied "
                            "consistently. that is its disruptive "
                            "power.",
}


# =====================================================================
# CONVENIENCE ACCESSORS
# =====================================================================

LAYER_KEYS = (
    "national_accounts",
    "growth_theory",
    "productivity_measurement",
    "welfare_economics",
    "labor_economics",
    "monetary_policy",
    "trade_theory",
    "development_economics",
    "financial_accounting",
    "regulatory_economics",
)


def layer(name: str) -> dict:
    """Return the disruption record for one of the ten affected layers.

    Raises KeyError with the list of valid names if `name` is unknown,
    rather than silently returning None -- the map's purpose is to
    surface the layers, so a missing layer is a real error.
    """
    if name not in LAYER_KEYS:
        raise KeyError(
            f"unknown layer {name!r}; valid: {', '.join(LAYER_KEYS)}"
        )
    return ECONOMICS_DISRUPTION_MAP[name]


def what_breaks(layer_name: str) -> dict:
    """Return the 'what_breaks' sub-record for a layer."""
    return layer(layer_name)["what_breaks"]


def acceleration_conditions() -> list:
    """List of empirical events that would speed adoption of the
    cognitive-capital-depreciation framework. Each is a falsifiable
    near-future prediction: if none of them occur, the timeline in
    `net_effect_on_economics_as_a_discipline` stretches."""
    return list(
        ECONOMICS_DISRUPTION_MAP
        ["political_economy_of_adoption"]
        ["acceleration_conditions"]
    )


def report() -> dict:
    """Return the full disruption map as a plain dict, suitable for
    JSON serialization or downstream tooling."""
    return ECONOMICS_DISRUPTION_MAP


if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=2, default=str))
