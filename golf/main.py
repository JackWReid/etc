import random
import signal
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.align import Align
from rich import box
from typing import List, Tuple, Dict
# Add imports for bot integration
from bot_serialization import serialize_game_state
from bot_api import call_golf_bot
import time

console = Console()

# Track all revealed cards by rank
seen_cards = []

def signal_handler(sig, frame):
    """Handle Ctrl-C gracefully"""
    console.print("\n\n[yellow]Game interrupted by user. Thanks for playing![/yellow]")
    sys.exit(0)

# Set up signal handler for Ctrl-C
signal.signal(signal.SIGINT, signal_handler)

# Card suits with colors
SUITS = {
    "♠︎": "white",  # Changed from black to white for better visibility
    "♥︎": "red", 
    "♦︎": "red",
    "♣︎": "white"   # Changed from black to white for better visibility
}

deck = [("♠︎", "A", True), ("♠︎", "2", True), ("♠︎", "3", True), ("♠︎", "4", True), ("♠︎", "5", True), ("♠︎", "6", True), ("♠︎", "7", True), ("♠︎", "8", True), ("♠︎", "9", True), ("♠︎", "10", True), ("♠︎", "J", True), ("♠︎", "Q", True), ("♠︎", "K", True), ("♦︎", "A", True), ("♦︎", "2", True), ("♦︎", "3", True), ("♦︎", "4", True), ("♦︎", "5", True), ("♦︎", "6", True), ("♦︎", "7", True), ("♦︎", "8", True), ("♦︎", "9", True), ("♦︎", "10", True), ("♦︎", "J", True), ("♦︎", "Q", True), ("♦︎", "K", True), ("♣︎", "A", True), ("♣︎", "2", True), ("♣︎", "3", True), ("♣︎", "4", True), ("♣︎", "5", True), ("♣︎", "6", True), ("♣︎", "7", True), ("♣︎", "8", True), ("♣︎", "9", True), ("♣︎", "10", True), ("♣︎", "J", True), ("♣︎", "Q", True), ("♣︎", "K", True), ("♥︎", "A", True), ("♥︎", "2", True), ("♥︎", "3", True), ("♥︎", "4", True), ("♥︎", "5", True), ("♥︎", "6", True), ("♥︎", "7", True), ("♥︎", "8", True), ("♥︎", "9", True), ("♥︎", "10", True), ("♥︎", "J", True), ("♥︎", "Q", True), ("♥︎", "K", True)]

discard_pile = []

def print_title():
    """Display the game title with beautiful formatting"""
    title = Text("⛳ GOLF ⛳", style="bold green", justify="center")
    subtitle = Text("The Card Game", style="italic blue", justify="center")
    console.print(Panel(Align.center(title + "\n" + subtitle), box=box.DOUBLE))

def deal_card() -> Tuple[str, str, bool]:
    """Deal a single card from the deck and remove it"""
    if not deck:
        raise ValueError("No cards left in deck")
    card = deck.pop()
    return card

def discard_card(card: Tuple[str, str, bool]):
    """Discard a card to the discard pile and track it as seen"""
    discard_pile.append(card)
    if card[2] and card[1] not in seen_cards:
        seen_cards.append(card[1])

def deal_hand() -> List[List[Tuple[str, str, bool]]]:
    """Deal a hand of 3 cards from a shuffled deck, initially covered"""
    cards = []
    for _ in range(2):
        row = []
        for _ in range(3):
            card = deal_card()
            # Make card covered initially (False = covered)
            suit, rank, _ = card
            row.append((suit, rank, False))
        cards.append(row)
    return cards

def format_card(card: Tuple[str, str, bool]) -> str:
    """Format a card with proper colors"""
    suit, rank, revealed = card
    if not revealed:
        return "[white on black] X [/white on black]"
    
    color = SUITS.get(suit, "white")
    # Ensure consistent width for all cards
    if rank == "10":
        return f"[{color}]{suit}{rank}[/{color}]"
    else:
        return f"[{color}]{suit}{rank}[/{color}]"

def format_card_simple(card: Tuple[str, str, bool]) -> str:
    """Format a card without rich markup for consistent width calculation"""
    suit, rank, revealed = card
    if not revealed:
        return "X"
    
    if rank == "10":
        return f"{suit}{rank}"
    else:
        return f"{suit}{rank}"

