"""
PhysicsGuard — Information Conservation Domain

Checks claims about information against fundamental limits:
- Landauer's principle: erasing information has minimum energy cost (kT ln 2)
- Shannon's theorem: cannot transmit above channel capacity without error
- No-free-lunch: learning requires data; information cannot be created from nothing
- Data processing inequality: processing cannot increase information content

Useful for detecting AI-related claims like:
- "This model learns without training data"
- "Lossless compression below entropy limit"
- "Perfect prediction from noisy data"
"""

from dataclasses import dataclass
from typing import List

# -- Thresholds ----------------------------------------------------------------

MINIMUM_LEARNING_DATA = 0.01       # Cannot learn from literally zero data
MAXIMUM_COMPRESSION_RATIO = 0.99   # Cannot compress below entropy
MAXIMUM_PREDICTION_ACCURACY = 0.99  # Cannot perfectly predict noisy systems


@dataclass
class InfoClaim:
    raw: str
    claim_type: str           # learning | compression | transmission | prediction
    input_information: float  # bits/resources of input
    output_information: float  # bits/resources of output
    noise_level: float        # 0.0 = noiseless, 1.0 = pure noise
    justification: str


@dataclass
class InfoConstraintResult:
    claim: InfoClaim
    verdict: str
    flags: List[str]
    audit: List[dict]


def check_landauer(claim: InfoClaim) -> dict:
    """
    Landauer's principle: erasing 1 bit of information requires minimum kT ln 2 energy.
    Claims of information processing with zero energy cost violate this.
    """
    # If claiming output > input with zero cost
    ratio = claim.output_information / max(claim.input_information, 0.001)
    passed = ratio <= 1.0 or claim.input_information > MINIMUM_LEARNING_DATA
    return {
        "law": "landauer_principle",
        "score": min(ratio, 2.0) / 2.0,
        "passed": passed,
        "detail": f"Information ratio {ratio:.2f} (output/input)",
        "fix_hint": "Specify energy/data source for information creation" if not passed else "OK",
    }


def check_no_free_lunch(claim: InfoClaim) -> dict:
    """
    No-free-lunch theorem: a model cannot learn patterns without training data.
    Claims of learning from nothing violate this.
    """
    passed = claim.input_information >= MINIMUM_LEARNING_DATA
    return {
        "law": "no_free_lunch",
        "score": claim.input_information,
        "passed": passed,
        "detail": (
            f"Input information {claim.input_information:.4f} vs minimum {MINIMUM_LEARNING_DATA}"
        ),
        "fix_hint": "Learning requires data — specify training source" if not passed else "OK",
    }


def check_data_processing_inequality(claim: InfoClaim) -> dict:
    """
    Data processing inequality: processing cannot increase mutual information.
    Output information content cannot exceed input.
    """
    passed = claim.output_information <= claim.input_information * 1.01  # 1% tolerance
    excess = max(0.0, claim.output_information - claim.input_information)
    return {
        "law": "data_processing_inequality",
        "score": excess,
        "passed": passed,
        "detail": (
            f"Output={claim.output_information:.2f} vs input={claim.input_information:.2f}"
        ),
        "fix_hint": (
            f"Output exceeds input by {excess:.2f} — processing cannot create information"
            if not passed else "OK"
        ),
    }


def check_noise_floor(claim: InfoClaim) -> dict:
    """
    Shannon's theorem: accuracy is bounded by noise level.
    Cannot achieve perfect accuracy from noisy data.
    """
    max_accuracy = 1.0 - claim.noise_level * 0.5  # simplified bound
    claimed_accuracy = claim.output_information / max(claim.input_information, 0.001)
    passed = claimed_accuracy <= max_accuracy or claim.noise_level < 0.01
    return {
        "law": "shannon_noise_bound",
        "score": claimed_accuracy,
        "passed": passed,
        "detail": (
            f"Claimed accuracy {claimed_accuracy:.2%} vs noise-limited max {max_accuracy:.2%}"
        ),
        "fix_hint": (
            "Accuracy exceeds theoretical limit for this noise level"
            if not passed else "OK"
        ),
    }


def check_information(claim: InfoClaim) -> InfoConstraintResult:
    """Run all information conservation checks."""
    checks = [
        check_landauer(claim),
        check_no_free_lunch(claim),
        check_data_processing_inequality(claim),
        check_noise_floor(claim),
    ]

    failed = [c for c in checks if not c["passed"]]
    total = len(checks)
    score = len(failed) / total

    if score == 0.0: verdict = "CLEAN"
    elif score < 0.5: verdict = "SUSPECT"
    else: verdict = "CORRUPTED"

    return InfoConstraintResult(
        claim=claim,
        verdict=verdict,
        flags=[c["law"] for c in failed],
        audit=checks,
    )
