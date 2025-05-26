from pydantic import BaseModel
from typing import List, Optional

class Action(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    level: Optional[int] = None
    target_heading: Optional[str] = None
    operation: Optional[str] = None  # 'insert', 'replace', 'delete', 'change_type'
    target_line: Optional[int] = None

class VoiceCommand(BaseModel):
    text: str

class DocumentState(BaseModel):
    content: List[Action]