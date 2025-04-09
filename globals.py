# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:20:52 2021

@author: sarab
"""
from typing import List

global suits
global directions
global seats

def initialize():
    global suits
    global directions
    global seats
    suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
    # West is first so it will appear first in the auction
    directions = ['West', 'North', 'East', 'South']
    seats = { 'S': 'South', 
        'W': 'West',
        'N': 'North',
        'E': 'East'
        }
    

def build_hand(suit_list: List[str]) -> dict:
    # input ['96432', 'KQ9', 'T5', '73']
    # output {'Spades': '96432', 'Hearts': 'KQ94', 'Diamonds': 'T5', 'Clubs': '73'}
    assert len(suit_list) == 4, "Invalid input to buildHand method"
    return dict(zip(suits, suit_list))
