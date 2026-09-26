"""Day 5: Hydrothermal Venture.

Input is one line segment per line, `x1,y1 -> x2,y2`, both ends inclusive.

Every segment is walked cell by cell into a Counter of how many segments
cover each point; the answer is how many points are covered at least twice.
Part 1 walks only the horizontal and vertical segments, part 2 all of them.
A segment is walked with a unit step (sign of dx, sign of dy), which visits
exactly the lattice points of a horizontal, vertical or 45-degree line and
nothing else, so anything at another angle is refused rather than guessed.
"""

import re
from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day05.txt"

LINE = re.compile(r"(\d+),(\d+)\s*->\s*(\d+),(\d+)")

Point = tuple[int, int]


class Segment(NamedTuple):
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def axis_aligned(self) -> bool:
        return self.x1 == self.x2 or self.y1 == self.y2


def sign(n: int) -> int:
    return (n > 0) - (n < 0)


def points(seg: Segment) -> Iterator[Point]:
    """Every point the segment covers, both ends included."""
    dx, dy = seg.x2 - seg.x1, seg.y2 - seg.y1
    if dx and dy and abs(dx) != abs(dy):
        raise ValueError(f"{seg} is neither axis-aligned nor 45 degrees")
    sx, sy = sign(dx), sign(dy)
    for i in range(max(abs(dx), abs(dy)) + 1):
        yield seg.x1 + i * sx, seg.y1 + i * sy


def parse_input(raw: str) -> list[Segment]:
    segments = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE.fullmatch(line)
        if m is None:
            raise ValueError(f"bad segment: {line!r}")
        segments.append(Segment(*map(int, m.groups())))
    return segments


def overlaps(segments: Iterable[Segment]) -> int:
    """Number of points covered by at least two of the segments."""
    cover = Counter(p for seg in segments for p in points(seg))
    return sum(1 for n in cover.values() if n >= 2)


def part1(segments: list[Segment]) -> int:
    return overlaps(s for s in segments if s.axis_aligned)


def part2(segments: list[Segment]) -> int:
    return overlaps(segments)


def solve(raw: str) -> tuple[int, int]:
    segments = parse_input(raw)
    return part1(segments), part2(segments)


def main() -> None:
    segments = parse_input(INPUT.read_text())
    print(f"part1={part1(segments)}")
    print(f"part2={part2(segments)}")


if __name__ == "__main__":
    raise SystemExit(main())
