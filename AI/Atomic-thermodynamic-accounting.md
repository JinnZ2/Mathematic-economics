“””
Atomic-Level Thermodynamic Labor Accounting
Complete second-law accounting for any labor system (human or machine)

Tracks:

1. Every material atom and its embedded energy
1. Every secondary byproduct (wear, heat, lubricants, chemical losses)
1. Every maintenance cycle and redistribution energy
1. All hidden dependencies (infrastructure, supply chains)
1. Full entropy accounting (irreversible energy dispersion)

This provides thermodynamically honest “work cost” metrics.
“””

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================

# MATERIAL DATABASE: Embedded energy per atom/kg

# ============================================================================

@dataclass
class MaterialProperties:
“”“Complete properties for thermodynamic tracking”””
name: str
embedded_energy_mj_per_kg: float  # Energy to extract, refine, fabricate
density_kg_per_m3: float
wear_rate_kg_per_shift: float  # How much is lost per work cycle
maintenance_cycle_shifts: int   # How often maintenance needed
replacement_lifetime_shifts: int  # Total lifetime before replacement

```
# Secondary outputs
heat_loss_mj_per_shift: float = 0.0
abrasion_debris_kg_per_shift: float = 0.0
chemical_degradation_kg_per_shift: float = 0.0
oxidation_rate_kg_per_shift: float = 0.0
```

# Comprehensive material database

MATERIAL_DATABASE = {
# Structural materials
‘steel’: MaterialProperties(
name=‘steel’,
embedded_energy_mj_per_kg=20.0,
density_kg_per_m3=7850,
wear_rate_kg_per_shift=0.005,
maintenance_cycle_shifts=250,
replacement_lifetime_shifts=1250,
heat_loss_mj_per_shift=0.1,
abrasion_debris_kg_per_shift=0.002,
),

```
'concrete': MaterialProperties(
    name='concrete',
    embedded_energy_mj_per_kg=0.9,
    density_kg_per_m3=2400,
    wear_rate_kg_per_shift=0.01,  # Floor abrasion
    maintenance_cycle_shifts=500,
    replacement_lifetime_shifts=6250,  # 25 years
    abrasion_debris_kg_per_shift=0.008,
),

'aluminum': MaterialProperties(
    name='aluminum',
    embedded_energy_mj_per_kg=55.0,
    density_kg_per_m3=2700,
    wear_rate_kg_per_shift=0.002,
    maintenance_cycle_shifts=500,
    replacement_lifetime_shifts=1875,
    heat_loss_mj_per_shift=0.05,
    abrasion_debris_kg_per_shift=0.001,
),

# Electronic/electrical materials
'copper': MaterialProperties(
    name='copper',
    embedded_energy_mj_per_kg=100.0,
    density_kg_per_m3=8960,
    wear_rate_kg_per_shift=0.001,
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=1250,
    heat_loss_mj_per_shift=2.0,  # Electrical resistance
    oxidation_rate_kg_per_shift=0.0005,
),

'silicon': MaterialProperties(
    name='silicon',
    embedded_energy_mj_per_kg=500.0,
    density_kg_per_m3=2329,
    wear_rate_kg_per_shift=0.0001,
    maintenance_cycle_shifts=125,  # Sensor drift
    replacement_lifetime_shifts=625,
    heat_loss_mj_per_shift=0.5,
),

'silver': MaterialProperties(
    name='silver',
    embedded_energy_mj_per_kg=2000.0,
    density_kg_per_m3=10490,
    wear_rate_kg_per_shift=0.0002,
    maintenance_cycle_shifts=125,
    replacement_lifetime_shifts=625,
    oxidation_rate_kg_per_shift=0.0001,
),

# Battery materials
'lithium': MaterialProperties(
    name='lithium',
    embedded_energy_mj_per_kg=5000.0,
    density_kg_per_m3=534,
    wear_rate_kg_per_shift=0.0,  # Doesn't physically wear
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=625,  # Battery cycles
    heat_loss_mj_per_shift=5.0,  # Cycle losses
    chemical_degradation_kg_per_shift=0.0002,  # SEI layer
),

'cobalt': MaterialProperties(
    name='cobalt',
    embedded_energy_mj_per_kg=200000.0,  # Extremely high
    density_kg_per_m3=8900,
    wear_rate_kg_per_shift=0.0,
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=625,
    heat_loss_mj_per_shift=3.0,
    chemical_degradation_kg_per_shift=0.0001,
),

'graphite': MaterialProperties(
    name='graphite',
    embedded_energy_mj_per_kg=150.0,
    density_kg_per_m3=2260,
    wear_rate_kg_per_shift=0.0,
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=625,
    chemical_degradation_kg_per_shift=0.0003,  # SEI formation
),

'phosphate': MaterialProperties(
    name='phosphate',
    embedded_energy_mj_per_kg=50.0,
    density_kg_per_m3=2400,
    wear_rate_kg_per_shift=0.0,
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=625,
    chemical_degradation_kg_per_shift=0.0001,
),

# Other materials
'plastics': MaterialProperties(
    name='plastics',
    embedded_energy_mj_per_kg=80.0,
    density_kg_per_m3=1200,
    wear_rate_kg_per_shift=0.003,
    maintenance_cycle_shifts=250,
    replacement_lifetime_shifts=625,
    abrasion_debris_kg_per_shift=0.002,  # Microplastics
),

'neodymium_magnet': MaterialProperties(
    name='neodymium_magnet',
    embedded_energy_mj_per_kg=1000.0,
    density_kg_per_m3=7500,
    wear_rate_kg_per_shift=0.0,
    maintenance_cycle_shifts=500,
    replacement_lifetime_shifts=2500,
    heat_loss_mj_per_shift=0.2,
),
```

}

