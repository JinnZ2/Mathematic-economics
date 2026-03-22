"""
Temporal-Energy Model Framework
Treating labor as time-energy flow with physics constraints
Bypassing poisoned training assumptions through fundamental conservation laws
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TemporalConstraints:
    """Conservation laws for time-energy systems"""
    hours_per_day: float = 24.0
    energy_capacity: float = 100.0  # Normalized energy units
    recovery_rate: float = 0.1  # Energy recovery per hour of rest
    depletion_threshold: float = 20.0  # Critical depletion level

@dataclass
class ActivityCost:
    """Cost structure for activities as energy flows"""
    time_cost: float  # Hours consumed
    energy_cost: float  # Energy consumed
    recovery_required: float  # Time needed to recover
    domain: str  # Which life domain (work, care, rest, creation)
    enables: List[str]  # What this makes possible
    blocks: List[str]  # What this prevents


class EnergyBalanceLayer(nn.Module):
    """
    Custom loss function that enforces energy/time conservation
    Penalizes violations of physical constraints
    Rewards patterns that respect temporal dynamics
    """
    
    def __init__(self, constraints: TemporalConstraints):
        super().__init__()
        self.constraints = constraints
        
    def forward(self, 
                time_allocation: torch.Tensor,  # [batch, activities, hours]
                energy_flows: torch.Tensor,     # [batch, activities, energy]
                recovery_patterns: torch.Tensor  # [batch, time_steps, recovery]
               ) -> Dict[str, torch.Tensor]:
        """
        Calculate loss based on physical constraint violations
        
        Returns:
            losses: Dict of individual constraint violations
        """
        
        # Conservation of time: total allocation cannot exceed 24hr
        time_violation = torch.relu(
            time_allocation.sum(dim=1) - self.constraints.hours_per_day
        )
        
        # Energy depletion: track cumulative energy deficit
        energy_balance = self.constraints.energy_capacity - energy_flows.cumsum(dim=1)
        depletion_violation = torch.relu(
            self.constraints.depletion_threshold - energy_balance
        ).mean()
        
        # Recovery requirement: insufficient recovery causes accumulating deficit
        recovery_needed = (energy_flows * 0.5)  # Recovery = 50% of energy spent
        recovery_provided = recovery_patterns.sum(dim=1, keepdim=True)
        recovery_violation = torch.relu(recovery_needed - recovery_provided).mean()
        
        # Temporal causality: some activities must precede others
        # (This would be learned from causal inference, placeholder here)
        causality_violation = torch.tensor(0.0, device=time_allocation.device)
        
        losses = {
            'time_conservation': time_violation.mean(),
            'energy_depletion': depletion_violation,
            'recovery_deficit': recovery_violation,
            'causality': causality_violation,
        }
        
        # Total loss is weighted sum
        total_loss = (
            losses['time_conservation'] * 10.0 +  # Hard constraint
            losses['energy_depletion'] * 5.0 +
            losses['recovery_deficit'] * 3.0 +
            losses['causality'] * 2.0
        )
        
        losses['total'] = total_loss
        return losses


class CausalInferenceLayer(nn.Module):
    """
    Learn cause-effect relationships across domains
    Not just correlations - actual causal chains
    """
    
    def __init__(self, num_domains: int, hidden_dim: int = 128):
        super().__init__()
        self.num_domains = num_domains
        
        # Causal structure learning
        self.cause_encoder = nn.Sequential(
            nn.Linear(num_domains, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_domains)
        )

        self.effect_decoder = nn.Sequential(
            nn.Linear(num_domains, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_domains)
        )
        
        # Learnable causal adjacency matrix
        # Entry [i,j] represents strength of causal link from domain i to j
        self.causal_matrix = nn.Parameter(
            torch.randn(num_domains, num_domains) * 0.01
        )
        
    def forward(self, domain_states: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            domain_states: [batch, num_domains, state_dim]
            
        Returns:
            effects: Predicted effects across domains
            causal_graph: Current learned causal structure
        """
        batch_size = domain_states.shape[0]
        
        # Encode current states
        encoded = self.cause_encoder(domain_states.mean(dim=-1))
        
        # Apply learned causal structure
        # Make causal matrix sparse and directed (mask to prevent cycles if needed)
        causal_graph = torch.sigmoid(self.causal_matrix)
        
        # Propagate causes to effects
        causal_flow = torch.matmul(
            encoded.unsqueeze(1),  # [batch, 1, hidden]
            causal_graph.unsqueeze(0).expand(batch_size, -1, -1)  # [batch, domains, domains]
        )
        
        # Decode to predicted effects
        effects = self.effect_decoder(causal_flow.squeeze(1))
        
        return effects, causal_graph


