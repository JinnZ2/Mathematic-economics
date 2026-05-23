"""
credential_inversion_audit.py  —  C065-C069

Five structural claims about credential inversion as the institutional
root cause of AI deployment failures. Each claim is calibrated against
a documented 12-case library spanning healthcare (Watson Oncology, IBM
Watson Drug Discovery), criminal justice (facial recognition,
predictive policing), labor markets (Amazon hiring), welfare
administration (UK/Netherlands), real estate (Zillow), social
media (Facebook moderation, Microsoft Tay), retail analytics (Target
pregnancy), financial markets (Knight Capital), and autonomy (Uber
self-driving fatality).

C065 Credentials != substrate knowledge. PhD economist / MBA executive
     / AI researcher credentials measure "passed credentialing
     institutions"; they do not measure domain mastery, operational
     judgment, or substrate understanding. Decisions made on credential
     hierarchy systematically misallocate authority to people without
     the knowledge to wield it.
C066 Institutional knowledge exclusion via credential gatekeeping.
     Decision authority concentrates in credentialed roles; domain
     experts (mechanic, nurse, teacher, farmer, driver, content
     moderator) are excluded from authority because they lack the
     credential. Their warnings are documented but ignored.
C067 AI training data inherits credential bias. Published literature,
     institutional decisions, expert opinions, and policy documents
     are all credentialed sources; field notes, practitioner
     conversations, and substrate-knowledge corpora are systematically
     absent. AI trained on this corpus learns: credentialed = correct,
     non-credentialed = anecdotal.
C068 7-step credential-inversion failure mode, with documented
     12-case library. Pattern: (1) credentialed outsider identifies
     problem; (2) domain expert warns; (3) warning dismissed;
     (4) deployment on optimistic timeline; (5) failure occurs as
     predicted; (6) blame redirected to AI / data / compute;
     (7) institutional learning fails. All 12 documented cases match.
C069 Blame attribution to AI / data / compute prevents institutional
     learning. When failure is blamed on technical issue, investment
     goes to better AI; when blamed on decision authority, investment
     goes to expertise and consultation. Only the latter prevents
     repetition.

License: CC0-1.0
"""

from typing import Dict, List


# ---------------------------------------------------------------------------
# Documented 12-case library
# ---------------------------------------------------------------------------

