import globals
import random

from typing import List

"""
The input method of this module asks for input from the user and returns a dictionary with deal info in the following format:
        {
                "Board number": <integer>,
                "Dealer": <"North", "South", "East", or "West" >,
                "Auction": <a list of calls eg. ['1C', 'D', 'R', '3N', 'P', 'P', 'P'] >,
                "Seats": [ 
                                        { "Player": <player's name>,
                                            "Direction":  <"North", "South", "East", or "West" >,
                                                "Hand": 
                                                        { "Spades": <string, using AKQJT for honors>,
                                                            "Hearts": <string, using AKQJT for honors>,
                                                            "Diamonds": <string, using AKQJT for honors>,
                                                            "Clubs": <string, using AKQJT for honors>
                                                        }
                                        },
                                        ...
                                ],
                "Play": <a list of cards played, e.g. ["CK", "C8"]>
            }
"""

globals.initialize()

RANKS = "AKQJT98765432"
SPOTS = "98765432"

def sortSuit(cards: str) -> str:
    return ''.join(sorted(cards, key=RANKS.index))

def fillSpots(hands: List[dict]):
    # Replace each 'x' with a random 2-9 not held by any hand, then sort each suit A to 2.
    # Explicit cards in all hands are reserved first so a random spot never collides with one.
    for suit in globals.suits:
        used = set(card for hand in hands for card in hand[suit] if card != 'x')
        for hand in hands:
            cards = [card for card in hand[suit] if card != 'x']
            for _ in range(hand[suit].count('x')):
                available = [spot for spot in SPOTS if spot not in used]
                if not available:
                    print(f"No unused spot cards left in {suit}; keeping 'x'")
                    cards.append('x')
                    continue
                spot = random.choice(available)
                used.add(spot)
                cards.append(spot)
            hand[suit] = sortSuit(''.join(card for card in cards if card != 'x')) + 'x' * cards.count('x')

def remainingHand(hands: List[dict]) -> dict:
    # Given three complete 13-card hands, return the hand holding the 13 unused cards,
    # or None if the three hands aren't complete and distinct.
    if len(hands) != 3:
        return None
    used = {suit: set() for suit in globals.suits}
    for hand in hands:
        if sum(len(hand[suit]) for suit in globals.suits) != 13:
            return None
        for suit in globals.suits:
            for card in hand[suit]:
                if card not in RANKS or card in used[suit]:
                    return None
                used[suit].add(card)
    return {suit: ''.join(r for r in RANKS if r not in used[suit]) for suit in globals.suits}

def inputHands() -> List[dict]:
    seats = []
    for direction in globals.directions:
        name = input(f"{direction} name (or leave blank): ")
        hand = input(f"{direction} hand (comma delimited, 'T' for 10): ")
        seats.append({ "Direction": direction})
        if len(name) > 0:
            seats[-1]["Player"] = name
        if len(hand) > 0:
            hand = hand.upper().replace(' ', '').replace('X', 'x')
            seats[-1]["Hand"] = globals.build_hand(hand.split(','))

    fillSpots([seat["Hand"] for seat in seats if "Hand" in seat])

    if "Hand" not in seats[-1]:
        rest = remainingHand([seat["Hand"] for seat in seats[:-1] if "Hand" in seat])
        if rest is not None:
            seats[-1]["Hand"] = rest
            print(f"{seats[-1]['Direction']} hand: " + ','.join(rest[suit] for suit in globals.suits))
    return seats

def inputAuction() -> List[str]:
    return(input("Enter auction (S, H, D, C, N, P, D, R), comma delimited: ").upper().split(','))


def inputPlay() -> list:
    play_input = input("Enter play as a comma-separated list of cards (e.g. CK,C8): ").strip()
    if len(play_input) > 0:
        return [card.strip().upper() for card in play_input.split(',') if card.strip()]
    return []

def inputDeal() -> dict:
    deal = {}

    boardNumber = input("Board number (or blank): ")
    if len(boardNumber) > 0:
        deal["Board number"] = int(boardNumber)

    dealer = input("Dealer (N, S, E, W): ")
    if len(dealer) > 0:
        deal["Dealer"] = globals.seats[dealer.upper()]

    hands = inputHands()
    if len(hands) > 0:
        deal["Seats"] = hands

    auction = inputAuction()
    if len(auction) > 0:
        deal["Auction"] = auction

    play = inputPlay()
    if len(play) > 0:
        deal["Play"] = play

    return deal
        
    
        
        
        
    
    