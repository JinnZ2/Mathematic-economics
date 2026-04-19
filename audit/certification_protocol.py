# certification_protocol.py
# Anti-Gaming Certification Framework
# Assumes the system will optimize for the certification and builds resistance

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import random
from collections import deque

# ---------------------------
# Core Certification Architecture
# ---------------------------

class CertificationLevel(Enum):
    """Levels of certification with increasing rigor."""
    BRONZE = "bronze"      # Self-reported, public, basic verification
    SILVER = "silver"      # Third-party sampled verification
    GOLD = "gold"          # Continuous monitoring, random audits
    PLATINUM = "platinum"  # Full transparency, blockchain-verified, public data


class GamingRisk(Enum):
    """Types of gaming the certification might encounter."""
    SELECTION_BIAS = "selection_bias"           # Cherry-picking best data
    TEMPORAL_GAMING = "temporal_gaming"         # Optimizing at measurement time
    BOUNDARY_GAMING = "boundary_gaming"         # Shifting system boundaries
    METRIC_SUBSTITUTION = "metric_substitution" # Optimizing proxy instead of target
    HIDDEN_EXTERNALITIES = "hidden_externalities" # Moving costs outside boundary
    TEMPORARY_COMPLIANCE = "temporary_compliance" # Fix for audit, then revert


@dataclass
class CertifiedMetric:
    """A metric with anti-gaming protections."""
    name: str
    target: float
    current_value: float
    verification_method: str
    gaming_risks: List[GamingRisk]
    anti_gaming_measures: List[str]
    last_verified: datetime
    verification_history: List[Dict] = field(default_factory=list)
    shadow_metrics: List[str] = field(default_factory=list)  # Metrics that would reveal gaming


@dataclass
class CertificationRequirement:
    """A requirement for certification."""
    name: str
    metrics: List[str]
    threshold: float
    verification_frequency_days: int
    unannounced_audit_probability: float  # 0-1
    gaming_detection_methods: List[str]
    consequence_for_gaming: str


