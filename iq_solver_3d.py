from typing import Tuple
from iq_solver_base import Board, IqSolverBase, Direction

from stones import EMPTY

BASE_WIDTH = 5


class IqSolver3d(IqSolverBase):
    def _init_board(self) -> Board:
        return [
            [
                [EMPTY for _ in range(BASE_WIDTH - h)]
                for _ in range(BASE_WIDTH - h)
            ]
            for h in range(BASE_WIDTH)
        ]

    def _init_all_directions(self) -> Tuple[Direction, ...]:
        return tuple(
            (level, orientation, rotation)  # type: ignore
            for level in (-1, 0, 1)
            for orientation in (0, 1, 2, 3)
            for rotation in ((1, -1))
        )


solver = IqSolver3d()

GAME: int = 1
TEST = False

if GAME == 1:  # pyright: ignore[reportUnnecessaryComparison]
    solver.place_stone("green", (0, 1, -1), (0, 0, 0))
    solver.place_stone("pink", (0, 1, 1), (3, 0, 0))
    solver.place_stone("red", (0, 1, -1), (0, 3, 0))
    solver.place_stone("lightred", (-1, 1, 1), (0, 4, 0))
    # solver.print_test_stone_directions("lightgreen", (0, 2, 1))
    solver.place_stone("lightgreen", (0, 0, 1), (1, 2, 1))
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
    solver.print_board(False)
else:
    solver.solve()
    solver.print_solutions()
    solver.save_solutions(f"{__file__}.{GAME}.solution.txt")
