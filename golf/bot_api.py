import os
import openai
import json
from typing import Dict, Any

def load_bot_strategy() -> str:
    """Load the bot strategy from the markdown file."""
    try:
        with open('bot_strategy.md', 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to basic strategy if file not found
        return """You are an AI playing Golf. Minimize your score. Pairs in columns score 0 points. 
        Cards 2,K,A are excellent. Cards 3,4 are good. Cards 5+ are poor. 
        Always consider pairing opportunities first."""

def call_golf_bot(game_state: Dict[str, Any], model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Calls the OpenAI API with the strategy prompt and game state, returns the bot's move as a dict.
    Accepts 'phase' and (optionally) 'drawn_card' in game_state.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")
    client = openai.OpenAI(api_key=api_key)

    phase = game_state.get("phase", "draw_choice")
    drawn_card = game_state.get("drawn_card")
    if phase == "draw_choice":
        user_prompt = f"Game state:\n```json\n{json.dumps(game_state, indent=2)}\n```\nYou must choose where to draw from. Respond ONLY with a JSON object: {{\"action\": \"draw\", \"source\": \"stock\" or \"discard\", \"reason\": \"...\"}}"
    elif phase == "post_draw":
        if drawn_card:
            user_prompt = f"Game state:\n```json\n{json.dumps(game_state, indent=2)}\n```\nYou have drawn a card. Respond ONLY with a JSON object: (see instructions in the system prompt for valid formats)"
        else:
            user_prompt = f"Game state:\n```json\n{json.dumps(game_state, indent=2)}\n```\nYou have drawn a card. Respond ONLY with a JSON object: (see instructions in the system prompt for valid formats)"
    else:
        user_prompt = f"Game state:\n```json\n{json.dumps(game_state, indent=2)}\n```\nRespond ONLY with a valid JSON object for your move."

    messages = [
        {"role": "system", "content": load_bot_strategy()},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(  # type: ignore[call-overload]
        model=model,
        messages=messages,
        temperature=0.2,
        max_tokens=256,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content
    try:
        move = json.loads(content)
    except Exception as e:
        raise RuntimeError(f"Bot response was not valid JSON: {content}") from e
    return move 