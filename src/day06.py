"""Day 6: Lanternfish.

Input is one line of comma-separated fish timers, each 0..8.

Fish are interchangeable, so nothing needs to know *which* fish has which
timer -- only how many fish sit at each timer value.  The state is a 9-slot
histogram, `counts[t]` = fish whose timer is t.  One day is:

    fish at 0 reset to 6 and each spawn a new fish at 8;
    fish at t > 0 move to t - 1.

As a list that is a rotate-left (slot 0 wraps to the end, becoming the new
8s) plus adding the same count into slot 6 for the parents.  Cost per day is
constant, so 80 and 256 days are the same code with a different loop count.
"""

from pathlib import Path

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day06.txt"

CYCLE = 7  # days between spawns for a fish that has already spawned
NEWBORN = 8  # a new fish's starting timer: two days behind the cycle
SLOTS = NEWBORN + 1


def parse_input(raw: str) -> list[int]:
    """Histogram of fish by timer: `counts[t]` fish have timer t."""
    counts = [0] * SLOTS
    for field in raw.replace(",", " ").split():
        timer = int(field)
        if not 0 <= timer < SLOTS:
            raise ValueError(f"timer out of range 0..{NEWBORN}: {timer}")
        counts[timer] += 1
    return counts


def step(counts: list[int]) -> list[int]:
    """The histogram one day later."""
    spawning = counts[0]
    nxt = counts[1:] + [spawning]  # everyone ages one day; spawns arrive at 8
    nxt[CYCLE - 1] += spawning  # the parents reset to 6
    return nxt


def population(counts: list[int], days: int) -> int:
    """Total fish after `days` days."""
    if days < 0:
        raise ValueError(f"days must be non-negative: {days}")
    for _ in range(days):
        counts = step(counts)
    return sum(counts)


def part1(counts: list[int]) -> int:
    return population(counts, 80)


def part2(counts: list[int]) -> int:
    return population(counts, 256)


def solve(raw: str) -> tuple[int, int]:
    counts = parse_input(raw)
    return part1(counts), part2(counts)


def main() -> None:
    counts = parse_input(INPUT.read_text())
    print(f"part1={part1(counts)}")
    print(f"part2={part2(counts)}")


if __name__ == "__main__":
    raise SystemExit(main())