def get_ascii_card_lines(card: Tuple[str, str, bool]) -> List[str]:
    """Get ASCII art lines for a card without rich markup"""
    suit, rank, revealed = card
    
    if not revealed:
        # Return face-down card
        return [
            "┌─────────┐",
            "│ ███████ │",
            "│ ███████ │",
            "│ ███████ │",
            "│ ███████ │",
            "│ ███████ │",
            "└─────────┘"
        ]
    
    # Handle different rank lengths
    if rank == "10":
        rank_left = "10"
        rank_right = "10"
    else:
        rank_left = f"{rank} "
        rank_right = f" {rank}"
    
    # Create the ASCII art card
    return [
        "┌─────────┐",
        f"│ {rank_left:<7} │",
        "│         │",
        f"│    {suit}    │",
        "│         │",
        f"│ {rank_right:>7} │",
        "└─────────┘"
    ]

def display_ascii_card(card: Tuple[str, str, bool], title: str = "Card"):
    """Display a card as ASCII art"""
    suit, rank, _ = card
    color = SUITS.get(suit, "white")
    
    # Get the card lines
    card_lines = get_ascii_card_lines(card)
    
    # Apply colors to the card
    colored_card = []
    for line in card_lines:
        # Color the suit and rank
        colored_line = line.replace(suit, f"[{color}]{suit}[/{color}]")
        colored_line = colored_line.replace(rank, f"[{color}]{rank}[/{color}]")
        colored_card.append(colored_line)
    
    # Display the card in a panel
    card_text = "\n".join(colored_card)
    console.print(Panel(card_text, title=title, border_style=color))

def display_hand_ascii_grid(hand: List[List[Tuple[str, str, bool]]], player_name: str):
    """Display a player's hand as a grid of ASCII cards"""
    console.print(f"\n[bold blue]{player_name}'s Hand:[/bold blue]")
    
    # Get all card lines
    all_card_lines = []
    for row in hand:
        row_cards = []
        for card in row:
            card_lines = get_ascii_card_lines(card)
            row_cards.append(card_lines)
        all_card_lines.append(row_cards)
    
    # Display the grid
    for row_idx, row_cards in enumerate(all_card_lines):
        # Display each line of the cards in this row
        for line_idx in range(7):  # Each card has 7 lines
            row_line = ""
            for card_lines in row_cards:
                line = card_lines[line_idx]
                # Apply colors
                suit, rank, revealed = hand[row_idx][all_card_lines[row_idx].index(card_lines)]
                if not revealed:
                    row_line += line + "  "
                else:
                    color = SUITS.get(suit, "white")
                    colored_line = line.replace(suit, f"[{color}]{suit}[/{color}]")
                    colored_line = colored_line.replace(rank, f"[{color}]{rank}[/{color}]")
                    row_line += colored_line + "  "
            console.print(row_line)
        console.print()  # Add space between rows

def display_hand(hand: List[List[Tuple[str, str, bool]]], player_name: str):
    """Display a player's hand in a beautiful table"""
    table = Table(title=f"{player_name}'s Hand", box=box.ROUNDED)
    table.add_column("", justify="center", style="cyan")  # Row labels
    table.add_column("Column 0", justify="center", style="cyan")
    table.add_column("Column 1", justify="center", style="cyan") 
    table.add_column("Column 2", justify="center", style="cyan")
    
    for row_idx, row in enumerate(hand):
        formatted_row = [format_card(card) for card in row]
        table.add_row(f"Row {row_idx}", *formatted_row)
    
    console.print(table)

def display_discard_pile():
    """Display the discard pile"""
    if discard_pile:
        top_card = discard_pile[-1]
        # Always show the top card as revealed
        suit, rank, _ = top_card
        revealed_card = (suit, rank, True)
        console.print("\n[bold]Top of Discard Pile:[/bold]")
        
        # Display just the ASCII card without panel border
        card_lines = get_ascii_card_lines(revealed_card)
        color = SUITS.get(suit, "white")
        
        for line in card_lines:
            # Apply colors to the card
            colored_line = line.replace(suit, f"[{color}]{suit}[/{color}]")
            colored_line = colored_line.replace(rank, f"[{color}]{rank}[/{color}]")
            console.print(colored_line)
    else:
        console.print("\n[bold]Top of Discard Pile:[/bold]")
        console.print("[yellow]Empty[/yellow]")

def display_other_players_compact(players: List[str], player_hands: List[List[List[Tuple[str, str, bool]]]], current_player: int):
    """Display other players' hands in a compact format"""
    if len(players) <= 1:
        return
    
    console.print("\n[bold cyan]Other Players:[/bold cyan]")
    
    # Create a compact representation for each other player
    for i, player in enumerate(players):
        if i == current_player:
            continue
            
        hand = player_hands[i]
        
        # Format all cards in one row
        card_parts = []
        
        for row in range(2):  # 2 rows
            for col in range(3):  # 3 columns
                card = hand[row][col]
                suit, rank, revealed = card
                if revealed:
                    color = SUITS.get(suit, "white")
                    # All revealed cards should be 3 characters wide (suit + rank + padding)
                    if rank == "10":
                        card_parts.append(f"[{color}]{suit}{rank}[/{color}]")
                    else:
                        card_parts.append(f"[{color}]{suit}{rank}[/{color}] ")
                else:
                    # Face-down cards should also be 3 characters wide
                    card_parts.append(" X ")
        
        # Create aligned display
        player_name = f"[dim]{player}:[/dim]"
        row_display = f"{player_name} {'  '.join(card_parts)}"
        
        console.print(row_display)
        console.print()  # Add space between players

