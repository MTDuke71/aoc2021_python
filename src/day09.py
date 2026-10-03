"""Day 9: Smoke Basin.

The input is a rectangular grid of digits 0-9, a heightmap of the cave floor.
parse_input turns it into a list of rows of ints.

Part 1 finds the *low points*: cells strictly lower than every orthogonal
neighbour (edges have fewer neighbours, diagonals do not count).  The answer
is the sum of height + 1 over them.  A cell on a flat plateau is never low,
because "lower than" is strict.

Part 2 sizes the *basins*.  A 9 belongs to no basin and every other cell
drains to exactly one low point, so a basin is a connected region of non-9
cells (4-connected) and holds exactly one low point.  The code flood-fills
from each low point and multiplies the three biggest sizes.  The "one low
point per region" claim is the puzzle's promise, not a theorem about
arbitrary grids, so basin_sizes checks it and raises if it fails; the tests
pin it on the real input.
"""

from collections.abc import Iterator
from math import prod
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day09.txt"

Grid = list[list[int]]


def parse_input(raw: str) -> Grid:
    """One row of ints per non-blank line; rows must be digits and the same width."""
    grid = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.isdigit() or not line.isascii():
            raise ValueError(f"heightmap row is not all digits: {line!r}")
        grid.append([int(ch) for ch in line])
    if len({len(row) for row in grid}) > 1:
        raise ValueError("heightmap rows differ in length")
    return grid


def neighbours(grid: Grid, r: int, c: int) -> Iterator[tuple[int, int]]:
    """Orthogonal in-bounds neighbours of (r, c): up, down, left, right."""
    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[nr]):
            yield nr, nc


def low_points(grid: Grid) -> list[tuple[int, int]]:
    """(row, col) of every cell strictly lower than all of its neighbours."""
    return [
        (r, c)
        for r, row in enumerate(grid)
        for c, height in enumerate(row)
        if all(height < grid[nr][nc] for nr, nc in neighbours(grid, r, c))
    ]


def part1(grid: Grid) -> int:
    return sum(grid[r][c] + 1 for r, c in low_points(grid))


def basin_sizes(grid: Grid) -> list[int]:
    """Size of the basin around each low point, in low_points order."""
    claimed: set[tuple[int, int]] = set()
    sizes = []
    for start in low_points(grid):
        if start in claimed:
            raise ValueError(f"low point {start} shares a basin with another low point")
        claimed.add(start)
        stack = [start]
        size = 0
        while stack:
            r, c = stack.pop()
            size += 1
            for nr, nc in neighbours(grid, r, c):
                if grid[nr][nc] != 9 and (nr, nc) not in claimed:
                    claimed.add((nr, nc))
                    stack.append((nr, nc))
        sizes.append(size)
    return sizes


def part2(grid: Grid) -> int:
    sizes = basin_sizes(grid)
    if len(sizes) < 3:
        raise ValueError(f"need at least three basins, found {len(sizes)}")
    return prod(sorted(sizes)[-3:])


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
