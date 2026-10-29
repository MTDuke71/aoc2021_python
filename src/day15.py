"""Day 15: Chiton.

The input is a grid of digits, one risk level per cell.  A path runs from the
top-left cell to the bottom-right one in orthogonal steps, and its total risk
is the sum of the cells it enters: the start is never entered, so it is never
counted.  Part 1 asks for the lowest total risk.  Part 2 asks the same of the
full cave: the scanned grid is one tile of a 5x5 arrangement, each tile one
higher than the tile above it or to its left, with 10 wrapping back to 1.

That is a shortest-path problem on a graph whose edges carry the risk of the
cell they lead into, and every weight is non-negative, so it is Dijkstra.
Moves are not restricted to right and down: the cheapest path can double back
up or left around an expensive wall, so a one-pass row-by-row DP is not enough
in general (the tests carry a grid where it gets the wrong answer).

parse_input turns the text into a tuple of rows of ints and checks the grid is
rectangular and all digits 1-9.  lowest_risk() runs Dijkstra from corner to corner.
tile() builds part 2's full map; the same lowest_risk() then runs on it.
"""

import heapq
from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day15.txt"

Grid = tuple[tuple[int, ...], ...]


def parse_input(raw: str) -> Grid:
    """One row of ints per non-blank line; rows must be digits 1-9 and the same width.

    0 is refused: part 2's "above 9 wraps back to 1" only defines risks 1-9, and
    tile()'s arithmetic relies on that.
    """
    rows = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.isdigit() or not line.isascii() or "0" in line:
            raise ValueError(f"risk row is not all digits 1-9: {line!r}")
        rows.append(tuple(int(ch) for ch in line))
    if not rows:
        raise ValueError("empty input")
    if len({len(row) for row in rows}) > 1:
        raise ValueError("risk rows differ in length")
    return tuple(rows)


def lowest_risk(grid: Grid) -> int:
    """Dijkstra from the top-left cell to the bottom-right; returns the path's total risk.

    `best` holds the lowest risk found so far for each cell.  The heap can hold
    stale entries for a cell whose risk has since dropped; they are skipped when
    popped.  The first time the target is popped its risk is final, because
    every entry still on the heap is at least as large and weights are >= 0.
    """
    height, width = len(grid), len(grid[0])
    target = (height - 1, width - 1)
    best = {(0, 0): 0}
    heap = [(0, 0, 0)]
    while heap:
        risk, r, c = heapq.heappop(heap)
        if (r, c) == target:
            return risk
        if risk > best[r, c]:
            continue
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < height and 0 <= nc < width:
                nxt = risk + grid[nr][nc]
                if nxt < best.get((nr, nc), nxt + 1):
                    best[nr, nc] = nxt
                    heapq.heappush(heap, (nxt, nr, nc))
    raise AssertionError("unreachable: a rectangular grid is connected")


def tile(grid: Grid, times: int) -> Grid:
    """The full map: `grid` repeated times x times, tile (i, j) raised by i + j, wrapping 9 -> 1.

    Risks run 1..9, so "add k, then wrap above 9 back to 1" is (v + k - 1) % 9 + 1:
    shift to 0..8, add mod 9, shift back.
    """
    return tuple(
        tuple((v + i + j - 1) % 9 + 1 for j in range(times) for v in row)
        for i in range(times)
        for row in grid
    )


def part1(parsed: Grid) -> int:
    return lowest_risk(parsed)


def part2(parsed: Grid) -> int:
    return lowest_risk(tile(parsed, 5))


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