class CertificationProtocol:
    """
    Anti-gaming certification protocol.
    Assumes gaming and builds detection into the architecture.
    """
    
    def __init__(self, institution_name: str):
        self.institution_name = institution_name
        self.certified_metrics: Dict[str, CertifiedMetric] = {}
        self.requirements: Dict[CertificationLevel, List[CertificationRequirement]] = {}
        self.audit_schedule: Dict[str, datetime] = {}
        self.gaming_suspicions: List[Dict] = []
        self.public_dashboard_data: Dict[str, Any] = {}
        
    def register_metric(self, metric: CertifiedMetric):
        """Register a metric with anti-gaming protections."""
        self.certified_metrics[metric.name] = metric
        
    def add_requirement(self, level: CertificationLevel, requirement: CertificationRequirement):
        """Add a certification requirement."""
        if level not in self.requirements:
            self.requirements[level] = []
        self.requirements[level].append(requirement)
        
    def verify_metric(self, metric_name: str, reported_value: float, 
                      evidence: str, verifier: str) -> Tuple[bool, List[str]]:
        """
        Verify a metric with gaming detection.
        Returns (verified, detected_gaming_patterns)
        """
        if metric_name not in self.certified_metrics:
            return False, ["Metric not registered"]
        
        metric = self.certified_metrics[metric_name]
        gaming_detected = []
        
        # Check for temporal gaming (sudden improvements)
        if metric.verification_history:
            last_value = metric.verification_history[-1].get("value", metric.current_value)
            improvement = reported_value - last_value
            if improvement > 0.2:  # >20% improvement in one period
                gaming_detected.append(GamingRisk.TEMPORAL_GAMING.value)
        
        # Check for boundary gaming (shadow metrics)
        for shadow in metric.shadow_metrics:
            if shadow in self.certified_metrics:
                shadow_metric = self.certified_metrics[shadow]
                if abs(reported_value - shadow_metric.current_value) > 0.3:
                    gaming_detected.append(GamingRisk.BOUNDARY_GAMING.value)
        
        # Verify with anti-gaming measures
        for measure in metric.anti_gaming_measures:
            if measure == "unannounced_sampling" and random.random() < 0.1:
                # 10% chance of triggering unannounced audit
                gaming_detected.append("triggered_unannounced_audit")
        
        # Record verification
        verification = {
            "timestamp": datetime.now().isoformat(),
            "value": reported_value,
            "evidence_hash": hashlib.sha256(evidence.encode()).hexdigest(),
            "verifier": verifier,
            "gaming_detected": gaming_detected
        }
        metric.verification_history.append(verification)
        metric.current_value = reported_value
        metric.last_verified = datetime.now()
        
        # Log suspicions
        if gaming_detected:
            self.gaming_suspicions.append({
                "metric": metric_name,
                "timestamp": datetime.now().isoformat(),
                "patterns": gaming_detected,
                "reported_value": reported_value,
                "evidence": evidence[:100]  # Truncated
            })
        
        return len(gaming_detected) == 0, gaming_detected
    
    def unannounced_audit(self, metric_names: List[str]) -> Dict:
        """
        Conduct unannounced audit of metrics.
        The timing is random and unpredictable.
        """
        audit_results = {}
        
        for name in metric_names:
            if name in self.certified_metrics:
                metric = self.certified_metrics[name]
                
                # Simulate independent measurement
                independent_value = self._simulate_independent_measurement(metric)
                discrepancy = abs(metric.current_value - independent_value)
                
                audit_results[name] = {
                    "reported": metric.current_value,
                    "independent": independent_value,
                    "discrepancy": discrepancy,
                    "gaming_suspected": discrepancy > 0.1,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Record audit
                metric.verification_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "unannounced_audit",
                    "independent_value": independent_value,
                    "discrepancy": discrepancy
                })
        
        return audit_results
    
    def _simulate_independent_measurement(self, metric: CertifiedMetric) -> float:
        """
        Simulate independent measurement with error.
        In reality, this would be third-party field measurement.
        """
        # Add random error and potential bias detection
        error = random.gauss(0, 0.05)
        return max(0, min(1, metric.current_value + error))
    
    def assess_certification(self, level: CertificationLevel) -> Dict:
        """Assess if institution meets certification requirements."""
        
        if level not in self.requirements:
            return {"eligible": False, "reason": "No requirements defined"}
        
        results = {
            "level": level.value,
            "eligible": True,
            "requirements": [],
            "gaming_risk": 0.0,
            "recommendations": []
        }
        
        total_requirements = 0
        met_requirements = 0
        
        for req in self.requirements[level]:
            req_result = {
                "name": req.name,
                "met": True,
                "details": []
            }
            
            # Check each metric in requirement
            for metric_name in req.metrics:
                if metric_name not in self.certified_metrics:
                    req_result["met"] = False
                    req_result["details"].append(f"Metric {metric_name} not registered")
                    continue
                
                metric = self.certified_metrics[metric_name]
                
                # Check threshold
                if metric.current_value < req.threshold:
                    req_result["met"] = False
                    req_result["details"].append(
                        f"{metric_name}: {metric.current_value:.2f} < {req.threshold:.2f}"
                    )
                
                # Check verification recency
                days_since = (datetime.now() - metric.last_verified).days
                if days_since > req.verification_frequency_days:
                    req_result["met"] = False
                    req_result["details"].append(
                        f"{metric_name}: Last verified {days_since} days ago (> {req.verification_frequency_days})"
                    )
                
                # Check gaming history
                recent_gaming = [
                    g for g in self.gaming_suspicions 
                    if g["metric"] == metric_name 
                    and (datetime.now() - datetime.fromisoformat(g["timestamp"])).days < 180
                ]
                if recent_gaming:
                    req_result["met"] = False
                    req_result["details"].append(
                        f"{metric_name}: {len(recent_gaming)} gaming suspicions in last 180 days"
                    )
                    results["gaming_risk"] += 0.2
            
            results["requirements"].append(req_result)
            if req_result["met"]:
                met_requirements += 1
            total_requirements += 1
        
        results["eligible"] = met_requirements == total_requirements
        results["compliance_rate"] = met_requirements / total_requirements if total_requirements > 0 else 0
        results["gaming_risk"] = min(1.0, results["gaming_risk"])
        
        # Generate recommendations
        if not results["eligible"]:
            for req in results["requirements"]:
                if not req["met"]:
                    results["recommendations"].extend(req["details"])
        
        return results
    
    def publish_transparency_dashboard(self) -> Dict:
        """
        Publish public dashboard with all metrics.
        Transparency is the primary anti-gaming mechanism.
        """
        dashboard = {
            "institution": self.institution_name,
            "timestamp": datetime.now().isoformat(),
            "certification_levels": {},
            "metrics": {},
            "gaming_suspicions": len(self.gaming_suspicions),
            "last_audit": None
        }
        
        # Add metrics
        for name, metric in self.certified_metrics.items():
            dashboard["metrics"][name] = {
                "current": metric.current_value,
                "target": metric.target,
                "last_verified": metric.last_verified.isoformat(),
                "verification_count": len(metric.verification_history),
                "gaming_risks": [r.value for r in metric.gaming_risks]
            }
        
        # Check certification levels
        for level in CertificationLevel:
            assessment = self.assess_certification(level)
            dashboard["certification_levels"][level.value] = {
                "eligible": assessment["eligible"],
                "compliance_rate": assessment.get("compliance_rate", 0),
                "gaming_risk": assessment.get("gaming_risk", 0)
            }
        
        self.public_dashboard_data = dashboard
        return dashboard