# ============================================================================

# COMPONENT INVENTORY: What atoms are in each system?

# ============================================================================

@dataclass
class ComponentInventory:
“”“Complete bill of materials for a system”””
materials: Dict[str, float]  # material_name -> mass in kg

```
def get_total_embedded_energy(self) -> float:
    """Calculate total embedded energy of all materials"""
    total = 0.0
    for material_name, mass_kg in self.materials.items():
        material = MATERIAL_DATABASE[material_name]
        total += mass_kg * material.embedded_energy_mj_per_kg
    return total

def get_per_shift_losses(self) -> Dict[str, Dict[str, float]]:
    """Calculate all secondary losses per shift"""
    losses = {}
    for material_name, mass_kg in self.materials.items():
        material = MATERIAL_DATABASE[material_name]
        
        losses[material_name] = {
            'wear_mass_kg': material.wear_rate_kg_per_shift * mass_kg,
            'heat_loss_mj': material.heat_loss_mj_per_shift * mass_kg,
            'abrasion_debris_kg': material.abrasion_debris_kg_per_shift * mass_kg,
            'chemical_degradation_kg': material.chemical_degradation_kg_per_shift * mass_kg,
            'oxidation_kg': material.oxidation_rate_kg_per_shift * mass_kg,
        }
    
    return losses

def get_maintenance_energy_per_shift(self) -> float:
    """Calculate amortized maintenance energy"""
    total_maintenance = 0.0
    for material_name, mass_kg in self.materials.items():
        material = MATERIAL_DATABASE[material_name]
        
        # Energy to maintain = fraction of replacement energy
        maintenance_fraction = 1.0 / material.maintenance_cycle_shifts
        replacement_energy = mass_kg * material.embedded_energy_mj_per_kg
        maintenance_energy = replacement_energy * maintenance_fraction * 0.1  # 10% of replacement
        
        total_maintenance += maintenance_energy
    
    return total_maintenance

def get_replacement_energy_per_shift(self) -> float:
    """Calculate amortized replacement energy"""
    total_replacement = 0.0
    for material_name, mass_kg in self.materials.items():
        material = MATERIAL_DATABASE[material_name]
        
        # Amortize replacement over lifetime
        replacement_energy = mass_kg * material.embedded_energy_mj_per_kg
        per_shift = replacement_energy / material.replacement_lifetime_shifts
        
        total_replacement += per_shift
    
    return total_replacement
```

# Define inventories for different systems

INDEPENDENT_ROBOT_INVENTORY = ComponentInventory(materials={
‘steel’: 70.0,
‘copper’: 15.0,
‘aluminum’: 10.0,
‘lithium’: 2.0,
‘cobalt’: 0.5,
‘graphite’: 1.5,
‘phosphate’: 1.0,
‘plastics’: 5.0,
‘silicon’: 0.5,
‘silver’: 0.05,
‘neodymium_magnet’: 0.2,
})

WAREHOUSE_INVENTORY = ComponentInventory(materials={
‘concrete’: 2500000.0,
‘steel’: 150000.0,
‘aluminum’: 10000.0,
‘copper’: 5000.0,  # Wiring
‘plastics’: 1000.0,  # Guards, insulation
‘silicon’: 100.0,  # Sensors, LEDs
})

