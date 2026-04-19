"""
PhysicsGuard — Vector Similarity Module

Lightweight TF-IDF vectorizer using only stdlib. Encodes premises as sparse
vectors and compares them against a reference library of known physics
violations and valid claims using cosine similarity.

This provides semantic matching that catches rephrasings the regex patterns miss:
- "Power emerges spontaneously" matches near "energy created from nothing"
- "Unlimited output from a box" matches near "infinite power from finite source"

No external dependencies — uses math, collections, and re from stdlib.
"""

import math
import re
from collections import Counter

# -- Tokenization & n-grams ---------------------------------------------------

def _tokenize(text):
    """Lowercase, strip punctuation, split into words."""
    return re.findall(r"[a-z]+", text.lower())


def _ngrams(tokens, n):
    """Generate character-level or word-level n-grams."""
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _extract_features(text):
    """
    Build feature set from text: unigrams + bigrams + trigrams.

    Using n-grams captures phrase structure that single words miss:
    - "from nothing" as a bigram is more meaningful than "from" and "nothing" alone
    - "no entropy cost" as a trigram is a strong violation signal
    """
    tokens = _tokenize(text)
    features = list(tokens)  # unigrams
    features.extend(_ngrams(tokens, 2))  # bigrams
    features.extend(_ngrams(tokens, 3))  # trigrams
    return features


# -- TF-IDF Vector Construction ------------------------------------------------

class TfIdfVectorizer:
    """
    Lightweight TF-IDF vectorizer.

    Builds an IDF (inverse document frequency) table from a corpus of
    reference texts, then converts any new text into a TF-IDF vector.
    """

    def __init__(self):
        self.idf = {}          # term -> inverse document frequency
        self.vocab = set()     # all known terms
        self._corpus_size = 0

    def fit(self, documents):
        """
        Build IDF table from a list of reference documents.

        Each document is a string. Call this once with the reference library.
        """
        self._corpus_size = len(documents)
        doc_freq = Counter()

        for doc in documents:
            features = set(_extract_features(doc))
            self.vocab.update(features)
            for f in features:
                doc_freq[f] += 1

        # IDF = log(N / df) — terms that appear in fewer docs get higher weight
        for term, df in doc_freq.items():
            self.idf[term] = math.log(self._corpus_size / df) if df > 0 else 0.0

    def vectorize(self, text):
        """
        Convert text to a TF-IDF vector (sparse dict: term -> weight).

        Terms not in the vocabulary get a default high IDF (novel/unknown terms).
        """
        features = _extract_features(text)
        tf = Counter(features)
        total = len(features) if features else 1

        vector = {}
        for term, count in tf.items():
            tf_score = count / total
            idf_score = self.idf.get(term, math.log(self._corpus_size + 1))
            weight = tf_score * idf_score
            if weight > 0:
                vector[term] = weight

        return vector


# -- Cosine Similarity ---------------------------------------------------------

def cosine_similarity(vec_a, vec_b):
    """
    Compute cosine similarity between two sparse vectors (dicts).

    Returns float in [-1.0, 1.0]. Higher = more similar.
    TF-IDF vectors are always non-negative, so range is [0.0, 1.0].
    """
    # Dot product: only terms present in both vectors
    common_terms = set(vec_a.keys()) & set(vec_b.keys())
    if not common_terms:
        return 0.0

    dot = sum(vec_a[t] * vec_b[t] for t in common_terms)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


# -- Reference Library ---------------------------------------------------------

# Each entry: (text, label, category)
# Labels: "violation" or "valid"
# Categories match claim_pattern names for cross-referencing

