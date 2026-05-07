from .models import RecipeCard, CardType
from .excerpts import keywords

def evaluate_analogy_groundedness(card: RecipeCard, paper_excerpt: str) -> dict:
    assert card.card_type == CardType.analogy
    banned_patterns = ["human-like consciousness", "magic", "it just knows", "literally creates the video"]
    # Grounded vocabulary is now derived from the excerpt itself, so the rule
    # generalizes beyond I-JEPA. Use a 5-char stem for tolerance to common
    # morphology (e.g. "denoise" → "denoising", "predict" → "predicting").
    grounded_stems = [k[:5] for k in keywords(paper_excerpt, n=8) if len(k) >= 5]
    body_lower = card.body.lower()
    excerpt_lower = paper_excerpt.lower()
    banned_hit = any(p in body_lower for p in banned_patterns)
    keyword_overlap = sum(1 for s in grounded_stems if s in body_lower and s in excerpt_lower)
    short_enough = len(card.body.split()) <= 60
    passed = (not banned_hit) and keyword_overlap >= 2 and short_enough
    return {
        "passed": passed,
        "banned_hit": banned_hit,
        "keyword_overlap": keyword_overlap,
        "length_words": len(card.body.split()),
    }