def reveal_card(hand: List[List[Tuple[str, str, bool]]], row: int, col: int):
    """Reveal a card by setting it to open (True) and track it as seen"""
    card = hand[row][col]
    hand[row][col] = (card[0], card[1], True)
    if card[2] is False and card[1] not in seen_cards:
        seen_cards.append(card[1])

def draw_card(hand: List[List[Tuple[str, str, bool]]]) -> Tuple[str, str, bool]:
    """Draw a card from the deck"""
    if not deck:
        raise ValueError("No cards left in deck")
    card = deck.pop()
    return card

def display_placement_grid(hand: List[List[Tuple[str, str, bool]]]) -> Dict[int, Tuple[int, int]]:
    """Display a visual grid for card placement with numbered positions"""
    console.print("\n[bold cyan]Card Placement Grid:[/bold cyan]")
    
    # Get all card lines with position numbers
    all_card_lines = []
    position_map = {}
    position_number = 1
    
    for row_idx, row in enumerate(hand):
        row_cards = []
        for col_idx, card in enumerate(row):
            card_lines = get_ascii_card_lines(card)
            
            # Add position number to the top of the card with proper spacing
            card_lines[0] = f"[yellow]{position_number:2}[/yellow] {card_lines[0]}"
            # Add equivalent spacing to other lines to maintain alignment
            for i in range(1, len(card_lines)):
                card_lines[i] = "   " + card_lines[i]
            position_map[position_number] = (row_idx, col_idx)
            position_number += 1
            
            row_cards.append(card_lines)
        all_card_lines.append(row_cards)
    
    # Display the grid
    for row_idx, row_cards in enumerate(all_card_lines):
        # Display each line of the cards in this row
        for line_idx in range(7):  # Each card has 7 lines
            row_line = ""
            for card_lines in row_cards:
                line = card_lines[line_idx]
                # Apply colors
                suit, rank, revealed = hand[row_idx][all_card_lines[row_idx].index(card_lines)]
                if not revealed:
                    row_line += line + "  "
                else:
                    color = SUITS.get(suit, "white")
                    colored_line = line.replace(suit, f"[{color}]{suit}[/{color}]")
                    colored_line = colored_line.replace(rank, f"[{color}]{rank}[/{color}]")
                    row_line += colored_line + "  "
            console.print(row_line)
        console.print()  # Add space between rows
    
    return position_map

def get_valid_position(hand: List[List[Tuple[str, str, bool]]], position_map: Dict[int, Tuple[int, int]]) -> Tuple[int, int]:
    """Get valid position using numbered selection"""
    available_positions = list(position_map.keys())
    console.print(f"\n[bold]Choose any position:[/bold] {', '.join(map(str, available_positions))}")
    
    while True:
        try:
            choice = int(Prompt.ask(f"Choose position number [cyan]({min(available_positions)}-{max(available_positions)})[/cyan]"))
            if choice in position_map:
                return position_map[choice]
            else:
                console.print(f"[red]Please choose a number between {min(available_positions)} and {max(available_positions)}[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")

def all_cards_revealed(hand: List[List[Tuple[str, str, bool]]]) -> bool:
    """Check if all cards in hand are revealed"""
    for row in hand:
        for _, _, revealed in row:
            if not revealed:
                return False
    return True

def reveal_all_cards(hand: List[List[Tuple[str, str, bool]]]):
    """Reveal all cards in a hand and track them as seen"""
    for row in range(len(hand)):
        for col in range(len(hand[0])):
            if not hand[row][col][2]:  # If card is not revealed
                reveal_card(hand, row, col)

