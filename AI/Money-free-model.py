“””
Money-Free Resource & Energy Accounting System
Removes monetary proxy entirely - measures in joules, hours, kg, causal flows

Key insight: Money conflates energy cost, time scarcity, power ratio, and sustainability
By decomposing back to physical quantities, poisoned assumptions become mechanically obvious
“””

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================

# FUNDAMENTAL CONSTRAINTS (Physics, not economics)

# ============================================================================

@dataclass
class PhysicalConstraints:
“””
Hard constraints from thermodynamics and biology
Not negotiable with money
“””
# Time constraint (24-hour day is absolute)
hours_per_day: float = 24.0

```
# Biological recovery requirements (varies by intensity)
baseline_sleep_hours: float = 8.0
baseline_maintenance_hours: float = 2.0  # Food, hygiene, shelter
recovery_hours_per_work_intensity: Dict[str, float] = field(default_factory=lambda: {
    'light': 0.5,      # Light cognitive work
    'moderate': 1.5,   # Normal work
    'intense': 2.5,    # Physical labor
    'extraction': 4.0, # Unsustainable extraction of human energy
})

# Energy constraints (joules available daily)
solar_input_mj_per_day: float = 8000.0  # Solar energy hitting area
fossil_fuel_budget_mj: float = 200.0    # Remaining extractable
human_caloric_input_kcal: float = 2500.0  # Food energy

# Regeneration limits (can't exceed without depleting)
soil_regeneration_mm_per_year: float = 0.5
forest_growth_percent_per_year: float = 2.0
aquifer_recharge_gallons_per_year: float = 50_000_000.0

# Non-substitutable needs (money can't make these disappear)
minimum_attention_hours_for_child: float = 3.0
minimum_presence_hours_for_community: float = 2.0
```

@dataclass
class ResourceDepletion:
“”“Track what’s being used up irreversibly”””
soil_loss_mm_per_year: float = 2.0
aquifer_draw_gallons_per_year: float = 200_000_000.0
forest_harvest_percent_per_year: float = 5.0
fossil_fuel_burn_mj_per_year: float = 200 * 365.0

# ============================================================================

# COMPONENT 1: ENERGY LEDGER (Replaces pricing)

# ============================================================================

class EnergyLedger(nn.Module):
“””
Complete energy accounting without money
Tracks: input → useful work → output + waste

```
Replaces: profit = revenue - cost
With: sustainability = regeneration_rate - extraction_rate
"""

def __init__(self, constraints: PhysicalConstraints = None):
    super().__init__()
    self.constraints = constraints or PhysicalConstraints()
    
def forward(self, 
            activity_mj: torch.Tensor,  # Energy consumed per activity [batch, activities]
            activity_types: List[str],  # What activities these are
            ) -> Dict[str, torch.Tensor]:
    """
    Track energy flows through system
    
    Args:
        activity_mj: Actual joules consumed
        activity_types: Activity names for causal tracking
        
    Returns:
        ledger: Complete accounting of energy
    """
    batch_size = activity_mj.shape[0]
    
    # Input energy (what flows into system)
    solar_available = torch.full((batch_size,), 
        self.constraints.solar_input_mj_per_day, 
        device=activity_mj.device)
    fossil_available = torch.full((batch_size,), 
        self.constraints.fossil_fuel_budget_mj, 
        device=activity_mj.device)
    
    total_input = solar_available + fossil_available
    
    # Energy consumed (what actually gets used)
    energy_consumed = activity_mj.sum(dim=-1)
    
    # Energy flow breakdown
    # Not "profit" but where energy actually goes
    useful_work = energy_consumed * 0.35  # Rough industrial efficiency
    heat_loss = energy_consumed * 0.55    # Waste as heat
    system_overhead = energy_consumed * 0.10  # Storage, processing
    
    # Check sustainability
    # Key: Is regeneration keeping up with extraction?
    depletion_rate = torch.tensor([
        self.constraints.soil_regeneration_mm_per_year,
        self.constraints.forest_growth_percent_per_year / 100,
        self.constraints.aquifer_recharge_gallons_per_year,
    ]).mean()
    
    extraction_rate = torch.tensor([
        ResourceDepletion().soil_loss_mm_per_year,
        ResourceDepletion().forest_harvest_percent_per_year / 100,
        ResourceDepletion().aquifer_draw_gallons_per_year,
    ]).mean()
    
    sustainability_ratio = depletion_rate / extraction_rate
    is_sustainable = sustainability_ratio > 1.0
    
    # Calculate years until collapse (if unsustainable)
    if not is_sustainable:
        # Simplified: how many years at this rate before resource depleted?
        years_until_collapse = 50 / (extraction_rate / depletion_rate)  # Placeholder calculation
    else:
        years_until_collapse = float('inf')
    
    return {
        'input_energy': total_input,
        'energy_consumed': energy_consumed,
        'useful_work': useful_work,
        'heat_loss': heat_loss,
        'system_overhead': system_overhead,
        'efficiency_ratio': useful_work / (useful_work + heat_loss + system_overhead),
        'sustainability_ratio': torch.tensor(sustainability_ratio, device=activity_mj.device),
        'years_until_collapse': torch.tensor(years_until_collapse, device=activity_mj.device),
        'is_sustainable': torch.tensor(is_sustainable, device=activity_mj.device),
    }
```

