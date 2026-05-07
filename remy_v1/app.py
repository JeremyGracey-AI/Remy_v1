import json
import tempfile
from pathlib import Path
from html import escape

from .models import SessionContext, CardType
from .generators import generate_all_cards
from .evaluation import evaluate_analogy_groundedness
from .export import export_filed_cards_jsonl


# (foreground, background) per card_type
CARD_COLORS = {
    "definition":       ("#475569", "#f1f5f9"),  # slate
    "common_stumble":   ("#b45309", "#fef3c7"),  # amber
    "speaker_phrasing": ("#0f766e", "#ccfbf1"),  # teal
    "spicy_question":   ("#be123c", "#ffe4e6"),  # rose
    "open_question":    ("#4338ca", "#e0e7ff"),  # indigo
    "analogy":          ("#047857", "#d1fae5"),  # emerald
}

CARD_LABELS = {
    "definition":       "Definition",
    "common_stumble":   "Common stumble",
    "speaker_phrasing": "Speaker phrasing",
    "spicy_question":   "Spicy question",
    "open_question":    "Open question",
    "analogy":          "Analogy",
}

CARD_ORDER = [
    "definition",
    "common_stumble",
    "speaker_phrasing",
    "spicy_question",
    "open_question",
    "analogy",
]

CARDS_CSS = """
<style>
  .remy-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin: 8px 0 4px;
  }
  @media (max-width: 768px) {
    .remy-grid { grid-template-columns: 1fr; }
  }
  .remy-card {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 14px 16px;
    background: var(--background-fill-primary, #ffffff);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }
  .remy-chip {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .remy-title { font-weight: 600; font-size: 16px; margin: 8px 0 4px; }
  .remy-intent {
    font-size: 12px;
    color: var(--body-text-color-subdued, #6b7280);
    margin-bottom: 8px;
    font-style: italic;
  }
  .remy-body { font-size: 14px; line-height: 1.5; }
</style>
"""


def _render_card_html(card) -> str:
    fg, bg = CARD_COLORS.get(card.card_type.value, ("#374151", "#f3f4f6"))
    label = CARD_LABELS.get(card.card_type.value, card.card_type.value)
    return (
        '<div class="remy-card">'
        f'<span class="remy-chip" style="color:{fg};background:{bg};">{escape(label)}</span>'
        f'<div class="remy-title">{escape(card.title or "")}</div>'
        f'<div class="remy-intent">{escape(card.intent_line or "")}</div>'
        f'<div class="remy-body">{escape(card.body or "")}</div>'
        '</div>'
    )


def _render_cards_html(cards) -> str:
    by_type = {c.card_type.value: c for c in cards}
    blocks = "".join(_render_card_html(by_type[t]) for t in CARD_ORDER if t in by_type)
    return CARDS_CSS + f'<div class="remy-grid">{blocks}</div>'


def _verdict_line(evaluation: dict) -> str:
    icon = "✅" if evaluation.get("passed") else "❌"
    status = "Pass" if evaluation.get("passed") else "Fail"
    return (
        f"{icon} **Analogy groundedness: {status}** — "
        f"keyword overlap `{evaluation.get('keyword_overlap')}`, "
        f"length `{evaluation.get('length_words')} words`, "
        f"banned terms `{evaluation.get('banned_hit')}`"
    )


def _write_filed_jsonl(cards) -> str:
    out = Path(tempfile.gettempdir()) / "remy_filed_cards.jsonl"
    export_filed_cards_jsonl(cards, out)
    if out.stat().st_size == 0:
        out.write_text(
            "# No filed cards yet — promote a card to state=filed to populate this file.\n",
            encoding="utf-8",
        )
    return str(out)


DEFAULT_TITLE = "I-JEPA"
DEFAULT_EXCERPT = (
    "The model learns a representation by predicting masked context "
    "in feature space rather than reconstructing pixels."
)
DEFAULT_QUESTION = "Is this generative?"
DEFAULT_GOAL = "Clarify the difference between representation prediction and pixel generation."
DEFAULT_LEVEL = "mixed"


def build_cards(paper_title: str, excerpt: str, audience_question: str, speaker_goal: str, audience_level: str):
    ctx = SessionContext(
        session_id="gradio-session",
        paper_id="paper-001",
        paper_title=paper_title or "Untitled paper",
        abstract=excerpt or "",
        selected_excerpt=excerpt or "",
        audience_question=audience_question,
        speaker_goal=speaker_goal,
        audience_level=audience_level,
    )
    cards = generate_all_cards(ctx)
    analogy = next(card for card in cards if card.card_type == CardType.analogy)
    evaluation = evaluate_analogy_groundedness(analogy, excerpt or "")
    cards_html = _render_cards_html(cards)
    verdict = _verdict_line(evaluation)
    eval_json = json.dumps(evaluation, indent=2)
    raw_json = json.dumps(
        {c.card_type.value: c.model_dump(mode="json") for c in cards},
        indent=2,
    )
    download_path = _write_filed_jsonl(cards)
    return cards_html, verdict, eval_json, raw_json, download_path


def create_app():
    import gradio as gr
    with gr.Blocks(title="Remy v1 — typed reading-group copilot") as demo:
        gr.Markdown(
            "# Remy v1 — typed reading-group copilot\n"
            "Generate six typed cards from a paper excerpt and audit the analogy for "
            "groundedness against the source. Part of the "
            "[À la carte](https://alacarte.jeremygracey.ai/) reading-group toolkit."
        )
        with gr.Row():
            with gr.Column(scale=1):
                paper_title = gr.Textbox(label="Paper title", value=DEFAULT_TITLE)
                excerpt = gr.Textbox(label="Paper excerpt", lines=8, value=DEFAULT_EXCERPT)
                audience_question = gr.Textbox(label="Audience question", value=DEFAULT_QUESTION)
                speaker_goal = gr.Textbox(label="Speaker goal", value=DEFAULT_GOAL)
                audience_level = gr.Dropdown(
                    label="Audience level",
                    choices=["novice", "mixed", "expert"],
                    value=DEFAULT_LEVEL,
                )
                run = gr.Button("Generate cards", variant="primary")
                download_btn = gr.DownloadButton(
                    label="Download filed cards (JSONL)",
                    value=None,
                )
            with gr.Column(scale=2):
                cards_view = gr.HTML(label="Cards")
                verdict_view = gr.Markdown()
                with gr.Accordion("Analogy evaluation (full JSON)", open=False):
                    eval_view = gr.Code(language="json")
                with gr.Accordion("Raw JSON (engineering view)", open=False):
                    raw_view = gr.Code(language="json")
        run.click(
            build_cards,
            inputs=[paper_title, excerpt, audience_question, speaker_goal, audience_level],
            outputs=[cards_view, verdict_view, eval_view, raw_view, download_btn],
        )
    return demo


if __name__ == "__main__":
    app = create_app()
    app.launch()