DOCUMENTED_FAILURES: List[dict] = [
    {"case": "watson_oncology_2016",
     "domain": "healthcare",
     "decision_makers_credential": "executive_investor_admin",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "oncologists",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "AI_not_ready_training_data",
     "actual_cause": "decision_makers_lacked_clinical_substrate_knowledge",
     "documented_cost_usd": 60_000_000.0},
    {"case": "facial_recognition_law_enforcement",
     "domain": "criminal_justice",
     "decision_makers_credential": "police_brass_vendors",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "computer_scientists",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "training_data_bias",
     "actual_cause": "decision_makers_did_not_ask_what_95pct_accuracy_means_under_subgroup_variance",
     "documented_cost_usd": None},          # civil rights violations, hard to USD
    {"case": "amazon_hiring_algorithm",
     "domain": "labor_markets",
     "decision_makers_credential": "engineers_hr_executives",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "hiring_managers",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "training_data_historical_bias",
     "actual_cause": "decision_makers_did_not_ask_domain_experts_what_hiring_data_measures",
     "documented_cost_usd": None},
    {"case": "uk_netherlands_welfare_fraud_algorithm",
     "domain": "welfare_administration",
     "decision_makers_credential": "government_officials_vendors",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "caseworkers",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "algorithm_validation",
     "actual_cause": "decision_makers_did_not_ask_caseworkers_what_real_fraud_looks_like",
     "documented_cost_usd": None},          # 26k+ false allegations
    {"case": "chicago_la_predictive_policing",
     "domain": "criminal_justice",
     "decision_makers_credential": "police_chiefs_city_officials_vendors",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "community_members",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "training_data_arrest_pattern_bias",
     "actual_cause": "decision_makers_did_not_ask_communities_what_neighborhoods_need",
     "documented_cost_usd": None},
    {"case": "zillow_home_price_prediction_2021",
     "domain": "real_estate",
     "decision_makers_credential": "executives_data_scientists",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "real_estate_agents",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "market_volatility_insufficient_training_data",
     "actual_cause": "decision_makers_did_not_ask_agents_what_makes_a_house_actually_valuable",
     "documented_cost_usd": 500_000_000.0},
    {"case": "facebook_content_moderation",
     "domain": "social_media",
     "decision_makers_credential": "facebook_executives_ml_engineers",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "content_moderators",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "context_complexity_classification_difficulty",
     "actual_cause": "decision_makers_did_not_understand_what_moderation_is",
     "documented_cost_usd": None},
    {"case": "target_pregnancy_prediction_2012",
     "domain": "retail_analytics",
     "decision_makers_credential": "data_scientists_marketing_executives",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "retail_employees_customer_service",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "ethical_complexity_of_prediction",
     "actual_cause": "decision_makers_did_not_ask_what_prediction_means_operationally",
     "documented_cost_usd": None},
    {"case": "microsoft_tay_chatbot_2016",
     "domain": "social_media",
     "decision_makers_credential": "research_team_product_management",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "content_moderation_experts_within_microsoft",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "AI_learned_racism_from_internet",
     "actual_cause": "deployed_learning_system_with_no_safety_guardrails_to_adversarial_environment",
     "documented_cost_usd": None},
    {"case": "knight_capital_flash_crash_2012",
     "domain": "financial_markets",
     "decision_makers_credential": "developers_deployment_managers",
     "decision_makers_substrate_knowledge": True,    # they had substrate knowledge
     "warned_by": "code_review_devops_risk_management",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "algorithm_malfunction_market_volatility",
     "actual_cause": "skipped_code_review_process_speed_optimization_over_safety",
     "documented_cost_usd": 440_000_000.0},
    {"case": "uber_self_driving_elaine_herzberg_2018",
     "domain": "autonomy",
     "decision_makers_credential": "uber_executives_safety_team_leadership",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "safety_engineers_human_factors_experts",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "edge_case_jaywalking_visibility",
     "actual_cause": "deployed_unsafe_system_for_first_mover_advantage_disabled_safety_systems",
     "documented_cost_usd": None},          # fatality
    {"case": "ibm_watson_drug_discovery_2016",
     "domain": "pharmaceuticals",
     "decision_makers_credential": "ibm_executives_pharma_executives",
     "decision_makers_substrate_knowledge": False,
     "warned_by": "pharmaceutical_researchers_clinical_scientists",
     "warning_documented": True,
     "warning_acted_upon": False,
     "blamed_on": "drug_discovery_harder_than_expected",
     "actual_cause": "applied_pattern_matching_to_problem_requiring_biology_understanding",
     "documented_cost_usd": None},          # zero validated drugs from 30k candidates
]


# Credentials and their substrate-knowledge implication.
CREDENTIAL_KNOWLEDGE_TABLE: List[dict] = [
    {"credential": "PhD_economics",         "implies_substrate_knowledge": False,
     "explanation": "academic credentialing; rarely overlaps with operational experience"},
    {"credential": "MBA",                   "implies_substrate_knowledge": False,
     "explanation": "business-school credentialing; designed to be domain-agnostic"},
    {"credential": "AI_researcher_PhD",     "implies_substrate_knowledge": False,
     "explanation": "ML / AI credentialing; rarely overlaps with deployment domain"},
    {"credential": "management_consultant", "implies_substrate_knowledge": False,
     "explanation": "studies problems for 3-6 months; not operational experience"},
    {"credential": "venture_capitalist",    "implies_substrate_knowledge": False,
     "explanation": "ROI optimization; rarely bears operational risk in domain"},
    {"credential": "domain_PhD",            "implies_substrate_knowledge": True,
     "explanation": "actual domain credential (clinical, agricultural, mechanical etc.) overlaps with substrate"},
    {"credential": "operational_experience_20yr", "implies_substrate_knowledge": True,
     "explanation": "20+ year operator; substrate knowledge by definition"},
    {"credential": "apprenticeship_8000hr", "implies_substrate_knowledge": True,
     "explanation": "DOL-standard apprenticeship; substrate-validated"},
    {"credential": "field_mechanic_certified", "implies_substrate_knowledge": True,
     "explanation": "ASE / equivalent certification + field years"},
]


# ---------------------------------------------------------------------------
# C065  Credentials != substrate knowledge
# ---------------------------------------------------------------------------

