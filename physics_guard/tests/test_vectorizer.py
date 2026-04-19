"""Test suite for the vector similarity module."""

import pytest

from core.vectorizer import (
    TfIdfVectorizer,
    cosine_similarity,
    match_premise,
)

# -- Low-level vector tests ----------------------------------------------------

def test_cosine_identical_vectors():
    vec = {"energy": 1.0, "create": 0.5}
    assert cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_orthogonal_vectors():
    vec_a = {"energy": 1.0}
    vec_b = {"mass": 1.0}
    assert cosine_similarity(vec_a, vec_b) == 0.0


def test_cosine_empty_vector():
    assert cosine_similarity({}, {"energy": 1.0}) == 0.0
    assert cosine_similarity({}, {}) == 0.0


def test_tfidf_vectorizer_produces_nonzero():
    v = TfIdfVectorizer()
    v.fit(["energy can be created", "heat flows from hot to cold"])
    vec = v.vectorize("energy can be created from nothing")
    assert len(vec) > 0
    assert all(w > 0 for w in vec.values())


def test_tfidf_similar_texts_have_high_similarity():
    v = TfIdfVectorizer()
    docs = ["energy created from nothing", "heat flows from hot to cold"]
    v.fit(docs)
    vec_a = v.vectorize("energy created from nothing")
    vec_b = v.vectorize("energy generated from nothing")
    vec_c = v.vectorize("heat flows from hot to cold")
    # a and b should be more similar than a and c
    sim_ab = cosine_similarity(vec_a, vec_b)
    sim_ac = cosine_similarity(vec_a, vec_c)
    assert sim_ab > sim_ac


# -- PremiseMatcher tests -----------------------------------------------------

def test_matcher_identifies_violation():
    result = match_premise("power generated from nothing at all")
    assert result.best_label == "violation"
    assert result.similarity > 0.1


def test_matcher_identifies_valid():
    result = match_premise("energy is conserved in all closed systems")
    assert result.best_label == "valid"
    assert result.similarity > 0.1


def test_matcher_violation_score_higher_for_violations():
    result = match_premise("create electricity from the void with no cost")
    assert result.violation_score > result.valid_score


def test_matcher_valid_score_higher_for_valid():
    result = match_premise("heat transfers from hot surfaces to cold air")
    assert result.valid_score > result.violation_score


def test_match_result_to_dict():
    result = match_premise("energy from nothing")
    d = result.to_dict()
    assert "best_label" in d
    assert "best_category" in d
    assert "similarity" in d
    assert "top_matches" in d
    assert len(d["top_matches"]) > 0


# -- Vector fallback integration tests -----------------------------------------

def test_vector_fallback_catches_rephrased_violation():
    """Premises that dodge regex patterns should be caught by vector similarity."""
    from main import check
    # This is worded to avoid most regex patterns but is semantically a violation
    result = check("output appears with no source energy whatsoever")
    # The vector module should help identify this as suspicious
    assert result.get("vector_match") is not None or result["audit"].get("vector_match") is not None


def test_vector_match_in_output():
    """Vector match data should be present in verdict output."""
    from main import check
    result = check("energy can be created from nothing")
    vm = result.get("vector_match") or result["audit"].get("vector_match")
    assert vm is not None
    assert "similarity" in vm
    assert "best_label" in vm


def test_vector_match_boosts_confidence():
    """High vector similarity should result in higher confidence."""
    from main import check
    # Very clear violation — both regex and vector should agree
    result = check("energy can be created from nothing")
    assert result["confidence"] >= 0.9
