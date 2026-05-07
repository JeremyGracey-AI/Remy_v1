from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class CardType(str, Enum):
    definition = "definition"
    common_stumble = "common_stumble"
    speaker_phrasing = "speaker_phrasing"
    spicy_question = "spicy_question"
    open_question = "open_question"
    analogy = "analogy"

class CardState(str, Enum):
    new = "new"
    in_service = "in_service"
    edited = "edited"
    filed = "filed"
    rejected = "rejected"

class Provenance(BaseModel):
    source_kind: Literal["paper", "speaker_edit", "audience_question", "prior_card", "session_note"]
    source_ref: str
    excerpt: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)

class EvaluationScores(BaseModel):
    groundedness: float = Field(ge=0.0, le=1.0)
    clarity: float = Field(ge=0.0, le=1.0)
    usefulness: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)

class RecipeCard(BaseModel):
    card_id: str
    session_id: str
    paper_id: str
    card_type: CardType
    title: str
    body: str
    intent_line: str
    state: CardState = CardState.new
    tags: List[str] = []
    pairs_with: List[str] = []
    audience_level: Literal["novice", "mixed", "expert"] = "mixed"
    provenance: List[Provenance]
    scores: Optional[EvaluationScores] = None
    created_at: datetime
    updated_at: datetime

class SessionContext(BaseModel):
    session_id: str
    paper_id: str
    paper_title: str
    abstract: str
    selected_excerpt: Optional[str] = None
    audience_question: Optional[str] = None
    speaker_goal: Optional[str] = None
    audience_level: Literal["novice", "mixed", "expert"] = "mixed"
    prior_cards: List[RecipeCard] = []
