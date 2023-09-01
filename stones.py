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
    "green": colored(_DARK, 'green'),
    "pink": colored(_LIGHT, "light_magenta"),
    "yellow": colored(_DARK, "yellow"),
    "violet": colored(_DARK, "magenta"),
    "lightred": colored(_LIGHT, "light_red"),
    "red": colored(_DARK, "red"),
    "orange": colored(_LIGHT, "light_yellow"),
    "blue": colored(_DARK, "blue"),
    "lightblue": colored(_LIGHT, "light_blue"),
    "cyan": colored(_DARK, "cyan"),
    "lightgreen": colored(_LIGHT, "light_green"),
    "lime": colored(_LIGHT, "light_cyan"),
}


EMPTY = '·'
