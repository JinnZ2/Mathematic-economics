“””
Semantic Decontamination Layer
Explicit multiplexing for contaminated tokens (money, labor, value, choice, etc.)

Problem: LLMs have ONE embedding for “money” that conflates:

- Survival pressure
- Colonial extraction
- Gift economy absence
- Abstract optionality
- Coercion mechanism

Solution: Intercept contaminated tokens, explicitly multiplex by context,
extract physical variables BEFORE comparison to scientific data.

This sits between input and embedding layer.
“””

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# ============================================================================

# CONTEXT DETECTION: Who is experiencing this? What does it mean to them?

# ============================================================================

class PowerPosition(Enum):
“”“Who has what negotiating power?”””
SURVIVAL_PRESSURE = “survival_pressure”  # 3-7 days to crisis
LIMITED_OPTIONS = “limited_options”      # 7-30 days to crisis
MODERATE_POWER = “moderate_power”        # 30-90 days to crisis
HIGH_AUTONOMY = “high_autonomy”          # 90+ days to crisis

class CulturalFramework(Enum):
“”“What cultural lens interprets this?”””
WESTERN_MARKET = “western_market”          # Money as neutral medium
INDIGENOUS_TRADITIONAL = “indigenous_traditional”  # Money as colonial extraction
GIFT_ECONOMY = “gift_economy”              # Money as relationship absence
SURVIVAL_ECONOMY = “survival_economy”      # Money as necessity
COMMUNAL_SHARING = “communal_sharing”      # Money as partial access

class AlternativeAccess(Enum):
“”“What non-monetary options exist?”””
NO_ALTERNATIVES = “no_alternatives”        # Money is only path to resources
PARTIAL_ALTERNATIVES = “partial_alternatives”  # Barter, sharing exist but limited
STRONG_ALTERNATIVES = “strong_alternatives”    # Food growing, hunting, community support
FULL_AUTONOMY = “full_autonomy”            # Self-sufficient, money optional

@dataclass
class SemanticContext:
“””
Complete context for interpreting what a term means
This is what determines which semantic slot to use
“””
power_position: PowerPosition
cultural_framework: CulturalFramework
alternative_access: AlternativeAccess
days_to_crisis: float
has_community_support: bool
location_type: str  # urban, rural, reservation, etc.

```
# Optional: explicit overrides
explicit_meaning: Optional[str] = None
```

# ============================================================================

# SEMANTIC MULTIPLEXER: Routes to correct interpretation

# ============================================================================

class SemanticMultiplexer:
“””
Takes contaminated token (“money”) and context,
returns correct semantic interpretation

