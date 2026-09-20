"""Day 2: Dive!.

Not solved yet.  part1 and part2 raise NotImplementedError; that is what
tests/conftest.py and bench.py key on to skip the day, so an unsolved day
can never show up as an answer or a timing.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day02.txt"


def parse_input(raw: str) -> list[str]:
    return [line for line in raw.splitlines() if line.strip()]


def part1(parsed: list[str]) -> int:
    raise NotImplementedError("day02 part1")


def part2(parsed: list[str]) -> int:
    raise NotImplementedError("day02 part2")


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
