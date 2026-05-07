from remy_v1.models import SessionContext, CardType
from remy_v1.generators import generate_all_cards
from remy_v1.evaluation import evaluate_analogy_groundedness
from remy_v1.excerpts import keywords, key_term, key_sentence, find_contrast


IJEPA_EXCERPT = (
    "The model learns a representation by predicting masked context "
    "in feature space rather than reconstructing pixels."
)
DIFFUSION_EXCERPT = (
    "Diffusion models gradually denoise random noise to produce images, "
    "iteratively reversing a forward corruption process."
)
RAG_EXCERPT = (
    "Retrieval augmented generation conditions a language model on documents "
    "fetched from an external index at query time."
)


def _ctx(excerpt: str, question: str = "Is this generative?") -> SessionContext:
    return SessionContext(
        session_id="t",
        paper_id="p",
        paper_title="t",
        abstract=excerpt,
        selected_excerpt=excerpt,
        audience_question=question,
        speaker_goal="x",
        audience_level="mixed",
    )


# --- excerpt helpers ---------------------------------------------------------

def test_keywords_excludes_low_information_terms():
    text = "The model and the method and the system are an approach to the paper."
    kws = keywords(text, n=10)
    for banned in ("model", "method", "system", "approach", "paper"):
        assert banned not in kws, f"{banned!r} should be filtered out, got {kws}"


def test_key_term_picks_contentful_word_for_ijepa():
    term = key_term(IJEPA_EXCERPT)
    assert term not in {"model", "method", "system", "approach", "paper", "this idea"}
    # should be a recognizable content word from the excerpt
    assert term in IJEPA_EXCERPT.lower()


def test_key_term_avoids_ing_when_nominal_is_available():
    # "representation" (nominal) should beat "predicting"/"reconstructing" (-ing verbs)
    assert key_term(IJEPA_EXCERPT) == "representation"


def test_key_sentence_returns_first_sentence():
    sent = key_sentence("First idea here. Second idea is unrelated.")
    assert sent == "First idea here."


def test_find_contrast_detects_known_pair():
    assert find_contrast(IJEPA_EXCERPT) is not None
    left, right = find_contrast(IJEPA_EXCERPT)
    assert "masked" in left or "representation" in left


def test_find_contrast_returns_none_for_unrelated_excerpt():
    assert find_contrast("A simple sentence with no opposing concepts.") is None


# --- excerpt-aware generation ------------------------------------------------

def test_all_card_types_still_present():
    cards = generate_all_cards(_ctx(IJEPA_EXCERPT))
    types = {c.card_type for c in cards}
    assert types == {
        CardType.definition,
        CardType.common_stumble,
        CardType.speaker_phrasing,
        CardType.spicy_question,
        CardType.open_question,
        CardType.analogy,
    }


def test_card_bodies_change_when_excerpt_changes():
    a = generate_all_cards(_ctx(IJEPA_EXCERPT))
    b = generate_all_cards(_ctx(DIFFUSION_EXCERPT))
    c = generate_all_cards(_ctx(RAG_EXCERPT))
    by_type_a = {card.card_type: card.body for card in a}
    by_type_b = {card.card_type: card.body for card in b}
    by_type_c = {card.card_type: card.body for card in c}
    for ct in by_type_a:
        assert by_type_a[ct] != by_type_b[ct], f"{ct} body did not change between I-JEPA and diffusion"
        assert by_type_a[ct] != by_type_c[ct], f"{ct} body did not change between I-JEPA and RAG"
        assert by_type_b[ct] != by_type_c[ct], f"{ct} body did not change between diffusion and RAG"


def test_each_card_body_references_an_excerpt_term():
    # stem-prefix matching: a body that uses "denoising" still counts as
    # referencing an excerpt keyword "denoise".
    excerpt = DIFFUSION_EXCERPT
    cards = generate_all_cards(_ctx(excerpt, question="How does this differ from GANs?"))
    stems = {k[:5] for k in keywords(excerpt, n=8) if len(k) >= 5}
    for card in cards:
        body_low = card.body.lower()
        assert any(s in body_low for s in stems), (
            f"{card.card_type} body has no overlap with excerpt stems {stems}: {card.body!r}"
        )


def test_analogy_still_passes_grounding_for_ijepa():
    cards = generate_all_cards(_ctx(IJEPA_EXCERPT))
    analogy = next(c for c in cards if c.card_type == CardType.analogy)
    result = evaluate_analogy_groundedness(analogy, IJEPA_EXCERPT)
    assert result["passed"], result
    assert not result["banned_hit"]


def test_session_context_shape_is_unchanged():
    ctx = _ctx(IJEPA_EXCERPT)
    # original fields must still construct and round-trip
    dumped = ctx.model_dump()
    assert set(dumped.keys()) >= {
        "session_id", "paper_id", "paper_title", "abstract", "selected_excerpt",
        "audience_question", "speaker_goal", "audience_level", "prior_cards",
    }


def test_audience_question_influences_open_and_spicy():
    a = generate_all_cards(_ctx(IJEPA_EXCERPT, question="Is this generative?"))
    b = generate_all_cards(_ctx(IJEPA_EXCERPT, question="What about computational cost?"))
    open_a = next(c.body for c in a if c.card_type == CardType.open_question)
    open_b = next(c.body for c in b if c.card_type == CardType.open_question)
    assert open_a != open_b
    spicy_a = next(c.body for c in a if c.card_type == CardType.spicy_question)
    spicy_b = next(c.body for c in b if c.card_type == CardType.spicy_question)
    assert spicy_a != spicy_b
