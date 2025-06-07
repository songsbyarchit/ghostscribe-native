import os
import json
from typing import List
from backend.models import Action
from openai import OpenAI
from dotenv import load_dotenv
from backend.state import doc
import re

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_current_doc():
    return [a.dict() for a in doc.get_content()]

def classify_instruction(text: str, model_name: str = "gpt-3.5-turbo") -> str:
    lowered = text.lower()

    if any(kw in lowered for kw in ["delete", "remove", "erase"]) and "line" in lowered:
        return "structural_delete"
    elif any(char.isdigit() for char in text):
        return "generate_content"
    
    prompt = f"""
    You are a classifier for document editing commands. Your job is to determine what kind of instruction the user has given. If the input is short and contains a number + nouns (e.g., "three headings squash paddle badminton"), infer it's a content generation request even without trigger words.

    ## POSSIBLE CASES:
    0. generate_headings — They want to add N headings EXACTLY as dictated based on short inputs like “write three headings squash paddle badminton”. These don’t need trigger verbs.
    1. generate_content — They want you to generate something creative or factual. Trigger words: "give me", "generate", "suggest", "list", "what are", "show", "come up with".
    2. dictation — They're dictating something to be added directly. Trigger words: "write", "dictate", "type".
    3A. structural_delete — They want to delete a line (e.g., "delete line 2", "remove line 2", "erase line 3", "delete second line"). Use this if the input contains a delete/remove verb and a line number.
    3B. structural_replace — They want to replace a line with something else (e.g., "replace line 2 with X").
    3C. structural_insert — They want to insert something at a specific line (e.g., "insert at line 3").
    3D. structural_change_type — They want to change the formatting of a line (e.g., "make line 3 a heading").

    If the input includes a number followed by a list of words (e.g., "three headings squash bobbins and racquetball"), interpret it as a request to generate that number of headings — one for each word — using each term in a title-like format.

    Do NOT generate full paragraphs unless explicitly asked.
    Respond only with a JSON list of actions like:
    [
    {{ "type": "heading", "content": "Squash", "level": 2 }},
    {{ "type": "heading", "content": "Bobbins", "level": 2 }},
    {{ "type": "heading", "content": "Racquetball", "level": 2 }}
    ]
    
    User Input: "{text}"

    Respond ONLY with one of the following strings:
    - generate_content
    - dictation
    - structural_delete
    - structural_replace
    - structural_insert
    - structural_change_type
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "dictation"  # fallback to safe default


def generate_actions(text: str, case: str, model_name: str = "gpt-3.5-turbo") -> List[Action]:
    current_state = get_current_doc()
    context_str = "\n".join([f"{b['type'].upper()}: {b['content']}" for b in current_state])

    # Shared preamble for document state
    base_prompt = f"## CURRENT DOCUMENT:\n{context_str}\n\n## USER INPUT:\n\"{text}\"\n\n"

    if case == "generate_content":
        prompt = base_prompt + """
        You must generate original document content from scratch based on the user input.

        If the input includes phrases like "under", "beneath", or "below", NEVER generate a heading. You must assume the heading already exists and only add bullets or paragraphs beneath it.

        Do not repeat or re-add existing headings from the document. Always target the nearest preceding heading or use the target_heading field if specified.

        All generated content must use sentence case. Do not use title case or lowercase for headings, bullets, or paragraphs. Capitalise only the first word of each sentence or proper nouns.

        Return a JSON array of actions (headings, paragraphs, bullets, etc.).
        If a heading is mentioned, set `target_heading`.

        Example output:
        [
            { "type": "heading", "content": "Morning Plan", "level": 2 },
            { "type": "bullet", "content": "Brush teeth", "target_heading": "Morning Plan" }
        ]
        """
    elif case == "generate_headings":
        prompt = base_prompt + """
        The user wants you to generate N headings, one for each word they mentioned.
        Do not write paragraphs or explanations.
        Return a JSON array like:
        [
            { "type": "heading", "content": "Squash", "level": 2 },
            { "type": "heading", "content": "Bobbins", "level": 2 },
            { "type": "heading", "content": "Racquetball", "level": 2 }
        ]
        """
    elif case == "dictation":
        stripped = re.sub(r"^\s*write\s+", "", text, flags=re.IGNORECASE).strip()
        return [Action(type="paragraph", content=stripped)]
    else:
        prompt = base_prompt + f"""
        You must parse structural editing instructions and return a list of JSON actions.

        Supported delete formats:
        - "delete lines 3 to 6"
        - "delete lines 2 and 5"
        Only include lines that exist (the document has {len(current_state)} lines).
        Ignore invalid line numbers or formats.

        CASE RULES:
        - structural_delete → multiple: [{{ "operation": "delete", "target_line": X }}, ...]
        - structural_replace → one: [{{ "operation": "replace", "target_line": 2, "type": "paragraph", "content": "New content here" }}]
        - structural_insert → one: [{{ "operation": "insert", "target_line": 3, "type": "bullet", "content": "New item" }}]
        - structural_change_type → one: [{{ "operation": "change_type", "target_line": 2, "type": "heading" }}]

        User Case: {case}
        """

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.0
        )
        raw = response.choices[0].message.content.strip()
        parsed = json.loads(raw)
        print("RAW OPENAI RESPONSE:", raw)
        if isinstance(parsed, dict):
            # unwrap nested key if GPT returns a dict (like {"structural_delete": [...]})
            parsed = list(parsed.values())[0]
        return [Action(**a) for a in parsed]
    except Exception as e:
        return []

def parse_text_to_actions(text: str, model_name: str = "gpt-3.5-turbo") -> List[Action]:
    case = classify_instruction(text, model_name=model_name)
    print("CLASSIFIED AS:", case)  # <-- Add this
    return generate_actions(text, case, model_name=model_name)