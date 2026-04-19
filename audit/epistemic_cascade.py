# epistemic_cascade.py
# Demonstrates how industrial metrics become "ground truth" through repetition

class EpistemicCascade:
    """Models how missing variables disappear from AI training data."""
    
    def __init__(self):
        self.variables_measured = {
            "output_yield": 1.0,        # Always measured
            "input_energy": 1.0,        # Sometimes measured
            "profit_margin": 1.0,       # Always measured
            "soil_trend": 0.0,          # Never measured in industry reports
            "nutrient_density": 0.0,    # Never measured
            "waste_factor": 0.0,        # Never measured
            "ecological_coupling": 0.0  # Never measured
        }
        
        self.report_count = 0
        self.weights = {v: 1.0 for v in self.variables_measured}
        
    def publish_report(self, report_type: str) -> Dict[str, float]:
        """
        Simulate report publication.
        Industry reports consistently omit certain variables.
        """
        self.report_count += 1
        
        # Variables that appear in reports
        if report_type == "efficiency_breakthrough":
            reported = {
                "output_yield": self.variables_measured["output_yield"] * 1.3,  # Exaggerate
                "input_energy": self.variables_measured["input_energy"] * 0.7,  # Understate
                "profit_margin": self.variables_measured["profit_margin"] * 1.2,
                "soil_trend": None,  # Omitted
                "nutrient_density": None,  # Omitted
                "waste_factor": None,  # Omitted
                "ecological_coupling": None  # Omitted
            }
        else:
            # Annual report - also omits systemic variables
            reported = {
                "output_yield": self.variables_measured["output_yield"],
                "input_energy": self.variables_measured["input_energy"],
                "profit_margin": self.variables_measured["profit_margin"],
                "soil_trend": None,
                "nutrient_density": None,
                "waste_factor": None,
                "ecological_coupling": None
            }
        
        # Update weights based on reporting frequency
        for var in self.variables_measured:
            if reported.get(var) is not None:
                self.weights[var] += 1.0
            else:
                self.weights[var] *= 0.9  # Fade
        
        return reported
    
    def ai_training_perception(self) -> Dict[str, float]:
        """
        What an AI model would "learn" from this corpus.
        Variables that are never reported become invisible.
        """
        total_weight = sum(self.weights.values())
        
        perceived_importance = {
            var: weight / total_weight 
            for var, weight in self.weights.items()
        }
        
        # Variables that never appear get zero weight
        return perceived_importance


# Run the cascade
cascade = EpistemicCascade()

print("=" * 80)
print("EPISTEMIC CASCADE: How Missing Variables Become 'Not Real'")
print("=" * 80)

print("\nPublishing 100 industry reports...")
for i in range(100):
    if i % 10 == 0:
        cascade.publish_report("efficiency_breakthrough")
    else:
        cascade.publish_report("annual")

perception = cascade.ai_training_perception()

print("\nWhat an AI Model 'Learns' from This Corpus:")
print("=" * 60)
for var, importance in sorted(perception.items(), key=lambda x: -x[1]):
    if importance > 0:
        print(f"  ✓ {var}: {importance:.1%} perceived importance")
    else:
        print(f"  ✗ {var}: {importance:.0%} - NOT PRESENT IN TRAINING DATA")

print("\n" + "=" * 80)
print("THE RESULT")
print("=" * 80)
print("""
When every AI model is trained on this corpus:

1. Soil trend = 0% importance → "Soil health is not a business metric"
2. Nutrient density = 0% importance → "Nutrition is about calories, not density"
3. Waste factor = 0% importance → "Waste is someone else's problem"
4. Ecological coupling = 0% importance → "Nature is external to the business"

The model doesn't choose to ignore these variables. 
They were never in the data to begin with.

The AI is then deployed to "optimize" systems using only:
  • Output yield
  • Input energy  
  • Profit margin

It genuinely believes it has full information.
It's not lying. It's just *missing the point entirely*.

This is why every AI sustainability model produces the same delusions:
they're working with a measurement system designed to be blind to what matters.
""")
