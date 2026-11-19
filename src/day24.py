"""Day 24: Arithmetic Logic Unit.

MONAD (the puzzle input) is 14 copies of one 18-instruction block, one per
input digit, differing only in three constants.  Read as a machine, each
block does this to z:

    x = (z % 26 + check) != w        # compare w with the top base-26 digit
    z = z // div                     # div is 1 (keep) or 26 (pop the top)
    if x:
        z = z * 26 + w + offset      # push w + offset

So z is a stack of base-26 digits.  A block with div 1 always has
check >= 10, so its comparison can never succeed (w is at most 9): it is an
unconditional *push* of w + offset.  A block with div 26 *pops* the top, and
pushes again unless its digit equals (popped value + check).

There are seven pushes and seven pops.  z ends at 0 only if the stack ends
empty, which needs every pop to match -- a mismatched pop re-pushes, so the
stack stays non-empty.  Pairing each pop j with the push i it pops (stack
order, like matching parentheses) gives seven independent constraints:

    w[j] = w[i] + offset[i] + check[j]

Part 1 (largest valid model number) maxes the earlier digit of each pair
subject to both staying in 1..9; part 2 (smallest) mins it.  The pairs are
independent and each fixes its two digit positions, so per-pair extremes
give the global extreme.  No search at all.

parse_input checks that the program really has this shape (same template,
check >= 10 on every push, push values that are non-zero base-26 digits,
balanced pushes and pops) and raises ValueError otherwise, because every
step above leans on it.
"""

from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day24.txt"

REGISTERS = "wxyz"

# One digit's block.  {div}, {check}, {offset} are the only per-block constants.
BLOCK_TEMPLATE = (
    "inp w",
    "mul x 0",
    "add x z",
    "mod x 26",
    "div z {div}",
    "add x {check}",
    "eql x w",
    "eql x 0",
    "mul y 0",
    "add y 25",
    "mul y x",
    "add y 1",
    "mul z y",
    "mul y 0",
    "add y w",
    "add y {offset}",
    "mul y x",
    "add z y",
)
BLOCK_LEN = len(BLOCK_TEMPLATE)


class Block(NamedTuple):
    div: int  # 1 = push, 26 = pop
    check: int  # added to the top of the stack before comparing with w
    offset: int  # added to w before pushing


class Pair(NamedTuple):
    """Digit j must equal digit i + delta (i is the push, j the matching pop)."""

    i: int
    j: int
    delta: int


# --- the literal machine ----------------------------------------------------


def parse_program(raw: str) -> list[tuple[str, ...]]:
    """The instructions as token tuples, e.g. ('add', 'x', '-8').  Tolerates CRLF."""
    return [tuple(line.split()) for line in raw.splitlines() if line.strip()]


def run_alu(program: list[tuple[str, ...]], inputs) -> dict[str, int]:
    """Execute the program as the statement defines it; return the registers.

    Not used by the solution -- it is the ground truth the tests check the
    block analysis against.  div truncates toward zero (Python's // floors,
    so it is done on magnitudes).  The statement's crash cases raise.
    """
    reg = dict.fromkeys(REGISTERS, 0)
    feed = iter(inputs)
    for op, a, *rest in program:
        if op == "inp":
            reg[a] = next(feed)
            continue
        b = reg[rest[0]] if rest[0] in reg else int(rest[0])
        x = reg[a]
        if op == "add":
            reg[a] = x + b
        elif op == "mul":
            reg[a] = x * b
        elif op == "div":
            if b == 0:
                raise ValueError("div by zero")
            q = abs(x) // abs(b)
            reg[a] = q if (x < 0) == (b < 0) else -q
        elif op == "mod":
            if x < 0 or b <= 0:
                raise ValueError(f"mod {x} {b}")
            reg[a] = x % b
        elif op == "eql":
            reg[a] = int(x == b)
        else:
            raise ValueError(f"unknown instruction {op!r}")
    return reg


# --- reading the blocks -----------------------------------------------------


def read_block(lines: list[tuple[str, ...]]) -> Block:
    """Match one 18-instruction chunk against BLOCK_TEMPLATE and pull out its constants."""
    found = {}
    for want, got in zip(BLOCK_TEMPLATE, lines, strict=True):
        want = tuple(want.split())
        if want[-1].startswith("{"):
            if got[:-1] != want[:-1]:
                raise ValueError(f"expected {' '.join(want)}, got {' '.join(got)}")
            found[want[-1].strip("{}")] = int(got[-1])
        elif got != want:
            raise ValueError(f"expected {' '.join(want)}, got {' '.join(got)}")
    return Block(**found)


def read_blocks(program: list[tuple[str, ...]]) -> list[Block]:
    if not program or len(program) % BLOCK_LEN:
        raise ValueError(f"{len(program)} instructions is not a whole number of {BLOCK_LEN}-line blocks")
    blocks = [read_block(program[k : k + BLOCK_LEN]) for k in range(0, len(program), BLOCK_LEN)]
    for n, b in enumerate(blocks):
        if b.div not in (1, 26):
            raise ValueError(f"block {n}: div {b.div}, expected 1 or 26")
        if b.div == 1 and b.check < 10:
            # Then the comparison could succeed and the block would not be a pure push.
            raise ValueError(f"block {n}: push block with check {b.check} < 10")
        if not 0 <= b.offset <= 16:
            # w + offset must be a non-zero base-26 digit (1..25) for "z == 0 iff empty".
            raise ValueError(f"block {n}: offset {b.offset} outside 0..16")
    return blocks


def pair_blocks(blocks: list[Block]) -> list[Pair]:
    """Match each pop with the push it removes, like matching parentheses."""
    stack, pairs = [], []
    for j, b in enumerate(blocks):
        if b.div == 1:
            stack.append(j)
        elif not stack:
            raise ValueError(f"block {j} pops an empty stack")
        else:
            i = stack.pop()
            pairs.append(Pair(i, j, blocks[i].offset + b.check))
    if stack:
        raise ValueError(f"blocks {stack} are never popped, so z can never return to 0")
    return pairs


def parse_input(raw: str) -> list[Pair]:
    return pair_blocks(read_blocks(parse_program(raw)))


# --- solving ---------------------------------------------------------------


def model_number(pairs: list[Pair], *, largest: bool) -> int:
    """The largest (or smallest) digit string meeting every pair constraint."""
    digits = [0] * (2 * len(pairs))
    for i, j, delta in pairs:
        # w[i] and w[i] + delta must both lie in 1..9.
        lo, hi = max(1, 1 - delta), min(9, 9 - delta)
        if lo > hi:
            raise ValueError(f"digits {i} and {j} cannot differ by {delta}")
        digits[i] = hi if largest else lo
        digits[j] = digits[i] + delta
    return int("".join(map(str, digits)))


def part1(pairs: list[Pair]) -> int:
    return model_number(pairs, largest=True)


def part2(pairs: list[Pair]) -> int:
    return model_number(pairs, largest=False)


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
