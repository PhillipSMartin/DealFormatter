import constants

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

def format_hand(hand: Dict[str, str], args=None, deal=None, with_breaks: bool = True, indent: int = 0) -> str:
    # convert dictionary of holdings by suit into an html string displaying the hand
    # input:  {'Spades': 'T5', 'Hearts': 'AJ7', 'Diamonds': 'KQJ2', 'Clubs': 'AJT6'}
    # output: 
    #    '&#9824; 10 5<br />
    #     <span style="color: rgb(192, 22, 22);">&#9829;</span> A J 7<br />
    #     <span style="color: rgb(192, 22, 22);">&#9830;</span> K Q J 2<br />
    #     &#9827; A J 10 6<br />'

    br = '<br />\n' if with_breaks else '&nbsp;&nbsp;'

    # Determine played cards if args.played > 0
    played_cards = set()
    if args and hasattr(args, 'played') and getattr(args, 'played', 0) > 0 and deal and 'Play' in deal:
        played_cards = set(deal['Play'][:args.played])

    def card_html(card, played):
        if played:
            return f'<span style="color: #aaa;">{card}</span>'
        return card

    suit_str = []
    for pip, suit in zip(pips.values(), globals.suits):
        cards = hand[suit]
        display = []
        i = 0
        while i < len(cards):
            card = cards[i]
            # Handle '10' as 'T'
            if card == 'T':
                card_str = '10'
            else:
                card_str = card
            # Build suit+rank string (e.g. 'CK')
            suit_letter = suit[0]
            card_id = f'{suit_letter}{card_str}'
            played = card_id in played_cards
            display.append(card_html(card_str, played))
            i += 1
        suit_line = (' ' * indent) + pip + ' ' + ' '.join(display) if display else (' ' * indent) + pip + ' --'
        suit_str.append(suit_line)
    return br.join(suit_str) + br

def format_hand_diagram(hand_info: dict, args=None, deal=None) -> str:
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
    diagram = constants.HAND_DIRECTION_TEMPLATE.format(direction=hand_info["Direction"].upper())
    # diagram = f'          <div class="hand-title">{hand_info["Direction"].upper()}</div>\n'
    if "Player" in hand_info:
        diagram += constants.HAND_NAME_TEMPLATE.format(name=hand_info["Player"])
    if "Hand" in hand_info:
        diagram += f'{format_hand(hand_info["Hand"], args=args, deal=deal, indent=10)}'
    return diagram
    
    
def format_hand_diagrams(hands: dict, args=None, deal=None) -> dict:
    # convert list of hands into a dictionary of hand diagrams, keyed by direction
     
    return dict([(hand['Direction'], format_hand_diagram(hand, args=args, deal=deal)) for hand in hands])

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

    players = dict([(seat['Direction'], seat.get('Player', '')) for seat in deal['Seats']])
    auction_header = '    <tr>\n'
    for direction in globals.directions:
        auction_header += constants.AUCTION_DIRECTIONS_TEMPLATE.format(direction=direction)
    auction_header += '    </tr>\n    <tr>\n'
    for direction in globals.directions:
        auction_header += constants.AUCTION_NAMES_TEMPLATE.format(name=players[direction])
    return auction_header + '    </tr>'
    
    
def format_auction(auction: List[str]) -> str:
    # take output of formatAuctionCalls and format it into html table rows
    
    # extend auction to make length a multiple of four
    auction.extend([' '] * (4 - len(auction) % 4))
    
    # build rows
    auction_html = ''
    for i in range(len(auction)):
        if 0 == i % 4:
            auction_html += '    <tr>\n'
        auction_html += constants.CALL_TEMPLATE.format(call=auction[i])
        if 3 == i % 4:
            auction_html += '    </tr>\n'
    return auction_html

def build_auction_table(deal: dict, width: int = 350) -> str:
    header = format_auction_header(deal)
    auction = format_auction((format_auction_calls(deal["Auction"], deal["Dealer"])))
    return constants.AUCTION_TEMPLATE.format(width=width, header=header, auction=auction)