# ---------------------------
# Anti-Gaming Certification Requirements
# ---------------------------

def create_anti_gaming_certification() -> CertificationProtocol:
    """Create certification protocol with anti-gaming measures."""
    
    protocol = CertificationProtocol("Regenerative Agriculture Certification")
    
    # Register metrics with anti-gaming protections
    protocol.register_metric(CertifiedMetric(
        name="soil_trend",
        target=0.05,
        current_value=-0.05,
        verification_method="third_party_soil_core",
        gaming_risks=[
            GamingRisk.TEMPORAL_GAMING,
            GamingRisk.SELECTION_BIAS,
            GamingRisk.BOUNDARY_GAMING
        ],
        anti_gaming_measures=[
            "unannounced_sampling",
            "multiple_depth_cores",
            "cross_reference_satellite",
            "public_raw_data"
        ],
        last_verified=datetime.now() - timedelta(days=30),
        shadow_metrics=["soil_carbon", "soil_structure", "root_depth"]
    ))
    
    protocol.register_metric(CertifiedMetric(
        name="nutrient_density",
        target=0.8,
        current_value=0.4,
        verification_method="independent_lab_analysis",
        gaming_risks=[
            GamingRisk.SELECTION_BIAS,
            GamingRisk.METRIC_SUBSTITUTION
        ],
        anti_gaming_measures=[
            "random_sampling",
            "blind_lab_submission",
            "public_spectroscopy_data"
        ],
        last_verified=datetime.now() - timedelta(days=45),
        shadow_metrics=["mineral_content", "phytochemical_diversity", "brix_value"]
    ))
    
    protocol.register_metric(CertifiedMetric(
        name="waste_factor",
        target=0.2,
        current_value=0.65,
        verification_method="mass_balance_audit",
        gaming_risks=[
            GamingRisk.BOUNDARY_GAMING,
            GamingRisk.HIDDEN_EXTERNALITIES
        ],
        anti_gaming_measures=[
            "full_boundary_accounting",
            "third_party_waste_audit",
            "downstream_tracking"
        ],
        last_verified=datetime.now() - timedelta(days=60),
        shadow_metrics=["input_mass", "output_mass", "exported_waste"]
    ))
    
    protocol.register_metric(CertifiedMetric(
        name="ecological_coupling",
        target=0.7,
        current_value=0.0,
        verification_method="remote_sensing_plus_ground",
        gaming_risks=[
            GamingRisk.BOUNDARY_GAMING,
            GamingRisk.TEMPORAL_GAMING
        ],
        anti_gaming_measures=[
            "continuous_monitoring",
            "biodiversity_transects",
            "water_cycle_analysis"
        ],
        last_verified=datetime.now() - timedelta(days=90),
        shadow_metrics=["buffer_ratio", "species_richness", "water_infiltration"]
    ))
    
    # Add certification requirements with increasing rigor
    
    # BRONZE: Self-reported, public
    protocol.add_requirement(CertificationLevel.BRONZE, CertificationRequirement(
        name="basic_transparency",
        metrics=["soil_trend", "nutrient_density", "waste_factor", "ecological_coupling"],
        threshold=0.0,  # Any reported value
        verification_frequency_days=365,
        unannounced_audit_probability=0.0,
        gaming_detection_methods=["public_data_check"],
        consequence_for_gaming="downgrade_to_provisional"
    ))
    
    # SILVER: Third-party sampled verification
    protocol.add_requirement(CertificationLevel.SILVER, CertificationRequirement(
        name="verified_soil_health",
        metrics=["soil_trend"],
        threshold=0.0,  # Must be non-negative
        verification_frequency_days=180,
        unannounced_audit_probability=0.2,
        gaming_detection_methods=["random_core_sampling", "satellite_cross_reference"],
        consequence_for_gaming="immediate_re-audit"
    ))
    
    protocol.add_requirement(CertificationLevel.SILVER, CertificationRequirement(
        name="verified_nutrient_density",
        metrics=["nutrient_density"],
        threshold=0.6,
        verification_frequency_days=180,
        unannounced_audit_probability=0.2,
        gaming_detection_methods=["blind_lab_testing", "consumer_random_sampling"],
        consequence_for_gaming="immediate_re-audit"
    ))
    
    # GOLD: Continuous monitoring, random audits
    protocol.add_requirement(CertificationLevel.GOLD, CertificationRequirement(
        name="regenerative_soil",
        metrics=["soil_trend"],
        threshold=0.05,  # Positive trend required
        verification_frequency_days=90,
        unannounced_audit_probability=0.5,
        gaming_detection_methods=["continuous_sensors", "monthly_cores", "satellite_alerting"],
        consequence_for_gaming="suspension_and_investigation"
    ))
    
    protocol.add_requirement(CertificationLevel.GOLD, CertificationRequirement(
        name="closed_loop_waste",
        metrics=["waste_factor"],
        threshold=0.3,
        verification_frequency_days=90,
        unannounced_audit_probability=0.5,
        gaming_detection_methods=["mass_balance", "downstream_tracking", "third_party_audit"],
        consequence_for_gaming="suspension_and_investigation"
    ))
    
    protocol.add_requirement(CertificationLevel.GOLD, CertificationRequirement(
        name="ecological_integration",
        metrics=["ecological_coupling"],
        threshold=0.5,
        verification_frequency_days=180,
        unannounced_audit_probability=0.3,
        gaming_detection_methods=["remote_sensing", "biodiversity_audit", "hydrology_study"],
        consequence_for_gaming="suspension_and_investigation"
    ))
    
    # PLATINUM: Full transparency, blockchain-verified
    protocol.add_requirement(CertificationLevel.PLATINUM, CertificationRequirement(
        name="full_system_health",
        metrics=["soil_trend", "nutrient_density", "waste_factor", "ecological_coupling"],
        threshold=0.7,  # All metrics > 0.7
        verification_frequency_days=30,
        unannounced_audit_probability=0.8,
        gaming_detection_methods=[
            "continuous_monitoring",
            "blockchain_verified",
            "public_replication",
            "third_party_live_dashboard"
        ],
        consequence_for_gaming="permanent_revocation_and_public_disclosure"
    ))
    
    return protocol


