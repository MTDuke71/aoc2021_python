"""Day 0: The Tyranny of the Rocket Equation (tutorial dry run).

Input is one integer module mass per line.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day00.txt"


def parse_input(raw: str) -> list[int]:
    return [int(line) for line in raw.splitlines() if line.strip()]


def fuel(mass: int) -> int:
    """Base equation: floor(mass / 3) - 2."""
    return mass // 3 - 2


def total_fuel(mass: int) -> int:
    """Part 2: fuel for the fuel, recursively, until a step is <= 0."""
    total = 0
    f = fuel(mass)
    while f > 0:
        total += f
        f = fuel(f)
    return total


def part1(data: list[int]) -> int:
    return sum(fuel(m) for m in data)


def part2(data: list[int]) -> int:
    return sum(total_fuel(m) for m in data)


def solve(raw: str) -> tuple[int, int]:
    data = parse_input(raw)
    return part1(data), part2(data)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
