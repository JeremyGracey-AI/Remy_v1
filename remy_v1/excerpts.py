import re
from typing import List, Optional, Tuple

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "by", "with", "from", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "into", "than", "then", "so",
    "we", "our", "their", "they", "them", "he", "she", "his", "her", "i", "you",
    "do", "does", "did", "not", "no", "can", "could", "should", "would", "may",
    "might", "must", "if", "while", "when", "what", "which", "who", "how", "why",
    "rather", "instead", "about", "over", "under", "via", "such", "any", "all",
    "more", "most", "less", "least", "very", "also", "only", "some", "many",
    "directly", "indirectly", "actually", "really", "always", "never", "often",
    "sometimes", "typically", "usually", "perhaps",
    # low-information generic terms — never anchor a card on these
    "model", "models", "method", "methods", "paper", "approach", "approaches",
    "system", "systems", "work", "works", "thing", "things", "idea", "ideas",
    "result", "results", "study", "studies", "framework", "frameworks",
    "technique", "techniques",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-]+")
_SENT_RE = re.compile(r"(?<=[\.!?])\s+")


def tokenize(text: str) -> List[str]:
    return _WORD_RE.findall(text or "")


def keywords(text: str, n: int = 5) -> List[str]:
    """Return up to n distinct content words from text. Ranked by frequency,
    de-prioritizing "-ing" verbs so nominal terms surface first; ties broken
    by length (longer first) and first-seen position. Deterministic."""
    counts: dict[str, int] = {}
    positions: dict[str, int] = {}
    for i, tok in enumerate(tokenize(text)):
        low = tok.lower()
        if len(low) < 4 or low in _STOPWORDS:
            continue
        counts[low] = counts.get(low, 0) + 1
        positions.setdefault(low, i)
    def _nominal_penalty(w: str) -> int:
        # push "-ing" verb forms and "-ly" adverbs below true nominal terms
        return int(w.endswith("ing") or w.endswith("ly"))
    ranked = sorted(
        counts.items(),
        key=lambda kv: (-kv[1], _nominal_penalty(kv[0]), -len(kv[0]), positions[kv[0]], kv[0]),
    )
    return [w for w, _ in ranked[:n]]


def key_term(text: str) -> str:
    """Single most salient content term to anchor card bodies."""
    kws = keywords(text, n=3)
    return kws[0] if kws else "this idea"


def key_sentence(text: str) -> str:
    """First non-empty sentence, normalized to end with a period."""
    if not text:
        return ""
    parts = [p.strip() for p in _SENT_RE.split(text.strip()) if p.strip()]
    sent = parts[0] if parts else text.strip()
    return sent.rstrip(".!?") + "."


# Pairs of excerpt signals → human-readable contrast (left vs right).
# Order matters: more specific patterns first.
_CONTRAST_PATTERNS: List[Tuple[Tuple[str, str], Tuple[str, str]]] = [
    (("masked",        "reconstruct"),    ("masked prediction", "reconstruction")),
    (("representation","pixel"),          ("representation",    "pixels")),
    (("feature",       "pixel"),          ("feature space",     "pixel space")),
    (("latent",        "raw"),            ("latent space",      "raw input")),
    (("predict",       "generate"),       ("prediction",        "generation")),
    (("self-supervised","supervised"),    ("self-supervised",   "fully supervised")),
    (("encode",        "decode"),         ("encoding",          "decoding")),
    (("denoise",       "noise"),          ("denoising",         "the original noise")),
    (("retrieve",      "generate"),       ("retrieval",         "generation")),
]


def find_contrast(text: str) -> Optional[Tuple[str, str]]:
    """Detect a salient binary contrast in the excerpt, e.g. (representation, pixels).
    Returns (left, right) or None. Both signals must be present."""
    low = (text or "").lower()
    for (a, b), (left, right) in _CONTRAST_PATTERNS:
        if a in low and b in low:
            return (left, right)
    return None


def contrast_pair(text: str, term: str) -> str:
    """Soft fallback contrast for excerpts where no binary pattern was detected."""
    low = (text or "").lower()
    if "feature" in low or "representation" in low:
        return "direct pixel reconstruction"
    if "predict" in low:
        return "naive copying of the input"
    if "latent" in low or "embedding" in low:
        return "raw surface features"
    if "self-supervised" in low or "unsupervised" in low:
        return "fully supervised labeling"
    return f"a surface-level reading of {term}"


def audience_focus(question: Optional[str], term: str) -> str:
    """Short focus phrase derived from the audience question, with a fallback."""
    if not question:
        return f"how {term} actually behaves"
    kws = keywords(question, n=2)
    if not kws:
        cleaned = question.strip().rstrip("?")
        return cleaned or term
    return " and ".join(kws)
