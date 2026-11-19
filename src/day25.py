"""Day 25: Sea Cucumber.

Two herds on a wrapping (toroidal) grid.  Each step the east herd (`>`) moves
as one, then the south herd (`v`) moves as one: every member of the moving
herd first checks whether the cell ahead (wrapping at the edges) is empty,
then all those that saw an empty cell move together.  Part 1 is the first
step on which nobody moves.

The state is two frozensets of (row, col) positions, one per herd.  "Moves as
one" falls out of building the next set from the *old* occupancy: no
cucumber can see a cell vacated or filled earlier in the same half-step.

Part 2 has no puzzle; the star is given for holding the other 49.  It
returns 0 so the five-name contract and the bench table still have an int
(same as aoc2020's day 25).
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day25.txt"

Cell = tuple[int, int]


class Seafloor(NamedTuple):
    height: int
    width: int
    east: frozenset[Cell]
    south: frozenset[Cell]


def parse_input(raw: str) -> Seafloor:
    rows = [line.strip() for line in raw.splitlines() if line.strip()]
    if not rows:
        raise ValueError("empty map")
    width = len(rows[0])
    east, south = set(), set()
    for r, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"row {r} has width {len(row)}, expected {width}")
        for c, ch in enumerate(row):
            if ch == ">":
                east.add((r, c))
            elif ch == "v":
                south.add((r, c))
            elif ch != ".":
                raise ValueError(f"unexpected {ch!r} at row {r}, col {c}")
    return Seafloor(len(rows), width, frozenset(east), frozenset(south))


def move_herd(herd: frozenset[Cell], blocker: frozenset[Cell], ahead) -> frozenset[Cell]:
    """One half-step: every member of `herd` whose cell `ahead` is empty moves.

    Occupancy is read from the sets as they stand *before* the move, which
    is the "all consider, then all move" rule.  `blocker` is the other herd.
    """
    return frozenset(
        nxt if (nxt := ahead(cell)) not in herd and nxt not in blocker else cell for cell in herd
    )


def step(floor: Seafloor) -> Seafloor:
    """East herd moves, then south herd moves against the *updated* east herd."""
    h, w = floor.height, floor.width
    east = move_herd(floor.east, floor.south, lambda rc: (rc[0], (rc[1] + 1) % w))
    south = move_herd(floor.south, east, lambda rc: ((rc[0] + 1) % h, rc[1]))
    return floor._replace(east=east, south=south)


def render(floor: Seafloor) -> str:
    """The map in the statement's notation, for tests and debugging."""
    grid = [["."] * floor.width for _ in range(floor.height)]
    for r, c in floor.east:
        grid[r][c] = ">"
    for r, c in floor.south:
        grid[r][c] = "v"
    return "\n".join("".join(row) for row in grid)


def part1(parsed: Seafloor) -> int:
    floor, steps = parsed, 0
    while True:
        steps += 1
        nxt = step(floor)
        if nxt == floor:
            return steps
        floor = nxt


def part2(parsed: Seafloor) -> int:
    """There is no second puzzle on day 25; the star is given."""
    return 0


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