def build_card_table(deal: dict, card_to_seat : dict, args) -> str:
    # Display played cards from the current trick on the felt
    play = deal.get('Play', [])
    n = args.played if hasattr(args, 'played') else 0
    if n == 0:
        return constants.TABLE_TEMPLATE

    # Only show the last (n-1)%4 + 1 cards if n > 0
    num_to_show = ((n-1) % 4 + 1) if n > 0 else 0
    cards_to_show = play[:n][-num_to_show:] if num_to_show > 0 else []

    # Find which player played each card (assume order matches directions cyclically)
    # The first card in cards_to_show was played by (n - num_to_show + 1) % 4
    html = constants.CARD_TABLE_INTRO
    for i, card in enumerate(cards_to_show):
        direction = card_to_seat.get(card, '')
        html += constants.CARD_TABLE_ENTRY_TEMPLATE.format(direction=direction, pip=pips[card[0]], rank=card[1:])
    html += constants.CARD_TABLE_OUTRO
    return html

def build_diagram(deal: dict, args) -> str:
    # Create a dictionary mapping cards to seat directions
    card_to_seat = {}
    for seat in deal["Seats"]:
        direction = seat.get("Direction", "")
        hand = seat.get("Hand", {})
        for suit in ["Spades", "Hearts", "Diamonds", "Clubs"]:
            cards = hand.get(suit, "")
            for card in cards:
                card_id = f"{suit[0]}{card}"
                card_to_seat[card_id] = direction.lower()

    # build html to display deal
    hands = format_hand_diagrams(deal["Seats"], args=args, deal=deal)
    table = constants.DIAGRAM_INTRO

    if args.north:
        table += constants.CENTER_HAND_TEMPLATE.format(hand=hands["North"])

    table += constants.WEST_HAND_TEMPLATE.format(hand=hands["West"] if args.west else '')       
    table += build_card_table(deal, card_to_seat, args)
    table += constants.EAST_HAND_TEMPLATE.format(hand=hands["East"] if args.east else '')
      
    if args.south:
        table += constants.CENTER_HAND_TEMPLATE.format(hand=hands["South"])

    table += constants.DIAGRAM_OUTRO
    return table
            
def build_single_hand(hand: Dict[str, str], args=None, deal=None) -> str:
    hand_html = format_hand(hand, args=args, deal=deal, with_breaks=False)
    return constants.HORIZONTAL_HAND_TEMPLATE.format(hand_html=hand_html)
 
def build(deal : dict, args) -> str: 
    import copy
    deal_copy = copy.deepcopy(deal)
    html = constants.STYLE

    # rotate deal if necessary
    if args.rotate:
        rotate_deal(deal_copy, args.rotate)

    # if a single seat is specified, format it as a single line
    seats_to_show = args.north * 'N' + args.east * 'E' + args.south * 'S' + args.west * 'W'
    if len(seats_to_show) == 1:
        for seat in deal_copy['Seats']:
            if seat['Direction'] == globals.seats[seats_to_show[0]]:
                 html = build_single_hand(seat['Hand'], args=args, deal=deal_copy)
                 break

    elif len(seats_to_show) > 1:
        html += build_diagram(deal_copy, args)

    # if specified, add auction
    if args.auction:
        html += build_auction_table(deal_copy)

    return html

if __name__ == '__main__' :
    import main
    sampleDeal = {'Board number': 12, 'Dealer': 'West', 'Auction': ['P', '1N', 'P', '2C', 'P', '2H', 'P', '3S', 'P', '4D', 'P', '4N', 'P', '5S', 'P', '7H', 'P', 'P', 'P'], 'Seats': [{'Player': 'Phillip', 'Direction': 'South', 'Hand': {'Spades': 'AK5', 'Hearts': 'KT43', 'Diamonds': 'K7', 'Clubs': 'AK62'}}, {'Player': 'Robot', 'Direction': 'West', 'Hand': {'Spades': 'J962', 'Hearts': '9', 'Diamonds': 'Q984', 'Clubs': 'T754'}}, {'Player': 'Robot', 'Direction': 'North', 'Hand': {'Spades': 'Q73', 'Hearts': 'AQJ52', 'Diamonds': 'AJ5', 'Clubs': 'J9'}}, {'Player': 'Robot', 'Direction': 'East', 'Hand': {'Spades': 'T84', 'Hearts': '876', 'Diamonds': 'T632', 'Clubs': 'Q83'}}], 'Play': ['S4', 'SA', 'S2', 'S3', 'HK', 'H9', 'H2', 'H6']}
    args = main.parse_args(['dummyinput', '-nsewa', '-r2', '-p2'])
    result = build(sampleDeal, args)
    with open('test.html', 'w') as f:
        f.write(result)

 