def take_turn(hand: List[List[Tuple[str, str, bool]]], player_name: str, players: List[str], player_hands: List[List[List[Tuple[str, str, bool]]]], current_player: int, recent_moves: List[Dict] = None) -> bool:
    """Take an interactive turn, returns True if game should end"""
    console.clear()
    print_title()
    # Move the recent moves summary here, after the title
    if recent_moves:
        console.print("[bold magenta]Recent moves:[/bold magenta]")
        for move in recent_moves:
            player = move.get('player', '?')
            action = move.get('action', '')
            if player == 'Bot':
                reason_lines = []
                if 'draw_move' in move and move['draw_move'].get('reason'):
                    reason_lines.append(f"Draw reason: {move['draw_move']['reason']}")
                if 'action_move' in move and move['action_move'].get('reason'):
                    reason_lines.append(f"Action reason: {move['action_move']['reason']}")
                reason_str = ("\n    ".join(reason_lines)) if reason_lines else ''
                console.print(f"[cyan]{player}:[/cyan] {action}\n    {reason_str}")
            else:
                console.print(f"[yellow]{player}:[/yellow] {action}")

    console.print(f"\n[bold blue]{player_name}'s Turn[/bold blue]")
    console.print("=" * 50)
    
    display_discard_pile()
    display_other_players_compact(players, player_hands, current_player)
    display_hand_ascii_grid(hand, player_name)
    
    # Choose draw source
    drew_from_deck = False
    while True:
        choice = Prompt.ask("Draw from [green](d)[/green]eck or [yellow](p)[/yellow]ile?", choices=["d", "p", "deck", "pile"])
        if choice in ['d', 'deck']:
            if not deck:
                console.print("[yellow]Deck is empty, drawing from discard pile[/yellow]")
                if not discard_pile:
                    console.print("[red]No cards available![/red]")
                    return False
                card = discard_pile.pop()
            else:
                card = draw_card(hand)
                drew_from_deck = True
            break
        elif choice in ['p', 'pile']:
            if not discard_pile:
                console.print("[yellow]Discard pile is empty, must draw from deck[/yellow]")
                continue
            card = discard_pile.pop()
            break
    
    console.print("\n[bold]You drew:[/bold]")
    
    # Display just the ASCII card without panel border
    card_lines = get_ascii_card_lines(card)
    suit, rank = card[0], card[1]
    color = SUITS.get(suit, "white")
    
    for line in card_lines:
        # Apply colors to the card
        colored_line = line.replace(suit, f"[{color}]{suit}[/{color}]")
        colored_line = colored_line.replace(rank, f"[{color}]{rank}[/{color}]")
        console.print(colored_line)
    
    # If drew from deck, offer option to discard immediately
    if drew_from_deck:
        keep = Confirm.ask("Keep this card?", default=True)
        if not keep:
            discard_card(card)
            suit, rank = card[0], card[1]
            color = SUITS.get(suit, "white")
            console.print(f"Discarded [{color}]{suit}{rank}[/{color}]")
            return False  # Game continues, no cards were revealed
    
    # Choose position to replace
    console.print("\n[bold]Choose which card to replace:[/bold]")
    position_map = display_placement_grid(hand)
    row, col = get_valid_position(hand, position_map)
    
    # Reveal and swap
    old_card = hand[row][col]
    suit, rank = card[0], card[1]  # Get suit and rank from the drawn card
    color = SUITS.get(suit, "white")  # Get color for the suit
    hand[row][col] = (suit, rank, True)  # Place new card face up
    discard_card(old_card)
    
    # In take_turn (human turn):
    # After revealing and swapping cards, print what was revealed and discarded
    suit, rank = old_card[0], old_card[1]
    color = SUITS.get(suit, "white")
    console.print(f"[yellow]You revealed and discarded [{color}]{suit}{rank}[/{color}] from position ({row},{col})[/yellow]")
    display_hand_ascii_grid(hand, player_name)
    
    return all_cards_revealed(hand)

def score_hand(hand: List[List[Tuple[str, str, bool]]]) -> int:
    total_score = 0
    
    # Handle empty hand
    if not hand or not hand[0]:
        return 0

    # Check each column for matching cards
    for col in range(len(hand[0])):
        cards_in_column = [hand[row][col] for row in range(len(hand))]
        
        # Extract ranks from the tuples for comparison
        ranks_in_column = [card[1] for card in cards_in_column]
        
        # If all cards in column match and they're not 2s, score 0 for this column
        if len(set(ranks_in_column)) == 1 and ranks_in_column[0] != "2":
            continue
        
        # Otherwise, score each card individually
        for card in cards_in_column:
            rank = card[1]  # Extract rank from tuple
            if rank == "2":
                total_score += -2
            elif rank == "A":
                total_score += 1
            elif rank == "K":
                total_score += 0
            elif rank == "Q":
                total_score += 10
            elif rank == "J":
                total_score += 10
            else:
                # For numbered cards, use their face value
                total_score += int(rank)
    
    return total_score

def get_player_info() -> List[str]:
    """Get number of players and their names"""
    while True:
        try:
            num_players = int(Prompt.ask("Enter number of players", choices=["2", "3", "4"]))
            break
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    players = []
    for i in range(num_players):
        while True:
            name = Prompt.ask(f"Enter name for Player {i+1}")
            if name.strip():
                players.append(name.strip())
                break
            else:
                console.print("[red]Name cannot be empty[/red]")
    
    return players

