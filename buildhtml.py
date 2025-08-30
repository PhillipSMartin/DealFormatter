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

def format_hand(hand: Dict[str, str], with_breaks: bool = True, indent: int = 0) -> str:
    # convert dictionary of holdings by suit into an html string displaying the hand
    # input:  {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'}
    # output: 
    #    '&#9824; 10 5<br />
    #     <span style="color: rgb(192, 22, 22);">&#9829;</span> A J 7<br />
    #     <span style="color: rgb(192, 22, 22);">&#9830;</span> K Q J 2<br />
    #     &#9827; A J 10 6<br />'

    br = '<br />\n' if with_breaks else '&nbsp;&nbsp;'
    suit_str = [(' ' * indent) + pip + ' ' + format_suit(hand[suit]) for pip, suit in zip(pips.values(), globals.suits)]
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
    diagram = f'          <div class="hand-title">{hand_info["Direction"].upper()}</div>\n'
    #diagram =  f'{hand_info["Direction"].upper()}<br />\n'
    if "Player" in hand_info:
        diagram += f'          <div class="name">{hand_info["Player"]}</div>\n'
    if "Hand" in hand_info:
        diagram += f'{format_hand(hand_info["Hand"], indent=10)}'
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
    return f'<br/><table align="center" border="0" cellpadding="0" cellspacing="0" style="width: {width}px;padding-left: 30">\n<tbody>\n' + \
        header + \
        auction + \
        '</tbody></table>'

def build_hand_table(deal: dict, args) -> str:
    # build html to display deal
    hands = format_hand_diagrams(deal["Seats"])
    table = """<div align="center" class="bridge-diagram">
  <table>
    <colgroup>
      <col class="col-left" />
      <col class="col-center" />
      <col class="col-right" />
    </colgroup>
    <tbody>\n"""

    if args.north:
        table += """      <tr>
        <td></td>
        <td class = "hand center-hand">\n"""
        table += hands["North"]
        table += """        </td>
        <td></td>    
      </tr>\n"""

    if True:   
        table += """      <tr>
        <td class="hand hand-west">\n"""
        table += hands["West"] if args.west else '' 
        table += '          <br />\n' if args.south else '\n'
        table += """        </td>
        <td class="table-cell">
          <div class="felt">
          </div>
        </td>
        <td class="hand hand-east">\n"""
        table += hands["East"] if args.east else ''
        table += '          <br />\n' if args.south else '\n'
        table += """        </td> 
      </tr>\n"""
        
    if args.south:
        table += """      <tr>
        <td></td>
        <td class = "hand center-hand">\n"""
        table += hands["South"]
        table += """        </td>
        <td></td>    
      </tr>\n"""
        # table += '   <tr>\n'  + \
        #     '      <td align="left" width="125"><br /></td>\n' + \
        #     '      <td align="left" width="125">' + hands["South"] + '</td>\n' + \
        #     '      <td align="left" width="125"><br /></td>\n' + \
        #     '   </tr>\n'
    table += "    </tbody>\n  </table>\n</div>\n"
    return table
            
def build_single_hand(hand: str) -> str:
    return f'<TABLE width="300" border="0" cellspacing="0" cellpadding="0" align="center"><TR><TD WIDTH="100%" Align="center">{hand}</TR></TABLE>'
 
def build(deal : dict, args) -> str:
    
    html = """<style>
    .bridge-diagram {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Color Emoji", "Segoe UI Emoji";
      /* Adjust these to fine-tune layout */
      --col-center: 145px; /* width of middle column */
      --felt-w:    120px;  /* width of green felt */
    }

    /* Let columns size from content; center column stays fixed via colgroup */
    .bridge-diagram table { border-collapse: collapse; margin: 0 auto; table-layout: auto; }
    .bridge-diagram td { vertical-align: top; padding: 0 .5rem; width: auto; }

    /* Column widths: left/right auto; center fixed */
    .bridge-diagram .col-center { width: var(--col-center); }

    /* Keep NORTH/SOUTH text left-aligned, but center the whole block under the felt.
       Uses max() to avoid negative padding if felt > center width. */
    .bridge-diagram .center-hand {
      text-align: left;
      padding-left: 30;
    }

    /* Vertically center the felt row so it's equidistant from NORTH/SOUTH */
    .bridge-diagram tbody tr:nth-child(2) td { vertical-align: middle; }

    /* Felt + played cards */
    .bridge-diagram .table-cell { text-align:center; }
    .bridge-diagram .felt {
      position: relative; width: var(--felt-w); height: 80px; margin: 8px auto; background: #215b33; border-radius: 12px;
      box-shadow: inset 0 0 0 3px #134022, inset 0 0 30px rgba(0,0,0,.35);
    }
    .bridge-diagram .card {
      position: absolute; background: #fff; border-radius: 6px; border: 1px solid #d9d9d9; padding: 2px 6px;
      font-size: 14px; font-weight: 700; line-height: 1; box-shadow: 0 2px 8px rgba(0,0,0,.18);
    }
    .bridge-diagram .north { top: 4px; left: 50%; transform: translateX(-50%); }
    .bridge-diagram .south { bottom: 4px; left: 50%; transform: translateX(-50%); }
    .bridge-diagram .west  { left: 4px; top: 50%; transform: translateY(-50%); }
    .bridge-diagram .east  { right: 4px; top: 50%; transform: translateY(-50%); }

    /* Suit coloring */
    .bridge-diagram .red { color:#c01616; }

    /* Hand formatting */
    .bridge-diagram .hand-title { font-weight: 700; }
    .bridge-diagram .name { font-style: italic; }
    .bridge-diagram .hand-west { 
      text-align: left; 
      white-space: nowrap;      /*  ensures column width equals the longest WEST line */
      padding-right: .2rem;    /* small margin beyond longest line */
    }
    .bridge-diagram .hand-east { text-align:left; }
</style>\n"""
    
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
        html += build_hand_table(deal, args)
        
    # if specified, add auction
    if args.auction:
        html += build_auction_table(deal)
        
    return html    

if __name__ == '__main__' :
    import main
    sampleDeal = {"Board number": 8, "Dealer": "West", "Auction": ["1S", "P", "1N", "2H", "2S", "P", "P", "3C", "P", "3H", "D", "P", "P", "P"], "Seats": [{"Player": "psmartin", "Direction": "South", "Hand": {"Spades": "2", "Hearts": "AK876", "Diamonds": "Q2", "Clubs": "KQ642"}}, {"Player": "Robot", "Direction": "West", "Hand": {"Spades": "AKQJ95", "Hearts": "5", "Diamonds": "74", "Clubs": "A975"}}, {"Player": "Robot", "Direction": "North", "Hand": {"Spades": "873", "Hearts": "Q4", "Diamonds": "KJT953", "Clubs": "J8"}}, {"Player": "Robot", "Direction": "East", "Hand": {"Spades": "T64", "Hearts": "JT932", "Diamonds": "A86", "Clubs": "T3"}}]}
    args = main.parse_args(['dummyinput', '-nsa'])
    result = build(sampleDeal, args)
    with open('test.html', 'w') as f:
        f.write(result)

 

