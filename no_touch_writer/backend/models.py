from pydantic import BaseModel
from typing import List, Optional

class Action(BaseModel):
    type: str  # 'heading', 'paragraph', 'bullet', etc.
    content: str
    level: Optional[int] = None  # for heading levels
    target_heading: Optional[str] = None  # NEW: where this action should go

class VoiceCommand(BaseModel):
    text: str

class DocumentState(BaseModel):
    content: List[Action]