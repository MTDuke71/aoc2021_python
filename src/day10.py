"""Day 10: Syntax Scoring.

Each input line is a run of nested chunks built from four bracket pairs:
(), [], {}, <>.  Every line is broken in one of two ways: *corrupted* (a
chunk is closed by the wrong kind of bracket) or *incomplete* (the line
just ends with chunks still open).

Checking a line is the classic bracket stack: push each opener, and on a
closer compare it with the opener on top.  A match pops; a mismatch is the
line's first illegal character and the scan stops there.  parse_input runs
that scan on every line, because the outcome -- the illegal character, or
the openers left on the stack -- does not depend on which part is asking.

Part 1 scores the corrupted lines: look up each first illegal character in
a points table and sum.

Part 2 scores the incomplete lines.  The completion is the stack read top
down, each opener replaced by its closer.  Its score is a base-5 number
built digit by digit (score = score * 5 + 1..4 per closer) and the answer is
the median of the line scores; the puzzle promises an odd count, so the
median is a real line's score and the code raises if the count is even.
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day10.txt"

CLOSER = {"(": ")", "[": "]", "{": "}", "<": ">"}
ILLEGAL_POINTS = {")": 3, "]": 57, "}": 1197, ">": 25137}
COMPLETION_POINTS = {")": 1, "]": 2, "}": 3, ">": 4}


class Scan(NamedTuple):
    """What the bracket stack says about one line.

    illegal is the first wrong closer, or None if the line is not corrupted.
    unclosed is the stack where the scan stopped, outermost opener first: at
    the illegal character for a corrupted line, at end of line otherwise.
    """

    illegal: str | None
    unclosed: str


def scan(line: str) -> Scan:
    """Run the bracket stack over one line, stopping at the first wrong closer."""
    stack: list[str] = []
    for ch in line:
        if ch in CLOSER:
            stack.append(ch)
        elif ch not in ILLEGAL_POINTS:
            raise ValueError(f"not a bracket: {ch!r} in {line!r}")
        elif not stack:
            raise ValueError(f"{ch!r} closes a chunk that was never opened in {line!r}")
        elif CLOSER[stack[-1]] == ch:
            stack.pop()
        else:
            return Scan(ch, "".join(stack))
    return Scan(None, "".join(stack))


def parse_input(raw: str) -> list[Scan]:
    """One Scan per non-blank line."""
    return [scan(line.strip()) for line in raw.splitlines() if line.strip()]


def part1(scans: list[Scan]) -> int:
    return sum(ILLEGAL_POINTS[s.illegal] for s in scans if s.illegal is not None)


def completion(unclosed: str) -> str:
    """The closers that finish a line, innermost chunk first."""
    return "".join(CLOSER[opener] for opener in reversed(unclosed))


def completion_score(closers: str) -> int:
    score = 0
    for ch in closers:
        score = score * 5 + COMPLETION_POINTS[ch]
    return score


def part2(scans: list[Scan]) -> int:
    scores = sorted(
        completion_score(completion(s.unclosed)) for s in scans if s.illegal is None and s.unclosed
    )
    if len(scores) % 2 == 0:
        raise ValueError(f"median needs an odd number of incomplete lines, found {len(scores)}")
    return scores[len(scores) // 2]


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
