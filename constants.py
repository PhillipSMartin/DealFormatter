STYLE = """\
<style>
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

HORIZONTAL_HAND_TEMPLATE = '<TABLE width="300" border="0" cellspacing="0" cellpadding="0" align="center"><TR><TD WIDTH="100%" Align="center">{hand_html}</TR></TABLE>'

DIAGRAM_INTRO = """\
<div align="center" class="bridge-diagram">
  <table>
    <colgroup>
      <col class="col-left" />
      <col class="col-center" />
      <col class="col-right" />
    </colgroup>
    <tbody>\n"""
DIAGRAM_OUTRO = "    </tbody>\n  </table>\n</div>\n"

CENTER_HAND_TEMPLATE = """\
      <tr>
        <td></td>
        <td class = "hand center-hand">
{hand}
        </td>
        <td></td>    
      </tr>\n"""

WEST_HAND_TEMPLATE = """\
      <tr>
        <td class="hand hand-west">
{hand} 
        </td>\n"""

TABLE_TEMPLATE = """\
        <td class="table-cell">
          <div class="felt">
          </div>
        </td>\n"""

EAST_HAND_TEMPLATE = """\
        <td class="hand hand-east">
{hand}
        </td> 
      </tr>\n"""

AUCTION_DIRECTIONS_TEMPLATE = """\
      <td align="direction in globals.directions:left" width="25%"><b>{direction}</b></td>\n"""

AUCTION_NAMES_TEMPLATE = """\
      <td align="left" width="25%"><i>{name}</i></td>\n"""

AUCTION_TEMPLATE = """\
<br/>
<table align="center" border="0" cellpadding="0" cellspacing="0" style="width: {width}px;padding-left: 30">
  <tbody>
{header}
{auction}  </tbody>
</table>\n"""

CALL_TEMPLATE="""\
      <td align="left" width="25%">{call}</td>\n"""

CARD_TABLE_INTRO = """\
        <td class="table-cell">
          <div class="felt">\n"""

CARD_TABLE_ENTRY_TEMPLATE = """\
            <div class="card {direction}">{pip} {rank}</div>\n"""

CARD_TABLE_OUTRO = """\
          </div>
        </td>\n"""

HAND_DIRECTION_TEMPLATE = """\
          <div class="hand-title">{direction}</div>\n"""

HAND_NAME_TEMPLATE = """\
          <div class="name">{name}</div>\n"""
 

