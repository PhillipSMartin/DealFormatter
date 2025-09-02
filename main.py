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
import re
import sys


def parse_args(argv):
    parser = argparse.ArgumentParser(description='Deal Formatter Tool', )
    parser.add_argument('input', help='html string, * for console input, or ** for previous deal ')
    parser.add_argument('-n', '--north', action='store_true', help='print North hand')
    parser.add_argument('-e', '--east', action='store_true', help='print East hand')
    parser.add_argument('-s', '--south', action='store_true', help='print South hand')
    parser.add_argument('-w', '--west', action='store_true', help='print West hand')
    parser.add_argument('-a', '--auction', action='store_true', help='print auction')
    parser.add_argument('-r', '--rotate', type=int, help='number of seats to rotate clockwise')
    parser.add_argument('-p', '--played', type=int, help='number of cards played', default=0)
    parser.add_argument('-o', '--output', default='output', help='common prefix for json and html output files')
    parser.add_argument('-v', '--vertical', action='store_true', help='use vertical (vs horizontal) hand layout')
    parser.add_argument ('-g', '--gray', action='store_true', help='gray out played cards rather than remove them')
    return parser.parse_args(argv)


def main(args):
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
        save_file.close()

    assert deal, 'Input must be *, **, or start with http'

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