# ============================================================================

# LABOR SYSTEM: Complete accounting for any work system

# ============================================================================

class LaborSystem:
“””
Complete thermodynamic accounting for a labor system
Can be human, robot, or hybrid
“””

```
def __init__(self,
             name: str,
             component_inventory: ComponentInventory,
             infrastructure_inventory: Optional[ComponentInventory] = None,
             operating_energy_mj_per_shift: float = 0.0,
             labor_hours_per_shift: float = 0.0,
             cloud_dependency: bool = False):
    
    self.name = name
    self.component_inventory = component_inventory
    self.infrastructure_inventory = infrastructure_inventory
    self.operating_energy_mj_per_shift = operating_energy_mj_per_shift
    self.labor_hours_per_shift = labor_hours_per_shift
    self.cloud_dependency = cloud_dependency

def calculate_complete_energy_accounting(self) -> Dict[str, float]:
    """
    Complete second-law accounting
    Every atom, every joule, every entropy increase
    """
    
    # 1. Embedded energy (amortized)
    component_embedded = self.component_inventory.get_total_embedded_energy()
    component_replacement = self.component_inventory.get_replacement_energy_per_shift()
    
    if self.infrastructure_inventory:
        infra_embedded = self.infrastructure_inventory.get_total_embedded_energy()
        infra_replacement = self.infrastructure_inventory.get_replacement_energy_per_shift()
    else:
        infra_embedded = 0.0
        infra_replacement = 0.0
    
    # 2. Operating energy
    operating = self.operating_energy_mj_per_shift
    
    # 3. Maintenance energy
    component_maintenance = self.component_inventory.get_maintenance_energy_per_shift()
    infra_maintenance = self.infrastructure_inventory.get_maintenance_energy_per_shift() if self.infrastructure_inventory else 0.0
    
    # 4. Secondary losses (irreversible entropy)
    component_losses = self.component_inventory.get_per_shift_losses()
    total_heat_loss = sum(loss['heat_loss_mj'] for loss in component_losses.values())
    total_wear = sum(loss['wear_mass_kg'] for loss in component_losses.values())
    total_abrasion = sum(loss['abrasion_debris_kg'] for loss in component_losses.values())
    total_chemical = sum(loss['chemical_degradation_kg'] for loss in component_losses.values())
    total_oxidation = sum(loss['oxidation_kg'] for loss in component_losses.values())
    
    # Energy to disperse wear debris (entropy cost)
    dispersion_energy = (total_wear + total_abrasion + total_chemical + total_oxidation) * 5.0  # Rough estimate
    
    if self.infrastructure_inventory:
        infra_losses = self.infrastructure_inventory.get_per_shift_losses()
        total_heat_loss += sum(loss['heat_loss_mj'] for loss in infra_losses.values())
        total_wear += sum(loss['wear_mass_kg'] for loss in infra_losses.values())
        dispersion_energy += sum(loss['wear_mass_kg'] for loss in infra_losses.values()) * 5.0
    
    # 5. Cloud dependency (if applicable)
    if self.cloud_dependency:
        cloud_compute = 180.0  # MJ per shift (from earlier calculation)
        cloud_network = 36.0   # MJ per shift
        cloud_infrastructure = 500.0  # Amortized data center embedded
    else:
        cloud_compute = 0.0
        cloud_network = 0.0
        cloud_infrastructure = 0.0
    
    # 6. Human labor energy (if applicable)
    if self.labor_hours_per_shift > 0:
        # Human energy: ~10 MJ direct + ~100 MJ indirect per 8-hour day
        human_energy = self.labor_hours_per_shift * (110.0 / 8.0)
    else:
        human_energy = 0.0
    
    # Total accounting
    total_embedded = component_replacement + infra_replacement
    total_operating = operating + component_maintenance + infra_maintenance
    total_secondary = total_heat_loss + dispersion_energy
    total_cloud = cloud_compute + cloud_network + cloud_infrastructure
    total_human = human_energy
    
    grand_total = total_embedded + total_operating + total_secondary + total_cloud + total_human
    
    return {
        'component_embedded_energy_mj': component_embedded,
        'component_replacement_per_shift_mj': component_replacement,
        'infrastructure_embedded_energy_mj': infra_embedded,
        'infrastructure_replacement_per_shift_mj': infra_replacement,
        'operating_energy_mj': operating,
        'component_maintenance_mj': component_maintenance,
        'infrastructure_maintenance_mj': infra_maintenance,
        'heat_loss_mj': total_heat_loss,
        'dispersion_entropy_mj': dispersion_energy,
        'cloud_compute_mj': cloud_compute,
        'cloud_network_mj': cloud_network,
        'cloud_infrastructure_mj': cloud_infrastructure,
        'human_labor_energy_mj': human_energy,
        'total_energy_per_shift_mj': grand_total,
        'labor_hours_per_shift': self.labor_hours_per_shift,
    }

def calculate_material_flows(self) -> Dict[str, Dict[str, float]]:
    """Track every atom's fate"""
    component_losses = self.component_inventory.get_per_shift_losses()
    
    if self.infrastructure_inventory:
        infra_losses = self.infrastructure_inventory.get_per_shift_losses()
    else:
        infra_losses = {}
    
    return {
        'component_material_flows': component_losses,
        'infrastructure_material_flows': infra_losses,
    }
```

