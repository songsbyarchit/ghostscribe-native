import os
import json
from typing import List
from backend.models import Action
from openai import OpenAI
from dotenv import load_dotenv

# Load your OpenAI key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_text_to_actions(text: str) -> List[Action]:
    prompt = f"""
        You are a document-writing assistant that must interpret spoken user instructions and convert them into structured editing actions.

        Your job is to determine:
        1. Is the user asking you to generate content (e.g., "suggest", "write", "generate", "draft")?
        2. Or are they simply dictating content to be inserted as-is?

        ### If they are asking for generated content:
        - Use your own words to write the output.
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

        return [Action(**a) for a in parsed if a.get("type") and a.get("content")]

    except Exception as e:
        return [Action(type="paragraph", content=f"[OpenAI Error] {str(e)}")]
