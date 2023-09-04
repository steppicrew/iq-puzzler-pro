from typing import Literal, Tuple

from termcolor import colored


StoneShape = Tuple[tuple[int, int], ...]

StoneColor = Literal[
    "green", "pink", "yellow", "violet", "lightred",
    "red", "orange", "blue", "lightblue",
    "cyan", "lightgreen", "lime", "empty"
]

EMPTY:StoneColor = "empty"


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

STONE_SIZES: dict[StoneColor, int] = {
    color: len(STONES[color]) for color in STONES
}

_LIGHT = "🟓"
_DARK = "🟔"

def _light(color: str, marker: str):
    return (colored(text=_LIGHT, color=color, force_color=True), marker)

def _dark(color: str, marker: str):
    return (colored(text=_DARK, color=color, force_color=True), marker)

STONE_MARKER: dict[StoneColor, tuple[str, str]] = {
    "green": _dark(color='green', marker='G'),
    "pink": _light(color="light_magenta", marker='p'),
    "yellow": _dark(color="yellow", marker='y'),
    "violet": _dark(color="magenta", marker='v'),
    "lightred": _light(color="light_red", marker='r'),
    "red": _dark(color="red", marker='R'),
    "orange": _light(color="light_yellow", marker='o'),
    "blue": _dark(color="blue", marker='B'),
    "lightblue": _light(color="light_blue", marker='b'),
    "cyan": _dark(color="cyan", marker='c'),
    "lightgreen": _light(color="light_green", marker='g'),
    "lime": _light(color="light_cyan", marker='l'),
    EMPTY: ('·', '·'),
}

