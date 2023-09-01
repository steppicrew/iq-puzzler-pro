from typing import Literal, Callable, Tuple

from stones import EMPTY, STONE_MARKER, STONES, StoneColor, StoneShape


StoneShape3d = Tuple[tuple[int, int, int], ...]
Stone = tuple[StoneShape3d, int]

Board = list[list[list[str]]]
BoardPostion = tuple[int, int, int]
BoardPostion_ = BoardPostion | None
BoardNeighbours = tuple[
    BoardPostion_, BoardPostion_, BoardPostion_, BoardPostion_,
    BoardPostion_, BoardPostion_, BoardPostion_, BoardPostion_,
    BoardPostion_, BoardPostion_, BoardPostion_, BoardPostion_,
]

DirectionLevel = Literal[-1, 0, 1]  # lower, same, upper level
DirectionOrientation = Literal[0, 1, 2, 3]  # (ne, se, sw, nw) or (e, s, w, n)
DirectionRotation = Literal[1, -1]  # 0°, 180° or up, down
Direction = tuple[DirectionLevel, DirectionOrientation, DirectionRotation]

all_directions: Tuple[Direction, ...] = tuple(
    (level, orientation, rotation)  # type: ignore
    for level in (-1, 0, 1)
    for orientation in (0, 1, 2, 3)
    for rotation in ((1, -1))
)

BASE_WIDTH = 5

board: Board = [
    [
        [EMPTY for _ in range(BASE_WIDTH - h)]
        for _ in range(BASE_WIDTH - h)
    ]
    for h in range(BASE_WIDTH)
]


def transform(p: tuple[int, int], direction: Direction) -> BoardPostion:
    level, orientation, rotation = direction

    # orientation: 0: right, 1: down, 2: left, 3: up
    # orientation: 0: ne, 1: se, 2: sw, 3: nw

    dx: BoardPostion
    dy: BoardPostion
    if level == 1:
        dx = (
            (0 if orientation == 0 or orientation == 1 else -1),
            (0 if orientation == 0 or orientation == 3 else -1),
            level
        )

        '''
        dx -> dy(0°/180°)
        0: (0, 0) -> (1, 1)/(-1, -1)
        1: (0, -1) -> (1, 0)/(-1, 0)
        2: (-1, -1) -> (0, 0)/(-1, -1)
        3: (-1, 0) -> (0, 1)/(0, -1)
        '''
        dy = (
            rotation * (-dx[0] - 1),
            rotation * (-dx[1] - 1),
            rotation
        )
    elif level == 0:
        dx = (
            (1 if orientation == 0 else -1 if orientation == 2 else 0),
            (1 if orientation == 1 else -1 if orientation == 3 else 0),
            0
        )

        # n: -> ( 1,  0, 0)
        # e: -> ( 0, -1, 0)
        # s: -> (-1,  0, 0)
        # w: -> ( 0,  1, 0)
        dy = (
            -dx[1] * rotation,
            dx[0] * rotation,
            0
        )
    else:  # level == -1
        dx = (
            (1 if orientation == 0 or orientation == 1 else 0),
            (1 if orientation == 0 or orientation == 3 else 0),
            level
        )

        '''
        dx -> dy(0°/180°)
        0: (1, 1) -> (0, 0)/(0, 0)
        1: (1, 0) -> (0, -1)/(0, -1)
        2: (0, 0) -> (-1, -1)/(-1, -1)
        3: (0, 1) -> (-1, 0)/(-1, 0)
        '''
        dy = (
            rotation * (dx[0] - 1),
            rotation * (dx[1] - 1),
            rotation
        )

    return (
        p[0] * dx[0] + p[1] * dy[0],
        p[0] * dx[1] + p[1] * dy[1],
        p[0] * dx[2] + p[1] * dy[2],
    )


used_stones: set[StoneColor] = set()
found_boards: set[str] = set()


def print_board(no_dups: bool = False, _print_board: bool = True):
    lines: Tuple[list[str], ...] = tuple([] for _ in board[0])

    for level in board:
        for y, line in enumerate(level):
            lines[y].append(' '.join(line))

    p = '\n'.join('  '.join(line) for line in lines)

    if no_dups:
        if p in found_boards:
            return None
        found_boards.add(p)

    if _print_board:
        print(p)
        print()


def apply_stone(stone: StoneShape3d, fn: Callable[[BoardPostion], BoardPostion]) -> StoneShape3d:
    return tuple(fn(p) for p in stone)


_rotate_cache: dict[tuple[StoneShape, Direction], StoneShape3d] = {}