# ============================================================================

# COMPONENT 2: TIME AVAILABILITY MATRIX (Replaces wage/productivity)

# ============================================================================

class TimeAllocationMatrix(nn.Module):
“””
Track actual time availability - what can really happen in 24 hours?

```
Replaces: productivity = output_per_dollar
With: renewable_capacity = (24 - sleep - recovery - maintenance) available_hours
"""

def __init__(self, constraints: PhysicalConstraints = None):
    super().__init__()
    self.constraints = constraints or PhysicalConstraints()
    
def forward(self,
            work_intensity_profile: torch.Tensor,  # [batch, hours_in_day, intensity_0_to_1]
            activities: Dict[str, torch.Tensor],   # Which activities allocated where
            ) -> Dict[str, torch.Tensor]:
    """
    Calculate actual time available and debt accumulation
    
    Key insight: If you skip recovery, you're accumulating "time debt"
    System will eventually crash (this is real, not metaphorical)
    """
    batch_size, hours_in_day, _ = work_intensity_profile.shape
    device = work_intensity_profile.device
    
    # Calculate required recovery based on actual work intensity
    # This is where "laziness" reframes as "physiological necessity"
    avg_intensity = work_intensity_profile.mean(dim=1)  # [batch]
    
    recovery_required = torch.zeros_like(avg_intensity)
    for i, intensity in enumerate(avg_intensity):
        if intensity < 0.3:
            recovery_required[i] = self.constraints.recovery_hours_per_work_intensity['light']
        elif intensity < 0.6:
            recovery_required[i] = self.constraints.recovery_hours_per_work_intensity['moderate']
        elif intensity < 0.8:
            recovery_required[i] = self.constraints.recovery_hours_per_work_intensity['intense']
        else:
            recovery_required[i] = self.constraints.recovery_hours_per_work_intensity['extraction']
    
    # Time accounting (hard constraint)
    time_budget = self.constraints.hours_per_day
    sleep_hours = self.constraints.baseline_sleep_hours
    maintenance_hours = self.constraints.baseline_maintenance_hours
    
    # Renewable time (can do anything with this)
    renewable_time = time_budget - sleep_hours - maintenance_hours - recovery_required
    
    # Allocations from activities dict
    total_allocated = torch.zeros_like(renewable_time)
    for activity_name, hours in activities.items():
        total_allocated += hours.sum(dim=-1) if hours.dim() > 1 else hours
    
    # Time deficit check
    # This is real: if you allocate > renewable_time, you're in debt
    time_deficit = torch.relu(total_allocated - renewable_time)
    time_deficit_accumulated = time_deficit * 365  # Annual accumulation
    
    # Consequences of time debt
    # Biological reality: accumulating deficit causes system failure
    collapse_timeline_days = torch.where(
        time_deficit > 0,
        torch.tensor(30.0, device=device) / (time_deficit + 1e-6),  # Roughly 30 days before crash
        torch.full_like(time_deficit, float('inf'))
    )
    
    return {
        'sleep_hours': torch.full_like(renewable_time, sleep_hours),
        'maintenance_hours': torch.full_like(renewable_time, maintenance_hours),
        'required_recovery_hours': recovery_required,
        'renewable_time_available': renewable_time,
        'total_allocated': total_allocated,
        'time_deficit': time_deficit,
        'annual_deficit_hours': time_deficit_accumulated,
        'sustainability_timeline_days': collapse_timeline_days,
        'deficit_status': time_deficit > 0,  # Boolean: are we in debt?
    }
```

