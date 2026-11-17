"""Day 22: Reactor Reboot.

A 3-D grid of unit cubes, all off.  Each reboot step turns every cube in an
axis-aligned cuboid on or off; later steps override earlier ones.  The answer
is how many cubes are on at the end.

Part 1 counts only cubes inside the initialisation region -50..50 on every
axis; part 2 counts every cube.  The input's cuboids span ~10^5 per axis
(part 2's answer is ~10^15 cubes), so cubes are never stored one by one,
not even for part 1.  Instead the on-set is kept as
a signed list of cuboids (inclusion-exclusion):

  * Every existing entry (box, sign) that overlaps the new step's cuboid C
    gets a cancelling entry (box & C, -sign).  Summed, those cancel exactly
    the part of the current on-set that lies inside C, so after them,
    nothing inside C is counted.
  * An "on" step then adds (C, +1).  An "off" step adds nothing.

The cube count is sum(sign * volume) over the list.  Equal boxes are merged
into one Counter key (their signs add, zeros are dropped), which keeps the
list from doubling every time steps repeat an overlap.

Part 2 is that procedure on the steps as given.  Part 1 clips each step to
the region before running it.
Clipping is exact, not an approximation: whether a cube inside the region is
on depends only on the steps that cover it, and clipping keeps exactly
those.

Coordinates are inclusive (x0..x1), as the statement words them, so a
cuboid's volume is (x1 - x0 + 1) * ... .
"""

import re
from collections import Counter
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day22.txt"

INIT_LIMIT = 50


class Cuboid(NamedTuple):
    """Inclusive ranges x0..x1, y0..y1, z0..z1 (each lo <= hi)."""

    x0: int
    x1: int
    y0: int
    y1: int
    z0: int
    z1: int

    def volume(self) -> int:
        return (self.x1 - self.x0 + 1) * (self.y1 - self.y0 + 1) * (self.z1 - self.z0 + 1)

    def intersect(self, other: "Cuboid") -> "Cuboid | None":
        """The overlap of two cuboids, or None when they share no cube."""
        x0, x1 = max(self.x0, other.x0), min(self.x1, other.x1)
        y0, y1 = max(self.y0, other.y0), min(self.y1, other.y1)
        z0, z1 = max(self.z0, other.z0), min(self.z1, other.z1)
        if x0 > x1 or y0 > y1 or z0 > z1:
            return None
        return Cuboid(x0, x1, y0, y1, z0, z1)


class Step(NamedTuple):
    on: bool
    box: Cuboid


INIT_REGION = Cuboid(-INIT_LIMIT, INIT_LIMIT, -INIT_LIMIT, INIT_LIMIT, -INIT_LIMIT, INIT_LIMIT)

STEP_RE = re.compile(
    r"(on|off) x=(-?\d+)\.\.(-?\d+),y=(-?\d+)\.\.(-?\d+),z=(-?\d+)\.\.(-?\d+)",
)


def parse_input(raw: str) -> list[Step]:
    steps = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        m = STEP_RE.fullmatch(line)
        if m is None:
            raise ValueError(f"not a reboot step: {line!r}")
        box = Cuboid(*map(int, m.groups()[1:]))
        if box.x0 > box.x1 or box.y0 > box.y1 or box.z0 > box.z1:
            raise ValueError(f"empty range (lo > hi): {line!r}")
        steps.append(Step(m[1] == "on", box))
    return steps


def count_on(steps: list[Step], region: Cuboid | None = None) -> int:
    """Cubes on after all steps, counting only inside `region` (None = everywhere)."""
    signed: Counter[Cuboid] = Counter()
    for on, box in steps:
        if region is not None:
            box = box.intersect(region)
            if box is None:
                continue
        update: Counter[Cuboid] = Counter()
        for prev, sign in signed.items():
            overlap = box.intersect(prev)
            if overlap is not None:
                update[overlap] -= sign
        if on:
            update[box] += 1
        for b, s in update.items():
            signed[b] += s
            if signed[b] == 0:
                del signed[b]
    return sum(sign * b.volume() for b, sign in signed.items())


def part1(steps: list[Step]) -> int:
    return count_on(steps, INIT_REGION)


def part2(steps: list[Step]) -> int:
    return count_on(steps)


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
