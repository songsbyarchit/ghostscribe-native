from pydantic import BaseModel
from typing import List, Optional

class Action(BaseModel):
    type: Optional[str] = None  # ✅ make optional
    content: Optional[str] = None  # ✅ make optional
    level: Optional[int] = None
    target_heading: Optional[str] = None
    operation: Optional[str] = None
    target_line: Optional[int] = None

class VoiceCommand(BaseModel):
    text: str

class DocumentState(BaseModel):
    content: List[Action]