from datetime import datetime, UTC
from .models import RecipeCard, CardType, Provenance, SessionContext

def utcnow():
    return datetime.now(UTC)

def _base_card(ctx: SessionContext, card_id: str, card_type: CardType, title: str, body: str, intent_line: str) -> RecipeCard:
    excerpt = ctx.selected_excerpt or ctx.abstract
    return RecipeCard(
        card_id=card_id,
        session_id=ctx.session_id,
        paper_id=ctx.paper_id,
        card_type=card_type,
        title=title,
        body=body,
        intent_line=intent_line,
        audience_level=ctx.audience_level,
        provenance=[Provenance(source_kind="paper", source_ref=f"{ctx.paper_id}:excerpt", excerpt=excerpt[:240], confidence=0.9)],
        created_at=utcnow(),
        updated_at=utcnow(),
    )

def generate_definition_card(ctx: SessionContext) -> RecipeCard:
    body = "This method predicts masked structure in representation space instead of rebuilding raw pixels."
    return _base_card(ctx, "c-def-1", CardType.definition, "Definition", body, "State what the audience is looking at.")

def generate_common_stumble_card(ctx: SessionContext) -> RecipeCard:
    body = "Do not confuse feature-space prediction with direct pixel generation."
    return _base_card(ctx, "c-stumble-1", CardType.common_stumble, "Common stumble", body, "Prevent the most likely wrong inference.")

def generate_speaker_phrasing_card(ctx: SessionContext) -> RecipeCard:
    body = "The important move is that the model predicts a representation of what is missing, not the literal pixels themselves."
    return _base_card(ctx, "c-speak-1", CardType.speaker_phrasing, "Speaker phrasing", body, "Give the speaker a clean next sentence.")

def generate_spicy_question_card(ctx: SessionContext) -> RecipeCard:
    body = "If the model never reconstructs pixels directly, what kinds of downstream reasoning does that help or limit?"
    return _base_card(ctx, "c-spicy-1", CardType.spicy_question, "Spicy question", body, "Open a productive discussion worth holding the room for.")

def generate_open_question_card(ctx: SessionContext) -> RecipeCard:
    body = "Are they really asking whether the system is generative, or whether its latent space is useful enough to replace generation for the task at hand?"
    return _base_card(ctx, "c-open-1", CardType.open_question, "Open question", body, "Infer the latent confusion under the visible question.")

def generate_analogy_card(ctx: SessionContext) -> RecipeCard:
    body = "Think of masked representation prediction as filling in missing semantic context rather than reconstructing raw pixels."
    return _base_card(ctx, "c-analogy-1", CardType.analogy, "Analogy", body, "Clarify the method without drift.")

def generate_all_cards(ctx):
    return [
        generate_definition_card(ctx),
        generate_common_stumble_card(ctx),
        generate_speaker_phrasing_card(ctx),
        generate_spicy_question_card(ctx),
        generate_open_question_card(ctx),
        generate_analogy_card(ctx),
    ]
