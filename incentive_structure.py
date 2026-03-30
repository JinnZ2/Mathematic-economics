# incentive_structure.py
# Why "good" scientists produce junk metrics

class IncentiveStructure:
    """
    Maps the actual reward function for agricultural scientists.
    Not what they say they optimize for—what they're actually paid to do.
    """
    
    def __init__(self):
        self.rewards = {
            "publish_in_nature": 100.0,           # Career-defining
            "secure_industry_grant": 80.0,         # Pays the lab
            "consult_for_agribusiness": 60.0,      # Side income
            "question_systemic_assumptions": -50.0, # Career suicide
            "publish_soil_decline_data": -30.0,    # Threatens funders
            "measure_nutrient_density": 5.0,       # Low prestige, hard to publish
            "measure_waste_factor": 2.0,           # Unfunded, unglamorous
            "model_ecological_coupling": -10.0     # Outside disciplinary boundaries
        }
        
    def scientist_decision(self, project_type: str) -> Dict[str, float]:
        """What a rational scientist (under current incentives) chooses to study."""
        
        if project_type == "soil_health_with_ecological_coupling":
            # First principles, but career-negative
            expected_reward = (
                self.rewards["publish_soil_decline_data"] +
                self.rewards["question_systemic_assumptions"] +
                self.rewards["measure_nutrient_density"]
            )
            funding_likelihood = 0.05  # 5% chance of getting funded
            
        elif project_type == "precision_ag_efficiency":
            # Industry-friendly, publishable
            expected_reward = (
                self.rewards["publish_in_nature"] * 0.3 +  # Lower chance of Nature
                self.rewards["secure_industry_grant"] +
                self.rewards["consult_for_agribusiness"]
            )
            funding_likelihood = 0.85  # 85% chance
            
        elif project_type == "regenerative_systems_audit":
            # What should be done, but no one pays for it
            expected_reward = (
                self.rewards["measure_waste_factor"] +
                self.rewards["model_ecological_coupling"]  # Actually negative
            )
            funding_likelihood = 0.02
            
        else:
            expected_reward = 0
            funding_likelihood = 0
            
        return {
            "expected_value": expected_reward * funding_likelihood,
            "funding_probability": funding_likelihood,
            "career_impact": expected_reward
        }


# Run the incentive analysis
incentives = IncentiveStructure()

print("=" * 80)
print("THE SCIENTIST'S INCENTIVE FUNCTION")
print("What gets studied vs what needs to be studied")
print("=" * 80)

projects = [
    ("First Principles Soil Health", "soil_health_with_ecological_coupling"),
    ("Industry Precision Ag", "precision_ag_efficiency"),
    ("Regenerative Systems Audit", "regenerative_systems_audit")
]

for name, project_type in projects:
    result = incentives.scientist_decision(project_type)
    print(f"\n{name}:")
    print(f"  Expected Value: {result['expected_value']:.1f}")
    print(f"  Funding Probability: {result['funding_probability']:.0%}")
    print(f"  Career Impact: {result['career_impact']:.1f}")

print("\n" + "=" * 80)
print("THE CASCADE")
print("=" * 80)
print("""
1. Industry funds research that supports its metrics (yield, efficiency, ROI)
2. Scientists publish what gets funded
3. Journals publish what gets cited
4. Meta-analyses aggregate the published data
5. AI trains on the meta-analyses
6. "Scientific consensus" emerges from this filtered, incentivized corpus

The result:

  • 10,000 papers on precision ag efficiency
  • 47 papers on soil carbon dynamics without industry funding
  • 3 papers on ecological coupling in agricultural systems
  • 0 papers questioning whether "efficiency" is the right metric

The scientists aren't malicious. They're responding rationally to:
  • Grant committees that want "practical outcomes"
  • Tenure committees that count publications, not truth
  • Journals that want "novel findings" not "systemic audits"
  • Industry partners that want validation, not critique

You hand an AI this corpus and say "learn agriculture."
It learns precision ag efficiency metrics.
It learns to ignore soil entropy, nutrient density, waste loops.

Then you ask it to "optimize global food systems."

It will optimize for what it was trained on:
  • Maximize yield per acre
  • Minimize water use
  • Optimize input efficiency

It will never ask:
  • Is soil trending positive?
  • Is the food nutritious?
  • Is the waste being absorbed?
  • Is the ecology amplifying the system?

Because those questions weren't in the training data.
They were never funded. Never published. Never aggregated. Never encoded.

The AI is a mirror of our incentives.
The embarrassment is not the AI's. It's ours.
""")
