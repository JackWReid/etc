import pytest
from unittest.mock import patch
from main import (
    score_hand, reveal_card, deal_card, deal_hand, discard_card,
    format_card, format_card_simple, get_ascii_card_lines,
    all_cards_revealed, reveal_all_cards, deck, discard_pile,
    SUITS
)


class TestGolfScoring:
    def test_matching_cards_in_column_score_zero(self):
        """Test that matching cards in a column score 0"""
        hand = [
            [("♠︎", "7", True), ("♠︎", "A", True), ("♠︎", "2", True)],
            [("♦︎", "7", True), ("♦︎", "K", True), ("♦︎", "8", True)]
        ]
        expected_score = 7
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_matching_twos_still_score_negative_two(self):
        """Test that matching 2s still score -2 each (exception to column rule)"""
        hand = [
            [("♠︎", "2", True), ("♠︎", "A", True), ("♠︎", "2", True)],
            [("♦︎", "2", True), ("♦︎", "K", True), ("♦︎", "8", True)]
        ]
        expected_score = 3
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_face_cards_scoring(self):
        """Test that Kings score 0, but Jacks and Queens score 10"""
        hand = [
            [("♠︎", "K", True), ("♠︎", "Q", True), ("♠︎", "J", True)],
            [("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "8", True)]
        ]
        # Column 1: K,A (0+1=1)
        # Column 2: Q,2 (10+(-2)=8) 
        # Column 3: J,8 (10+8=18)
        # Total: 1+8+18=27
        expected_score = 27
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_kings_score_zero(self):
        """Test that Kings specifically score 0"""
        hand = [
            [("♠︎", "K", True), ("♠︎", "A", True), ("♠︎", "2", True)],
            [("♦︎", "K", True), ("♦︎", "3", True), ("♦︎", "4", True)]
        ]
        # Column 1: K,K (matching, so 0)
        # Column 2: A,3 (1+3=4)
        # Column 3: 2,4 (-2+4=2)
        # Total: 0+4+2=6
        expected_score = 6
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_jacks_and_queens_score_ten(self):
        """Test that Jacks and Queens score 10"""
        hand = [
            [("♠︎", "J", True), ("♠︎", "Q", True), ("♠︎", "5", True)],
            [("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "J", True)]
        ]
        # Column 1: J,A (10+1=11)
        # Column 2: Q,2 (10+(-2)=8)
        # Column 3: 5,J (5+10=15)
        # Total: 11+8+15=34
        expected_score = 34
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_aces_score_one(self):
        """Test that Aces score 1"""
        hand = [
            [("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True)],
            [("♦︎", "K", True), ("♦︎", "A", True), ("♦︎", "4", True)]
        ]
        # Column 1: A,K (1+0=1)
        # Column 2: 2,A (matching, but 2s are exception) (-2+1=-1)
        # Column 3: 3,4 (3+4=7)
        # Total: 1+(-1)+7=7
        expected_score = 7
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_numbered_cards_score_face_value(self):
        """Test that numbered cards score their face value"""
        hand = [
            [("♠︎", "5", True), ("♠︎", "6", True), ("♠︎", "7", True)],
            [("♦︎", "8", True), ("♦︎", "9", True), ("♦︎", "10", True)]
        ]
        # Column 1: 5,8 (5+8=13)
        # Column 2: 6,9 (6+9=15)
        # Column 3: 7,10 (7+10=17)
        # Total: 13+15+17=45
        expected_score = 45
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_covered_cards_are_scored(self):
        """Test that covered cards are scored the same as uncovered cards"""
        hand = [
            [("♠︎", "7", False), ("♠︎", "A", True), ("♠︎", "2", True)],
            [("♦︎", "7", False), ("♦︎", "K", True), ("♦︎", "8", True)]
        ]
        # Column 1: 7,7 (matching, so 0)
        # Column 2: A,K (1+0=1)
        # Column 3: 2,8 (-2+8=6)
        # Total: 0+1+6=7
        expected_score = 7
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_covered_cards_scored_individually(self):
        """Test that covered cards are scored individually when they don't match"""
        hand = [
            [("♠︎", "7", False), ("♠︎", "A", False), ("♠︎", "2", False)],
            [("♦︎", "8", False), ("♦︎", "K", False), ("♦︎", "8", False)]
        ]
        # Column 1: 7,8 (7+8=15)
        # Column 2: A,K (1+0=1)
        # Column 3: 2,8 (-2+8=6)
        # Total: 15+1+6=22
        expected_score = 22
        actual_score = score_hand(hand)
        assert actual_score == expected_score

    def test_reveal_card_function(self):
        """Test that reveal_card function properly reveals cards"""
        hand = [
            [("♠︎", "7", False), ("♠︎", "A", False), ("♠︎", "2", False)],
            [("♦︎", "8", False), ("♦︎", "K", False), ("♦︎", "8", False)]
        ]
        
        # Initially all cards should be covered
        assert not hand[0][0][2]  # covered
        assert not hand[1][1][2]  # covered
        
        # Reveal two cards
        reveal_card(hand, 0, 0)
        reveal_card(hand, 1, 1)
        
        # Check that the revealed cards are now open
        assert hand[0][0][2]   # open
        assert hand[1][1][2]   # open
        
        # Check that other cards remain covered
        assert not hand[0][1][2]  # still covered
        assert not hand[0][2][2]  # still covered
        assert not hand[1][0][2]  # still covered
        assert not hand[1][2][2]  # still covered 


class TestCardDeckOperations:
    def setup_method(self):
        """Reset deck and discard pile before each test"""
        global deck, discard_pile
        # Reset to a fresh deck
        deck.clear()
        deck.extend([
            ("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True),
            ("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True)
        ])
        discard_pile.clear()
    
    def test_deal_card_removes_from_deck(self):
        """Test that dealing a card removes it from the deck"""
        initial_count = len(deck)
        card = deal_card()
        assert len(deck) == initial_count - 1
        assert card not in deck
    
    def test_deal_card_returns_tuple(self):
        """Test that deal_card returns a properly formatted card tuple"""
        card = deal_card()
        assert isinstance(card, tuple)
        assert len(card) == 3
        suit, rank, revealed = card
        assert suit in SUITS
        assert isinstance(rank, str)
        assert isinstance(revealed, bool)
    
    def test_deal_card_empty_deck_raises_error(self):
        """Test that dealing from empty deck raises ValueError"""
        deck.clear()
        with pytest.raises(ValueError, match="No cards left in deck"):
            deal_card()
    
    def test_discard_card_adds_to_pile(self):
        """Test that discarding a card adds it to the discard pile"""
        card = ("♠︎", "A", True)
        initial_count = len(discard_pile)
        discard_card(card)
        assert len(discard_pile) == initial_count + 1
        assert discard_pile[-1] == card
    
    def test_deal_hand_creates_correct_structure(self):
        """Test that deal_hand creates a 2x3 grid of cards"""
        hand = deal_hand()
        assert len(hand) == 2  # 2 rows
        assert len(hand[0]) == 3  # 3 columns
        assert len(hand[1]) == 3  # 3 columns
    
    def test_deal_hand_cards_initially_covered(self):
        """Test that all cards in a dealt hand are initially covered"""
        hand = deal_hand()
        for row in hand:
            for card in row:
                suit, rank, revealed = card
                assert not revealed  # Initially covered
    
    def test_deal_hand_reduces_deck(self):
        """Test that dealing a hand reduces deck by 6 cards"""
        initial_count = len(deck)
        deal_hand()
        assert len(deck) == initial_count - 6


class TestCardFormatting:
    def test_format_card_revealed(self):
        """Test formatting of revealed cards"""
        card = ("♠︎", "A", True)
        formatted = format_card(card)
        assert "♠︎A" in formatted
        assert "white" in formatted  # Check color markup
    
    def test_format_card_covered(self):
        """Test formatting of covered cards"""
        card = ("♠︎", "A", False)
        formatted = format_card(card)
        assert "X" in formatted
        assert "white on black" in formatted
    
    def test_format_card_ten_special_case(self):
        """Test formatting of 10 cards (different width)"""
        card = ("♠︎", "10", True)
        formatted = format_card(card)
        assert "♠︎10" in formatted
    
    def test_format_card_simple_revealed(self):
        """Test simple formatting without markup"""
        card = ("♠︎", "A", True)
        formatted = format_card_simple(card)
        assert formatted == "♠︎A"
    
    def test_format_card_simple_covered(self):
        """Test simple formatting of covered cards"""
        card = ("♠︎", "A", False)
        formatted = format_card_simple(card)
        assert formatted == "X"
    
    def test_get_ascii_card_lines_covered(self):
        """Test ASCII art for covered cards"""
        card = ("♠︎", "A", False)
        lines = get_ascii_card_lines(card)
        assert len(lines) == 7
        assert "███████" in lines[1]  # Check for covered pattern
    
    def test_get_ascii_card_lines_revealed(self):
        """Test ASCII art for revealed cards"""
        card = ("♠︎", "A", True)
        lines = get_ascii_card_lines(card)
        assert len(lines) == 7
        assert "♠︎" in lines[3]  # Suit in middle
        assert "A" in lines[1]  # Rank in corner


class TestGameLogic:
    def test_all_cards_revealed_true(self):
        """Test all_cards_revealed when all cards are revealed"""
        hand = [
            [("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True)],
            [("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True)]
        ]
        assert all_cards_revealed(hand)
    
    def test_all_cards_revealed_false(self):
        """Test all_cards_revealed when some cards are covered"""
        hand = [
            [("♠︎", "A", True), ("♠︎", "2", False), ("♠︎", "3", True)],
            [("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True)]
        ]
        assert not all_cards_revealed(hand)
    
    def test_all_cards_revealed_empty_hand(self):
        """Test all_cards_revealed with empty hand"""
        hand = []
        assert all_cards_revealed(hand)
    
    def test_reveal_all_cards(self):
        """Test that reveal_all_cards reveals all covered cards"""
        hand = [
            [("♠︎", "A", False), ("♠︎", "2", True), ("♠︎", "3", False)],
            [("♦︎", "A", False), ("♦︎", "2", False), ("♦︎", "3", True)]
        ]
        reveal_all_cards(hand)
        assert all_cards_revealed(hand)
        # Check specific cards
        assert hand[0][0][2]
        assert hand[0][2][2]
        assert hand[1][0][2]
        assert hand[1][1][2]


class TestEdgeCases:
    def test_score_hand_empty_hand(self):
        """Test scoring an empty hand"""
        hand = []
        score = score_hand(hand)
        assert score == 0
    
    def test_score_hand_single_row(self):
        """Test scoring a hand with only one row"""
        hand = [[("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True)]]
        score = score_hand(hand)
        # With single row, each column has only one card, so they "match" themselves
        # A matches (scores 0), 2 is exception (scores -2), 3 matches (scores 0) 
        # Total: 0 + (-2) + 0 = -2
        assert score == -2
    
    def test_reveal_card_already_revealed(self):
        """Test revealing a card that's already revealed"""
        hand = [[("♠︎", "A", True)]]
        original_card = hand[0][0]
        reveal_card(hand, 0, 0)
        assert hand[0][0] == original_card  # Should remain the same
    
    def test_card_suits_coverage(self):
        """Test that all suits are properly defined"""
        expected_suits = {"♠︎", "♥︎", "♦︎", "♣︎"}
        assert set(SUITS.keys()) == expected_suits
        # All suits should have colors defined
        for suit, color in SUITS.items():
            assert color in ["white", "red"]
    
    def test_score_matching_columns_with_all_ranks(self):
        """Test scoring with matching columns for all possible ranks"""
        # Test matching Aces
        hand = [[("♠︎", "A", True)], [("♦︎", "A", True)]]
        assert score_hand(hand) == 0  # Matching column
        
        # Test matching Kings
        hand = [[("♠︎", "K", True)], [("♦︎", "K", True)]]
        assert score_hand(hand) == 0  # Matching column
        
        # Test matching numbered cards
        hand = [[("♠︎", "5", True)], [("♦︎", "5", True)]]
        assert score_hand(hand) == 0  # Matching column


class TestScoringSuite:
    """Comprehensive scoring tests"""
    
    def test_complex_scoring_scenario(self):
        """Test a complex real-game scoring scenario"""
        hand = [
            [("♠︎", "A", True), ("♥︎", "Q", True), ("♦︎", "2", True)],
            [("♣︎", "A", True), ("♠︎", "J", True), ("♥︎", "K", True)]
        ]
        # Column 1: A,A (matching) = 0
        # Column 2: Q,J (10+10) = 20
        # Column 3: 2,K (-2+0) = -2
        # Total: 0 + 20 + (-2) = 18
        assert score_hand(hand) == 18
    
    def test_all_twos_in_column(self):
        """Test that a column of all 2s still scores each 2 individually"""
        hand = [
            [("♠︎", "2", True)],
            [("♦︎", "2", True)]
        ]
        # 2s are exception to matching rule
        assert score_hand(hand) == -4  # -2 + -2
    
    def test_perfect_score_scenario(self):
        """Test a scenario that could result in a very low score"""
        hand = [
            [("♠︎", "K", True), ("♠︎", "K", True), ("♠︎", "2", True)],
            [("♦︎", "K", True), ("♦︎", "K", True), ("♦︎", "2", True)]
        ]
        # Column 1: K,K (matching) = 0
        # Column 2: K,K (matching) = 0  
        # Column 3: 2,2 (both score -2) = -4
        # Total: 0 + 0 + (-4) = -4
        assert score_hand(hand) == -4


class TestPlayerInteraction:
    """Tests for player interaction functions with mocking"""
    
    @patch('main.Prompt.ask')
    def test_get_player_info_two_players(self, mock_prompt):
        """Test getting player information for 2 players"""
        from main import get_player_info
        
        # Mock the prompts: first for number of players, then player names
        mock_prompt.side_effect = ["2", "Alice", "Bob"]
        
        players = get_player_info()
        assert len(players) == 2
        assert players == ["Alice", "Bob"]
    
    @patch('main.Prompt.ask')
    def test_get_player_info_with_empty_name_retry(self, mock_prompt):
        """Test that empty names are rejected and retried"""
        from main import get_player_info
        
        # Mock sequence: 2 players, empty name (retry), then valid names
        mock_prompt.side_effect = ["2", "", "Alice", "Bob"]
        
        players = get_player_info()
        assert players == ["Alice", "Bob"]
    
    @patch('main.Prompt.ask')
    def test_get_valid_position(self, mock_prompt):
        """Test getting valid position from user input"""
        from main import get_valid_position
        
        hand = [
            [("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True)],
            [("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True)]
        ]
        position_map = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}
        
        mock_prompt.return_value = "3"
        row, col = get_valid_position(hand, position_map)
        assert (row, col) == (0, 2)
    
    @patch('main.Prompt.ask')
    def test_get_valid_position_invalid_then_valid(self, mock_prompt):
        """Test that invalid positions are rejected and retried"""
        from main import get_valid_position
        
        hand = [
            [("♠︎", "A", True), ("♠︎", "2", True)],
            [("♦︎", "A", True), ("♦︎", "2", True)]
        ]
        position_map = {1: (0, 0), 2: (0, 1), 3: (1, 0), 4: (1, 1)}
        
        # Mock sequence: invalid number, then valid
        mock_prompt.side_effect = ["7", "2"]
        
        row, col = get_valid_position(hand, position_map)
        assert (row, col) == (0, 1)


class TestIntegrationTests:
    """Integration tests for full game flow"""
    
    def setup_method(self):
        """Reset global state before each test"""
        global deck, discard_pile
        deck.clear()
        # Add minimal deck for testing
        deck.extend([
            ("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True),
            ("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True),
            ("♣︎", "K", True), ("♣︎", "Q", True), ("♣︎", "J", True),
            ("♥︎", "K", True), ("♥︎", "Q", True), ("♥︎", "J", True)
        ])
        discard_pile.clear()
    
    def test_deal_multiple_hands(self):
        """Test dealing hands for multiple players"""
        num_players = 2
        player_hands = []
        
        for _ in range(num_players):
            player_hands.append(deal_hand())
        
        # Check structure
        assert len(player_hands) == 2
        for hand in player_hands:
            assert len(hand) == 2  # 2 rows
            assert len(hand[0]) == 3  # 3 columns each
            assert len(hand[1]) == 3
    
    def test_game_end_condition(self):
        """Test that game ends when all cards are revealed"""
        hand = [
            [("♠︎", "A", False), ("♠︎", "2", False), ("♠︎", "3", False)],
            [("♦︎", "A", False), ("♦︎", "2", False), ("♦︎", "3", True)]
        ]
        
        # Game should not end with covered cards
        assert not all_cards_revealed(hand)
        
        # Reveal all cards
        reveal_all_cards(hand)
        
        # Game should end now
        assert all_cards_revealed(hand)
    
    def test_card_replacement_workflow(self):
        """Test the complete card replacement workflow"""
        hand = [
            [("♠︎", "A", False), ("♠︎", "2", False), ("♠︎", "3", False)],
            [("♦︎", "A", False), ("♦︎", "2", False), ("♦︎", "3", False)]
        ]
        
        # Simulate drawing a card
        drawn_card = ("♥︎", "K", True)
        
        # Replace a card at position (0, 1)
        old_card = hand[0][1]
        hand[0][1] = (drawn_card[0], drawn_card[1], True)  # Place new card face up
        
        # Verify replacement
        assert hand[0][1] == ("♥︎", "K", True)
        assert hand[0][1][2]  # Should be revealed
        
        # Add old card to discard pile
        discard_card(old_card)
        assert discard_pile[-1] == old_card
    
    def test_scoring_integration_with_real_game_state(self):
        """Test scoring with a realistic game state"""
        # Simulate end-game state where some cards are revealed
        hand = [
            [("♠︎", "A", True), ("♥︎", "Q", True), ("♦︎", "2", True)],
            [("♣︎", "K", True), ("♠︎", "J", True), ("♥︎", "K", True)]
        ]
        
        score = score_hand(hand)
        
        # Verify expected score calculation:
        # Column 1: A,K (1+0=1)
        # Column 2: Q,J (10+10=20)
        # Column 3: 2,K (-2+0=-2)
        # Total: 1+20+(-2)=19
        assert score == 19
    
    @patch('main.console.clear')
    @patch('main.console.print')
    def test_display_functions_dont_crash(self, mock_print, mock_clear):
        """Test that display functions can be called without crashing"""
        from main import (
            display_hand, display_hand_ascii_grid, display_discard_pile,
            display_other_players_compact, print_title
        )
        
        hand = [
            [("♠︎", "A", True), ("♥︎", "Q", False), ("♦︎", "2", True)],
            [("♣︎", "K", False), ("♠︎", "J", True), ("♥︎", "K", True)]
        ]
        
        players = ["Alice", "Bob"]
        player_hands = [hand, hand]  # Same hand for simplicity
        
        # These should not raise exceptions
        print_title()
        display_hand(hand, "Alice")
        display_hand_ascii_grid(hand, "Alice")
        display_discard_pile()
        display_other_players_compact(players, player_hands, 0)
        
        # Verify that console functions were called
        assert mock_print.called


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_deal_from_empty_deck_error_message(self):
        """Test specific error message when dealing from empty deck"""
        global deck
        deck.clear()
        
        with pytest.raises(ValueError) as exc_info:
            deal_card()
        
        assert "No cards left in deck" in str(exc_info.value)
    
    def test_robust_card_tuple_handling(self):
        """Test that functions handle card tuples robustly"""
        # Test with different but valid card formats
        valid_card = ("♠︎", "A", True)
        covered_card = ("♦︎", "10", False)
        
        # These should not raise exceptions
        format_card(valid_card)
        format_card(covered_card)
        format_card_simple(valid_card)
        format_card_simple(covered_card)
        get_ascii_card_lines(valid_card)
        get_ascii_card_lines(covered_card)
    
    def test_position_map_edge_cases(self):
        """Test position mapping with different hand sizes"""
        from main import display_placement_grid
        
        # Test with normal hand
        hand = [
            [("♠︎", "A", True), ("♥︎", "Q", True)],
            [("♣︎", "K", True), ("♠︎", "J", True)]
        ]
        
        with patch('main.console.print'):
            position_map = display_placement_grid(hand)
        
        # Should have correct number of positions
        assert len(position_map) == 4  # 2x2 grid
        assert all(isinstance(pos, int) for pos in position_map.keys())
        assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in position_map.values())