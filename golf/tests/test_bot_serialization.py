from bot_serialization import serialize_card, serialize_hand, serialize_game_state

# Test data
face_down = ("♠︎", "7", False)
face_up = ("♥︎", "2", True)

hand = [
    [face_down, face_up, ("♣︎", "K", False)],
    [("♦︎", "A", True), ("♠︎", "Q", False), ("♥︎", "10", True)]
]

opponent_hand = [
    [("♠︎", "3", True), ("♣︎", "5", False), ("♦︎", "J", False)],
    [("♥︎", "2", True), ("♣︎", "K", True), ("♠︎", "7", False)]
]

def test_serialize_card():
    assert serialize_card(face_down) == {"value": None, "face_up": False}
    assert serialize_card(face_up) == {"value": "2", "face_up": True}

def test_serialize_hand():
    result = serialize_hand(hand)
    assert result == [
        [
            {"value": None, "face_up": False},
            {"value": "2", "face_up": True},
            {"value": None, "face_up": False}
        ],
        [
            {"value": "A", "face_up": True},
            {"value": None, "face_up": False},
            {"value": "10", "face_up": True}
        ]
    ]

def test_serialize_game_state():
    discard_pile = [("♣︎", "5", True), ("♦︎", "A", True)]
    seen_cards = ["2", "A", "K", "5"]
    player_hands = [hand, opponent_hand]
    player_names = ["Bot", "Opponent"]
    bot_index = 0
    state = serialize_game_state(
        player_hands=player_hands,
        player_names=player_names,
        bot_index=bot_index,
        discard_pile=discard_pile,
        seen_cards=seen_cards,
        current_turn="Bot"
    )
    # Check players
    assert state["players"][0]["name"] == "Bot"
    assert state["players"][1]["name"] == "Opponent"
    assert state["players"][0]["hand"] == serialize_hand(hand)
    assert state["players"][1]["hand"] == serialize_hand(opponent_hand)
    # Bot hand
    assert state["bot_hand"] == serialize_hand(hand)
    # Seen cards (should not include cards in bot's hand)
    bot_hand_ranks = set(card[1] for row in hand for card in row)
    for c in state["seen_cards"]:
        assert c not in bot_hand_ranks
    # Discard pile (top card first)
    assert state["discard_pile"] == ["♦︎A", "♣︎5"]
    # Current turn
    assert state["current_turn"] == "Bot" 