"""Day 1: Sonar Sweep.

Input is one integer sea-floor depth per line, in sweep order.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day01.txt"


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def count_increases(depths: list[int], gap: int) -> int:
    """How many readings are larger than the reading `gap` places earlier.

    gap=1 is part 1 as stated.  gap=3 is part 2: adjacent three-wide windows
    share their two middle readings, so comparing the window sums is the same
    as comparing the one reading each window has that the other does not.
    """
    return sum(later > earlier for earlier, later in zip(depths, depths[gap:]))


def part1(depths: list[int]) -> int:
    return count_increases(depths, 1)


def part2(depths: list[int]) -> int:
    return count_increases(depths, 3)


def solve(raw: str) -> tuple[int, int]:
    depths = parse_input(raw)
    return part1(depths), part2(depths)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
