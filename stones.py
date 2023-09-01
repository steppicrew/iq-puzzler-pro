from typing import Literal, Tuple

from termcolor import colored


StoneShape = Tuple[tuple[int, int], ...]

StoneColor = Literal[
    "green", "pink", "yellow", "violet", "lightred",
    "red", "orange", "blue", "lightblue",
    "cyan", "lightgreen", "lime",
]

# Default orientation:
#
# green: GGG
#         G
#
# pink:  ppp
#       pp
#
# yellow: yyyy
#           y
#
# violet:   v
#          vv
#         vv
#
# lightred: rrrr
#              r
#
# red: R
#      RR
#       R
#
# orange: oo
#          oo
#          o
#
# blue: B
#       BBB
#
# lightblue: bbb
#              b
#              b
#
# cyan:  c
#       cc
#
# lightgreen: g g
#             ggg
#
# lime:  l
#       ll
#       ll

STONES: dict[StoneColor, StoneShape] = {
    "green": ((0, 0), (1, 0), (1, 1), (2, 0)),
    "pink": ((0, 0), (1, 0), (1, -1), (2, -1), (3, -1)),
    "yellow": ((0, 0), (1, 0), (2, 0), (2, 1), (3, 0)),
    "violet": ((0, 0), (1, 0), (1, -1), (2, -1), (2, -2)),
    "lightred": ((0, 0), (0, 1), (0, 2), (0, 3), (1, 3)),
    "red": ((0, 0), (0, 1), (1, 1), (1, 2)),
    "orange": ((0, 0), (1, 0), (1, 1), (2, 1), (1, 2)),
    "blue": ((0, 0), (0, 1), (1, 1), (2, 1)),
    "lightblue": ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
    "cyan": ((0, 0), (1, 0), (1, -1)),
    "lightgreen": ((0, 0), (0, 1), (1, 1), (2, 1), (2, 0)),
    "lime": ((0, 0), (0, 1), (1, -1), (1, 0), (1, 1)),
}

_LIGHT = "🟓"
_DARK = "🟔"

STONE_MARKER: dict[StoneColor, str] = {
    "green": colored(_DARK, 'green', force_color=True),
    "pink": colored(_LIGHT, "light_magenta", force_color=True),
    "yellow": colored(_DARK, "yellow", force_color=True),
    "violet": colored(_DARK, "magenta", force_color=True),
    "lightred": colored(_LIGHT, "light_red", force_color=True),
    "red": colored(_DARK, "red", force_color=True),
    "orange": colored(_LIGHT, "light_yellow", force_color=True),
    "blue": colored(_DARK, "blue", force_color=True),
    "lightblue": colored(_LIGHT, "light_blue", force_color=True),
    "cyan": colored(_DARK, "cyan", force_color=True),
    "lightgreen": colored(_LIGHT, "light_green", force_color=True),
    "lime": colored(_LIGHT, "light_cyan", force_color=True),
}


EMPTY = '·'
