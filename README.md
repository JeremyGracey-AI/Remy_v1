# Remy v1 Interface

A compact, GitHub-ready engineering companion to the À La Carte case study.

This repo includes:
- a typed SessionContext
- all six typed card generators
- an evaluation rule for analogy groundedness
- a CLI demo
- a Gradio app
- a JSONL export path for filed cards
- a Hugging Face Spaces-ready entry point

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Hugging Face Spaces

This repo is structured for a Gradio Space:
- root-level app.py
- root-level requirements.txt
- package code under remy_v1/