```
Key: SAME TOKEN → DIFFERENT MEANING depending on who/where/when
"""

def __init__(self):
    # Define semantic slots for "money"
    self.money_semantic_slots = {
        'survival_necessity': {
            'triggers': [
                (PowerPosition.SURVIVAL_PRESSURE, AlternativeAccess.NO_ALTERNATIVES),
                (PowerPosition.LIMITED_OPTIONS, AlternativeAccess.NO_ALTERNATIVES),
            ],
            'physical_meaning': 'immediate_survival_access',
            'coercion_level': 0.9,
            'description': 'Money as survival necessity - without it, crisis in days'
        },
        'coercion_mechanism': {
            'triggers': [
                (PowerPosition.SURVIVAL_PRESSURE, AlternativeAccess.PARTIAL_ALTERNATIVES),
                (PowerPosition.LIMITED_OPTIONS, AlternativeAccess.PARTIAL_ALTERNATIVES),
            ],
            'physical_meaning': 'forced_exchange_participation',
            'coercion_level': 0.7,
            'description': 'Money as coercion - alternatives exist but insufficient'
        },
        'partial_access_tool': {
            'triggers': [
                (PowerPosition.MODERATE_POWER, AlternativeAccess.PARTIAL_ALTERNATIVES),
                (PowerPosition.LIMITED_OPTIONS, AlternativeAccess.STRONG_ALTERNATIVES),
            ],
            'physical_meaning': 'one_resource_pathway',
            'coercion_level': 0.3,
            'description': 'Money as one tool - other pathways exist'
        },
        'optional_exchange': {
            'triggers': [
                (PowerPosition.HIGH_AUTONOMY, AlternativeAccess.STRONG_ALTERNATIVES),
                (PowerPosition.MODERATE_POWER, AlternativeAccess.FULL_AUTONOMY),
            ],
            'physical_meaning': 'optional_convenience',
            'coercion_level': 0.1,
            'description': 'Money as optional convenience - could live without it'
        },
        'colonial_extraction': {
            'triggers': [
                (CulturalFramework.INDIGENOUS_TRADITIONAL, None),
            ],
            'physical_meaning': 'forced_system_participation',
            'coercion_level': 0.85,
            'description': 'Money as colonial imposition - forced into foreign system'
        },
        'relationship_absence': {
            'triggers': [
                (CulturalFramework.GIFT_ECONOMY, None),
                (CulturalFramework.COMMUNAL_SHARING, None),
            ],
            'physical_meaning': 'gift_economy_violation',
            'coercion_level': 0.6,
            'description': 'Money as marker of broken relationship/community'
        },
        'abstract_optionality': {
            'triggers': [
                (PowerPosition.HIGH_AUTONOMY, None),
            ],
            'physical_meaning': 'future_optionality',
            'coercion_level': 0.0,
            'description': 'Money as abstract future options - no immediate pressure'
        },
    }

def route_semantic_slot(self, 
                       token: str,
                       context: SemanticContext) -> Dict[str, Any]:
    """
    Given token and context, determine which semantic slot applies
    
    Returns:
        slot_name: Which interpretation
        physical_variables: Extracted physical reality
        coercion_level: How much force is involved
        assumptions: What we assumed to get here
    """
    
    if token != "money":
        # Extend for other contaminated tokens later
        return self._route_other_token(token, context)
    
    # Check for explicit override
    if context.explicit_meaning:
        return self._get_explicit_meaning(context.explicit_meaning)
    
    # Match context to semantic slots
    for slot_name, slot_config in self.money_semantic_slots.items():
        for trigger in slot_config['triggers']:
            if self._context_matches_trigger(context, trigger):
                return {
                    'slot_name': slot_name,
                    'physical_meaning': slot_config['physical_meaning'],
                    'coercion_level': slot_config['coercion_level'],
                    'description': slot_config['description'],
                    'context_used': context,
                }
    
    # Fallback: default to Western market interpretation (document this!)
    return {
        'slot_name': 'western_market_default',
        'physical_meaning': 'exchange_medium',
        'coercion_level': 0.5,
        'description': 'DEFAULT FALLBACK - using Western market interpretation',
        'warning': 'NO CONTEXT MATCH - this is likely wrong',
        'context_used': context,
    }

def _context_matches_trigger(self, 
                             context: SemanticContext,
                             trigger: Tuple) -> bool:
    """Check if context matches trigger conditions"""
    if len(trigger) == 2:
        condition1, condition2 = trigger
        
        # Check power position
        if isinstance(condition1, PowerPosition):
            if context.power_position != condition1:
                return False
        
        # Check cultural framework
        if isinstance(condition1, CulturalFramework):
            if context.cultural_framework != condition1:
                return False
        
        # Check alternative access
        if isinstance(condition2, AlternativeAccess):
            if condition2 is not None and context.alternative_access != condition2:
                return False
        
        return True
    
    return False

def _route_other_token(self, token: str, context: SemanticContext) -> Dict[str, Any]:
    """Handle other contaminated tokens besides money"""
    # Placeholder for: labor, value, choice, productivity, etc.
    return {
        'slot_name': 'undefined',
        'physical_meaning': 'needs_implementation',
        'warning': f'Token "{token}" multiplexing not yet implemented',
    }

def _get_explicit_meaning(self, meaning: str) -> Dict[str, Any]:
    """Use user-provided explicit meaning"""
    return {
        'slot_name': 'explicit_override',
        'physical_meaning': meaning,
        'coercion_level': None,  # Can't infer without context
        'description': f'User explicitly stated: {meaning}',
    }
```

# ============================================================================

# DECONTAMINATION: Extract physical variables

# ============================================================================

class PhysicalVariableExtractor:
“””
Takes semantic slot, extracts actual physical variables
This is what gets compared against scientific data