def rotate_stone(stone: StoneShape, direction: Direction) -> StoneShape3d:
    index: tuple[StoneShape, Direction] = (stone, direction)
    if index not in _rotate_cache:
        _rotate_cache[index] = tuple(transform(p, direction) for p in stone)
    return _rotate_cache[index]


STONE_DIRECTIONS: dict[StoneColor, Tuple[Direction, ...]] = {}
for color, stone in STONES.items():
    normalized_shapes: set[StoneShape3d] = set()
    directions: list[Direction] = []
    for direction in all_directions:
        shape = rotate_stone(stone=stone, direction=direction)
        min_x = min(p[0] for p in shape)
        min_y = min(p[1] for p in shape)
        min_z = min(p[2] for p in shape)
        normalized_shape = tuple(sorted(
            apply_stone(
                stone=shape,
                fn=lambda p: (
                    p[0] - min_x,
                    p[1] - min_y,
                    p[2] - min_z,
                )
            ),
            key=lambda p: f"{p[0]}:{p[1]}:{p[2]}"
        ))
        if normalized_shape not in normalized_shapes:
            directions.append(direction)
            normalized_shapes.add(normalized_shape)

    STONE_DIRECTIONS[color] = tuple(directions)


def remove_stone(stone_color: StoneColor):
    marker = STONE_MARKER[stone_color]
    for z, level in enumerate(board):
        for y, line in enumerate(level):
            for x, c in enumerate(line):
                if c == marker:
                    board[z][y][x] = EMPTY
    if stone_color in used_stones:
        used_stones.remove(stone_color)


def check_coordinates(x: int, y: int, z: int) -> bool:
    return (
        x >= 0 and y >= 0 and z >= 0 and
        z < len(board) and y < len(board[z]) and x < len(board[z][y])
    )


def place_stone(stone_color: StoneColor, direction: Direction, start: BoardPostion) -> bool:
    shape = rotate_stone(STONES[stone_color], direction)
    shape = apply_stone(
        stone=shape,
        fn=lambda p: (p[0] + start[0], p[1] + start[1], p[2] + start[2])
    )

    marker = STONE_MARKER[stone_color]
    for (x, y, z) in shape:

        if not check_coordinates(x, y, z) or board[z][y][x] != EMPTY:
            remove_stone(stone_color)
            return False

        board[z][y][x] = marker

    used_stones.add(stone_color)
    return True


def test_board() -> bool:
    checked: set[BoardPostion] = set()

    def test_xy(x: int, y: int, z: int) -> int:
        if (x, y, z) in checked:
            return 0

        if not check_coordinates(x, y, z):
            return 0

        if board[z][y][x] != EMPTY:
            return 0

        checked.add((x, y, z))

        result = 1
        for d in (
            (0, 0, 1), (-1, 0, 1), (-1, -1, 1), (0, -1, 1),
            (-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0),
            (0, 0, -1), (1, 0, -1), (1, 1, -1), (0, 1, -1),
        ):
            result += test_xy(x + d[0], y + d[1], z + d[2])
        return result

    for z, level in enumerate(board):
        for y, line in enumerate(level):
            for x in range(len(line)):
                if (x, y, z) in checked:
                    continue
                t = test_xy(x, y, z)
                if t > 0 and t < 3:
                    # print_board()
                    # print(t, (x, y), checked, "XXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    return False
    return True


def place_next_stone(colors: list[StoneColor]):
    color = colors[0]
    colors = colors[1:]
    for z, level in enumerate(board):
        for y, line in enumerate(level):
            for x in range(len(line)):
                for direction in STONE_DIRECTIONS[color]:
                    if place_stone(color, direction, (x, y, z)):
                        if len(colors) == 0:
                            print_board(True)
                            return
                            # print_board(True, True)
                            # exit()
                        if test_board():
                            print_board()
                            place_next_stone(colors)
                        remove_stone(color)


GAME: int = 0
TEST = False

if GAME == 1:  # pyright: ignore[reportUnnecessaryComparison]
    place_stone("green", (0, 1, -1), (0, 0, 0))
    place_stone("pink", (0, 0, 1), (1, 2, 0))
    # place_stone("orange", 3, (4, 0))
    # place_stone("blue", -1, (6, 0))
    # place_stone("red", 1, (4, 2))
    # place_stone("lime", 4, (6, 3))
    # place_stone("cyan", -3, (3, 3))
    # place_stone("green", 2, (2, 1))
    # place_stone("lightblue", 3, (0, 2))
elif GAME == 32:  # pyright: ignore[reportUnnecessaryComparison]
    pass
    # place_stone("lime", 4, (0, 0))
    # place_stone("yellow", -3, (2, 0))
    # place_stone("cyan", 3, (6, 0))
    # place_stone("red", -2, (4, 1))


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
