# -*- coding: utf-8 -*-
"""
The build method of this module takes as input a dictionary describing a deal in the following format:
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
        
    it outputs an html string, displaying the deal in a variety of formats
    as specified by the options string
    
    the options specified must contain at least one of SWNE and may also contain A
    if it contains only one of SWNE, that hand is formatted on a single line
    if it contains more than one of SWNE, all the specified hands are formatted in a diagram
    
    if it contains A, the auction is formatted below the diagram
    
    if r is specified, the deal is shifted clockwise that number of positions (and directions are reassigned before formatting)
"""
import globals

from typing import Dict, List


globals.initialize()
pips = { 'S': '&#9824;', 
        'H': '<span style="color: rgb(192, 22, 22);">&#9829;</span>',
        'D': '<span style="color: rgb(192, 22, 22);">&#9830;</span>',
        'C': '&#9827;'
        }


def shift(direction: str, n: int) -> str:
    # returns direction n places clockwise from specified direction
    # shift("South", 1) returns "West"
    return globals.directions[(globals.directions.index(direction) + n) % 4]

def rotate_deal(deal: dict, n: int) -> dict:
    # rotates deal n seats counter-clockwise
    deal["Dealer"] = shift(deal["Dealer"], n)
    for seat in deal['Seats']:
        seat["Direction"] = shift(seat["Direction"], n)
    return deal
    
def format_suit(suit: str) -> str:
    # input: 'AJT6'
    # output: ' A J 10 6'
    return ' '.join(suit).replace('T','10') or '--'

def format_hand(hand: Dict[str, str], with_breaks: bool = True) -> str:
    # convert dictionary of holdings by suit into an html string displaying the hand
    # input:  {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'}
    # output: 
    #    '&#9824; 10 5<br />
    #     <span style="color: rgb(192, 22, 22);">&#9829;</span> A J 7<br />
    #     <span style="color: rgb(192, 22, 22);">&#9830;</span> K Q J 2<br />
    #     &#9827; A J 10 6<br />'

    br = '<br />\n' if with_breaks else '&nbsp;&nbsp;'
    suit_str = [pip + ' ' + format_suit(hand[suit]) for pip, suit in zip(pips.values(), globals.suits)]
    return br.join(suit_str) + br

def format_hand_diagram(hand_info: dict) -> str:
    # convert dictionary of hand info into an html string displaying the direction, player, and hand itself
    # input:  { "Player": "Phillip", "Direction": "North", "Hand": ...}
    # output: 
    #   NORTH<br />
    #   <i>Phillip</i><br />
    #   ♠ A Q 10 7 6<br />
    #   <span style="color: #c01616;">♥</span> A J 7 5 4<br />
    #   <span style="color: #c01616;">♦</span> 10 3<br />
    #   ♣ 6<br />
    # 
    
    diagram =  f'{hand_info["Direction"].upper()}<br />\n'
    if "Player" in hand_info:
        diagram += f'<i>{hand_info["Player"]}</i><br />\n'
    if "Hand" in hand_info:
        diagram += f'{format_hand(hand_info["Hand"])}\n'
    return diagram
    
    
def format_hand_diagrams(hands: dict) -> dict:
    # convert list of hands into a dictionary of hand diagrams, keyed by direction
     
    return dict([(hand['Direction'], format_hand_diagram(hand)) for hand in hands])

def format_call(call: str) -> str:
    # convert abbreviation into a displayable html string
    # input: '1C'
    # output: '1 &#9827;</span>'
    for suit, pip in pips.items():
        if len(call) > 1:
            call = call.replace(suit, ' ' + pip)
    return call.replace('P', 'Pass').replace('D', 'Double').replace('R', 'Redouble').replace('N', ' NT')

def format_auction_calls(auction: List[str], dealer: str) -> list:
    # convert list of call  abbreviations into a  list of displayable calls with the first call being West
    # input: ['1C', 'Pass', '2C', 'Pass', '2S', 'Pass', '3 NT', 'Pass', 'Pass', 'Pass'], North dealer
    # output: [' ', '1 &#9827;', 'Pass', '2 &#9827;',
    #     'Pass', '2 &#9824;', 'Pass', '3 NT', 
    #     '(All pass)']
        
    # translate abbreviations to full calls
    call_list = [format_call(call) for call in auction]
    
    # replace three or four final passes with (All pass)
    if len(call_list) > 3:
        if call_list[-3:] == ['Pass', 'Pass', 'Pass']:
            call_list[-3:] = ['(All pass)']
        if call_list[-1] == 'Pass':
            del call_list[-1]
         
    # determine how many empty cells should begin the auction
    new_auction = ([' '] * ((globals.directions.index(dealer)) % 4))
    new_auction.extend(call_list)
    return new_auction

