from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models import VoiceCommand, Action
from backend.document import Document
from backend.actions import parse_text_to_actions
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize app and document state
app = FastAPI()
doc = Document()

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
    actions = parse_text_to_actions(command.text)
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