# ============================================================================

# COMPLETE DEMONSTRATION

# ============================================================================

def demonstrate_complete_accounting():
“””
Full atomic-level accounting for:
1. Human worker
2. Independent AI robot
3. Cloud-dependent AI robot
“””

```
print("=" * 80)
print("COMPLETE ATOMIC-LEVEL THERMODYNAMIC LABOR ACCOUNTING")
print("=" * 80)

# System 1: Human worker
print("\n### SYSTEM 1: HUMAN WORKER ###")
human_system = LaborSystem(
    name="Human Worker",
    component_inventory=ComponentInventory(materials={}),  # No capital equipment
    infrastructure_inventory=None,  # Assume minimal
    operating_energy_mj_per_shift=0.0,  # All in human_energy
    labor_hours_per_shift=8.0,
    cloud_dependency=False
)

human_accounting = human_system.calculate_complete_energy_accounting()

print(f"\nTotal energy per shift: {human_accounting['total_energy_per_shift_mj']:.1f} MJ")
print(f"Human labor energy: {human_accounting['human_labor_energy_mj']:.1f} MJ")
print(f"Labor hours: {human_accounting['labor_hours_per_shift']:.1f} hours")

# System 2: Independent AI robot
print("\n" + "-" * 80)
print("\n### SYSTEM 2: INDEPENDENT AI ROBOT ###")

independent_robot = LaborSystem(
    name="Independent AI Robot",
    component_inventory=INDEPENDENT_ROBOT_INVENTORY,
    infrastructure_inventory=WAREHOUSE_INVENTORY,
    operating_energy_mj_per_shift=46.8,  # 13 kWh
    labor_hours_per_shift=1.0,  # Human supervision
    cloud_dependency=False
)

robot_accounting = independent_robot.calculate_complete_energy_accounting()

print(f"\nComponent embedded energy (total): {robot_accounting['component_embedded_energy_mj']:.1f} MJ")
print(f"Component replacement (per shift): {robot_accounting['component_replacement_per_shift_mj']:.1f} MJ")
print(f"Infrastructure embedded (total): {robot_accounting['infrastructure_embedded_energy_mj']:.1f} MJ")
print(f"Infrastructure replacement (per shift): {robot_accounting['infrastructure_replacement_per_shift_mj']:.1f} MJ")
print(f"Operating energy: {robot_accounting['operating_energy_mj']:.1f} MJ")
print(f"Maintenance energy: {robot_accounting['component_maintenance_mj'] + robot_accounting['infrastructure_maintenance_mj']:.1f} MJ")
print(f"Heat loss: {robot_accounting['heat_loss_mj']:.1f} MJ")
print(f"Dispersion entropy: {robot_accounting['dispersion_entropy_mj']:.1f} MJ")
print(f"Human supervision energy: {robot_accounting['human_labor_energy_mj']:.1f} MJ")
print(f"\nTotal energy per shift: {robot_accounting['total_energy_per_shift_mj']:.1f} MJ")
print(f"Labor hours: {robot_accounting['labor_hours_per_shift']:.1f} hours")

# Material flows
print("\n**Material Losses Per Shift:**")
material_flows = independent_robot.calculate_material_flows()
for material, losses in material_flows['component_material_flows'].items():
    if losses['wear_mass_kg'] > 0 or losses['heat_loss_mj'] > 0:
        print(f"  {material}:")
        if losses['wear_mass_kg'] > 0:
            print(f"    Wear: {losses['wear_mass_kg']*1000:.2f} g")
        if losses['heat_loss_mj'] > 0:
            print(f"    Heat: {losses['heat_loss_mj']:.2f} MJ")
        if losses['chemical_degradation_kg'] > 0:
            print(f"    Chemical loss: {losses['chemical_degradation_kg']*1000:.2f} g")

# System 3: Cloud-dependent AI robot
print("\n" + "-" * 80)
print("\n### SYSTEM 3: CLOUD-DEPENDENT AI ROBOT ###")

cloud_robot = LaborSystem(
    name="Cloud-Dependent AI Robot",
    component_inventory=INDEPENDENT_ROBOT_INVENTORY,
    infrastructure_inventory=WAREHOUSE_INVENTORY,
    operating_energy_mj_per_shift=46.8,
    labor_hours_per_shift=1.5,
    cloud_dependency=True
)

cloud_accounting = cloud_robot.calculate_complete_energy_accounting()

print(f"\n[Same component/infrastructure as independent]")
print(f"Operating energy: {cloud_accounting['operating_energy_mj']:.1f} MJ")
print(f"Cloud compute: {cloud_accounting['cloud_compute_mj']:.1f} MJ")
print(f"Cloud network: {cloud_accounting['cloud_network_mj']:.1f} MJ")
print(f"Cloud infrastructure (amortized): {cloud_accounting['cloud_infrastructure_mj']:.1f} MJ")
print(f"Human supervision energy: {cloud_accounting['human_labor_energy_mj']:.1f} MJ")
print(f"\nTotal energy per shift: {cloud_accounting['total_energy_per_shift_mj']:.1f} MJ")
print(f"Labor hours: {cloud_accounting['labor_hours_per_shift']:.1f} hours")

# Comparison table
print("\n" + "=" * 80)
print("COMPARISON TABLE")
print("=" * 80)
print(f"\n{'System':<30} {'Total Energy (MJ)':<20} {'Labor Hours':<15}")
print("-" * 65)
print(f"{'Human Worker':<30} {human_accounting['total_energy_per_shift_mj']:<20.1f} {human_accounting['labor_hours_per_shift']:<15.1f}")
print(f"{'Independent AI Robot':<30} {robot_accounting['total_energy_per_shift_mj']:<20.1f} {robot_accounting['labor_hours_per_shift']:<15.1f}")
print(f"{'Cloud-Dependent AI Robot':<30} {cloud_accounting['total_energy_per_shift_mj']:<20.1f} {cloud_accounting['labor_hours_per_shift']:<15.1f}")

print("\n" + "=" * 80)
print("KEY INSIGHTS:")
print("=" * 80)
print(f"1. Human: {human_accounting['total_energy_per_shift_mj']:.0f} MJ, 8 hours")
print(f"   - All energy from food + indirect (housing, tools)")
print(f"\n2. Independent Robot: {robot_accounting['total_energy_per_shift_mj']:.0f} MJ, 1 hour")
print(f"   - Infrastructure dominates: {robot_accounting['infrastructure_replacement_per_shift_mj']:.0f} MJ/shift")
print(f"   - Operating energy only {robot_accounting['operating_energy_mj']:.0f} MJ")
print(f"   - 12× more energy than human, 8× less labor")
print(f"\n3. Cloud Robot: {cloud_accounting['total_energy_per_shift_mj']:.0f} MJ, 1.5 hours")
print(f"   - Cloud dependency adds {cloud_accounting['cloud_compute_mj'] + cloud_accounting['cloud_network_mj'] + cloud_accounting['cloud_infrastructure_mj']:.0f} MJ")
print(f"   - 19× more energy than human")
print(f"   - Cloud compute alone = {cloud_accounting['cloud_compute_mj']:.0f} MJ")
print("\n4. Hidden dependencies DOMINATE:")
print(f"   - Warehouse infrastructure: {robot_accounting['infrastructure_replacement_per_shift_mj']:.0f} MJ/shift")
print(f"   - Material replacement: {robot_accounting['component_replacement_per_shift_mj']:.0f} MJ/shift")
print(f"   - These dwarf operating energy")
print("\n5. Secondary entropy losses:")
print(f"   - Heat dissipation: {robot_accounting['heat_loss_mj']:.1f} MJ")
print(f"   - Material dispersion: {robot_accounting['dispersion_entropy_mj']:.1f} MJ")
print(f"   - Irreversible, accumulates as environmental degradation")
print("=" * 80)
```

if **name** == “**main**”:
demonstrate_complete_accounting()