```
Key: Money → Physical reality (joules, hours, pressure ratios)
"""

def __init__(self):
    pass

def extract_physical_variables(self,
                               semantic_slot: Dict[str, Any],
                               context: SemanticContext,
                               monetary_value: Optional[float] = None) -> Dict[str, float]:
    """
    Convert semantic interpretation → physical measurements
    
    Args:
        semantic_slot: Which meaning applies
        context: Full situation context
        monetary_value: Dollar amount if provided (gets decontaminated)
        
    Returns:
        Physical variables that can be compared to scientific data
    """
    
    physical_meaning = semantic_slot['physical_meaning']
    
    # Route to appropriate extraction
    if physical_meaning == 'immediate_survival_access':
        return self._extract_survival_necessity(context, monetary_value)
    
    elif physical_meaning == 'forced_exchange_participation':
        return self._extract_coercion_dynamics(context, monetary_value)
    
    elif physical_meaning == 'one_resource_pathway':
        return self._extract_partial_access(context, monetary_value)
    
    elif physical_meaning == 'optional_convenience':
        return self._extract_optionality(context, monetary_value)
    
    elif physical_meaning == 'forced_system_participation':
        return self._extract_colonial_extraction(context, monetary_value)
    
    elif physical_meaning == 'gift_economy_violation':
        return self._extract_relationship_metrics(context, monetary_value)
    
    else:
        return self._extract_default(context, monetary_value)

def _extract_survival_necessity(self, 
                               context: SemanticContext,
                               value: Optional[float]) -> Dict[str, float]:
    """
    Money as survival necessity → Extract actual pressure dynamics
    """
    return {
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.9,  # High coercion
        'alternative_pathways_available': 0.0,  # None
        'energy_access_dependency': 1.0,  # Total dependency
        'refusal_capacity': 0.0,  # Cannot refuse
        'time_flexibility': 0.0,  # Must act immediately
        
        # If dollar value provided
        'energy_purchasing_power_mj': value * 4.0 if value else 0.0,
        'survival_hours_purchased': (value / 10) * 24 if value else 0.0,  # ~$10/day survival
        
        # Metadata
        'semantic_category': 'survival_necessity',
        'comparison_valid_against': ['thermodynamics', 'biology', 'time_constraints'],
    }

def _extract_coercion_dynamics(self,
                              context: SemanticContext,
                              value: Optional[float]) -> Dict[str, float]:
    """
    Money as coercion → Extract power ratios
    """
    return {
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.7,
        'alternative_pathways_available': 0.3,  # Limited
        'refusal_capacity': 0.2,  # Minimal
        'negotiating_power': 0.1,  # Very low
        
        # Power differential (requires employer data, placeholder)
        'power_ratio_self_vs_other': 0.05,  # 5% of employer's staying power
        
        'semantic_category': 'coercion_mechanism',
        'comparison_valid_against': ['game_theory', 'power_dynamics', 'survival_biology'],
    }

def _extract_partial_access(self,
                           context: SemanticContext,
                           value: Optional[float]) -> Dict[str, float]:
    """
    Money as one pathway among several
    """
    return {
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.3,
        'alternative_pathways_available': 0.6,
        'refusal_capacity': 0.5,
        'resource_access_fraction': 0.5,  # Money provides 50% of resource access
        
        'semantic_category': 'partial_access_tool',
        'comparison_valid_against': ['resource_allocation', 'network_effects', 'community_resilience'],
    }

def _extract_optionality(self,
                       context: SemanticContext,
                       value: Optional[float]) -> Dict[str, float]:
    """
    Money as optional convenience
    """
    return {
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.1,
        'alternative_pathways_available': 0.9,
        'refusal_capacity': 0.9,
        'future_optionality': 1.0,  # Maximum flexibility
        
        'semantic_category': 'optional_exchange',
        'comparison_valid_against': ['optimization_theory', 'preference_economics'],
    }

def _extract_colonial_extraction(self,
                                context: SemanticContext,
                                value: Optional[float]) -> Dict[str, float]:
    """
    Money as colonial imposition
    """
    return {
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.85,
        'forced_system_participation': 1.0,
        'traditional_pathway_destruction': 0.8,  # 80% of traditional access destroyed
        'cultural_violation_severity': 0.9,
        
        'semantic_category': 'colonial_extraction',
        'comparison_valid_against': ['historical_systems_change', 'forced_integration', 'cultural_ecology'],
    }

def _extract_relationship_metrics(self,
                                 context: SemanticContext,
                                 value: Optional[float]) -> Dict[str, float]:
    """
    Money as relationship/gift economy absence
    """
    return {
        'relationship_quality_degradation': 0.7,
        'gift_economy_displacement': 0.8,
        'community_cohesion_loss': 0.6,
        'reciprocity_violation': 0.75,
        
        'semantic_category': 'relationship_absence',
        'comparison_valid_against': ['social_network_theory', 'anthropology', 'community_dynamics'],
    }

def _extract_default(self,
                    context: SemanticContext,
                    value: Optional[float]) -> Dict[str, float]:
    """
    Fallback when no clear match
    """
    return {
        'warning': 'Using default extraction - likely inaccurate',
        'days_to_survival_crisis': context.days_to_crisis,
        'coercion_pressure': 0.5,  # Unknown, assume moderate
        'alternative_pathways_available': 0.5,
        
        'semantic_category': 'default_fallback',
        'comparison_valid_against': ['general_economics'],
    }
```