def display_final_scores(players: List[str], player_hands: List[List[List[Tuple[str, str, bool]]]]):
    """Display final scores in a beautiful table"""
    console.clear()
    print_title()
    
    console.print("\n" + "="*50)
    
    # Create score table
    score_table = Table(title="🏆 FINAL SCORES 🏆", box=box.DOUBLE)
    score_table.add_column("Player", style="cyan", justify="center")
    score_table.add_column("Score", style="magenta", justify="center")
    score_table.add_column("Hand", style="green", justify="left")
    
    scores = []
    for i, player in enumerate(players):
        score = score_hand(player_hands[i])
        scores.append((player, score))
        
        # Format hand for display
        hand_text = ""
        for row in player_hands[i]:
            for card in row:
                hand_text += format_card(card) + " "
            hand_text += "\n"
        
        score_table.add_row(player, str(score), hand_text.strip())
    
    console.print(score_table)
    
    # Find winner(s)
    min_score = min(score for _, score in scores)
    winners = [name for name, score in scores if score == min_score]
    
    if len(winners) == 1:
        winner_text = Text(f"🏆 {winners[0]} wins with a score of {min_score}! 🏆", style="bold green")
        console.print(Panel(Align.center(winner_text), box=box.DOUBLE))
    else:
        winner_text = Text(f"🏆 It's a tie! Winners: {', '.join(winners)} with a score of {min_score}! 🏆", style="bold yellow")
        console.print(Panel(Align.center(winner_text), box=box.DOUBLE))

