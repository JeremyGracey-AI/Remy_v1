import json
from .models import SessionContext
from .generators import generate_all_cards
from .evaluation import evaluate_analogy_groundedness

def build_cards(paper_title: str, excerpt: str, audience_question: str, speaker_goal: str, audience_level: str):
    ctx = SessionContext(
        session_id="gradio-session",
        paper_id="paper-001",
        paper_title=paper_title or "Untitled paper",
        abstract=excerpt,
        selected_excerpt=excerpt,
        audience_question=audience_question,
        speaker_goal=speaker_goal,
        audience_level=audience_level,
    )
    cards = generate_all_cards(ctx)
    analogy = next(card for card in cards if card.card_type.value == "analogy")
    evaluation = evaluate_analogy_groundedness(analogy, excerpt)
    card_map = {card.card_type.value: card.model_dump(mode="json") for card in cards}
    return json.dumps(card_map, indent=2), json.dumps(evaluation, indent=2)

def create_app():
    import gradio as gr
    with gr.Blocks(title="Remy v1 Demo") as demo:
        gr.Markdown("# Remy v1 Demo\nGenerate six typed cards from a paper excerpt and run the analogy groundedness check.")
        with gr.Row():
            with gr.Column():
                paper_title = gr.Textbox(label="Paper title", value="I-JEPA")
                excerpt = gr.Textbox(label="Paper excerpt", lines=8, value="The model learns a representation by predicting masked context in feature space rather than reconstructing pixels.")
                audience_question = gr.Textbox(label="Audience question", value="Is this generative?")
                speaker_goal = gr.Textbox(label="Speaker goal", value="Clarify the difference between representation prediction and pixel generation.")
                audience_level = gr.Dropdown(label="Audience level", choices=["novice", "mixed", "expert"], value="mixed")
                run = gr.Button("Generate cards")
            with gr.Column():
                cards_out = gr.Code(label="Cards JSON", language="json")
                eval_out = gr.Code(label="Evaluation JSON", language="json")
        run.click(build_cards, inputs=[paper_title, excerpt, audience_question, speaker_goal, audience_level], outputs=[cards_out, eval_out])
    return demo

if __name__ == "__main__":
    app = create_app()
    app.launch()
