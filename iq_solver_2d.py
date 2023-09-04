from typing import Tuple
from iq_solver_base import Board, Direction, IqSolverBase, DirectionOrientation, DirectionRotation

from stones import EMPTY, StoneColor

BOARD_WIDTH = 11
BOARD_HEIGHT = 5


class IqSolver2d(IqSolverBase):
    def _init_board(self) -> Board:
        return [
            [
                [EMPTY for _ in range(BOARD_WIDTH)]
                for _ in range(BOARD_HEIGHT)
            ]
        ]

    def _init_all_directions(self) -> Tuple[Direction, ...]:
        return tuple(
            (0, orientation, rotation)  # type: ignore
            for orientation in (0, 1, 2, 3)
            for rotation in ((1, -1))
        )


GAME: int = 0
TEST = False

solver = IqSolver2d(file_name_color=f"{__file__}.{GAME}.solution-color.txt",
                    file_name_text=f"{__file__}.{GAME}.solution.txt")


def place_stone(color: StoneColor, direction: tuple[DirectionOrientation, DirectionRotation], start: tuple[int, int]):
    solver.place_stone(color, (0, *direction), start=(*start, 0))


if GAME == 1:  # pyright: ignore[reportUnnecessaryComparison]
    place_stone("pink", (1, 1), (0, 0))
    place_stone("yellow", (0, 1), (1, 0))
    place_stone("orange", (2, 1), (6, 2))
    place_stone("blue", (0, -1), (6, 1))
    place_stone("red", (0, 1), (4, 2))
    place_stone("lime", (1, 1), (7, 3))
    place_stone("cyan", (1, 1), (3, 3))
    place_stone("green", (3, 1), (2, 3))
    place_stone("lightblue", (2, 1), (2, 4))
elif GAME == 32:  # pyright: ignore[reportUnnecessaryComparison]
    place_stone("lime", (1, 1), (1, 0))
    place_stone("yellow", (2, -1), (5, 0))
    place_stone("cyan", (2, 1), (7, 0))
    place_stone("red", (1, -1), (4, 1))


if TEST:
    solver.print_board(no_dups=False)
else:
    solver.load_board()
    solver.solve()
    solver.print_solutions()
    # solver.save_solutions(f"{__file__}.{GAME}.solution.txt")
