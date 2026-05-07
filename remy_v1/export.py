import json
from pathlib import Path
from .models import RecipeCard, CardState

def export_filed_cards_jsonl(cards: list[RecipeCard], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    filed = [card for card in cards if card.state == CardState.filed]
    with path.open("w", encoding="utf-8") as f:
        for card in filed:
            f.write(json.dumps(card.model_dump(mode="json")) + "\n")
    return path
