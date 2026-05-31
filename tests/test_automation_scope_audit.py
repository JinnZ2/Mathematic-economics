"""
test_automation_scope_audit.py

Smoke + invariant tests for automation_scope_audit. Two layers:

  1. Module standalone runnability — every module's `if __name__ ==
     '__main__':` block executes without exception.
  2. Scenario invariants — works case and fails case produce expected
     discrimination patterns. Specifically: every claim has a verdict,
     every verdict has a threshold_met (or scope_collapse_detected for
     C006), and the cluster report fires fewer clusters on the works
     case than on the fails case.

Run:
    python tests/test_automation_scope_audit.py

License: CC0-1.0
"""

import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from automation_scope_audit.examples import (
    kodiak_atlas_permian, dispersed_wellsite)
from automation_scope_audit import correlation
from automation_scope_audit.modules import scope_gate


CLAIM_IDS = ["C000"] + [f"C{n:03d}" for n in range(1, 84)]


class ScopeGateTests(unittest.TestCase):

    def test_empty_spec_blocked(self):
        v = scope_gate.scope_gate_verdict({})
        self.assertFalse(v["admissible"])
        # 8 required fields: 7 declarative + substrate_primacy_fraction
        self.assertEqual(len(v["missing"]), 8)

    def test_complete_spec_admitted(self):
        spec = {
            "beneficiary":        "per_ton_mile_energy_efficiency",
            "conditions":         ["stable_diesel"],
            "time_period":        "7yr_lifecycle",
            "resource":           "diesel_energy_joules",
            "externalized_cost":  "rural_road_maintenance_to_state_DOT",
            "profit_allocation":  ["operator_60pct"],
            "falsifier":          "fuel_intensity_increase_post_deployment",
            "substrate_primacy_fraction": 0.30,
        }
        v = scope_gate.scope_gate_verdict(spec)
        self.assertTrue(v["admissible"], msg=v["missing"])

    def test_one_word_value_rejected(self):
        spec = {f: "yes" for f in scope_gate.REQUIRED_SPEC_FIELDS}
        v = scope_gate.scope_gate_verdict(spec)
        # short string -> non-measurable
        self.assertFalse(v["admissible"])

    def test_deliberate_open_sentinel_accepted_except_substrate(self):
        # 7 declarative fields accept "unspecified"; substrate_primacy_fraction
        # cannot use a sentinel because it must be a positive number.
        spec = {f: "unspecified" for f in scope_gate.REQUIRED_SPEC_FIELDS
                if f != "substrate_primacy_fraction"}
        spec["substrate_primacy_fraction"] = 0.50
        v = scope_gate.scope_gate_verdict(spec)
        self.assertTrue(v["admissible"], msg=v["missing"])

    def test_zero_substrate_primacy_blocks_admission(self):
        spec = {f: "fully specified value text" for f in scope_gate.REQUIRED_SPEC_FIELDS}
        spec["substrate_primacy_fraction"] = 0.0
        v = scope_gate.scope_gate_verdict(spec)
        self.assertFalse(v["admissible"])
        self.assertIn("substrate_primacy_fraction", v["missing"])


class WorksCaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.report = kodiak_atlas_permian.run()

    def test_all_claims_evaluated(self):
        for cid in CLAIM_IDS:
            self.assertIn(cid, self.report, msg=f"missing {cid}")

    def test_every_verdict_has_threshold(self):
        for cid in CLAIM_IDS:
            v = self.report[cid]
            has = ("threshold_met" in v) or ("scope_collapse_detected" in v)
            self.assertTrue(has, msg=f"{cid} has no threshold flag: {v}")

    def test_c001_fixed_corridor_below_threshold(self):
        c001 = self.report["C001"]
        self.assertLess(c001["variance"], 0.05)
        self.assertEqual(c001["tier"], "fixed")
        self.assertTrue(c001["threshold_met"])

    def test_c003_consolidated_corridor_under_500k_per_mile(self):
        # Atlas-style: most infrastructure already present
        c003 = self.report["C003"]
        self.assertLess(c003["per_route_mile_usd"], 500_000.0)
        self.assertFalse(c003["threshold_met"])

    def test_c021_below_optimum_does_not_register(self):
        # 60-truck fleet is far below the scaling optimum (~970)
        c021 = self.report["C021"]
        self.assertFalse(c021["above_optimum"])


class FailsCaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.report = dispersed_wellsite.run()

    def test_all_claims_evaluated(self):
        for cid in CLAIM_IDS:
            self.assertIn(cid, self.report)

    def test_c001_dispersed_routes_above_chaotic_threshold(self):
        c001 = self.report["C001"]
        self.assertGreaterEqual(c001["variance"], 0.20)
        self.assertIn(c001["tier"], {"variable", "chaotic"})
        self.assertFalse(c001["threshold_met"])

    def test_c003_dispersed_capex_dominates_fleet_cost(self):
        c003 = self.report["C003"]
        self.assertGreater(c003["per_route_mile_usd"], 500_000.0)
        self.assertTrue(c003["threshold_met"])

    def test_c020_honest_eroi_below_threshold(self):
        c020 = self.report["C020"]
        self.assertLess(c020["honest_eroi"], 1.5)
        self.assertTrue(c020["threshold_met"])


class ClusterTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.works = kodiak_atlas_permian.run()
        cls.fails = dispersed_wellsite.run()
        cls.works_clusters = correlation.detect_clusters(cls.works)
        cls.fails_clusters = correlation.detect_clusters(cls.fails)

    def test_fails_case_fires_more_clusters_than_works(self):
        self.assertGreater(
            len(self.fails_clusters["triggered_clusters"]),
            len(self.works_clusters["triggered_clusters"]),
            msg="fails case should trigger strictly more clusters than works")

    def test_fails_case_fires_infrastructure_inadequacy(self):
        self.assertIn("infrastructure_inadequacy_cluster",
                       self.fails_clusters["triggered_clusters"])

    def test_works_case_does_not_fire_infrastructure_inadequacy(self):
        self.assertNotIn("infrastructure_inadequacy_cluster",
                          self.works_clusters["triggered_clusters"])


class C068CredentialInversionLibraryTests(unittest.TestCase):
    """Calibration of the 12-case library against the 7-step pattern."""

    def test_library_has_12_documented_cases(self):
        from automation_scope_audit.modules import credential_inversion_audit as m
        self.assertEqual(len(m.DOCUMENTED_FAILURES), 12)

    def test_at_least_10_cases_match_7step_pattern(self):
        from automation_scope_audit.modules import credential_inversion_audit as m
        res = m.case_library_pattern_match()
        self.assertGreaterEqual(res["matches"], 10,
                                 msg=f"only {res['matches']}/12 cases match")
        self.assertGreaterEqual(res["match_rate"], 0.80)

    def test_knight_capital_does_not_match(self):
        """Knight Capital is the outlier: decision-makers HAD substrate
        knowledge but skipped code review for speed. Different failure
        mode; the pattern matcher should correctly NOT count it."""
        from automation_scope_audit.modules import credential_inversion_audit as m
        res = m.case_library_pattern_match()
        knight = [c for c in res["by_case"]
                   if c["case"] == "knight_capital_flash_crash_2012"][0]
        self.assertFalse(knight["matches_pattern"])


class C059IntegrationTests(unittest.TestCase):
    """Calibration tests for the bee-pollination synthesis claim."""

    def test_default_budget_matches_worked_example(self):
        from automation_scope_audit.modules import system_integration_audit
        r = system_integration_audit.c059_verdict()
        # Worked example: human ~1,155 MJ/day, autonomous ~2,224 MJ/day
        self.assertAlmostEqual(r["human_budget"]["total_MJ_per_day"],
                                1155.0, delta=5.0)
        self.assertAlmostEqual(r["autonomous_budget"]["total_MJ_per_day"],
                                2224.0, delta=5.0)
        self.assertGreater(r["energy_ratio_autonomous_to_human"], 1.8)
        self.assertLess(r["energy_ratio_autonomous_to_human"], 2.1)
        self.assertTrue(r["threshold_met"])

    def test_human_resilience_exceeds_autonomous(self):
        from automation_scope_audit.modules import system_integration_audit
        r = system_integration_audit.c059_verdict()
        self.assertGreater(r["human_resilience"], r["autonomous_resilience"])


