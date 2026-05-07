from .models import RecipeCard, CardType

def evaluate_analogy_groundedness(card: RecipeCard, paper_excerpt: str) -> dict:
    assert card.card_type == CardType.analogy
    banned_patterns = ["human-like consciousness", "magic", "it just knows", "literally creates the video"]
    grounded_keywords = ["feature", "representation", "masked", "predict", "context"]
    body_lower = card.body.lower()
    excerpt_lower = paper_excerpt.lower()
    banned_hit = any(p in body_lower for p in banned_patterns)
    keyword_overlap = sum(1 for k in grounded_keywords if k in body_lower and k in excerpt_lower)
    short_enough = len(card.body.split()) <= 60
    passed = (not banned_hit) and keyword_overlap >= 2 and short_enough
    return {
        "passed": passed,
        "banned_hit": banned_hit,
        "keyword_overlap": keyword_overlap,
        "length_words": len(card.body.split()),
    }
