# Golf

A Python implementation of the card game Golf.

## Rules

## Deal
A single 52-card deck is recommended for a two or three player game. If played with four or more players, a double-deck of 104 cards is ideal.

Each player is dealt six face-down cards from a shuffled deck. The remaining cards are placed face down to form the stockpile, from which the top card is taken and turned up to start the discard pile beside it. Players arrange their cards in two rows of three in front of them and turn any two of these cards face up. This arrangement is maintained throughout the game; players always have six cards in front of them. 

The objective is for players to reduce the value of the cards in front of them by swapping them for lesser value cards. After the end of each round, players calculate the score of their respective six cards.

## Play
Beginning with the dealer's left, players take turns drawing a single card from either the stockpile or discard pile. The drawn card may either be swapped for one of that player's six cards or, if drawn from the stockpile, discarded. If the card is swapped for one of the face-down cards, the card swapped in remains face up. If the card drawn is discarded, the player can then choose to flip a card face up.

The round ends when a player has six face-up cards (sometimes the other players are given one final turn following this), after which scoring happens as follows:
- Each Ace scores one point
- Each Two scores minus two points
- Each numeral card from 3 to 10 scores its face value
- Each Jack or Queen scores 10 points
- Each King scores zero points
- A pair of equal-ranked cards in the same column scores zero points for that column regardless of the rank of those cards

During play, it is not legal to return a card drawn from the discard pile without playing it. When a player picks up the top card of the discard pile, that card must be played by swapping it with one of that player's cards.

A full game is typically nine hands, also known as "holes", after which the player with the fewest points total is designated the winner. A longer game can be played to eighteen hands.