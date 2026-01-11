import bot_api
import json
from unittest.mock import patch, MagicMock

def example_game_state():
    return {
        "players": [
            {"name": "Bot", "hand": [
                [{"value": None, "face_up": False}, {"value": "2", "face_up": True}, {"value": None, "face_up": False}],
                [{"value": "A", "face_up": True}, {"value": None, "face_up": False}, {"value": "10", "face_up": True}]
            ]},
            {"name": "Opponent", "hand": [
                [{"value": "3", "face_up": True}, {"value": None, "face_up": False}, {"value": None, "face_up": False}],
                [{"value": "2", "face_up": True}, {"value": "K", "face_up": True}, {"value": None, "face_up": False}]
            ]}
        ],
        "bot_hand": [
            [{"value": None, "face_up": False}, {"value": "2", "face_up": True}, {"value": None, "face_up": False}],
            [{"value": "A", "face_up": True}, {"value": None, "face_up": False}, {"value": "10", "face_up": True}]
        ],
        "seen_cards": ["2", "A", "K"],
        "discard_pile": ["♦︎A", "♣︎5"],
        "current_turn": "Bot"
    }

def test_call_golf_bot_example():
    # Example expected bot response
    example_response = {
        "action": "draw",
        "source": "stock"
    }
    # Mock the OpenAI API call
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock(message=MagicMock(content=json.dumps(example_response)))]
        mock_client.chat.completions.create.return_value = mock_completion
        
        move = bot_api.call_golf_bot(example_game_state(), model="gpt-4o")
        assert move == example_response
        # Ensure the OpenAI client was called with the right model
        mock_client.chat.completions.create.assert_called()

# Example usage (not a test, but for documentation):
def example_usage():
    """
    Example of how to call the bot API in your game loop:
    
    from bot_api import call_golf_bot
    game_state = example_game_state()
    move = call_golf_bot(game_state)
    print("Bot move:", move)
    """
    pass 