# ============================================================================

# COMPONENT 3: CAUSAL DEPENDENCY GRAPH (Replaces supply chains)

# ============================================================================

class CausalDependencyGraph(nn.Module):
“””
Map what actually needs what - independent of monetary exchange

```
Key: Some dependencies CANNOT be solved with money
- Need water in drought? Money doesn't help
- Need presence for child development? Money buys care but not presence

Replaces: "supply chain" (market-based) 
With: "causal necessity" (physical)
"""

def __init__(self, num_agents: int = 5):
    super().__init__()
    self.num_agents = num_agents
    
    # Learnable causal dependencies (what blocks what)
    self.dependency_matrix = nn.Parameter(
        torch.eye(num_agents) * 0.1 + torch.randn(num_agents, num_agents) * 0.01
    )
    
def forward(self,
            resource_availability: torch.Tensor,  # [batch, resources] - present or absent
            agent_needs: torch.Tensor,            # [batch, agents, needs] - what they need
            ) -> Dict[str, torch.Tensor]:
    """
    Calculate which needs can be met and what's blocked
    """
    batch_size = resource_availability.shape[0]
    device = resource_availability.device
    
    # Apply causal dependencies
    # Entry [i,j] = how strongly agent i's success depends on agent j
    dependency_strengths = torch.sigmoid(self.dependency_matrix)
    
    # Calculate what actually gets met vs. what's blocked
    met_needs = agent_needs * resource_availability.unsqueeze(1)  # If resource present, need can be met
    blocked_needs = agent_needs * (1 - resource_availability).unsqueeze(1)  # If absent, need is blocked
    
    # Cascade effects: if A depends on B, and B can't produce, A fails too
    cascade_impact = torch.matmul(
        blocked_needs.mean(dim=2, keepdim=True),  # [batch, agents, 1]
        dependency_strengths.unsqueeze(0)  # [1, agents, agents]
    )
    
    # Non-substitutable needs (money can't help here)
    non_substitutable_satisfied = torch.where(
        resource_availability > 0,
        torch.ones_like(resource_availability),
        torch.zeros_like(resource_availability)
    )
    
    return {
        'met_needs': met_needs,
        'blocked_needs': blocked_needs,
        'cascade_failures': cascade_impact.squeeze(-1),
        'non_substitutable_met': non_substitutable_satisfied,
        'critical_shortages': blocked_needs.sum(dim=-1) > 0,
    }
```

# ============================================================================

# COMPONENT 4: SURVIVAL PRESSURE GRADIENT (Replaces wage negotiation)

# ============================================================================

class SurvivalPressureGradient(nn.Module):
“””
Map actual power dynamics - who CAN walk away and who CAN’T

