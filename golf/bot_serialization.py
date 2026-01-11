from typing import List, Tuple, Dict, Any, Optional

# Card: (suit, rank, revealed)
def serialize_card(card: Tuple[str, str, bool]) -> Dict[str, Any]:
    suit, rank, revealed = card
    value = None if not revealed else rank
    return {
        "value": value,  # e.g., "2", "K", "A", etc. or None if face-down
        "face_up": revealed
    }

def serialize_hand(hand: List[List[Tuple[str, str, bool]]]) -> List[List[Dict[str, Any]]]:
    return [[serialize_card(card) for card in row] for row in hand]

def serialize_game_state(
    player_hands: List[List[List[Tuple[str, str, bool]]]],
    player_names: List[str],
    bot_index: int,
    discard_pile: List[Tuple[str, str, bool]],
    seen_cards: Optional[List[str]] = None,
    current_turn: Optional[str] = None,
    phase: Optional[str] = None,
    drawn_card: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    # Serialize all players
    players = []
    for name, hand in zip(player_names, player_hands):
        players.append({
            "name": name,
            "hand": serialize_hand(hand)
        })
    # Bot's hand
    bot_hand = serialize_hand(player_hands[bot_index])
    # Seen cards (not in bot's hand)
    bot_hand_cards = set()
    for row in player_hands[bot_index]:
        for card in row:
            bot_hand_cards.add((card[0], card[1]))
    filtered_seen = [c for c in (seen_cards or []) if c not in [card[1] for card in bot_hand_cards]]
    # Discard pile as strings (top card first)
    discard_pile_serialized = [f"{suit}{rank}" for suit, rank, _ in reversed(discard_pile)]
    state = {
        "players": players,
        "bot_hand": bot_hand,
        "seen_cards": filtered_seen,
        "discard_pile": discard_pile_serialized,
        "current_turn": current_turn
    }
    if phase:
        state["phase"] = phase
    if drawn_card:
        state["drawn_card"] = drawn_card
    return state

def serialize_compact_game_state(
    player_hands: List[List[List[Tuple[str, str, bool]]]],
    player_names: List[str],
    bot_index: int,
    discard_pile: List[Tuple[str, str, bool]],
    seen_cards: Optional[List[str]] = None,
    current_turn: Optional[str] = None,
    scores: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """
    Produce a compact, information-dense summary of the game state for the bot.
    Each player's hand is shown as a grid of card strings (e.g., '♠︎K', 'X' for face-down).
    Includes player names, (optional) scores, and top of discard pile.
    """
    def card_str(card):
        suit, rank, revealed = card
        return f"{suit}{rank}" if revealed else "X"
    players = []
    for i, (name, hand) in enumerate(zip(player_names, player_hands)):
        hand_grid = [[card_str(card) for card in row] for row in hand]
        player_info = {
            "name": name,
            "hand": hand_grid
        }
        if scores and name in scores:
            player_info["score"] = scores[name]
        players.append(player_info)
    discard_top = f"{discard_pile[-1][0]}{discard_pile[-1][1]}" if discard_pile else None
    return {
        "players": players,
        "discard_top": discard_top,
        "current_turn": current_turn
    } 