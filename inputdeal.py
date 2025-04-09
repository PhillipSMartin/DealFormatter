# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
The input method of this module asks for input from the user and returns a dictionary with deal info in the following format:
    {
        "Board number": <integer>
        "Dealer": <"North", "South", "East", or "West" >
        "Auction": <a list of calls eg. ['1C', 'D', 'R', '3N', 'P', 'P', 'P'] >
        "Seats": [ 
                    { "Player": <player's name>',
                      "Direction":  <"North", "South", "East", or "West" >
                        "Hand": 
                            { "Spades": <string, using AKQJT for honors>
                              "Hearts": <string, using AKQJT for honors>
                              "Diamonds": <string, using AKQJT for honors>
                              "Clubs": <string, using AKQJT for honors>
                            }
                    },
                    ...
                ]
      }
"""
import globals

from typing import List

globals.initialize()

def inputHands() -> List[dict]:
    seats = []
    for direction in globals.directions:
        name = input(f"{direction} name (or leave blank): ")
        hand = input(f"{direction} hand (comma delimited, 'T' for 10): ")
        seats.append({ "Direction": direction})
        if len(name) > 0:
            seats[-1]["Player"] = name
        if len(hand) > 0:
            hand = (hand.upper()).replace('X', 'x')
            seats[-1]["Hand"] = globals.build_hand(hand.upper().split(','))
    return seats

def inputAuction() -> List[str]:
    return(input("Enter auction (S, H, D, C, N, P, D, R), comma delimited: ").upper().split(','))


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
        
    return deal;
        
    
        
        
        
    
    