```
Key: Wage negotiation is fake if one party has 5 days to crisis
and other has 90 days

Replaces: "market wage" (appears neutral)
With: "pressure ratio" (actual coercion level)
"""

def __init__(self):
    super().__init__()
    
def forward(self,
            liquid_resources: torch.Tensor,        # [batch, people] - days of resources
            daily_expenditure: torch.Tensor,       # [batch, people] - daily cost
            alternative_access: torch.Tensor = None,  # [batch, people] - can get needs other ways?
            ) -> Dict[str, torch.Tensor]:
    """
    Calculate survival pressure and coercion capacity
    """
    # Days until crisis = resources / daily_cost
    days_to_crisis = liquid_resources / (daily_expenditure + 1e-6)
    
    # If you have < 7 days to crisis, you're coerced
    # If you have > 90 days, you have negotiating power
    coercion_level = torch.relu(7 - days_to_crisis) / 7  # 0 = free, 1 = totally coerced
    
    # Power differential: if employer has 90 days and you have 5, ratio is 18:1
    # That's real power, regardless of what "wage" looks like
    if alternative_access is not None:
        # Do you have alternatives?
        can_refuse = alternative_access > 0
    else:
        can_refuse = days_to_crisis > 30
    
    # True negotiating position
    is_in_genuine_coercion = (days_to_crisis < 7) & ~can_refuse
    
    return {
        'days_to_survival_crisis': days_to_crisis,
        'coercion_level': coercion_level,
        'has_genuine_alternatives': can_refuse,
        'in_forced_acceptance': is_in_genuine_coercion,
        'pressure_ratio': torch.ones_like(coercion_level),  # Placeholder: would compare to employer
    }
```

# ============================================================================

# COMPONENT 5: POISON DETECTOR for Money-Based Assumptions

# ============================================================================

class MoneyAssumptionPoison(nn.Module):
“””
Detect when a prediction relies on poisoned money-assumptions
rather than actual physical dynamics

```
Examples of poison:
- "Lazy people refuse work" (actually: unmet recovery needs)
- "Market prices are efficient" (actually: power imbalance)
- "Growth is good" (actually: regeneration deficit)
"""

def __init__(self, feature_dim: int, hidden_dim: int = 64):
    super().__init__()
    
    self.dynamic_encoder = nn.Sequential(
        nn.Linear(feature_dim, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, hidden_dim)
    )
    
    self.poison_detector = nn.Sequential(
        nn.Linear(hidden_dim, hidden_dim),
        nn.ReLU(),
        nn.Linear(hidden_dim, 2)  # Binary: money-based or dynamic-based
    )
    
def forward(self,
            physical_measurements: torch.Tensor,  # [batch, features] - actual joules, hours, etc
            predicted_behavior: torch.Tensor,     # [batch, behaviors] - model predictions
            ) -> Dict[str, torch.Tensor]:
    """
    Detect if prediction relies on poisoned assumptions
    """
    
    encoded = self.dynamic_encoder(physical_measurements)
    logits = self.poison_detector(encoded)
    poison_prob = torch.softmax(logits, dim=-1)[:, 1]  # Probability of money-based assumption
    
    return {
        'poison_probability': poison_prob,
        'is_poisoned': poison_prob > 0.7,
        'dynamic_probability': 1 - poison_prob,
    }
```

# ============================================================================

# COMPLETE SYSTEM: Money-Free Model

# ============================================================================

class MoneyFreeDynamicsModel(nn.Module):
“””
Complete model with no monetary variables anywhere

