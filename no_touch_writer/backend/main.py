from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models import VoiceCommand, Action
from backend.state import doc
from backend.actions import parse_text_to_actions
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize app and document state
app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to receive transcribed voice text and convert to actions
@app.post("/voice")
def process_voice(command: VoiceCommand):
    lowered = command.text.strip().lower()

    if lowered.startswith("undo") or "remove last" in lowered:
        import re
        match = re.search(r"(undo|remove last)\s*(\d+)?", lowered)
        count = int(match.group(2)) if match and match.group(2) else 1
        doc.undo_last(count)
        return {"status": f"undid {count} action(s)"}

    actions = parse_text_to_actions(command.text)
    if actions:
        doc.apply_actions(actions)
    return {"actions": actions}

# Undo the last N sets of actions
@app.post("/undo")
def undo_last(n: int = 1):
    doc.undo_last(n)
    return {"status": "undone", "remaining_actions": doc.get_content()}

# Get current document state
@app.get("/doc")
def get_doc():
    return {"content": doc.get_content()}

@app.post("/redo")
def redo_last(n: int = 1):
    doc.redo_last(n)
    return {"status": "redone", "remaining_actions": doc.get_content()}

@app.post("/clear")
def clear_doc():
    doc.actions.clear()
    doc.history.clear()
    doc.redo_stack.clear()
    return {"status": "cleared"}