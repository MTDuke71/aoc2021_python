"""Day 11: Dumbo Octopus.

The input is a 10x10 grid of digits 0-9, one octopus energy level per cell.
parse_input turns it into a list of rows of ints.

One step is three phases: every octopus gains 1; any octopus above 9 flashes,
which gives each of its eight neighbours (diagonals count) another 1 and can
push them over 9 in turn; finally every octopus that flashed drops to 0.

step() runs the cascade with a work stack.  A cell is pushed at the moment
its energy becomes exactly 10, which happens once per step at most because
energy only rises during the cascade.  That is the whole "an octopus flashes
at most once per step" rule: a flashed cell keeps soaking up neighbours'
flashes (11, 12, ...) without being pushed again, and the reset to 0 waits
until the cascade is over.

Part 1 counts the flashes over 100 steps.

Part 2 asks for the first step on which every octopus flashes.  It runs the
same step() from the original grid until one step's flash count equals the
number of cells.  Nothing guarantees an arbitrary grid ever gets there (the
two-cell grid "05" never does), so part2 remembers every state it has seen
and raises when one repeats: the step is deterministic, so a repeat without
a full flash means there never will be one.
"""

from collections.abc import Iterator
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day11.txt"

Grid = list[list[int]]

STEPS = 100


def parse_input(raw: str) -> Grid:
    """One row of ints per non-blank line; rows must be digits and the same width."""
    grid = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.isdigit() or not line.isascii():
            raise ValueError(f"energy row is not all digits: {line!r}")
        grid.append([int(ch) for ch in line])
    if len({len(row) for row in grid}) > 1:
        raise ValueError("energy rows differ in length")
    return grid


def neighbours(grid: Grid, r: int, c: int) -> Iterator[tuple[int, int]]:
    """The up-to-eight in-bounds neighbours of (r, c), diagonals included."""
    for nr in (r - 1, r, r + 1):
        for nc in (c - 1, c, c + 1):
            if (nr, nc) != (r, c) and 0 <= nr < len(grid) and 0 <= nc < len(grid[nr]):
                yield nr, nc


def step(grid: Grid) -> int:
    """Advance the grid one step in place; return how many octopuses flashed."""
    flashing = []
    for r, row in enumerate(grid):
        for c in range(len(row)):
            row[c] += 1
            if row[c] == 10:
                flashing.append((r, c))

    flashes = 0
    while flashing:
        r, c = flashing.pop()
        flashes += 1
        for nr, nc in neighbours(grid, r, c):
            grid[nr][nc] += 1
            if grid[nr][nc] == 10:
                flashing.append((nr, nc))

    for row in grid:
        for c, energy in enumerate(row):
            if energy > 9:
                row[c] = 0
    return flashes


def part1(parsed: Grid) -> int:
    grid = [row[:] for row in parsed]  # step mutates; part 2 needs the original
    return sum(step(grid) for _ in range(STEPS))


def part2(parsed: Grid) -> int:
    grid = [row[:] for row in parsed]
    cells = sum(len(row) for row in grid)
    if cells == 0:
        raise ValueError("no octopuses")
    seen = set()
    steps = 0
    while True:
        state = tuple(map(tuple, grid))
        if state in seen:
            raise ValueError(f"the grid repeats after {steps} steps without ever flashing all at once")
        seen.add(state)
        steps += 1
        if step(grid) == cells:
            return steps


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