def format_auction_header(deal: dict) -> str:
    # construct auction heading from list of players (West first)
    # input: each player's name can be found in deal[direction]["PLayer"]
    # output: 
    # <tr>
    #    <td align="left" width="25%"><b>West</b></td>
    #    <td align="left" width="25%"><b>North</b></td>
    #    <td align="left" width="25%"><b>East</b></td>
    #    <td align="left" width="25%"><b>South</b></td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Robot</i></td>
    #    <td align="left" width="25%"><i>Phillip</i></td>
    # </tr>
    players = dict([(seat['Direction'], seat.get('Player', '')) for seat in deal['Seats']])
    auction_header = '<tr>\n'
    for direction in globals.directions:
        auction_header += f'   <td align="direction in globals.directions:left" width="25%"><b>{direction}</b></td>\n'
    auction_header += '</tr>\n<tr>\n'
    for direction in globals.directions:
        auction_header += f'   <td align="left" width="25%"><i>{players[direction]}</i></td>\n'
    return auction_header + '</tr>\n'
    
    
def format_auction(auction: List[str]) -> str:
    # take output of formatAuctionCalls and format it into html table rows
    # output: 
    # <tr>
    #    <td align="left" width="25%"> <br /></td>
    #    <td align="left" width="25%">1 ♣</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">2 ♣</td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">2 ♠</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">3 NT</td>
    # </tr>
    # <tr>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%">Pass</td>
    #    <td align="left" width="25%"> <br /></td>
    # </tr>
    
    # extend auction to make length a multiple of four
    auction.extend([' '] * (4 - len(auction) % 4))
    
    # build rows
    new_auction = ''
    for i in range(len(auction)):
        if 0 == i % 4:
            new_auction += '<tr>\n'
        new_auction += f'   <td align="left" width="25%">{auction[i]}</td>\n'
        if 3 == i % 4:
            new_auction += '</tr>\n'
    return new_auction

def build_auction_table(deal: dict, width: int = 350) -> str:
    header = format_auction_header(deal)
    auction = format_auction((format_auction_calls(deal["Auction"], deal["Dealer"])))
    return f'<br/><table align="center" border="0" cellpadding="0" cellspacing="0" style="width: {width}px;">\n<tbody>\n' + \
        header + \
        auction + \
        '</tbody></table>'
 
def build_hand_table(deal: dict, args) -> str:
    # build html to display deal
    hands = format_hand_diagrams(deal["Seats"])
    table = '<div align="center"><table><tbody>\n'
    if args.north:
        table += '   <tr>\n'  + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + (hands["North"] if args.north else '') + '<br /></td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '   </tr>\n'
    if args.east or args.west:
        table += '   <tr>\n'  + \
            '      <td align="left" width="125">' + (hands["West"] if args.west else '') + ('<br />' if args.south else '') + '</td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + (hands["East"] if args.east else '') + ('<br />' if args.south else '') + '</td>\n' + \
            '   </tr>\n'
    if args.south:
        table += '   <tr>\n'  + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '      <td align="left" width="125">' + hands["South"] + '</td>\n' + \
            '      <td align="left" width="125"><br /></td>\n' + \
            '   </tr>\n'
    table += '</tbody></table></div>\n'
    return table
            
def build_single_hand(hand: str) -> str:
    return f'<TABLE width="300" border="0" cellspacing="0" cellpadding="0" align="center"><TR><TD WIDTH="100%" Align="center">{hand}</TR></TABLE>'
        
    
def build(deal : dict, args) -> str:
    
    html = ''
    
    # rotate deal if necessary
    if args.rotate:
        rotate_deal(deal, args.rotate)
    
    # if a single seat is specified, format it as a single line
    seats_to_show = args.north * 'N' + args.east * 'E' + args.south * 'S' + args.west * 'W'
    if len(seats_to_show) == 1:
        for seat in deal['Seats']:
            if seat['Direction'] == globals.seats[seats_to_show[0]]:
                 html = build_single_hand(format_hand(seat['Hand'], False))
                 break
    
    elif len(seats_to_show) > 1:
        html = build_hand_table(deal, args)
        
    # if specified, add auction
    if args.auction:
        html += build_auction_table(deal)
        
    return html

    

# for testing
if __name__ == '__main__' :
   
    sampleDeal = {"Seats": [{"Direction": "West", "Hand": {"Spades": "K6", "Hearts": "8643", "Diamonds": "Q954", "Clubs": "Q96"}}, {"Direction": "North"}, {"Direction": "East", "Hand": {"Spades": "AJT743", "Hearts": "", "Diamonds": "7", "Clubs": "AKJT84"}}, {"Direction": "South"}], "Auction": [""]}
    result = build(sampleDeal, 'EW')
    """
    sampleDeal = {'Dealer': 'West',
 'Seats': [{'Direction': 'West'},
  {'Direction': 'North', 
   'Hand': {'Spades': 'K7542',
    'Hearts': 'K752',
    'Diamonds': 'J6',
    'Clubs': 'Q4'}},
  {'Direction': 'East',
   'Hand': {'Spades': 'A6',
    'Hearts': 'AT6',
    'Diamonds': 'QT842',
    'Clubs': 'AT9'}},
  {'Direction': 'South'}],
 'Auction': ['P', 'P', '1D', '1S', 'D', '3S']}
    result = build(sampleDeal, 'NEA')
     """
    print (result)

 

