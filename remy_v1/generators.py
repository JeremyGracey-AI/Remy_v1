from datetime import datetime, UTC
from .models import RecipeCard, CardType, Provenance, SessionContext
from .excerpts import (
    key_term,
    key_sentence,
    find_contrast,
    contrast_pair,
    audience_focus,
)

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

def _excerpt_text(ctx: SessionContext) -> str:
    return ctx.selected_excerpt or ctx.abstract or ""


def generate_definition_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    term = key_term(excerpt)
    sent = key_sentence(excerpt)
    body = f'Anchor the audience on "{term}". {sent}'
    return _base_card(ctx, "c-def-1", CardType.definition, "Definition", body, "State what the audience is looking at.")


def generate_common_stumble_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    term = key_term(excerpt)
    contrast = find_contrast(excerpt)
    if contrast:
        left, right = contrast
        body = f"Do not collapse {left} into {right} — the excerpt distinguishes them."
    else:
        body = f'Do not reduce "{term}" to {contrast_pair(excerpt, term)}.'
    return _base_card(ctx, "c-stumble-1", CardType.common_stumble, "Common stumble", body, "Prevent the most likely wrong inference.")


def generate_speaker_phrasing_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    sent = key_sentence(excerpt)
    body = f"The line to deliver from the passage: {sent}"
    return _base_card(ctx, "c-speak-1", CardType.speaker_phrasing, "Speaker phrasing", body, "Give the speaker a clean next sentence.")


def generate_spicy_question_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    term = key_term(excerpt)
    focus = audience_focus(ctx.audience_question, term)
    contrast = find_contrast(excerpt)
    if contrast:
        left, right = contrast
        body = f"If the excerpt holds {left} apart from {right}, what does that change about {focus}?"
    else:
        body = f"If the excerpt frames {term} this way, what does that change about {focus}?"
    return _base_card(ctx, "c-spicy-1", CardType.spicy_question, "Spicy question", body, "Open a productive discussion worth holding the room for.")


def generate_open_question_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    term = key_term(excerpt)
    focus = audience_focus(ctx.audience_question, term)
    body = f"Are they actually asking about {focus}, or about {term} as the excerpt defines it?"
    return _base_card(ctx, "c-open-1", CardType.open_question, "Open question", body, "Infer the latent confusion under the visible question.")


def generate_analogy_card(ctx: SessionContext) -> RecipeCard:
    excerpt = _excerpt_text(ctx)
    term = key_term(excerpt)
    sent = key_sentence(excerpt)
    contrast = find_contrast(excerpt)
    if contrast:
        left, right = contrast
        body = (
            f"Picture {term} the way the excerpt frames it: {sent.lower()} "
            f"The split worth holding is {left} versus {right}."
        )
    else:
        body = f"Picture {term} the way the excerpt frames it: {sent.lower()}"
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