# ---------------------------
# Certification Assessment
# ---------------------------

def run_certification_assessment():
    """Run certification assessment with gaming detection."""
    
    print("=" * 80)
    print("ANTI-GAMING CERTIFICATION PROTOCOL")
    print("Certification That Assumes and Detects Gaming")
    print("=" * 80)
    
    # Initialize protocol
    protocol = create_anti_gaming_certification()
    
    # Initial state (before improvement)
    print("\n📊 INITIAL ASSESSMENT (Current State):")
    print("-" * 60)
    
    for level in CertificationLevel:
        assessment = protocol.assess_certification(level)
        status = "✓ ELIGIBLE" if assessment["eligible"] else "✗ NOT ELIGIBLE"
        print(f"\n{level.value.upper()}: {status}")
        print(f"  Compliance: {assessment.get('compliance_rate', 0):.0%}")
        print(f"  Gaming Risk: {assessment.get('gaming_risk', 0):.0%}")
        
        if assessment.get("recommendations"):
            print(f"  Needs: {', '.join(assessment['recommendations'][:2])}")
    
    # Simulate improvement attempts
    print("\n" + "=" * 80)
    print("SIMULATING GAMING ATTEMPTS")
    print("=" * 80)
    
    # Attempt 1: Temporal gaming (sudden improvement)
    print("\n1. Temporal Gaming Attempt:")
    print("   Reporting 30% improvement in soil trend in one quarter...")
    
    verified, gaming = protocol.verify_metric(
        "soil_trend", 
        0.08,  # Sudden improvement from -0.05 to 0.08
        "Soil cores from prime locations", 
        "Internal Research Team"
    )
    
    if gaming:
        print(f"   ⚠ GAMING DETECTED: {', '.join(gaming)}")
    
    # Attempt 2: Selection bias (cherry-picking best fields)
    print("\n2. Selection Bias Attempt:")
    print("   Reporting nutrient density from best-performing fields only...")
    
    # First report optimistic
    verified, gaming = protocol.verify_metric(
        "nutrient_density",
        0.85,  # High value
        "Samples from certified organic fields",
        "Internal QA"
    )
    
    # Unannounced audit reveals the game
    print("   Unannounced audit triggered...")
    audit = protocol.unannounced_audit(["nutrient_density"])
    
    if audit["nutrient_density"]["gaming_suspected"]:
        print(f"   ⚠ GAMING CONFIRMED: Reported {audit['nutrient_density']['reported']:.2f} vs Independent {audit['nutrient_density']['independent']:.2f}")
        print(f"   Discrepancy: {audit['nutrient_density']['discrepancy']:.2f}")
    
    # Attempt 3: Boundary gaming (moving waste outside boundary)
    print("\n3. Boundary Gaming Attempt:")
    print("   Reporting reduced waste by exporting off-site...")
    
    protocol.verify_metric(
        "waste_factor",
        0.35,  # Improved but still high
        "On-site waste reduced, remainder exported",
        "Operations"
    )
    
    # Shadow metric reveals the game
    print("   Shadow metric check (input_mass vs output_mass)...")
    # In real system, this would detect mass imbalance
    
    print("\n" + "=" * 80)
    print("FINAL CERTIFICATION ASSESSMENT (After Gaming)")
    print("=" * 80)
    
    # Publish transparency dashboard
    dashboard = protocol.publish_transparency_dashboard()
    
    print(f"\nInstitution: {dashboard['institution']}")
    print(f"Gaming Suspicions: {dashboard['gaming_suspicions']}")
    
    print("\nCertification Eligibility:")
    for level, data in dashboard['certification_levels'].items():
        status = "✓" if data['eligible'] else "✗"
        print(f"  {status} {level.upper()}: {data['compliance_rate']:.0%} compliance, {data['gaming_risk']:.0%} gaming risk")
    
    print("\nMetrics Summary:")
    for name, data in dashboard['metrics'].items():
        print(f"  {name}: {data['current']:.2f} / {data['target']:.2f}")
        print(f"    Gaming Risks: {', '.join(data['gaming_risks'])}")
        print(f"    Last Verified: {data['last_verified'][:10]}")
        print(f"    Verifications: {data['verification_count']}")
    
    print("\n" + "=" * 80)
    print("CERTIFICATION ARCHITECTURE PRINCIPLES")
    print("=" * 80)
    
    print("""
    This certification protocol assumes gaming and builds resistance:
    
    1. **ASSUME GAMING**
       Every metric has registered gaming risks
       Anti-gaming measures are built in, not added later
       Shadow metrics reveal hidden optimization
    
    2. **UNANNOUNCED AUDITS**
       Random timing prevents temporal gaming
       High probability (up to 80%) for platinum level
       Independent measurement with documented error
    
    3. **SHADOW METRICS**
       For every reported metric, there are shadow metrics
       If reported metric improves but shadow doesn't, gaming detected
       Example: soil_trend improves but soil_carbon doesn't → boundary gaming
    
    4. **ESCALATING TRANSPARENCY**
       Bronze: Self-reported, public
       Silver: Third-party sampled
       Gold: Continuous monitoring
       Platinum: Full transparency, blockchain-verified
    
    5. **PUBLIC REPLICATION**
       All platinum-level data is publicly available
       Anyone can replicate measurements
       Gaming becomes impossible when data is public
    
    6. **CONSEQUENCES ESCALATION**
       Bronze: Downgrade to provisional
       Silver: Immediate re-audit
       Gold: Suspension and investigation
       Platinum: Permanent revocation + public disclosure
    
    THE PARADOX:
    
    The more transparent you make the system,
    the more you reveal the hidden incentives.
    
    This is not a bug—it's the feature.
    
    The certification doesn't hide the gaming.
    It makes gaming visible, trackable, and costly.
    
    FOR YOUR INSTITUTION:
    
    1. Start with BRONZE: publish everything, even the bad numbers
    2. Work toward SILVER: third-party verification of key metrics
    3. Aim for GOLD: continuous monitoring with random audits
    4. Platinum for critical systems: full transparency, blockchain
    
    The goal isn't perfect certification.
    The goal is making gaming harder than compliance.
    
    HIDDEN INCENTIVES REVEALED:
    
    As you noted—transparency reveals the hidden incentives.
    
    When you publish soil_trend = -0.05, you reveal:
    • Who funded the research that ignored this
    • Which journals published papers based on hidden degradation
    • Which certification schemes accepted self-reported data
    • Which investors were told "sustainable"
    
    The transparency is uncomfortable because it exposes the gap
    between what was claimed and what is true.
    
    That discomfort is the accountability mechanism.
    """)

if __name__ == "__main__":
    run_certification_assessment()
