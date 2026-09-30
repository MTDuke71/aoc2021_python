"""Day 7: The Treachery of Whales.

Input is one line of comma-separated crab positions.

Part 1 cost is the sum of |x - target|.  That sum is minimised at a median
of the positions: moving the target one step right costs +1 for every crab
at or left of it and saves 1 for every crab to its right, so the total stops
falling exactly when half the crabs are on each side.  For an even count any
point between the two middle values ties, and `sorted[n // 2]` is one of
them.  No search over targets is needed.

Part 2 charges d * (d + 1) / 2 for a move of d steps (1 + 2 + ... + d).  The
total is f(t) = sum((t - p)^2) / 2 + sum(|t - p|) / 2.  The first term is a
parabola with its minimum at the mean and slope n * (t - mean); the second
has slope between -n / 2 and n / 2.  The slopes can only cancel within half
a step of the mean, so the integer optimum is floor(mean) or floor(mean) + 1
and two evaluations suffice.  The tests pin this against a full search.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day07.txt"


def parse_input(raw: str) -> list[int]:
    """Crab positions, sorted ascending (both parts want the order)."""
    positions = sorted(int(field) for field in raw.replace(",", " ").split())
    if not positions:
        raise ValueError("no crab positions in input")
    return positions


def linear_fuel(positions: list[int], target: int) -> int:
    """Fuel to bring every crab to `target` at 1 fuel per step."""
    return sum(abs(p - target) for p in positions)


def part1(positions: list[int]) -> int:
    return linear_fuel(positions, positions[len(positions) // 2])


def triangular_fuel(positions: list[int], target: int) -> int:
    """Fuel to bring every crab to `target` when step k costs k fuel."""
    return sum(d * (d + 1) // 2 for d in (abs(p - target) for p in positions))


def part2(positions: list[int]) -> int:
    low = sum(positions) // len(positions)
    return min(triangular_fuel(positions, low), triangular_fuel(positions, low + 1))


def solve(raw: str) -> tuple[int, int]:
    positions = parse_input(raw)
    return part1(positions), part2(positions)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    positions = parse_input(INPUT.read_text())
    print(f"part1={part1(positions)}")
    print(f"part2={part2(positions)}")


if __name__ == "__main__":
    raise SystemExit(main())