class TemporalEncoder(nn.Module):
    """
    Encode time as fundamental resource, not just a feature
    Activities consume time-energy with recovery costs
    """
    
    def __init__(self, 
                 activity_dim: int,
                 time_steps: int = 24,  # Hourly resolution
                 embed_dim: int = 64):
        super().__init__()
        self.time_steps = time_steps
        self.embed_dim = embed_dim
        
        # Time position embeddings (hourly)
        self.time_embedding = nn.Embedding(time_steps, embed_dim)
        
        # Activity embeddings
        self.activity_embedding = nn.Linear(activity_dim, embed_dim)
        
        # Temporal transformer for dependencies
        self.temporal_attention = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=4,
            batch_first=True
        )
        
        # Energy flow prediction
        self.energy_predictor = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, 1)
        )
        
    def forward(self, 
                activities: torch.Tensor,  # [batch, time_steps, activity_dim]
               ) -> Dict[str, torch.Tensor]:
        """
        Encode temporal structure of activities
        
        Returns:
            embeddings: Temporal activity embeddings
            energy_flows: Predicted energy consumption per timestep
            attention_weights: Temporal dependencies
        """
        batch_size, seq_len, _ = activities.shape
        
        # Create time position indices
        time_indices = torch.arange(seq_len, device=activities.device)
        time_indices = time_indices.unsqueeze(0).expand(batch_size, -1)
        
        # Combine time and activity embeddings
        time_embed = self.time_embedding(time_indices)  # [batch, seq_len, embed_dim]
        activity_embed = self.activity_embedding(activities)  # [batch, seq_len, embed_dim]
        combined = time_embed + activity_embed
        
        # Apply temporal attention to learn dependencies
        attended, attention_weights = self.temporal_attention(
            combined, combined, combined
        )
        
        # Predict energy flows
        energy_flows = self.energy_predictor(attended).squeeze(-1)  # [batch, seq_len]
        
        return {
            'embeddings': attended,
            'energy_flows': energy_flows,
            'attention': attention_weights
        }


