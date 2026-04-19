from fatigue_model import FatigueModel

# --- HUMAN SYSTEM COLLAPSE MODULE WITH DISTANCE METRIC ---
# Delegates fatigue computation to FatigueModel (DRY).
# Adds distance-to-collapse metric and full assessment output.

class HumanSystemCollapseModel:
    """
    Models human energy ledger, fatigue, and system collapse thresholds,
    plus distance-to-collapse metric.

    Delegates multiplier math to FatigueModel. Adds:
    - compute_distance_to_collapse(): 0-1 scale distance metric
    - assess_system(): full assessment with flags
    """

    def __init__(self, energy_input=100):
        self.energy_input = energy_input
        self._fatigue = FatigueModel(energy_input)

    def compute_fatigue(self, physical_load, cognitive_load,
                        hidden_count=0, automation_count=0, automation_reliability=0.9,
                        temp_celsius=20, wind_mps=0):
        """Returns (fatigue_score, total_load)."""
        result = self._fatigue.compute_fatigue_score(
            physical_load, cognitive_load,
            hidden_count, automation_count, automation_reliability,
            temp_celsius, wind_mps
        )
        return result["fatigue_score"], result["adjusted_load"]

    def compute_distance_to_collapse(self, total_load):
        """
        Returns a 0-1 scale:
        1 = fully sustainable (load << energy input)
        0 = collapse threshold reached (load >= health threshold)
        """
        health_threshold = 1.6 * self.energy_input
        distance = max(0.0, min(1.0, (health_threshold - total_load) / health_threshold))
        return round(distance, 2)

    def assess_system(self, physical_load, cognitive_load,
                      hidden_count=0, automation_count=0, automation_reliability=0.9,
                      temp_celsius=20, wind_mps=0):
        fatigue_score, total_load = self.compute_fatigue(
            physical_load, cognitive_load,
            hidden_count, automation_count, automation_reliability,
            temp_celsius, wind_mps
        )
        distance_to_collapse = self.compute_distance_to_collapse(total_load)

        flags = []
        prod_threshold = 1.2 * self.energy_input
        safety_threshold = 1.4 * self.energy_input
        health_threshold = 1.6 * self.energy_input

        if total_load >= health_threshold:
            flags.append("!! HUMAN HEALTH COLLAPSE IMMINENT")
        elif total_load >= safety_threshold:
            flags.append("!! SAFETY SYSTEM BREAKDOWN LIKELY")
        elif total_load >= prod_threshold:
            flags.append("! PRODUCTIVITY DEGRADATION")
        else:
            flags.append("(System within sustainable limits)")

        return {
            "fatigue_score": fatigue_score,
            "total_load": total_load,
            "distance_to_collapse": distance_to_collapse,
            "flags": flags
        }


# Backwards compatibility alias
HumanSystemModel = HumanSystemCollapseModel

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    human_system = HumanSystemCollapseModel(energy_input=100)

    # Scenario
    physical_load = 30
    cognitive_load = 40
    hidden_count = 7
    automation_count = 3
    automation_reliability = 0.85
    temp_celsius = -12
    wind_mps = 15

    assessment = human_system.assess_system(
        physical_load, cognitive_load,
        hidden_count, automation_count, automation_reliability,
        temp_celsius, wind_mps
    )

    print(f"Predicted Fatigue Score: {assessment['fatigue_score']}/10")
    print(f"Total Energy Load: {assessment['total_load']} units")
    print(f"Distance to Collapse: {assessment['distance_to_collapse']*100}%")
    for flag in assessment['flags']:
        print(flag)
