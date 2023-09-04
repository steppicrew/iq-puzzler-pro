import os
import re
from typing import Callable, Literal, Tuple

from stones import EMPTY, STONE_MARKER, STONE_SIZES, STONES, StoneColor, StoneShape


Coordinate = tuple[int, int, int]
StoneShape3d = Tuple[Coordinate, ...]

Board = list[list[list[StoneColor]]]

DirectionLevel = Literal[-1, 0, 1]  # lower, same, upper level
# (ne, se, sw, nw) or (e, s, w, n)
DirectionOrientation = Literal[0, 1, 2, 3]
DirectionRotation = Literal[1, -1]  # 0°, 180° or up, down
Direction = tuple[DirectionLevel, DirectionOrientation, DirectionRotation]


class IqSolverBase:
    def __init__(
            self,
            file_name_text: str | None = None,
            file_name_color: str | None = None,
            print_all_boards: bool = True,
    ) -> None:
        super().__init__()
        self.file_name_text = file_name_text
        self.file_name_color = file_name_color
        self.print_all_boards = print_all_boards
        self.board = self._init_board()
        self.all_directions: Tuple[Direction, ...] = self._init_all_directions(
        )
        self.found_boards: set[str] = set()
        self._init_stone_directions()
        self.last_board: str | None = None

    def _init_board(self) -> Board:
        raise NotImplementedError()

    def _init_all_directions(self) -> Tuple[Direction, ...]:
        raise NotImplementedError()

    def _clone_board(self, board: Board) -> Board:
        return [
            [
                [
                    cell
                    for cell in line
                ]
                for line in level
            ]
            for level in board
        ]

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

    def _board_to_str(self, board: Board, marker_index: Literal[0, 1] = 0):
        lines: Tuple[list[str], ...] = tuple([] for _ in board[0])

        def _map(color: StoneColor):
            return STONE_MARKER[color][marker_index]

        for level in board:
            for y, line in enumerate(level):
                lines[y].append(' '.join(_map(c) for c in line))

        return '\n'.join('  '.join(line) for line in lines)

    def save_board(self, board: Board):
        board_str = self._board_to_str(board)
        self.found_boards.add(board_str)
        # return
        if self.file_name_color is not None:
            with open(self.file_name_color, mode="a", encoding='utf-8') as file:
                file.write(f"{board_str}\n\n")
        if self.file_name_text is not None:
            with open(self.file_name_text, mode="a", encoding='utf-8') as file:
                file.write(
                    f"{self._board_to_str(board=board, marker_index=1)}\n\n")

    def load_board(self):
        if self.file_name_text is not None and os.path.isfile(self.file_name_text):
            with open(self.file_name_text, "r", encoding='utf-8') as file:
                last_boards = [
                    board for board in file.read().split('\n\n') if board]
                if last_boards:
                    self.last_board = last_boards[-1]

    def print_board(self, board: Board | None = None, no_dups: bool = False):
        if board is None:
            board = self.board
        board_str = self._board_to_str(board)
        if no_dups and board_str in self.found_boards:
            return None

        print(board_str)
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

    def check_coordinates(self, board: Board, x: int, y: int, z: int) -> bool:
        return (
            x >= 0 and y >= 0 and z >= 0 and
            z < len(board) and
            y < len(board[z]) and
            x < len(board[z][y])
        )

    def _place_stone(self, board: Board, stone_color: StoneColor, shape: StoneShape3d, start: Coordinate) -> Board | None:
        shape = self.apply_stone(
            stone=shape,
            fn=lambda p: (p[0] + start[0], p[1] + start[1], p[2] + start[2])
        )

        board = self._clone_board(board)

        for (x, y, z) in shape:

            if not self.check_coordinates(board, x, y, z) or board[z][y][x] != EMPTY:
                return None

            board[z][y][x] = stone_color

        return board

    def test_board(self, board: Board, remaining_colors: list[StoneColor]) -> bool:
        checked: set[Coordinate] = set()

        max_size = max(STONE_SIZES[color] for color in remaining_colors)
        min_size = min(STONE_SIZES[color] for color in remaining_colors)

        def test_xy(x: int, y: int, z: int) -> int:
            if (x, y, z) in checked:
                return 0

            if not self.check_coordinates(board, x, y, z):
                return 0

            if board[z][y][x] != EMPTY:
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

        sizes: set[int] = set()

        for z, level in enumerate(board):
            for y, line in enumerate(level):
                for x in range(len(line)):
                    if (x, y, z) in checked:
                        continue
                    t = test_xy(x, y, z)
                    if t > 0:
                        if t < min_size:
                            return False

                        sizes.add(t)

        return max_size <= max(sizes)

    def _clear_last_board(self, board: str | None, color: StoneColor) -> str | None:
        if board is None:
            return None
        marker = STONE_MARKER[color][1]
        empty = STONE_MARKER[EMPTY][1]
        return re.sub(r'[^' + empty + marker + r'\n ]', empty, board)

    def place_next_stone(self, board: Board, colors: list[StoneColor]):
        color = colors[0]
        colors = colors[1:]
        last_stone = len(colors) == 0
        last_clean_board = self._clear_last_board(self.last_board, color)
        for z, level in enumerate(board):
            for y, line in enumerate(level):
                for x in range(len(line)):
                    for shape in self.stone_rotations[color]:
                        next_board: Board | None = self._place_stone(
                            board=board,
                            stone_color=color,
                            shape=shape,
                            start=(x, y, z)
                        )

                        if next_board is None:
                            continue

                        if last_clean_board is not None:
                            next_board_str: str | None = self._clear_last_board(
                                board=self._board_to_str(
                                    board=next_board, marker_index=1),
                                color=color
                            )
                            if next_board_str == last_clean_board:
                                last_clean_board = None
                                if last_stone:
                                    self.last_board = None
                                    self.print_board(next_board)
                                    # exit()
                                else:
                                    self.place_next_stone(next_board, colors)
                            continue

                        if self.print_all_boards:
                            self.print_board(next_board)
                            # exit()
                        if last_stone:
                            self.save_board(next_board)
                            # print_board(True, True)
                            # exit()
                        elif self.test_board(next_board, colors):
                            self.place_next_stone(next_board, colors)

    def place_stone(self, color: StoneColor, direction: Direction, start: Coordinate):
        shape = self.rotate_stone(stone=STONES[color], direction=direction)
        # print(self.apply_stone(
        #    stone=shape,
        #    fn=lambda p: (p[0] + start[0], p[1] + start[1], p[2] + start[2])
        # ))
        next_board = self._place_stone(self.board, color, shape, start)
        if next_board is not None:
            self.board = next_board
        return next_board

    def solve(self):
        used_colors = set(
            color
            for level in self.board
            for line in level
            for color in line
        )

        self.place_next_stone(
            board=self.board,
            colors=[
                c for c in STONES if c not in used_colors
            ]
        )

    def print_solutions(self):
        for b in self.found_boards:
            print(b)
            print()

    def save_solutions(self, file_name: str):
        with open(file_name, mode="w", encoding='utf-8') as file:
            file.write("\n".join(f"{b}\n" for b in self.found_boards))

    def print_test_stone_directions(self, color: StoneColor, start: Coordinate):
        for direction in self.stone_directions[color]:
            next_board = self.place_stone(color, direction, start)
            if next_board is not None:
                print(direction)
                self.print_board(next_board)
