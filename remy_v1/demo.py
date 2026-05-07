import json
from .models import SessionContext, CardState
from .generators import generate_all_cards
from .evaluation import evaluate_analogy_groundedness

EXCERPT = "The model learns a representation by predicting masked context in feature space rather than reconstructing pixels."

def run_demo() -> dict:
    ctx = SessionContext(
        session_id="demo-session",
        paper_id="ijepa-001",
        paper_title="I-JEPA",
        abstract="A world model that predicts representations in feature space.",
        selected_excerpt=EXCERPT,
        audience_question="Is this generative?",
        speaker_goal="Explain the difference between representation prediction and pixel generation.",
        audience_level="mixed",
    )
    cards = generate_all_cards(ctx)
    cards[0].state = CardState.filed
    cards[1].state = CardState.filed
    analogy = next(card for card in cards if card.card_type.value == "analogy")
    evaluation = evaluate_analogy_groundedness(analogy, ctx.selected_excerpt or ctx.abstract)
    return {
        "context": ctx.model_dump(),
        "cards": [card.model_dump(mode="json") for card in cards],
        "evaluation": evaluation,
    }

if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