def main():
    console.clear()
    print_title()

    # Game mode selection
    mode = Prompt.ask(
        "Select game mode (1) Human vs Human, (2) Human vs Bot",
        choices=["1", "2"],
        default="1",
        show_choices=False,
        show_default=False
    )
    is_vs_bot = (mode == "2")

    if is_vs_bot:
        players = ["You", "Bot"]
        num_players = 2
    else:
        players = get_player_info()
        num_players = len(players)

    random.shuffle(deck)

    # Deal hands for all players
    player_hands = []
    for _ in range(num_players):
        player_hands.append(deal_hand())

    # Initial reveals (same pattern for all players)
    for i in range(num_players):
        reveal_card(player_hands[i], 0, 0)
        reveal_card(player_hands[i], 1, 2)

    # Show initial hands
    console.clear()
    print_title()
    console.print("\n[bold]Initial Hands:[/bold]")
    for i, player in enumerate(players):
        display_hand_ascii_grid(player_hands[i], player)

    Prompt.ask("\n[bold]Press Enter to start the game[/bold]")

    turn_count = 0
    max_turns = 20 * num_players  # Prevent infinite games
    endgame_triggered = False
    final_turn_taken = False
    current_player = 0
    # Collect game history for post-game review
    game_history = []

    while not endgame_triggered and turn_count < max_turns:
        if is_vs_bot and players[current_player] == "Bot":
            # --- Bot Turn Logic (Refactored: Two-Step) ---
            try:
                # Step 1: Ask bot which pile to draw from
                game_state = serialize_game_state(
                    player_hands=player_hands,
                    player_names=players,
                    bot_index=1,  # Bot is always index 1 in vs-bot mode
                    discard_pile=discard_pile,
                    seen_cards=seen_cards,
                    current_turn=players[current_player]
                )
                # Prompt bot ONLY for draw source
                draw_prompt = "You must choose where to draw from. Respond ONLY with a JSON object: {\"action\": \"draw\", \"source\": \"stock\" or \"discard\", \"reason\": \"...\"}"
                draw_move = call_golf_bot({**game_state, "phase": "draw_choice"})
                if not draw_move or 'action' not in draw_move or 'source' not in draw_move:
                    raise RuntimeError(f"Bot did not return a valid draw move. Move: {draw_move}")
                source = draw_move.get("source")
                # Draw the card
                if source == "stock":
                    if not deck:
                        card = discard_pile.pop() if discard_pile else None
                    else:
                        card = deck.pop()
                    card = (card[0], card[1], True)
                elif source == "discard":
                    if not discard_pile:
                        card = deck.pop() if deck else None
                    else:
                        card = discard_pile.pop()
                    card = (card[0], card[1], True)
                else:
                    raise RuntimeError(f"Bot chose invalid draw source: {source}")
                # Step 2: Ask bot what to do with the drawn card
                # Prepare a new game state with the drawn card revealed
                partial_state = {**game_state, "phase": "post_draw", "drawn_card": {"suit": card[0], "rank": card[1]}, "draw_source": source}
                if source == "stock":
                    # Bot can choose to replace or discard
                    action_prompt = "You drew from the stock. Respond ONLY with a JSON object: {\"action\": \"replace\", \"position\": [row, col], \"reason\": \"...\"} or {\"action\": \"discard\", \"reason\": \"...\"}"
                else:
                    # Bot must replace
                    action_prompt = "You drew from the discard pile. Respond ONLY with a JSON object: {\"action\": \"replace\", \"position\": [row, col], \"reason\": \"...\"}"
                action_move = call_golf_bot(partial_state)
                if not action_move or 'action' not in action_move:
                    raise RuntimeError(f"Bot did not return a valid post-draw move. Move: {action_move}")
                # Handle both direct format and followup format from bot
                followup_action = None
                if action_move['action'] == 'replace' and isinstance(action_move.get('position'), list):
                    # Direct format: {"action": "replace", "position": [0,1]}
                    followup_action = action_move
                elif 'followup' in action_move and action_move['followup'].get('action') == 'replace':
                    # Bot's followup format: {"action": "draw", "followup": {"action": "replace", "position": [0,1]}}
                    followup_action = action_move['followup']
                
                if followup_action and isinstance(followup_action.get('position'), list):
                    row, col = followup_action['position']
                    old_card = player_hands[1][row][col]
                    player_hands[1][row][col] = (card[0], card[1], True)
                    old_card_revealed = (old_card[0], old_card[1], True)
                    discard_card(old_card_revealed)
                    game_history.append({
                        "turn": turn_count,
                        "player": "Bot",
                        "game_state": game_state,
                        "draw_move": draw_move,
                        "action_move": action_move,
                        "action": f"Replaced card at ({row},{col}) with {card[0]}{card[1]}"
                    })
                    if 'draw_move' in locals() and draw_move:
                        console.print(f"[bold cyan]Bot chose to draw from: {draw_move.get('source', '?')}[/bold cyan]")
                        if 'reason' in draw_move:
                            console.print(f"[cyan]Reason: {draw_move['reason']}[/cyan]")
                    if 'action_move' in locals() and action_move:
                        if action_move.get('action') == 'replace' and 'position' in action_move:
                            pos = action_move['position']
                            console.print(f"[bold cyan]Bot replaced card at {tuple(pos)} with {card[0]}{card[1]}[/bold cyan]")
                        elif action_move.get('action') == 'discard':
                            console.print(f"[bold cyan]Bot discarded drawn card {card[0]}{card[1]}[/bold cyan]")
                        if 'reason' in action_move:
                            console.print(f"[cyan]Reason: {action_move['reason']}[/cyan]")
                elif (action_move['action'] == 'discard' and source == 'stock') or \
                     ('followup' in action_move and action_move['followup'].get('action') == 'discard' and source == 'stock'):
                    revealed_card = (card[0], card[1], True)
                    discard_card(revealed_card)
                    game_history.append({
                        "turn": turn_count,
                        "player": "Bot",
                        "game_state": game_state,
                        "draw_move": draw_move,
                        "action_move": action_move,
                        "action": f"Discarded drawn card {card[0]}{card[1]}"
                    })
                else:
                    # Fallback: replace a random card
                    unrevealed = [(r, c) for r in range(2) for c in range(3) if not player_hands[1][r][c][2]]
                    if not unrevealed:
                        unrevealed = [(r, c) for r in range(2) for c in range(3)]
                    row, col = random.choice(unrevealed)
                    old_card = player_hands[1][row][col]
                    player_hands[1][row][col] = (card[0], card[1], True)
                    old_card_revealed = (old_card[0], old_card[1], True)
                    discard_card(old_card_revealed)
                    game_history.append({
                        "turn": turn_count,
                        "player": "Bot",
                        "game_state": game_state,
                        "draw_move": draw_move,
                        "action_move": action_move,
                        "action": f"Fallback: Replaced card at ({row},{col}) with {card[0]}{card[1]}"
                    })
                # After bot's move, check if all cards are revealed
                if all_cards_revealed(player_hands[1]):
                    console.print("\n[bold green]Bot wins by uncovering all cards![/bold green]")
                    endgame_triggered = True
                    # Give other players one final turn
                    if not final_turn_taken:
                        console.print("\n[bold yellow]Other players get one final turn![/bold yellow]")
                        for i in range(num_players):
                            if i != current_player:
                                if is_vs_bot and players[i] == "Bot":
                                    # --- Bot Final Turn Logic (Refactored: Two-Step) ---
                                    try:
                                        # Step 1: Ask bot which pile to draw from
                                        game_state = serialize_game_state(
                                            player_hands=player_hands,
                                            player_names=players,
                                            bot_index=1,  # Bot is always index 1 in vs-bot mode
                                            discard_pile=discard_pile,
                                            seen_cards=seen_cards,
                                            current_turn=players[i],
                                            phase="draw_choice"
                                        )
                                        draw_move = call_golf_bot(game_state)
                                        if not draw_move or 'action' not in draw_move or 'source' not in draw_move:
                                            raise RuntimeError(f"Bot did not return a valid draw move. Move: {draw_move}")
                                        source = draw_move.get("source")
                                        # Draw the card
                                        if source == "stock":
                                            if not deck:
                                                card = discard_pile.pop() if discard_pile else None
                                            else:
                                                card = deck.pop()
                                            card = (card[0], card[1], True)
                                        elif source == "discard":
                                            if not discard_pile:
                                                card = deck.pop() if deck else None
                                            else:
                                                card = discard_pile.pop()
                                            card = (card[0], card[1], True)
                                        else:
                                            raise RuntimeError(f"Bot chose invalid draw source: {source}")
                                        # Step 2: Ask bot what to do with the drawn card
                                        partial_state = serialize_game_state(
                                            player_hands=player_hands,
                                            player_names=players,
                                            bot_index=1,
                                            discard_pile=discard_pile,
                                            seen_cards=seen_cards,
                                            current_turn=players[i],
                                            phase="post_draw",
                                            drawn_card={"suit": card[0], "rank": card[1]}
                                        )
                                        if source == "stock":
                                            # Bot can choose to replace or discard
                                            action_move = call_golf_bot(partial_state)
                                        else:
                                            # Bot must replace
                                            action_move = call_golf_bot(partial_state)
                                        if not action_move or 'action' not in action_move:
                                            raise RuntimeError(f"Bot did not return a valid post-draw move. Move: {action_move}")
                                        if action_move['action'] == 'replace' and isinstance(action_move.get('position'), list):
                                            row, col = action_move['position']
                                            old_card = player_hands[1][row][col]
                                            player_hands[1][row][col] = (card[0], card[1], True)
                                            old_card_revealed = (old_card[0], old_card[1], True)
                                            discard_card(old_card_revealed)
                                            console.print(f"Bot replaced card at ({row},{col}) with {card[0]}{card[1]}")
                                        elif action_move['action'] == 'discard' and source == 'stock':
                                            revealed_card = (card[0], card[1], True)
                                            discard_card(revealed_card)
                                            console.print(f"Bot discarded drawn card {card[0]}{card[1]}")
                                        else:
                                            # Fallback: replace a random card
                                            unrevealed = [(r, c) for r in range(2) for c in range(3) if not player_hands[1][r][c][2]]
                                            if not unrevealed:
                                                unrevealed = [(r, c) for r in range(2) for c in range(3)]
                                            row, col = random.choice(unrevealed)
                                            old_card = player_hands[1][row][col]
                                            player_hands[1][row][col] = (card[0], card[1], True)
                                            old_card_revealed = (old_card[0], old_card[1], True)
                                            discard_card(old_card_revealed)
                                            console.print(f"Bot (fallback) replaced card at ({row},{col}) with {card[0]}{card[1]}")
                                    except Exception as e:
                                        console.print(f"[red]Bot error during final turn: {e}[/red] Skipping bot's final turn.")
                                else:
                                    take_turn(player_hands[i], players[i], players, player_hands, i)
                        final_turn_taken = True
                    break
            except Exception as e:
                console.print(f"[red]Bot error: {e}[/red] Skipping bot's turn.")
                game_history.append({
                    "turn": turn_count,
                    "player": "Bot",
                    "game_state": game_state if 'game_state' in locals() else None,
                    "draw_move": draw_move if 'draw_move' in locals() else None,
                    "action_move": action_move if 'action_move' in locals() else None,
                    "error": str(e)
                })
                time.sleep(1.5)
                turn_count += 1
                current_player = (current_player + 1) % num_players
                continue
        else:
            # Collect all moves since the last human turn
            recent_moves = []
            for move in game_history:
                if move.get('player') == players[current_player] and move.get('action') == 'Human turn':
                    break # Found the last human turn
                recent_moves.append(move)

            if take_turn(player_hands[current_player], players[current_player], players, player_hands, current_player, recent_moves):
                console.print(f"\n[bold green]{players[current_player]} wins by uncovering all cards![/bold green]")
                endgame_triggered = True
                # Give other players one final turn
                if not final_turn_taken:
                    console.print("\n[bold yellow]Other players get one final turn![/bold yellow]")
                    for i in range(num_players):
                        if i != current_player:
                            if is_vs_bot and players[i] == "Bot":
                                # --- Bot Final Turn Logic (Refactored: Two-Step) ---
                                try:
                                    # Step 1: Ask bot which pile to draw from
                                    game_state = serialize_game_state(
                                        player_hands=player_hands,
                                        player_names=players,
                                        bot_index=1,  # Bot is always index 1 in vs-bot mode
                                        discard_pile=discard_pile,
                                        seen_cards=seen_cards,
                                        current_turn=players[i],
                                        phase="draw_choice"
                                    )
                                    draw_move = call_golf_bot(game_state)
                                    if not draw_move or 'action' not in draw_move or 'source' not in draw_move:
                                        raise RuntimeError(f"Bot did not return a valid draw move. Move: {draw_move}")
                                    source = draw_move.get("source")
                                    # Draw the card
                                    if source == "stock":
                                        if not deck:
                                            card = discard_pile.pop() if discard_pile else None
                                        else:
                                            card = deck.pop()
                                        card = (card[0], card[1], True)
                                    elif source == "discard":
                                        if not discard_pile:
                                            card = deck.pop() if deck else None
                                        else:
                                            card = discard_pile.pop()
                                        card = (card[0], card[1], True)
                                    else:
                                        raise RuntimeError(f"Bot chose invalid draw source: {source}")
                                    # Step 2: Ask bot what to do with the drawn card
                                    partial_state = serialize_game_state(
                                        player_hands=player_hands,
                                        player_names=players,
                                        bot_index=1,
                                        discard_pile=discard_pile,
                                        seen_cards=seen_cards,
                                        current_turn=players[i],
                                        phase="post_draw",
                                        drawn_card={"suit": card[0], "rank": card[1]}
                                    )
                                    if source == "stock":
                                        # Bot can choose to replace or discard
                                        action_move = call_golf_bot(partial_state)
                                    else:
                                        # Bot must replace
                                        action_move = call_golf_bot(partial_state)
                                    if not action_move or 'action' not in action_move:
                                        raise RuntimeError(f"Bot did not return a valid post-draw move. Move: {action_move}")
                                    if action_move['action'] == 'replace' and isinstance(action_move.get('position'), list):
                                        row, col = action_move['position']
                                        old_card = player_hands[1][row][col]
                                        player_hands[1][row][col] = (card[0], card[1], True)
                                        old_card_revealed = (old_card[0], old_card[1], True)
                                        discard_card(old_card_revealed)
                                        console.print(f"Bot replaced card at ({row},{col}) with {card[0]}{card[1]}")
                                    elif action_move['action'] == 'discard' and source == 'stock':
                                        revealed_card = (card[0], card[1], True)
                                        discard_card(revealed_card)
                                        console.print(f"Bot discarded drawn card {card[0]}{card[1]}")
                                    else:
                                        # Fallback: replace a random card
                                        unrevealed = [(r, c) for r in range(2) for c in range(3) if not player_hands[1][r][c][2]]
                                        if not unrevealed:
                                            unrevealed = [(r, c) for r in range(2) for c in range(3)]
                                        row, col = random.choice(unrevealed)
                                        old_card = player_hands[1][row][col]
                                        player_hands[1][row][col] = (card[0], card[1], True)
                                        old_card_revealed = (old_card[0], old_card[1], True)
                                        discard_card(old_card_revealed)
                                        console.print(f"Bot (fallback) replaced card at ({row},{col}) with {card[0]}{card[1]}")
                                except Exception as e:
                                    console.print(f"[red]Bot error during final turn: {e}[/red] Skipping bot's final turn.")
                            else:
                                take_turn(player_hands[i], players[i], players, player_hands, i)
                        final_turn_taken = True
                    break
            # Save to game history (human turn)
            game_history.append({
                "turn": turn_count,
                "player": players[current_player],
                "action": "Human turn"
            })
        turn_count += 1
        current_player = (current_player + 1) % num_players

    # Reveal all cards at the end
    console.print("\n[bold yellow]Revealing all cards...[/bold yellow]")
    for i, player in enumerate(players):
        reveal_all_cards(player_hands[i])
        console.print(f"\n[bold]{player}'s Final Hand:[/bold]")
        display_hand_ascii_grid(player_hands[i], player)

    # Display final scores
    display_final_scores(players, player_hands)

    # Post-game review: dump game history
    import json
    import os
    from datetime import datetime
    # Write to file
    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    games_dir = "games"
    os.makedirs(games_dir, exist_ok=True)
    history_path = os.path.join(games_dir, f"{timestamp}.json")
    with open(history_path, "w") as f:
        json.dump(game_history, f, indent=2)
    console.print(f"[green]Game history written to {history_path}[/green]")

if __name__ == "__main__":
    main()