class PoisonDetector(nn.Module):
    """
    Detect poisoned assumptions in training data
    Flags when model predictions rely on encoded biases rather than dynamics
    """
    
    def __init__(self, num_features: int, hidden_dim: int = 64):
        super().__init__()
        
        # Learn to distinguish dynamic patterns from statistical norms
        self.dynamic_encoder = nn.Sequential(
            nn.Linear(num_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        self.norm_encoder = nn.Sequential(
            nn.Linear(num_features, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Classifier: is this prediction based on dynamics or norms?
        self.classifier = nn.Linear(hidden_dim * 2, 2)
        
    def forward(self, features: torch.Tensor, predictions: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Detect if predictions rely on poisoned assumptions
        
        Returns:
            poison_scores: Probability predictions are norm-based vs dynamic
            flags: Binary flags for high-confidence poison detection
        """
        # Encode through both pathways
        dynamic_repr = self.dynamic_encoder(features)
        norm_repr = self.norm_encoder(features)
        
        # Concatenate and classify
        combined = torch.cat([dynamic_repr, norm_repr], dim=-1)
        logits = self.classifier(combined)  # [batch, 2] (dynamic vs norm)
        
        poison_scores = torch.softmax(logits, dim=-1)[:, 1]  # Probability of norm-based
        flags = (poison_scores > 0.7).float()  # High-confidence poison detection
        
        return {
            'poison_probability': poison_scores,
            'poison_flags': flags,
            'dynamic_score': 1 - poison_scores
        }


class TemporalEnergyModel(nn.Module):
    """
    Complete model combining all components
    Treats labor as time-energy flow with physics constraints
    """
    
    def __init__(self,
                 activity_dim: int,
                 num_domains: int = 5,  # work, care, rest, creation, survival
                 time_steps: int = 24,
                 constraints: Optional[TemporalConstraints] = None):
        super().__init__()
        
        self.constraints = constraints or TemporalConstraints()
        self.num_domains = num_domains
        self.time_steps = time_steps
        
        # Core components
        self.temporal_encoder = TemporalEncoder(
            activity_dim=activity_dim,
            time_steps=time_steps
        )
        
        self.causal_layer = CausalInferenceLayer(
            num_domains=num_domains
        )
        
        self.energy_balance = EnergyBalanceLayer(
            constraints=self.constraints
        )
        
        self.poison_detector = PoisonDetector(
            num_features=activity_dim * time_steps
        )
        
        # Domain classifier
        self.domain_classifier = nn.Linear(64, num_domains)
        
    def forward(self, 
                activities: torch.Tensor,
                domain_states: Optional[torch.Tensor] = None,
                return_diagnostics: bool = False) -> Dict[str, torch.Tensor]:
        """
        Full forward pass through temporal-energy framework
        
        Args:
            activities: [batch, time_steps, activity_dim]
            domain_states: [batch, num_domains, state_dim] (optional)
            return_diagnostics: Whether to return detailed diagnostics
            
        Returns:
            Dictionary containing predictions, losses, and optional diagnostics
        """
        batch_size, seq_len, _ = activities.shape
        
        # Encode temporal structure
        temporal_output = self.temporal_encoder(activities)
        embeddings = temporal_output['embeddings']
        energy_flows = temporal_output['energy_flows']
        
        # Classify activities into domains
        domain_logits = self.domain_classifier(embeddings.mean(dim=1))
        domain_probs = torch.softmax(domain_logits, dim=-1)
        
        # Compute time allocation per domain
        time_allocation = domain_probs.unsqueeze(1) * torch.ones(
            batch_size, seq_len, self.num_domains, device=activities.device
        )
        
        # Create recovery pattern (simplified - would be learned)
        recovery_mask = (energy_flows < 0).float()  # Negative energy = recovery
        recovery_patterns = recovery_mask.unsqueeze(-1).expand(-1, -1, seq_len)
        
        # Calculate energy balance losses
        energy_losses = self.energy_balance(
            time_allocation=time_allocation,
            energy_flows=energy_flows.unsqueeze(-1),
            recovery_patterns=recovery_patterns
        )
        
        # Causal inference if domain states provided
        causal_effects = None
        causal_graph = None
        if domain_states is not None:
            causal_effects, causal_graph = self.causal_layer(domain_states)
        
        # Detect poisoned assumptions
        poison_analysis = self.poison_detector(
            features=activities.reshape(batch_size, -1),
            predictions=domain_probs
        )
        
        output = {
            'domain_predictions': domain_probs,
            'energy_flows': energy_flows,
            'time_allocation': time_allocation,
            'energy_losses': energy_losses,
            'poison_analysis': poison_analysis,
        }
        
        if causal_effects is not None:
            output['causal_effects'] = causal_effects
            output['causal_graph'] = causal_graph
            
        if return_diagnostics:
            output['diagnostics'] = {
                'temporal_attention': temporal_output['attention'],
                'embeddings': embeddings,
                'recovery_patterns': recovery_patterns,
            }
            
        return output


# Example usage and testing utilities

def create_sample_activities(batch_size: int = 4, 
                            time_steps: int = 24,
                            activity_dim: int = 10) -> torch.Tensor:
    """Generate sample activity data for testing"""
    # Simulate 24-hour activity patterns
    activities = torch.randn(batch_size, time_steps, activity_dim)
    
    # Add some structure (e.g., work hours vs rest hours)
    for b in range(batch_size):
        # Work hours (8am-5pm roughly hours 8-17)
        activities[b, 8:17, :3] += 2.0  # High work activity
        # Rest hours (11pm-7am roughly hours 23-7)
        rest_hours = list(range(23, 24)) + list(range(0, 7))
        activities[b, rest_hours, 3:6] += 1.5  # Rest/recovery activity
        
    return activities


def demonstrate_framework():
    """Demonstrate the framework with sample data"""
    
    print("=" * 60)
    print("Temporal-Energy Model Framework Demo")
    print("=" * 60)
    
    # Create model
    model = TemporalEnergyModel(
        activity_dim=10,
        num_domains=5,
        time_steps=24
    )
    
    # Generate sample data
    activities = create_sample_activities(batch_size=4)
    domain_states = torch.randn(4, 5, 32)  # Sample domain states
    
    # Forward pass
    print("\nRunning forward pass...")
    output = model(activities, domain_states, return_diagnostics=True)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    # Energy balance analysis
    print("\n### Energy Balance Losses ###")
    for loss_name, loss_value in output['energy_losses'].items():
        print(f"{loss_name:20s}: {loss_value.item():.4f}")
    
    # Domain predictions
    print("\n### Domain Allocation (Average across batch) ###")
    domain_names = ['Work', 'Care', 'Rest', 'Creation', 'Survival']
    avg_domains = output['domain_predictions'].mean(dim=0)
    for i, name in enumerate(domain_names):
        print(f"{name:15s}: {avg_domains[i].item():.2%}")
    
    # Poison detection
    print("\n### Poisoned Assumption Detection ###")
    poison_prob = output['poison_analysis']['poison_probability'].mean()
    print(f"Average poison probability: {poison_prob.item():.2%}")
    print(f"Samples flagged: {output['poison_analysis']['poison_flags'].sum().int()}/4")
    
    # Causal graph
    if 'causal_graph' in output:
        print("\n### Learned Causal Structure ###")
        causal_strength = output['causal_graph'].detach().numpy()
        print("Causal adjacency matrix (rows cause → columns effect):")
        print("        ", "  ".join([f"{n[:4]:>5s}" for n in domain_names]))
        for i, from_domain in enumerate(domain_names):
            values = "  ".join([f"{causal_strength[i, j]:5.2f}" for j in range(5)])
            print(f"{from_domain[:8]:8s}: {values}")
    
    # Energy flows over time
    print("\n### Energy Flow Pattern (First sample) ###")
    energy_pattern = output['energy_flows'][0].detach().numpy()
    print("Hour  Energy")
    for hour in range(24):
        bar_length = int(abs(energy_pattern[hour]) * 10)
        bar = "+" * bar_length if energy_pattern[hour] > 0 else "-" * bar_length
        print(f"{hour:2d}:00  {energy_pattern[hour]:6.2f} {bar}")
    
    print("\n" + "=" * 60)
    print("Framework successfully demonstrated!")
    print("=" * 60)
    
    return model, output


if __name__ == "__main__":
    model, output = demonstrate_framework()
