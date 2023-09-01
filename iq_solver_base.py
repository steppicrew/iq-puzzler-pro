from typing import Callable, Literal, Tuple

from stones import EMPTY, STONE_MARKER, STONES, StoneColor, StoneShape


Coordinate = tuple[int, int, int]
StoneShape3d = Tuple[Coordinate, ...]

Board = list[list[list[str]]]

DirectionLevel = Literal[-1, 0, 1]  # lower, same, upper level
# (ne, se, sw, nw) or (e, s, w, n)
DirectionOrientation = Literal[0, 1, 2, 3]
DirectionRotation = Literal[1, -1]  # 0°, 180° or up, down
Direction = tuple[DirectionLevel, DirectionOrientation, DirectionRotation]


class IqSolverBase:
    def __init__(self) -> None:
        super().__init__()
        self.board = self._init_board()
        self.all_directions: Tuple[Direction, ...] = self._init_all_directions(
        )
        self.used_stones: set[StoneColor] = set()
        self.found_boards: set[str] = set()
        self._init_stone_directions()

    def _init_board(self) -> Board:
        raise NotImplementedError()

    def _init_all_directions(self) -> Tuple[Direction, ...]:
        raise NotImplementedError()

    def _init_stone_directions(self):
        self.stone_rotations: dict[
            StoneColor, Tuple[StoneShape3d, ...]
        ] = {}
        self.stone_directions: dict[
            StoneColor, Tuple[Direction, ...]
        ] = {}
        for color, stone in STONES.items():
            normalized_shapes: set[str] = set()
            shapes: list[StoneShape3d] = []
            directions: list[Direction] = []
            for direction in self.all_directions:
                shape = self.rotate_stone(
                    stone=stone, direction=direction)
                mins = tuple(min(p[i] for p in shape)
                             for i in range(len(shape[0])))
                normalized_shape = ','.join(
                    sorted(
                        ':'.join(
                            str(c - m)
                            for c, m in zip(p, mins)
                        )
                        for p in shape
                    )
                )
                if normalized_shape not in normalized_shapes:
                    shapes.append(shape)
                    directions.append(direction)
                    normalized_shapes.add(normalized_shape)

                self.stone_rotations[color] = tuple(shapes)
                self.stone_directions[color] = tuple(directions)

    def _board_to_str(self):
        lines: Tuple[list[str], ...] = tuple([] for _ in self.board[0])

        for level in self.board:
            for y, line in enumerate(level):
                lines[y].append(' '.join(line))

        return '\n'.join('  '.join(line) for line in lines)

    def save_board(self):
        board = self._board_to_str()
        self.found_boards.add(board)

    def print_board(self, no_dups: bool = False):
        board = self._board_to_str()
        if no_dups and board in self.found_boards:
            return None

        print(board)
        print()

    def transform(self, p: tuple[int, int], direction: Direction) -> Coordinate:
        level, orientation, rotation = direction

        # orientation: 0: right, 1: down, 2: left, 3: up
        # orientation: 0: ne, 1: se, 2: sw, 3: nw

        dx: Coordinate
        dy: Coordinate
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

    def apply_stone(self, stone: Tuple[Coordinate, ...], fn: Callable[[Coordinate], Coordinate]) -> Tuple[Coordinate, ...]:
        return tuple(fn(p) for p in stone)

    def rotate_stone(self, stone: StoneShape, direction: Direction) -> StoneShape3d:
        return tuple(self.transform(p, direction) for p in stone)

    def remove_stone(self, stone_color: StoneColor):
        marker = STONE_MARKER[stone_color]

        for level in self.board:
            for line in level:
                for x, cell in enumerate(line):
                    if cell == marker:
                        line[x] = EMPTY

        if stone_color in self.used_stones:
            self.used_stones.remove(stone_color)

    def check_coordinates(self, x: int, y: int, z: int) -> bool:
        return (
            x >= 0 and y >= 0 and z >= 0 and
            z < len(self.board) and
            y < len(self.board[z]) and
            x < len(self.board[z][y])
        )

    def _place_stone(self, stone_color: StoneColor, shape: StoneShape3d, start: Coordinate) -> bool:
        shape = self.apply_stone(
            stone=shape,
            fn=lambda p: (p[0] + start[0], p[1] + start[1], p[2] + start[2])
        )

        marker = STONE_MARKER[stone_color]
        for (x, y, z) in shape:

            if not self.check_coordinates(x, y, z) or self.board[z][y][x] != EMPTY:
                self.remove_stone(stone_color)
                return False

            self.board[z][y][x] = marker

        self.used_stones.add(stone_color)
        return True

    def test_board(self) -> bool:
        checked: set[Coordinate] = set()

        def test_xy(x: int, y: int, z: int) -> int:
            if (x, y, z) in checked:
                return 0

            if not self.check_coordinates(x, y, z):
                return 0

            if self.board[z][y][x] != EMPTY:
                return 0

            checked.add((x, y, z))

            result = 1
            for dx, dy, dz in (
                (0, 0, 1), (-1, 0, 1), (-1, -1, 1), (0, -1, 1),
                (-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0),
                (0, 0, -1), (1, 0, -1), (1, 1, -1), (0, 1, -1),
            ):
                result += test_xy(x + dx, y + dy, z + dz)
            return result

        for z, level in enumerate(self.board):
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

    def place_next_stone(self, colors: list[StoneColor]):
        color = colors[0]
        colors = colors[1:]
        for z, level in enumerate(self.board):
            for y, line in enumerate(level):
                for x in range(len(line)):
                    for shape in self.stone_rotations[color]:
                        if self._place_stone(color, shape, (x, y, z)):
                            if len(colors) == 0:
                                self.print_board(True)
                                self.save_board()
                                return
                                # print_board(True, True)
                                # exit()
                            if self.test_board():
                                self.print_board()
                                self.place_next_stone(colors)
                            self.remove_stone(color)

    def place_stone(self, color: StoneColor, direction: Direction, start: Coordinate):
        shape = self.rotate_stone(stone=STONES[color], direction=direction)
        # print(self.apply_stone(
        #    stone=shape,
        #    fn=lambda p: (p[0] + start[0], p[1] + start[1], p[2] + start[2])
        # ))
        return self._place_stone(color, shape, start)

    def solve(self):
        remaining_colors: list[StoneColor] = [
            c for c in STONES if c not in self.used_stones
        ]
        self.place_next_stone(remaining_colors)

    def print_solutions(self):
        for b in self.found_boards:
            print(b)
            print()

    def save_solutions(self, file_name: str):
        with open(file_name, mode="w") as file:
            file.write("\n".join(f"{b}\n" for b in self.found_boards))

    def print_test_stone_directions(self, color: StoneColor, start: Coordinate):
        for direction in self.stone_directions[color]:
            if self.place_stone(color, direction, start):
                print(direction)
                self.print_board()
                self.remove_stone(color)
