"""Day 17: Trick Shot.

A probe starts at (0, 0) with an integer launch velocity (vx, vy).  Each
step adds the velocity to the position, then drag pulls vx one toward 0 and
gravity takes 1 off vy.  The input is a target rectangle; a launch "hits" if
the probe is inside it after some step.  Part 1 asks for the highest y any
hitting trajectory reaches; part 2 for how many distinct launches hit.

The two axes never interact: x depends only on vx and the step count t, y
only on vy and t.  So a launch hits exactly when some step t puts x in range
*and* y in range at the same t.  parse_target reads the rectangle, and
hits() lists every hitting launch by computing, per axis, the steps each
velocity spends inside its band and intersecting the two step sets.  Both
parts are reductions over that list, so parse_input builds it: part1 takes
the highest apex, part2 the count.

The search box is finite because the target sits right of and below the
origin (parse_target refuses anything else):
  vx in 1..x_max      -- vx <= 0 never moves right; vx > x_max overshoots on step 1.
  vy in y_min..-y_min-1 -- vy < y_min is below the target on step 1; a probe
                          fired up at vy comes back through y = 0 moving at
                          -(vy + 1), so vy >= -y_min jumps clean over it.
"""

import re
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day17.txt"

TARGET_RE = re.compile(r"target area: x=(-?\d+)\.\.(-?\d+), y=(-?\d+)\.\.(-?\d+)")


class Target(NamedTuple):
    x_min: int
    x_max: int
    y_min: int
    y_max: int


def parse_target(raw: str) -> Target:
    match = TARGET_RE.fullmatch(raw.strip())
    if match is None:
        raise ValueError(f"not a target area line: {raw.strip()!r}")
    target = Target(*map(int, match.groups()))
    if target.x_min > target.x_max or target.y_min > target.y_max:
        raise ValueError(f"empty target range: {target}")
    if target.x_min <= 0 or target.y_max >= 0:
        # The velocity bounds in the module docstring rely on this quadrant.
        raise ValueError(f"target must lie at x > 0 and y < 0: {target}")
    return target


def y_steps(vy: int, target: Target) -> list[int]:
    """Steps t >= 1 at which a probe launched with vertical speed vy is in the y band.

    Runs until the probe is below the band; it never comes back up.
    """
    steps = []
    y, t = 0, 0
    while y >= target.y_min:
        y += vy
        vy -= 1
        t += 1
        if target.y_min <= y <= target.y_max:
            steps.append(t)
    return steps


def x_steps(vx: int, target: Target, t_max: int) -> set[int]:
    """Steps 1..t_max at which a probe launched with horizontal speed vx is in the x band.

    Once drag brings vx to 0 the probe hangs at a fixed x, so a vx that
    stalls inside the band is in range at every later step -- hence the
    t_max cap supplied by the caller.
    """
    steps = set()
    x = 0
    for t in range(1, t_max + 1):
        x += vx
        vx -= vx > 0
        if x > target.x_max:
            break
        if x >= target.x_min:
            steps.add(t)
    return steps


def hits(target: Target) -> list[tuple[int, int]]:
    """Every launch velocity (vx, vy) whose probe is in the target after some step."""
    by_vy = {vy: y_steps(vy, target) for vy in range(target.y_min, -target.y_min)}
    by_vy = {vy: steps for vy, steps in by_vy.items() if steps}
    t_max = max(steps[-1] for steps in by_vy.values())
    by_vx = {vx: x_steps(vx, target, t_max) for vx in range(1, target.x_max + 1)}
    return [(vx, vy) for vx, xs in by_vx.items() if xs for vy, ys in by_vy.items() if not xs.isdisjoint(ys)]


def apex(vy: int) -> int:
    """Highest y on the trajectory: 0 if fired level or down, else vy + (vy-1) + ... + 1."""
    return vy * (vy + 1) // 2 if vy > 0 else 0


def parse_input(raw: str) -> list[tuple[int, int]]:
    """Every hitting launch velocity for the input's target area."""
    return hits(parse_target(raw))


def part1(shots: list[tuple[int, int]]) -> int:
    return max(apex(vy) for _, vy in shots)


def part2(shots: list[tuple[int, int]]) -> int:
    return len(shots)


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