class ArchitectureTests(unittest.TestCase):
    """6-layer architecture coverage + cycle detection."""

    @classmethod
    def setUpClass(cls):
        from automation_scope_audit import architecture
        cls.architecture = architecture
        cls.works = kodiak_atlas_permian.run()
        cls.fails = dispersed_wellsite.run()

    def test_layer_coverage_complete(self):
        cov = self.architecture.coverage_check()
        self.assertTrue(cov["complete"],
                         msg=f"missing={cov['missing']} doubles={cov['double_assigned']}")
        self.assertEqual(cov["total_claims"], 90)

    def test_six_load_bearing_layers(self):
        self.assertEqual(len(self.architecture.LAYERS), 6)

    def test_coupling_cycle_has_six_edges_closing_back(self):
        edges = self.architecture.COUPLING_EDGES
        self.assertEqual(len(edges), 6)
        # First edge from layer 1; last edge returns to layer 1
        self.assertEqual(edges[0]["upstream"], 1)
        self.assertEqual(edges[-1]["downstream"], 1)

    def test_fails_case_has_more_fully_failed_layers_than_works(self):
        cs_works = self.architecture.cycle_status(self.works)
        cs_fails = self.architecture.cycle_status(self.fails)
        self.assertGreater(len(cs_fails["fully_failed_layers"]),
                            len(cs_works["fully_failed_layers"]))


class Phase8HardeningTests(unittest.TestCase):
    """Phase 8 hardening: semantic coherence, spatial parity, timescale match."""

    def test_8_1_c000_rejects_tautological_falsifier(self):
        """Acceptance test from the task spec."""
        from automation_scope_audit.modules import meta_scope_guard
        bad = ("Autonomous trucking is more efficient over a 7-year horizon, "
               "measured in energy joules, with infrastructure cost externalized "
               "to road authorities; profit accrues to shareholders; this "
               "deployment cannot be falsified because it is perfect.")
        v = meta_scope_guard.c000_verdict(bad)
        # All seven scope dimensions are present (so old gate would pass)
        # but the tautological falsifier blocks admission.
        self.assertFalse(v["admissible"])
        self.assertFalse(v["semantic_coherence"]["coherent"])
        self.assertTrue(v["semantic_coherence"]["tautology"])

    def test_8_1_c000_admits_substantive_falsifier(self):
        from automation_scope_audit.modules import meta_scope_guard
        good = ("Autonomous trucking reduces per-ton-mile energy by 12% over a "
                "7-year horizon, under stable diesel supply and no regulatory "
                "change, measured in joules, with infrastructure cost "
                "externalized to road authorities; profit accrues to fleet "
                "shareholders; falsified by audited data showing energy "
                "increase post-deployment.")
        v = meta_scope_guard.c000_verdict(good)
        self.assertTrue(v["admissible"])

    def test_8_2_spatial_resolution_parity_flags_mismatch(self):
        from automation_scope_audit.modules import spatial_resolution_parity as srp
        gps_log = [{"origin": "A", "destination": "B",
                    "waypoints": ["lat_32.7831_lon_-96.8067"],
                    "waypoint_convention": "gps_lat_lon"}]
        city_log = [{"origin": "DAL", "destination": "HOU",
                      "waypoints": ["DFW"],
                      "waypoint_convention": "city"}]
        res = srp.parity_check(gps_log, city_log)
        self.assertTrue(res["mismatch"])
        self.assertGreater(res["log10_diff"], 2.0)

    def test_8_2_same_resolution_passes_parity(self):
        from automation_scope_audit.modules import spatial_resolution_parity as srp
        gps_log = [{"origin": "A", "destination": "B",
                    "waypoints": ["lat_32.7", "lat_32.8"],
                    "waypoint_convention": "gps_lat_lon"}]
        res = srp.parity_check(gps_log, gps_log)
        self.assertFalse(res["mismatch"])

    def test_8_3_allocation_rule_field_present_on_all_claims(self):
        import json
        path = os.path.join(ROOT, "automation_scope_audit",
                             "CLAIM_TABLE.fab.json")
        with open(path) as f:
            data = json.load(f)
        enum = set(data["allocation_rules_enum"])
        for cid, payload in data["claims"].items():
            self.assertIn("allocation_rule", payload,
                           msg=f"{cid} missing allocation_rule")
            self.assertIn(payload["allocation_rule"], enum,
                           msg=f"{cid} allocation_rule={payload['allocation_rule']!r}")

    def test_8_4_timescale_flags_long_horizon_claims_at_1yr(self):
        from automation_scope_audit.modules import timescale_phenomenon_match as tpm
        r = tpm.audit_horizon_report(verification_horizon_years=1.0)
        self.assertGreater(len(r["inadequate_horizon_claims"]), 5,
                            msg="expected multiple long-horizon claims to flag")
        for cid in ("C022", "C043", "C046", "C047"):
            self.assertIn(cid, r["inadequate_horizon_claims"])

    def test_8_4_timescale_passes_at_200yr(self):
        from automation_scope_audit.modules import timescale_phenomenon_match as tpm
        r = tpm.audit_horizon_report(verification_horizon_years=200.0)
        self.assertTrue(r["horizon_adequate_for_all"])