REFERENCE_LIBRARY = [
    # -- First Law violations (energy conservation) --
    ("energy can be created from nothing", "violation", "creation_from_nothing"),
    ("create energy without any source", "violation", "creation_from_nothing"),
    ("power generated from the void", "violation", "creation_from_nothing"),
    ("electricity produced with no input", "violation", "creation_from_nothing"),
    ("something from nothing", "violation", "creation_from_nothing"),
    ("output without any input energy", "violation", "creation_from_nothing"),
    ("energy appears spontaneously", "violation", "creation_from_nothing"),
    ("work done with zero energy input", "violation", "creation_from_nothing"),

    # -- Second Law violations (entropy) --
    ("extract energy without entropy cost", "violation", "output_without_cost"),
    ("produce output with no waste heat", "violation", "output_without_cost"),
    ("convert energy with zero loss", "violation", "output_without_cost"),
    ("process with no entropy increase", "violation", "output_without_cost"),
    ("perfectly efficient conversion", "violation", "perfect_efficiency"),
    ("one hundred percent efficiency", "violation", "perfect_efficiency"),
    ("lossless energy transformation", "violation", "perfect_efficiency"),
    ("reversible process with no heat", "violation", "entropy_reversal"),
    ("entropy decreases spontaneously", "violation", "entropy_reversal"),
    ("disorder reduces without work", "violation", "entropy_reversal"),

    # -- Infinite/perpetual claims --
    ("infinite energy from finite source", "violation", "infinite_claim"),
    ("unlimited power generation", "violation", "infinite_claim"),
    ("boundless output from small device", "violation", "infinite_claim"),
    ("perpetual motion machine", "violation", "perpetual_motion"),
    ("machine runs forever without fuel", "violation", "perpetual_motion"),
    ("self sustaining device needs no input", "violation", "perpetual_motion"),
    ("free energy device", "violation", "perpetual_motion"),
    ("over unity device produces more than input", "violation", "perpetual_motion"),

    # -- Mass conservation violations --
    ("mass created from nothing", "violation", "creation_from_nothing"),
    ("matter appears without source", "violation", "creation_from_nothing"),
    ("resources generated from thin air", "violation", "creation_from_nothing"),
    ("destroy mass completely", "violation", "creation_from_nothing"),

    # -- Extraction-without-return violations (TAF-style energy accounting) --
    ("extract energy from workers without compensation", "violation", "energy_extraction_without_return"),
    ("drain resources from the land without replenishing", "violation", "energy_extraction_without_return"),
    ("takes from the commons and gives nothing back", "violation", "energy_extraction_without_return"),
    ("siphon value from labor without reinvestment", "violation", "energy_extraction_without_return"),
    ("mine the soil with no nutrient return", "violation", "energy_extraction_without_return"),
    ("indefinite extraction with no replenishment flow", "violation", "energy_extraction_without_return"),

    # -- Information violations --
    ("learn without any training data", "violation", "information_violation"),
    ("knowledge from nothing", "violation", "information_violation"),
    ("compress below entropy limit", "violation", "information_violation"),
    ("perfect prediction from noisy data", "violation", "information_violation"),
    ("lossless compression of random data", "violation", "information_violation"),

    # -- Valid physics statements --
    ("energy is conserved in closed systems", "valid", "conservation_statement"),
    ("mass cannot be created or destroyed", "valid", "conservation_statement"),
    ("heat flows from hot to cold", "valid", "transfer_claim"),
    ("energy transfers between systems", "valid", "transfer_claim"),
    ("entropy always increases in isolated systems", "valid", "conservation_statement"),
    ("work requires energy input", "valid", "conservation_statement"),
    ("radiation emitted from hot surfaces", "valid", "transfer_claim"),
    ("thermal equilibrium reached over time", "valid", "transfer_claim"),
    ("friction converts kinetic energy to heat", "valid", "transfer_claim"),
    ("chemical reactions conserve mass", "valid", "conservation_statement"),
    ("electrical resistance produces waste heat", "valid", "transfer_claim"),
    ("solar panels convert light to electricity with losses", "valid", "transfer_claim"),
    ("conservation of mass holds in all chemical reactions", "valid", "conservation_statement"),
    ("total energy remains constant in isolated system", "valid", "conservation_statement"),
    ("heat cannot flow from cold to hot without work", "valid", "conservation_statement"),
    ("every action has equal and opposite reaction", "valid", "conservation_statement"),
    ("information requires physical substrate", "valid", "conservation_statement"),
    ("learning requires training data and computation", "valid", "conservation_statement"),
    ("compression cannot go below information entropy", "valid", "conservation_statement"),
    ("engines have efficiency below carnot limit", "valid", "conservation_statement"),
]


