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
    return ''.join(sorted(cards, key=lambda card: RANKS.find(card) if card in RANKS else len(RANKS)))

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

def remainingHand(seats: List[dict]) -> dict:
    # Given three complete 13-card hands, return the hand holding the 13 unused cards.
    # Prints the reason and returns None if the three hands aren't complete and distinct.
    if len(seats) != 3 or any("Hand" not in seat for seat in seats):
        print("Can't fill in the last hand: the other three hands must all be entered")
        return None
    used = {suit: set() for suit in globals.suits}
    for seat in seats:
        hand = seat["Hand"]
        count = sum(len(hand[suit]) for suit in globals.suits)
        if count != 13:
            print(f"Can't fill in the last hand: {seat['Direction']} has {count} cards")
            return None
        for suit in globals.suits:
            for card in hand[suit]:
                if card not in RANKS:
                    print(f"Can't fill in the last hand: {seat['Direction']} has unknown card '{card}' in {suit}")
                    return None
                if card in used[suit]:
                    print(f"Can't fill in the last hand: {card} of {suit} appears twice")
                    return None
                used[suit].add(card)
    return {suit: ''.join(r for r in RANKS if r not in used[suit]) for suit in globals.suits}

def handError(suit_list: List[str], earlier: List[dict]) -> str:
    # Return a description of what's wrong with a newly entered hand, or None if it's valid.
    # A hand may have fewer than 13 cards, but not more, and no card may repeat one already entered.
    if len(suit_list) != 4:
        return f"Expected 4 suits separated by commas, got {len(suit_list)}"
    count = sum(len(cards) for cards in suit_list)
    if count > 13:
        return f"Hand has {count} cards"
    for suit, cards in zip(globals.suits, suit_list):
        for card in cards:
            if card not in RANKS and card != 'x':
                return f"Unknown card '{card}' in {suit}"
        for card in set(cards) - {'x'}:
            if cards.count(card) > 1:
                return f"{card} of {suit} entered twice"
            for seat in earlier:
                if card in seat["Hand"][suit]:
                    return f"{card} of {suit} is already in {seat['Direction']}'s hand"
        spots_left = len([spot for spot in SPOTS if all(spot not in seat["Hand"][suit] for seat in earlier) and spot not in cards])
        xs = cards.count('x') + sum(seat["Hand"][suit].count('x') for seat in earlier)
        if xs > spots_left:
            return f"Too many x's in {suit}: only {spots_left} unused spot cards left"
    return None

def inputHands() -> List[dict]:
    seats = []
    for direction in globals.directions:
        name = input(f"{direction} name (or leave blank): ")
        seats.append({ "Direction": direction})
        if len(name) > 0:
            seats[-1]["Player"] = name
        while True:
            hand = input(f"{direction} hand (comma delimited, 'T' or '10' for 10): ")
            if len(hand) == 0:
                break
            suit_list = hand.upper().replace(' ', '').replace('10', 'T').replace('X', 'x').split(',')
            error = handError(suit_list, [seat for seat in seats if "Hand" in seat])
            if error is None:
                seats[-1]["Hand"] = globals.build_hand(suit_list)
                break
            print(f"Error: {error}. Please reenter {direction}'s hand.")

    fillSpots([seat["Hand"] for seat in seats if "Hand" in seat])

    if "Hand" not in seats[-1]:
        rest = remainingHand(seats[:-1])
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
        
    
        
        
        
    
    