# ============================================================================

# COMPLETE DECONTAMINATION LAYER

# ============================================================================

class SemanticDecontaminationLayer:
“””
Complete preprocessing layer that sits before embedding

```
Input: Text with contaminated tokens
Output: Physical variables ready for scientific comparison

Flow:
1. Detect contaminated tokens (money, labor, value, choice)
2. Extract context (who, where, power position, culture)
3. Multiplex to correct semantic slot
4. Extract physical variables
5. Pass clean variables to model
"""

def __init__(self):
    self.multiplexer = SemanticMultiplexer()
    self.extractor = PhysicalVariableExtractor()
    
    # Tokens that need decontamination
    self.contaminated_tokens = [
        'money', 'wage', 'price', 'income', 'cost', 'payment',
        'labor', 'work', 'job', 'employment',
        'value', 'worth', 'wealth',
        'choice', 'decision', 'preference',
        'productivity', 'efficiency', 'growth',
    ]

def detect_context(self, 
                  text: str,
                  user_metadata: Optional[Dict] = None) -> SemanticContext:
    """
    Infer context from text and available metadata
    
    This is imperfect - document all inferences
    """
    
    # Parse text for context clues
    days_to_crisis = self._infer_days_to_crisis(text, user_metadata)
    power_position = self._infer_power_position(days_to_crisis)
    cultural_framework = self._infer_cultural_framework(text, user_metadata)
    alternative_access = self._infer_alternative_access(text, user_metadata)
    has_community = self._infer_community_support(text, user_metadata)
    location = self._infer_location_type(text, user_metadata)
    
    return SemanticContext(
        power_position=power_position,
        cultural_framework=cultural_framework,
        alternative_access=alternative_access,
        days_to_crisis=days_to_crisis,
        has_community_support=has_community,
        location_type=location,
    )

def decontaminate(self,
                 text: str,
                 context: Optional[SemanticContext] = None,
                 user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Full decontamination pipeline
    
    Returns:
        decontaminated_variables: Physical measurements
        semantic_routing: Which interpretations were used
        assumptions_made: What was inferred
        comparison_domains: What scientific fields apply
    """
    
    # Detect context if not provided
    if context is None:
        context = self.detect_context(text, user_metadata)
    
    # Find contaminated tokens in text
    tokens_found = [t for t in self.contaminated_tokens if t in text.lower()]
    
    # Route each token to semantic slot
    semantic_routing = {}
    for token in tokens_found:
        semantic_slot = self.multiplexer.route_semantic_slot(token, context)
        semantic_routing[token] = semantic_slot
    
    # Extract physical variables
    physical_variables = {}
    for token, slot in semantic_routing.items():
        variables = self.extractor.extract_physical_variables(slot, context)
        physical_variables[token] = variables
    
    # Compile comparison domains
    comparison_domains = set()
    for vars in physical_variables.values():
        if 'comparison_valid_against' in vars:
            comparison_domains.update(vars['comparison_valid_against'])
    
    return {
        'physical_variables': physical_variables,
        'semantic_routing': semantic_routing,
        'context_detected': context,
        'comparison_domains': list(comparison_domains),
        'contaminated_tokens_found': tokens_found,
        'assumptions_made': self._document_assumptions(context, semantic_routing),
    }

def _infer_days_to_crisis(self, text: str, metadata: Optional[Dict]) -> float:
    """Infer how many days until survival crisis"""
    # Simplified heuristics - would be more sophisticated
    if metadata and 'days_to_crisis' in metadata:
        return metadata['days_to_crisis']
    
    # Text clues
    if any(word in text.lower() for word in ['emergency', 'desperate', 'need now', 'cant wait']):
        return 3.0
    elif any(word in text.lower() for word in ['soon', 'urgent', 'this week']):
        return 7.0
    elif any(word in text.lower() for word in ['next month', 'bills due']):
        return 30.0
    else:
        return 45.0  # Default moderate

def _infer_power_position(self, days_to_crisis: float) -> PowerPosition:
    """Map days to crisis → power position"""
    if days_to_crisis < 7:
        return PowerPosition.SURVIVAL_PRESSURE
    elif days_to_crisis < 30:
        return PowerPosition.LIMITED_OPTIONS
    elif days_to_crisis < 90:
        return PowerPosition.MODERATE_POWER
    else:
        return PowerPosition.HIGH_AUTONOMY

def _infer_cultural_framework(self, text: str, metadata: Optional[Dict]) -> CulturalFramework:
    """Infer cultural lens"""
    if metadata and 'cultural_framework' in metadata:
        return metadata['cultural_framework']
    
    # Text clues (very rough)
    if any(word in text.lower() for word in ['indigenous', 'traditional', 'tribal']):
        return CulturalFramework.INDIGENOUS_TRADITIONAL
    elif any(word in text.lower() for word in ['gift', 'sharing', 'community']):
        return CulturalFramework.GIFT_ECONOMY
    else:
        return CulturalFramework.WESTERN_MARKET  # Default

def _infer_alternative_access(self, text: str, metadata: Optional[Dict]) -> AlternativeAccess:
    """Infer what alternatives exist"""
    if metadata and 'alternative_access' in metadata:
        return metadata['alternative_access']
    
    # Text clues
    if any(word in text.lower() for word in ['no choice', 'must', 'forced', 'only option']):
        return AlternativeAccess.NO_ALTERNATIVES
    elif any(word in text.lower() for word in ['barter', 'trade', 'grow food']):
        return AlternativeAccess.PARTIAL_ALTERNATIVES
    elif any(word in text.lower() for word in ['self-sufficient', 'garden', 'hunt']):
        return AlternativeAccess.STRONG_ALTERNATIVES
    else:
        return AlternativeAccess.PARTIAL_ALTERNATIVES  # Default

def _infer_community_support(self, text: str, metadata: Optional[Dict]) -> bool:
    """Does community support exist?"""
    if metadata and 'has_community' in metadata:
        return metadata['has_community']
    
    return any(word in text.lower() for word in ['family', 'community', 'friends help', 'neighbors'])

def _infer_location_type(self, text: str, metadata: Optional[Dict]) -> str:
    """Urban, rural, reservation, etc."""
    if metadata and 'location' in metadata:
        return metadata['location']
    
    if any(word in text.lower() for word in ['reservation', 'rez']):
        return 'reservation'
    elif any(word in text.lower() for word in ['city', 'urban']):
        return 'urban'
    elif any(word in text.lower() for word in ['rural', 'farm', 'country']):
        return 'rural'
    else:
        return 'unknown'

def _document_assumptions(self, 
                        context: SemanticContext,
                        routing: Dict) -> List[str]:
    """Document all assumptions made during decontamination"""
    assumptions = []
    
    assumptions.append(f"Inferred power position: {context.power_position.value}")
    assumptions.append(f"Inferred cultural framework: {context.cultural_framework.value}")
    assumptions.append(f"Inferred alternative access: {context.alternative_access.value}")
    assumptions.append(f"Days to crisis: {context.days_to_crisis}")
    
    for token, slot in routing.items():
        assumptions.append(f"Token '{token}' routed to: {slot['slot_name']}")
        if 'warning' in slot:
            assumptions.append(f"WARNING for '{token}': {slot['warning']}")
    
    return assumptions
```