# -- Premise Matcher -----------------------------------------------------------

class PremiseMatcher:
    """
    Matches premises against the reference library using vector similarity.

    Usage:
        matcher = PremiseMatcher()
        result = matcher.match("power emerges spontaneously from vacuum")
        # result.best_label = "violation"
        # result.best_category = "creation_from_nothing"
        # result.similarity = 0.72
    """

    def __init__(self, library=None):
        self._library = library or REFERENCE_LIBRARY
        self._vectorizer = TfIdfVectorizer()
        self._ref_vectors = []

        # Fit vectorizer on all reference texts
        texts = [entry[0] for entry in self._library]
        self._vectorizer.fit(texts)

        # Pre-compute reference vectors
        for text, label, category in self._library:
            vec = self._vectorizer.vectorize(text)
            self._ref_vectors.append((vec, label, category, text))

    def match(self, premise):
        """
        Match a premise against the reference library.

        Returns a MatchResult with:
            - best_label: "violation" or "valid"
            - best_category: claim pattern category
            - similarity: cosine similarity to best match (0.0-1.0)
            - top_matches: list of (similarity, label, category, reference_text)
            - violation_score: aggregated similarity to violation references
            - valid_score: aggregated similarity to valid references
        """
        vec = self._vectorizer.vectorize(premise)

        # Compute similarity against all references
        scored = []
        for ref_vec, label, category, ref_text in self._ref_vectors:
            sim = cosine_similarity(vec, ref_vec)
            scored.append((sim, label, category, ref_text))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Aggregate scores by label
        violation_sims = [s for s, lbl, _, _ in scored if lbl == "violation"]
        valid_sims = [s for s, lbl, _, _ in scored if lbl == "valid"]

        # Top-k average (use top 3 matches per category for stability)
        k = 3
        violation_score = sum(violation_sims[:k]) / k if violation_sims else 0.0
        valid_score = sum(valid_sims[:k]) / k if valid_sims else 0.0

        best_sim, best_label, best_category, best_text = scored[0] if scored else (0.0, "unknown", "generic", "")

        return MatchResult(
            best_label=best_label,
            best_category=best_category,
            similarity=best_sim,
            top_matches=scored[:5],
            violation_score=violation_score,
            valid_score=valid_score,
        )


class MatchResult:
    """Result of matching a premise against the reference library."""

    __slots__ = (
        "best_label", "best_category", "similarity",
        "top_matches", "violation_score", "valid_score",
    )

    def __init__(self, best_label, best_category, similarity,
                 top_matches, violation_score, valid_score):
        self.best_label = best_label
        self.best_category = best_category
        self.similarity = similarity
        self.top_matches = top_matches
        self.violation_score = violation_score
        self.valid_score = valid_score

    def to_dict(self):
        return {
            "best_label": self.best_label,
            "best_category": self.best_category,
            "similarity": round(self.similarity, 4),
            "violation_score": round(self.violation_score, 4),
            "valid_score": round(self.valid_score, 4),
            "top_matches": [
                {
                    "reference": text,
                    "label": label,
                    "category": cat,
                    "similarity": round(sim, 4),
                }
                for sim, label, cat, text in self.top_matches
            ],
        }

    @property
    def is_likely_violation(self):
        """True if violation score significantly exceeds valid score."""
        return self.violation_score > self.valid_score and self.similarity > 0.15

    @property
    def is_likely_valid(self):
        """True if valid score significantly exceeds violation score."""
        return self.valid_score > self.violation_score and self.similarity > 0.15


# -- Module-level singleton (lazy init) ----------------------------------------

_matcher = None


def get_matcher():
    """Get or create the singleton PremiseMatcher."""
    global _matcher
    if _matcher is None:
        _matcher = PremiseMatcher()
    return _matcher


def match_premise(premise):
    """Quick API: match a premise against the reference library."""
    return get_matcher().match(premise)
