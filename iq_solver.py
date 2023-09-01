from typing import Callable, Literal, Tuple

from stones import EMPTY, STONE_MARKER, STONES, StoneColor, StoneShape


Board = list[list[str]]

Direction = Literal[1, 2, 3, 4, -1, -2, -3, -4]

all_directions: Tuple[Direction, ...] = (1, 2, 3, 4, -1, -2, -3, -4)

BOARD_WIDTH = 11
BOARD_HEIGHT = 5

board: Board = [
    [EMPTY for _ in range(BOARD_WIDTH)]
    for _ in range(BOARD_HEIGHT)
]

used_stones: set[StoneColor] = set()
found_boards: set[str] = set()


def print_board(no_dups: bool = False, _print_board: bool = True):
    p = '\n'.join(' '.join(c for c in line) for line in board)
    if no_dups:
        if p in found_boards:
            return None
        found_boards.add(p)
    if _print_board:
        print(p)
        print()


def apply_stone(stone: StoneShape, fn: Callable[[tuple[int, int]], tuple[int, int]]) -> StoneShape:
    return tuple(fn(p) for p in stone)


_rotate_cache: dict[tuple[StoneShape, Direction], StoneShape] = {}


def rotate_stone(stone: StoneShape, direction: Direction) -> StoneShape:
    index: tuple[StoneShape, Direction] = (stone, direction)
    if index not in _rotate_cache:
        if direction < 0:
            stone = apply_stone(stone, lambda p: (p[0], -p[1]))
            direction = -direction
        for _ in range(direction - 1):
            stone = apply_stone(stone, lambda p: (p[1], -p[0]))
        _rotate_cache[index] = stone
    return _rotate_cache[index]


# Find unique stone rotations
STONE_DIRECTIONS: dict[StoneColor, Tuple[Direction, ...]] = {}
for color, stone in STONES.items():
    normalized_shapes: set[StoneShape] = set()
    directions: list[Direction] = []
    for direction in all_directions:
        shape = rotate_stone(stone=stone, direction=direction)
        min_x = min(p[0] for p in shape)
        min_y = min(p[1] for p in shape)
        normalized_shape = tuple(sorted(
            apply_stone(
                stone=shape,
                fn=lambda p: (
                    p[0] - min_x,
                    p[1] - min_y,
                )
            ),
            key=lambda p: f"{p[0]}:{p[1]}"
        ))
        if normalized_shape not in normalized_shapes:
            directions.append(direction)
            normalized_shapes.add(normalized_shape)

        STONE_DIRECTIONS[color] = tuple(directions)


def remove_stone(stone_color: StoneColor):
    marker = STONE_MARKER[stone_color]
    for y, line in enumerate(board):
        for x, c in enumerate(line):
            if c == marker:
                board[y][x] = EMPTY
    if stone_color in used_stones:
        used_stones.remove(stone_color)


def place_stone(stone_color: StoneColor, direction: Direction, start: tuple[int, int]) -> bool:
    shape = rotate_stone(stone=STONES[stone_color], direction=direction)
    offset_x = min(p[0] for p in shape) - start[0]
    offset_y = min(p[1] for p in shape) - start[1]
    shape = apply_stone(shape, lambda p: (p[0] - offset_x, p[1] - offset_y))
    max_x = max(p[0] for p in shape)
    max_y = max(p[1] for p in shape)

    if max_x >= len(board[0]) or max_y >= len(board):
        return False

    marker = STONE_MARKER[stone_color]
    for p in shape:
        if board[p[1]][p[0]] != EMPTY:
            remove_stone(stone_color)
            return False

        board[p[1]][p[0]] = marker

    used_stones.add(stone_color)
    return True


def test_board() -> bool:
    checked: set[tuple[int, int]] = set()

    def test_xy(x: int, y: int) -> int:
        if (x, y) in checked:
            return 0

        if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT:
            return 0

        if board[y][x] != EMPTY:
            return 0

        checked.add((x, y))

        result = 1
        for d in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            result += test_xy(x + d[0], y + d[1])
        return result

    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if (x, y) in checked:
                continue
            t = test_xy(x, y)
            if t > 0 and t < 3:
                # print_board()
                # print(t, (x, y), checked, "XXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                return False
    return True


def place_next_stone(colors: list[StoneColor]):
    color = colors[0]
    colors = colors[1:]
    for y in range(BOARD_HEIGHT-1):
        for x in range(BOARD_WIDTH-1):
            for direction in STONE_DIRECTIONS[color]:
                if place_stone(color, direction, (x, y)):
                    if len(colors) == 0:
                        print_board(True, False)
                        return
                    if test_board():
                        print_board()
                        place_next_stone(colors)
                    remove_stone(color)


GAME: int = 1
TEST = False

if GAME == 1:  # pyright: ignore[reportUnnecessaryComparison]
    place_stone("pink", 4, (0, 0))
    place_stone("yellow", 1, (1, 0))
    place_stone("orange", 3, (4, 0))
    place_stone("blue", -1, (6, 0))
    place_stone("red", 1, (4, 2))
    place_stone("lime", 4, (6, 3))
    place_stone("cyan", -3, (3, 3))
    place_stone("green", 2, (2, 1))
    place_stone("lightblue", 3, (0, 2))
elif GAME == 32:  # pyright: ignore[reportUnnecessaryComparison]
    place_stone("lime", 4, (0, 0))
    place_stone("yellow", -3, (2, 0))
    place_stone("cyan", 3, (6, 0))
    place_stone("red", -2, (4, 1))


if TEST:
    print_board(False, True)
else:
    remaining_colors: list[StoneColor] = [
        c for c in STONES if c not in used_stones
    ]
    place_next_stone(remaining_colors)
    for b in found_boards:
        print(b)
        print()

    out_file = f"{__file__}.{GAME}.solution.txt"
    with open(out_file, mode="w") as file:
        file.write("\n".join(f"{b}\n" for b in found_boards))


# print(''.join(str(i) for i in range(1)))