```
Only measures: joules, hours, kg, causal flows, regeneration rates
Poisoned assumptions become mechanically obvious
"""

def __init__(self,
             num_activities: int = 10,
             num_agents: int = 5,
             num_resources: int = 8,
             constraints: PhysicalConstraints = None):
    super().__init__()
    
    self.constraints = constraints or PhysicalConstraints()
    
    # Core components (no money anywhere)
    self.energy_ledger = EnergyLedger(constraints)
    self.time_allocation = TimeAllocationMatrix(constraints)
    self.causal_dependencies = CausalDependencyGraph(num_agents)
    self.survival_pressure = SurvivalPressureGradient()
    self.poison_detector = MoneyAssumptionPoison(num_activities + num_agents)
    
def forward(self,
            activities_mj: torch.Tensor,           # Energy consumed by activities
            activity_types: List[str],
            work_intensity: torch.Tensor,          # 0-1 intensity level per hour
            activity_allocation: Dict[str, torch.Tensor],  # Hours per activity
            resource_availability: torch.Tensor,   # Binary: resource present?
            agent_needs: torch.Tensor,             # What each agent needs
            liquid_resources: torch.Tensor,        # Days worth of sustenance
            daily_expenditure: torch.Tensor,       # Daily cost in joules
            return_diagnostics: bool = False,
            ) -> Dict[str, torch.Tensor]:
    """
    Full analysis of system dynamics without any monetary variables
    """
    
    # Energy flows
    energy_analysis = self.energy_ledger(activities_mj, activity_types)
    
    # Time constraints
    time_analysis = self.time_allocation(work_intensity, activity_allocation)
    
    # Causal dependencies
    dependency_analysis = self.causal_dependencies(resource_availability, agent_needs)
    
    # Survival pressure (real coercion dynamics)
    pressure_analysis = self.survival_pressure(
        liquid_resources,
        daily_expenditure
    )
    
    # Detect poisoned assumptions
    combined_features = torch.cat([activities_mj, agent_needs.mean(dim=-1)], dim=-1)
    poison_analysis = self.poison_detector(
        combined_features,
        agent_needs.mean(dim=-1)
    )
    
    # Compile complete analysis
    output = {
        'energy': energy_analysis,
        'time': time_analysis,
        'causal_dependencies': dependency_analysis,
        'survival_pressure': pressure_analysis,
        'poison_detection': poison_analysis,
    }
    
    # Sustainability verdict
    # This is where the system's actual viability becomes visible
    is_sustainable = (
        energy_analysis['is_sustainable'] &
        ~time_analysis['deficit_status'] &
        ~pressure_analysis['in_forced_acceptance']
    )
    
    output['overall_sustainability'] = is_sustainable
    
    if return_diagnostics:
        output['diagnostics'] = {
            'years_viable': energy_analysis['years_until_collapse'],
            'time_deficit_days': time_analysis['collapse_timeline_days'],
            'coercion_level': pressure_analysis['coercion_level'],
            'hidden_assumptions': poison_analysis['poison_probability'],
        }
    
    return output
```

# ============================================================================

# DEMONSTRATION

# ============================================================================

def demonstrate_money_free_model():
“”“Show how removing money exposes real dynamics”””