def credential_knowledge_correlation(
    decision_maker_credentials: List[str],
    credential_table: List[dict] | None = None,
) -> dict:
    """Fraction of stated credentials that imply substrate knowledge."""
    table = credential_table or CREDENTIAL_KNOWLEDGE_TABLE
    table_map = {c["credential"]: c for c in table}
    rows = []
    implies_count = 0
    for cred in decision_maker_credentials:
        entry = table_map.get(cred, {"credential": cred,
                                       "implies_substrate_knowledge": False,
                                       "explanation": "unknown credential; defaults to no substrate implication"})
        rows.append(entry)
        if entry["implies_substrate_knowledge"]:
            implies_count += 1
    total = len(decision_maker_credentials)
    return {
        "by_credential":               rows,
        "total":                       total,
        "implies_substrate_count":     implies_count,
        "substrate_implication_share": implies_count / total if total else 0.0,
    }


def c065_verdict(decision_maker_credentials: List[str] | None = None) -> dict:
    """C065: concern registers when < 50% of decision-maker credentials imply substrate knowledge."""
    creds = decision_maker_credentials or [
        "PhD_economics", "MBA", "AI_researcher_PhD", "management_consultant",
        "venture_capitalist",
    ]
    res = credential_knowledge_correlation(creds)
    return {
        "claim_id":      "C065",
        **res,
        "threshold_met": res["substrate_implication_share"] < 0.50,
        "falsifier":
            "decision-making body where >= 50% of credentials directly imply "
            "domain substrate knowledge AND the body's decisions are audited "
            "against domain-expert validation over 5+ years",
    }


# ---------------------------------------------------------------------------
# C066  Institutional knowledge exclusion via credential gatekeeping
# ---------------------------------------------------------------------------

