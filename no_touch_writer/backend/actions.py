import os
import json
from typing import List
from backend.models import Action
from openai import OpenAI
from dotenv import load_dotenv
from backend.state import doc

# Load your OpenAI key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_text_to_actions(text: str) -> List[Action]:
    current_state = get_current_doc()  # This should return a list of blocks
    context_str = "\n".join([f"{b['type'].upper()}: {b['content']}" for b in current_state])

    prompt = f"""
        You are a document-writing assistant that must interpret spoken user instructions and convert them into structured editing actions.

        ## CURRENT DOCUMENT:
        {context_str}

        ## USER INPUT:
        "{text}"
        
        Your job is to determine:
        1. Is the user asking you to generate content? (e.g., they say: "give me", "list", "what are", "show", "create", "write", "generate", "suggest", "come up with")
        2. Are they simply dictating content to be inserted as-is?
        3. Or are they giving structural editing instructions (e.g., "replace line 2", "delete line 4", "insert at line 3", "turn line 6 into a heading", "turn line 1 into a bullet point")?

        If it's case 3:
        - Use the fields `operation: "replace" | "delete" | "insert" | "change_type"` and `target_line: <number>`.
        - If no line is specified, assume the insertion should be at the end.
        - For `change_type`, you must also include the new `type` (e.g., "heading", "bullet", "subheading").
        - For `replace` or `insert`, include both `type` and `content`.
        - If the user says "turn line 3 into a heading" or "make line 5 a bullet point", treat it as `operation: "change_type"` with `target_line` and `type`.

        ### If they are asking for generated content:
        - Interpret the user’s intent and generate original content using your own words and factual reasoning.
        - For example, if the user says "Give me three reasons why squash is dangerous", you must generate three relevant bullet points as output.
        - Make sure to include relevant bullet points or paragraph content based on the request.
        - Include a field called "target_heading" if the user specifies where it should go.

        ### If they are dictating (no trigger words):
        - Just treat their full sentence as a "paragraph" or "bullet".
        - Still use "target_heading" if applicable.

        Always return a valid JSON array of actions:
        [
        {{ "type": "heading", "content": "Morning Plan", "level": 2 }},
        {{ "type": "paragraph", "content": "Start your day with intention", "target_heading": "Morning" }},
        {{ "type": "bullet", "content": "Drink water first thing", "target_heading": "Morning" }}
        ]

        Now respond ONLY with the action list based on this input:
        "{text}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.4
        )

        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)

        return [Action(**a) for a in parsed if "operation" in a or ("type" in a and "content" in a)]

    except Exception as e:
        return [Action(type="paragraph", content=f"[OpenAI Error] {str(e)}")]
    
def get_current_doc():
    return [a.dict() for a in doc.get_content()]