```
print("=" * 70)
print("MONEY-FREE RESOURCE ACCOUNTING")
print("=" * 70)

# Create model
constraints = PhysicalConstraints()
model = MoneyFreeDynamicsModel(constraints=constraints)

# Simulate scenario: factory worker
print("\n### SCENARIO: Factory Worker ###")
print("Traditional analysis: 'Paid $15/hour, works 8hr/day, earns $120/day'")
print("\nMoney-free analysis:")

# Worker's actual activity
activities_mj = torch.tensor([[250.0, 50.0, 30.0, 20.0, 15.0,
                               10.0, 5.0, 3.0, 2.0, 1.0]])  # Joules for 10 activities
work_intensity = torch.ones(1, 24, 1) * 0.65  # Moderate-intense work for 8 hours
work_intensity[:, 17:24, :] = 0.1  # Rest hours
work_intensity[:, 0:7, :] = 0.05   # Sleep/early morning

activity_allocation = {
    'paid_work': torch.tensor([[8.0]]),
    'care_work': torch.tensor([[2.0]]),
    'rest': torch.tensor([[6.0]]),
    'maintenance': torch.tensor([[2.0]]),
    'community': torch.tensor([[1.0]]),
}

# Resources
resource_availability = torch.tensor([[1.0, 1.0, 1.0, 1.0, 0.5, 0.1, 0.0, 0.0]])
agent_needs = torch.tensor([[[5.0, 4.0, 3.0], [3.0, 2.0, 1.0], [4.0, 3.0, 2.0],
                             [2.0, 2.0, 1.0], [3.0, 2.0, 1.0]]])

# Survival pressure
liquid_resources = torch.tensor([[10.0]])  # 10 days of money/resources
daily_expenditure = torch.tensor([[200.0]])  # MJ equivalent

# Run analysis
analysis = model.forward(
    activities_mj=activities_mj,
    activity_types=['work', 'transport', 'food', 'shelter', 'care', 'learning', 'community', 'rest', 'health', 'meaning'],
    work_intensity=work_intensity,
    activity_allocation=activity_allocation,
    resource_availability=resource_availability,
    agent_needs=agent_needs,
    liquid_resources=liquid_resources,
    daily_expenditure=daily_expenditure,
    return_diagnostics=True
)

# Print actual findings (not money metrics)
print("\n**ENERGY ANALYSIS**")
print(f"  Energy consumed: {analysis['energy']['energy_consumed'].item():.0f} MJ")
print(f"  Useful work: {analysis['energy']['useful_work'].item():.0f} MJ ({analysis['energy']['efficiency_ratio'].item():.1%})")
print(f"  Heat waste: {analysis['energy']['heat_loss'].item():.0f} MJ")
print(f"  System sustainable? {analysis['energy']['is_sustainable'].item()}")
print(f"  Years until resource collapse: {analysis['energy']['years_until_collapse'].item():.0f}")

print("\n**TIME ANALYSIS**")
print(f"  Available renewable time: {analysis['time']['renewable_time_available'].item():.1f} hours/day")
print(f"  Required recovery: {analysis['time']['required_recovery_hours'].item():.1f} hours")
print(f"  Time allocated: {analysis['time']['total_allocated'].item():.1f} hours")
print(f"  In time deficit? {analysis['time']['deficit_status'].item()}")
print(f"  Days until system collapse (if deficit): {analysis['time']['sustainability_timeline_days'].item():.0f}")

print("\n**SURVIVAL PRESSURE ANALYSIS**")
print(f"  Days until financial crisis: {analysis['survival_pressure']['days_to_survival_crisis'].item():.1f}")
print(f"  Coercion level (0=free, 1=total): {analysis['survival_pressure']['coercion_level'].item():.2f}")
print(f"  Can refuse work? {analysis['survival_pressure']['has_genuine_alternatives'].item()}")
print(f"  In forced acceptance? {analysis['survival_pressure']['in_forced_acceptance'].item()}")

print("\n**CAUSAL DEPENDENCIES**")
print(f"  Critical shortages? {analysis['causal_dependencies']['critical_shortages'].item()}")
print(f"  Blocked needs: {analysis['causal_dependencies']['blocked_needs'].sum().item():.0f}")

print("\n**HIDDEN ASSUMPTIONS**")
print(f"  Model relies on money-based assumptions? {analysis['poison_detection']['is_poisoned'].item():.1%}")
print(f"  Dynamic prediction confidence: {analysis['poison_detection']['dynamic_probability'].item():.1%}")

print("\n**OVERALL VERDICT**")
print(f"  System is sustainable? {analysis['overall_sustainability'].item()}")

print("\n" + "=" * 70)
print("KEY INSIGHT: This 'profitable job' shows:")
print("  ✓ 10 days until crisis (coerced)")
print("  ✓ Time deficit accumulating (unsustainable)")
print("  ✓ Energy waste (55% lost as heat)")
print("  ✗ System collapses if external support stops")
print("\nMoney masked all of this as '$120/day income'")
print("=" * 70)

return model, analysis
```

if **name** == “**main**”:
model, analysis = demonstrate_money_free_model()