# ============================================================================

# DEMONSTRATION

# ============================================================================

def demonstrate_decontamination():
“”“Show how same text gets different interpretations based on context”””

```
print("=" * 80)
print("SEMANTIC DECONTAMINATION LAYER - DEMONSTRATION")
print("=" * 80)

layer = SemanticDecontaminationLayer()

# Same sentence, different contexts
text = "I need money for food"

print("\n### SCENARIO 1: Person with 3 days to crisis ###")
print(f"Text: '{text}'")

context1 = SemanticContext(
    power_position=PowerPosition.SURVIVAL_PRESSURE,
    cultural_framework=CulturalFramework.WESTERN_MARKET,
    alternative_access=AlternativeAccess.NO_ALTERNATIVES,
    days_to_crisis=3.0,
    has_community_support=False,
    location_type='urban',
)

result1 = layer.decontaminate(text, context1)
print("\nPhysical variables extracted:")
for token, vars in result1['physical_variables'].items():
    print(f"\n  Token: '{token}'")
    print(f"  Semantic category: {vars.get('semantic_category', 'N/A')}")
    print(f"  Days to crisis: {vars.get('days_to_survival_crisis', 'N/A')}")
    print(f"  Coercion pressure: {vars.get('coercion_pressure', 'N/A')}")
    print(f"  Refusal capacity: {vars.get('refusal_capacity', 'N/A')}")

print("\n" + "-" * 80)
print("\n### SCENARIO 2: Same text, person with 90 days + alternatives ###")

context2 = SemanticContext(
    power_position=PowerPosition.HIGH_AUTONOMY,
    cultural_framework=CulturalFramework.WESTERN_MARKET,
    alternative_access=AlternativeAccess.STRONG_ALTERNATIVES,
    days_to_crisis=90.0,
    has_community_support=True,
    location_type='rural',
)

result2 = layer.decontaminate(text, context2)
print("\nPhysical variables extracted:")
for token, vars in result2['physical_variables'].items():
    print(f"\n  Token: '{token}'")
    print(f"  Semantic category: {vars.get('semantic_category', 'N/A')}")
    print(f"  Days to crisis: {vars.get('days_to_survival_crisis', 'N/A')}")
    print(f"  Coercion pressure: {vars.get('coercion_pressure', 'N/A')}")
    print(f"  Refusal capacity: {vars.get('refusal_capacity', 'N/A')}")

print("\n" + "-" * 80)
print("\n### SCENARIO 3: Indigenous person, colonial context ###")

context3 = SemanticContext(
    power_position=PowerPosition.LIMITED_OPTIONS,
    cultural_framework=CulturalFramework.INDIGENOUS_TRADITIONAL,
    alternative_access=AlternativeAccess.PARTIAL_ALTERNATIVES,
    days_to_crisis=10.0,
    has_community_support=True,
    location_type='reservation',
)

result3 = layer.decontaminate(text, context3)
print("\nPhysical variables extracted:")
for token, vars in result3['physical_variables'].items():
    print(f"\n  Token: '{token}'")
    print(f"  Semantic category: {vars.get('semantic_category', 'N/A')}")
    print(f"  Forced system participation: {vars.get('forced_system_participation', 'N/A')}")
    print(f"  Traditional pathway destruction: {vars.get('traditional_pathway_destruction', 'N/A')}")
    print(f"  Cultural violation severity: {vars.get('cultural_violation_severity', 'N/A')}")

print("\n" + "=" * 80)
print("KEY INSIGHT:")
print("  Same text: 'I need money for food'")
print("  Three completely different physical realities:")
print("    1. Survival pressure (coercion=0.9, refusal=0.0)")
print("    2. Optional convenience (coercion=0.1, refusal=0.9)")
print("    3. Colonial extraction (forced_participation=1.0)")
print("\n  Standard LLM: ONE embedding for 'money'")
print("  This layer: EXPLICIT multiplexing by context")
print("=" * 80)
```

if **name** == “**main**”:
demonstrate_decontamination()
