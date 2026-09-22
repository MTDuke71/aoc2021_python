"""Day 2: Dive!.

Input is one command per line: `forward X`, `down X` or `up X`.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day02.txt"


def parse_input(raw: str) -> list[tuple[int, int]]:
    """Each command as a (forward, dive) pair of signed deltas.

    `forward 5` -> (5, 0), `down 5` -> (0, 5), `up 3` -> (0, -3).  Down is
    the positive direction.  What `dive` is a delta *of* is up to the caller:
    part 1 reads it as depth, part 2 as aim.
    """
    moves = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        command, amount = line.split()
        x = int(amount)
        if command == "forward":
            moves.append((x, 0))
        elif command == "down":
            moves.append((0, x))
        elif command == "up":
            moves.append((0, -x))
        else:
            raise ValueError(f"unknown command: {line!r}")
    return moves


def part1(moves: list[tuple[int, int]]) -> int:
    horizontal = depth = 0
    for forward, dive in moves:
        horizontal += forward
        depth += dive
    return horizontal * depth


def steer(moves: list[tuple[int, int]]) -> tuple[int, int, int]:
    """Part 2's rules: (horizontal, depth, aim) after the whole course.

    Every pair has one zero in it, so both updates can run unconditionally:
    a down/up has forward == 0 and moves nothing, a forward has dive == 0
    and leaves aim alone.
    """
    horizontal = depth = aim = 0
    for forward, dive in moves:
        aim += dive
        horizontal += forward
        depth += aim * forward
    return horizontal, depth, aim


def part2(moves: list[tuple[int, int]]) -> int:
    horizontal, depth, _ = steer(moves)
    return horizontal * depth


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