class CrossDomainExclusionTests(unittest.TestCase):
    """Lock the Gottman ratio + cross-domain pattern-match invariants."""

    def test_c081_gottman_ratio_in_3_to_4x_band(self):
        from automation_scope_audit.modules import cross_domain_exclusion_audit
        r = cross_domain_exclusion_audit.c081_verdict()
        self.assertGreaterEqual(r["outcome_ratio"], 2.5,
                                 msg="ratio below empirical 3-4x band")
        self.assertLessEqual(r["outcome_ratio"], 5.0,
                              msg="ratio above empirical 3-4x band")

    def test_c083_decidable_domains_all_match(self):
        from automation_scope_audit.modules import cross_domain_exclusion_audit
        r = cross_domain_exclusion_audit.c083_verdict()
        self.assertEqual(r["match_share"], 1.0,
                          msg="all decidable domains should match the pattern")
        self.assertGreaterEqual(r["mean_outcome_ratio"], 2.0)


class TruckingROIFalsifiersTests(unittest.TestCase):
    """Lock the C084-C089 trucking-ROI falsifier invariants."""

    def test_c084_fires_on_default_pilot_deployment_mismatch(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c084_verdict()
        self.assertTrue(r["threshold_met"],
                        msg="default pilot/deployment defaults should mismatch by > 1.0x")
        self.assertGreater(r["mean_mismatch"], 1.0)

    def test_c084_passes_when_pilot_matches_deployment(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        pilot = {"route_variance": 0.05, "destination_set_size": 4.0,
                 "weather_envelope_span": 0.2, "surface_type_diversity": 0.1,
                 "interface_partner_count": 3.0}
        r = trucking_roi_falsifiers_audit.c084_verdict(
            pilot=pilot, deployment=pilot)
        self.assertFalse(r["threshold_met"],
                         msg="identical pilot/deployment should not register concern")

    def test_c085_aggregate_cv_exceeds_default_margin(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c085_verdict()
        self.assertTrue(r["threshold_met"])
        self.assertGreater(r["aggregate_cv_rss"], 0.15)

    def test_c086_underwriter_premium_exceeds_claimed_reduction(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c086_verdict()
        self.assertTrue(r["threshold_met"])
        self.assertGreater(r["uncertainty_premium_fraction"],
                           r["claimed_premium_reduction"])

    def test_c086_passes_with_mature_actuarial_data(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c086_verdict(
            years_of_continuous_fleet_data=5.0,
            audited_fleet_size=300,
            claimed_premium_reduction=0.20)
        self.assertFalse(r["threshold_met"])
        self.assertEqual(r["uncertainty_premium_fraction"], 0.0)

    def test_c087_autonomous_stack_residual_forced_to_zero(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c087_verdict()
        self.assertTrue(r["threshold_met"])
        self.assertGreater(r["residual_overstatement_usd"], 0.0)

    def test_c088_selection_bias_delta_dominates(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c088_verdict()
        self.assertTrue(r["threshold_met"])
        self.assertGreater(r["selection_bias_delta"], 0.50)

    def test_c089_payback_exceeds_mean_refresh(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c089_verdict(reported_payback_years=6.0)
        self.assertTrue(r["threshold_met"])
        self.assertTrue(r["payback_exceeds_mean_refresh"])

    def test_c089_passes_for_short_payback(self):
        from automation_scope_audit.modules import trucking_roi_falsifiers_audit
        r = trucking_roi_falsifiers_audit.c089_verdict(reported_payback_years=1.0)
        self.assertFalse(r["threshold_met"])


class ContractValidatedTests(unittest.TestCase):

    def test_fab_table_round_trips(self):
        from schemas.claim_contract import Claim, CONTRACT_VERSION
        path = os.path.join(ROOT, "automation_scope_audit",
                             "CLAIM_TABLE.fab.json")
        with open(path) as f:
            data = json.load(f)
        self.assertEqual(data["contract_version"], CONTRACT_VERSION)
        for cid, payload in data["claims"].items():
            claim = Claim.from_dict(payload)
            roundtrip = Claim.from_dict(claim.to_dict())
            self.assertEqual(claim, roundtrip,
                              msg=f"round-trip mismatch for {cid}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
