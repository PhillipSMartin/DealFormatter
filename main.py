# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:33:59 2021

@author: sarab


"""
import argparse
import buildhtml
import inputdeal
import json
import parseurl
import globals
import os
import re
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Deal Formatter Tool', )
    parser.add_argument('input', help='html string, path to pbn file, * for console input, or ** for previous deal ')
    parser.add_argument('-n', '--north', action='store_true', help='print North hand')
    parser.add_argument('-e', '--east', action='store_true', help='print East hand')
    parser.add_argument('-s', '--south', action='store_true', help='print South hand')
    parser.add_argument('-w', '--west', action='store_true', help='print West hand')
    parser.add_argument('-a', '--auction', action='store_true', help='print auction')
    parser.add_argument('-r', '--rotate', type=int, help='number of seats to rotate clockwise')
    parser.add_argument('-p', '--played', type=int, help='number of cards played', default=0)
    parser.add_argument('-o', '--output', default='output', help='common prefix for json and html output files')
    parser.add_argument('-v', '--vertical', action='store_true', help='use vertical (vs horizontal) hand layout')
    parser.add_argument('-g', '--gray', action='store_true', help='gray out played cards rather than remove them')
    parser.add_argument('--name', default='', help='name of South player')
    parser.add_argument('-x', '--exclude', default='', help='suits to exclude (shdc, e.g. "shc")')
    return parser.parse_args(argv)


def main(args):
    globals.initialize()
    assert '.' not in args.output, "Output file name should be prefix only"

    # Build the switch string based on specified seat switches
    attr_map = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west', 'a': 'auction'}
    seat_switches = ''.join(c for c in 'nsewa' if getattr(args, attr_map[c], False))
    filename_base = args.output + ('-' + seat_switches if seat_switches else '')


    deal = {}

    # build deal
    if args.input == '**':
        save_file = open(args.output + ".json", "r")
        deal = json.load(save_file)
        save_file.close()
    else:
        save_file = open(args.output + ".json", "w")
        if args.input == '*':
            deal = inputdeal.inputDeal()
            json.dump(deal, save_file)
        elif re.match("http", args.input):
            deal = parseurl.parse(args.input)
            json.dump(deal, save_file)
        elif args.input.lower().endswith('.pbn') and os.path.exists(args.input):
            # Parse a PBN file and build deal structure
            with open(args.input, 'r') as pf:
                pbn_text = pf.read()

            deal = {}
            # Board number
            m = re.search(r'\[Board\s+"?(\d+)"?\]', pbn_text)
            if m:
                deal['Board number'] = int(m.group(1))

            # Deal tag: format like N:hand1 hand2 hand3 hand4
            m = re.search(r'\[Deal\s+"?([NESW]:[^"\]]+)"?\]', pbn_text)
            if m:
                deal_str = m.group(1).strip()
                first_dir = deal_str[0]
                hands_str = deal_str[2:].strip()
                hand_tokens = hands_str.split()
                # Ensure we have four hands
                if len(hand_tokens) >= 4:
                    globals.initialize()
                    # Map first hand to direction and proceed clockwise
                    clockwise = ['North', 'East', 'South', 'West']
                    start_dir = globals.seats.get(first_dir.upper(), 'North')
                    si = clockwise.index(start_dir)
                    directions_order = clockwise[si:] + clockwise[:si]
                    seats = []
                    for dir_name, hand_token in zip(directions_order, hand_tokens[:4]):
                        suits = hand_token.split('.')
                        # normalize ranks (uppercase, T for 10)
                        suits = [s.replace('10', 'T').upper() for s in suits]
                        seats.append({ 'Direction': dir_name, 'Hand': globals.build_hand(suits) })
                    deal['Seats'] = seats

            # Dealer tag (optional)
            m = re.search(r'\[Dealer\s+"?([NESW])"?\]', pbn_text)
            if m:
                deal['Dealer'] = globals.seats.get(m.group(1).upper(), '')

            # Attempt to extract auction lines between the [Auction] tag and the following blank line or '{}' block
            m = re.search(r'\[Auction[^\]]*\][\r\n]+([^\{\[]+)', pbn_text)
            if m:
                auction_block = m.group(1).strip()
                # Split on whitespace and normalize tokens (convert Pass to P etc.)
                tokens = [t.strip() for t in re.split(r'\s+', auction_block) if t.strip()]
                # Basic normalization: map Pass -> P, Double -> D, Redouble -> R, NoTrump/N -> N
                norm = []
                for t in tokens:
                    tt = t.upper()
                    if tt in ('PASS', 'P'):
                        norm.append('P')
                    elif tt in ('DOUBLE', 'D'):
                        norm.append('D')
                    elif tt in ('REDOUBLE', 'R'):
                        norm.append('R')
                    else:
                        norm.append(tt.replace('NT', 'N'))
                if norm:
                    deal['Auction'] = norm

            json.dump(deal, save_file)
        save_file.close()

    assert deal, 'Input must be *, **, or start with http'

    # Preprocess: sort suit lists in each hand
    suit_order = 'AKQJT98765432x'
    for seat in deal.get('Seats', []):
        hand = seat.get('Hand', {})
        for suit in ['Spades', 'Hearts', 'Diamonds', 'Clubs']:
            cards = hand.get(suit, '')
            # Convert to uppercase before sorting
            cards = cards.upper()
            sorted_cards = ''.join(sorted(cards, key=lambda c: suit_order.index(c) if c in suit_order else 99))
            hand[suit] = sorted_cards

    # change name of South player if specified
    if args.name:
        for seat in deal['Seats']:
            if seat['Direction'] == 'South':
                seat['Player'] = args.name

    # if 'played' is negative, show all played cards
    if args.played < 0:
        played_list = list(range(1, len(deal.get('Play', [])) + 1))
    else:
        played_list = [args.played]

    for n in played_list:
        suffix = f"-{n}" if n > 0 else ''

        # build html
        args.played = n
        html = buildhtml.build(deal, args)
    
        # write it to the specified file
        filename = filename_base + suffix + ".html"
        f = open(filename, 'w')
        f.write(html)
        f.close()

        print(f"Html has been written to {filename}")


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))