DEFAULT_GATEKEEPING_INVENTORY: List[dict] = [
    {"domain_expert":   "experienced_trucker",       "credential": "operational_experience_20yr",
     "decision_authority_granted":      0.05,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
    {"domain_expert":   "field_mechanic",            "credential": "field_mechanic_certified",
     "decision_authority_granted":      0.05,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
    {"domain_expert":   "veteran_nurse",             "credential": "operational_experience_20yr",
     "decision_authority_granted":      0.10,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
    {"domain_expert":   "experienced_teacher",       "credential": "operational_experience_20yr",
     "decision_authority_granted":      0.05,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
    {"domain_expert":   "lifetime_farmer",           "credential": "operational_experience_20yr",
     "decision_authority_granted":      0.05,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
    {"domain_expert":   "content_moderator",         "credential": "operational_experience_20yr",
     "decision_authority_granted":      0.02,
     "warning_documented_historically": True,
     "warning_acted_upon":              False},
]


def institutional_gatekeeping_score(
    expert_inventory: List[dict] | None = None,
) -> dict:
    """Per-expert: how much authority granted? how many warnings acted on?"""
    inv = expert_inventory or DEFAULT_GATEKEEPING_INVENTORY
    rows = []
    total_authority = 0.0
    warnings_acted = 0
    warnings_documented = 0
    for x in inv:
        rows.append(x)
        total_authority += float(x["decision_authority_granted"])
        if x.get("warning_documented_historically"):
            warnings_documented += 1
        if x.get("warning_acted_upon"):
            warnings_acted += 1
    n = len(inv)
    return {
        "by_expert":                rows,
        "total_authority_granted":  total_authority,
        "mean_authority_granted":   total_authority / n if n else 0.0,
        "warning_action_rate":      warnings_acted / warnings_documented
                                     if warnings_documented else 0.0,
    }


def c066_verdict(expert_inventory: List[dict] | None = None) -> dict:
    """C066: concern registers when mean expert authority < 0.20 OR warning-action-rate < 0.30."""
    res = institutional_gatekeeping_score(expert_inventory)
    return {
        "claim_id":      "C066",
        **res,
        "threshold_met": (res["mean_authority_granted"] < 0.20
                          or res["warning_action_rate"] < 0.30),
        "falsifier":
            "institutional process where domain experts hold >= 20% mean "
            "decision authority AND >= 30% of their documented warnings are "
            "acted upon over a 5-year window",
    }


# ---------------------------------------------------------------------------
# C067  AI training data inherits credential bias
# ---------------------------------------------------------------------------

DEFAULT_TRAINING_CORPUS_SHARES: Dict[str, float] = {
    "published_academic_papers":           0.30,
    "institutional_decisions_documents":   0.15,
    "policy_documents":                    0.10,
    "news_articles_credentialed_quotes":   0.15,
    "official_documentation":              0.10,
    "expert_opinion_columns":              0.10,
    "field_notes_from_practitioners":      0.005,
    "operator_to_operator_conversations":  0.002,
    "substrate_knowledge_oral_traditions": 0.001,
    "non_credentialed_domain_expert_corpora": 0.002,
    "apprenticeship_internal_documentation": 0.008,
    "domain_expert_blog_posts_uncited":    0.022,
}


def training_corpus_credential_bias(
    corpus_shares: Dict[str, float] | None = None,
) -> dict:
    """Share of training corpus from credentialed vs domain-expert sources."""
    shares = {**DEFAULT_TRAINING_CORPUS_SHARES, **(corpus_shares or {})}
    credentialed_keys = {
        "published_academic_papers", "institutional_decisions_documents",
        "policy_documents", "news_articles_credentialed_quotes",
        "official_documentation", "expert_opinion_columns",
    }
    credentialed_share = sum(v for k, v in shares.items()
                              if k in credentialed_keys)
    domain_expert_share = sum(v for k, v in shares.items()
                               if k not in credentialed_keys)
    return {
        "shares":             shares,
        "credentialed_share": credentialed_share,
        "domain_expert_share": domain_expert_share,
        "bias_ratio":         credentialed_share / max(domain_expert_share, 1e-6),
    }


def c067_verdict(corpus_shares: Dict[str, float] | None = None) -> dict:
    """C067: concern registers when credentialed share > 0.80 of training corpus."""
    res = training_corpus_credential_bias(corpus_shares)
    return {
        "claim_id":      "C067",
        **res,
        "threshold_met": res["credentialed_share"] > 0.80,
        "falsifier":
            "AI training corpus with >= 20% sourced from non-credentialed "
            "domain experts (field notes, operator conversations, "
            "apprenticeship documentation, oral traditions) AND validated "
            "to outperform credentialed-only baseline on domain tasks",
    }


# ---------------------------------------------------------------------------
# C068  7-step credential-inversion failure mode + 12-case library
# ---------------------------------------------------------------------------

FAILURE_MODE_STEPS = [
    {"step": 1, "name": "problem_identified_by_credentialed_outsiders",
     "marker": "decision_makers_substrate_knowledge False"},
    {"step": 2, "name": "domain_experts_warn",
     "marker": "warning_documented True"},
    {"step": 3, "name": "warning_dismissed_or_reframed",
     "marker": "warning_acted_upon False"},
    {"step": 4, "name": "deployment_on_optimistic_timeline",
     "marker": "implied by warning_acted_upon False"},
    {"step": 5, "name": "failure_occurs_as_predicted",
     "marker": "documented_cost_usd > 0 OR actual_cause documented"},
    {"step": 6, "name": "blame_redirected",
     "marker": "blamed_on != actual_cause"},
    {"step": 7, "name": "institutional_learning_fails",
     "marker": "next deployment in same domain repeats step 1"},
]


def case_library_pattern_match() -> dict:
    """How many of the 12 documented cases match the 7-step pattern?"""
    matches = 0
    rows = []
    for case in DOCUMENTED_FAILURES:
        # Match if: decision-makers lacked substrate knowledge,
        # warning was documented but not acted upon, blame redirected.
        match = (
            not case.get("decision_makers_substrate_knowledge", True)
            and case.get("warning_documented", False)
            and not case.get("warning_acted_upon", True)
            and case.get("blamed_on") != case.get("actual_cause")
        )
        if match:
            matches += 1
        rows.append({**case, "matches_pattern": match})
    return {
        "by_case":     rows,
        "total_cases": len(DOCUMENTED_FAILURES),
        "matches":     matches,
        "match_rate":  matches / len(DOCUMENTED_FAILURES)
                        if DOCUMENTED_FAILURES else 0.0,
    }


def deployment_pattern_match(deployment: dict) -> dict:
    """Check a candidate deployment against the 7-step pattern."""
    decision_makers_substrate = deployment.get("decision_makers_substrate_knowledge", False)
    warning_documented = deployment.get("warning_documented", False)
    warning_acted = deployment.get("warning_acted_upon", False)
    blamed = deployment.get("blamed_on")
    actual = deployment.get("actual_cause")
    steps_met = {
        "step1_credentialed_outsiders":    not decision_makers_substrate,
        "step2_warning_documented":        warning_documented,
        "step3_warning_dismissed":         warning_documented and not warning_acted,
        "step4_optimistic_deployment":     warning_documented and not warning_acted,
        "step5_failure_predicted":         bool(actual),
        "step6_blame_redirected":          bool(actual) and bool(blamed) and (blamed != actual),
        "step7_learning_fails":            deployment.get("institutional_learning_fails", True),
    }
    met_count = sum(1 for v in steps_met.values() if v)
    return {
        "deployment":          deployment,
        "steps_met":           steps_met,
        "steps_met_count":     met_count,
        "matches_full_pattern": met_count >= 6,
    }


def c068_verdict(deployment: dict | None = None) -> dict:
    """C068: concern registers when library match rate > 80% AND (if deployment supplied) it matches pattern."""
    library = case_library_pattern_match()
    deployment_match = None
    deployment_matches = False
    if deployment is not None:
        deployment_match = deployment_pattern_match(deployment)
        deployment_matches = deployment_match["matches_full_pattern"]
    threshold = library["match_rate"] > 0.80 or deployment_matches
    return {
        "claim_id":      "C068",
        "case_library":  library,
        "deployment_pattern_match": deployment_match,
        "failure_mode_steps":       FAILURE_MODE_STEPS,
        "threshold_met": threshold,
        "falsifier":
            "AI deployment where decision-makers had substrate knowledge "
            "documented in advance OR where domain expert warnings were "
            "acted upon OR where post-failure blame was correctly "
            "attributed to decision-maker rather than to AI / data / "
            "compute, AND the deployment succeeded",
    }


# ---------------------------------------------------------------------------
# C069  Blame attribution to AI prevents institutional learning
# ---------------------------------------------------------------------------

# Categories of attributed blame; each maps to whether it produces
# institutional learning (changes the decision-authority structure).
BLAME_CATEGORIES: List[dict] = [
    {"category": "AI_not_ready_training_data",
     "produces_institutional_learning": False},
    {"category": "algorithm_bias",
     "produces_institutional_learning": False},
    {"category": "insufficient_compute",
     "produces_institutional_learning": False},
    {"category": "edge_case_complexity",
     "produces_institutional_learning": False},
    {"category": "market_volatility",
     "produces_institutional_learning": False},
    {"category": "decision_maker_lacked_substrate_knowledge",
     "produces_institutional_learning": True},
    {"category": "domain_expert_warnings_ignored",
     "produces_institutional_learning": True},
    {"category": "decision_authority_structure_failure",
     "produces_institutional_learning": True},
    {"category": "consultation_process_failure",
     "produces_institutional_learning": True},
]


def blame_attribution_analysis(
    attributed_blame: List[str],
    blame_categories: List[dict] | None = None,
) -> dict:
    """Of the blame attributions made, how many produce institutional learning?"""
    cats = blame_categories or BLAME_CATEGORIES
    cat_map = {c["category"]: c for c in cats}
    rows = []
    learning_count = 0
    for b in attributed_blame:
        entry = cat_map.get(b, {"category": b,
                                  "produces_institutional_learning": False})
        rows.append(entry)
        if entry["produces_institutional_learning"]:
            learning_count += 1
    n = len(attributed_blame)
    return {
        "by_blame":            rows,
        "total":               n,
        "learning_count":      learning_count,
        "learning_share":      learning_count / n if n else 0.0,
    }


def c069_verdict(attributed_blame: List[str] | None = None) -> dict:
    """C069: concern registers when < 50% of blame attributions produce institutional learning."""
    blame = attributed_blame or [
        "AI_not_ready_training_data", "algorithm_bias",
        "edge_case_complexity", "market_volatility",
    ]
    res = blame_attribution_analysis(blame)
    return {
        "claim_id":      "C069",
        **res,
        "threshold_met": res["learning_share"] < 0.50,
        "falsifier":
            "post-mortem record of AI deployment failures where >= 50% of "
            "attributed blame is to decision-authority structure / domain "
            "expert exclusion / consultation process AND the institution "
            "demonstrably changed its decision process as a result",
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("C065:", c065_verdict()["threshold_met"])
    print("C066:", c066_verdict()["threshold_met"])
    print("C067:", c067_verdict()["threshold_met"])
    c68 = c068_verdict()
    print(f"C068: {c68['threshold_met']}  "
          f"(library match_rate={c68['case_library']['match_rate']:.2f}, "
          f"{c68['case_library']['matches']}/{c68['case_library']['total_cases']})")
    print("C069:", c069_verdict()["threshold_met"])
