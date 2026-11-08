"""Day 18: Snailfish.

A snailfish number is a binary tree whose leaves are small integers, written
as nested pairs `[x,y]`.  Addition pairs two numbers up and then *reduces*:
repeatedly explode the leftmost pair nested inside four pairs, or failing
that split the leftmost leaf >= 10 into [floor(n/2), ceil(n/2)].  The
answer is the *magnitude*: 3*left + 2*right, recursively.

Representation: no tree.  A number is its leaves in left-to-right order,
each tagged with its depth (how many pairs enclose it):

    [[1,2],3]  ->  [(1, 2), (2, 2), (3, 1)]

Every operation the puzzle asks for is about *neighbouring leaves*, which a
tree makes awkward (the "first regular number to the left" can be far away
in the tree) and a flat list makes trivial (index - 1):

  add      concatenate, every depth + 1
  explode  leaves i, i+1 at depth 5: add them into i-1 and i+2, replace the
           two with one 0 at depth 4
  split    leaf n at depth d -> (n//2, d+1), (n - n//2, d+1)
  magnitude  fold(): a stack pass that re-pairs adjacent equal-depth leaves

Depth never exceeds 5: inputs are reduced (depth <= 4, checked in parse),
adding makes it 5 at most, and a split only happens once nothing is at
depth 5, so it makes at most 5 too.  A depth-5 leaf is therefore always half
of a pair of two leaves, which is what the statement promises explode will
see.
"""

from collections.abc import Callable, Sequence
from itertools import permutations
from pathlib import Path
from typing import TypeVar

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day18.txt"

Leaf = tuple[int, int]  # (value, depth)
Number = list[Leaf]
T = TypeVar("T")

EXPLODE_DEPTH = 5  # "nested inside four pairs"
MAX_INPUT_DEPTH = EXPLODE_DEPTH - 1


def parse_number(text: str) -> Number:
    """Parse one `[x,y]` line into its flat (value, depth) leaf list.

    Recursive descent so that malformed text (`[1,2,3]`, `[1]`, unbalanced
    brackets) is refused rather than silently flattened.
    """
    text = text.strip()
    leaves: Number = []
    pos = 0

    def element(depth: int) -> None:
        nonlocal pos
        if pos < len(text) and text[pos] == "[":
            pos += 1
            element(depth + 1)
            expect(",")
            element(depth + 1)
            expect("]")
            return
        start = pos
        while pos < len(text) and text[pos].isdigit():
            pos += 1
        if start == pos:
            raise ValueError(f"expected a digit or '[' at column {pos} of {text!r}")
        leaves.append((int(text[start:pos]), depth))

    def expect(char: str) -> None:
        nonlocal pos
        if pos >= len(text) or text[pos] != char:
            raise ValueError(f"expected {char!r} at column {pos} of {text!r}")
        pos += 1

    if not text.startswith("["):
        raise ValueError(f"a snailfish number is a pair: {text!r}")
    element(0)
    if pos != len(text):
        raise ValueError(f"trailing text at column {pos} of {text!r}")
    return leaves


def fold(number: Sequence[Leaf], leaf: Callable[[int], T], pair: Callable[[T, T], T]) -> T:
    """Rebuild the tree bottom-up from the flat leaf list, combining with `pair`.

    Push leaves left to right.  Whenever the top two stack entries share a
    depth they are the two halves of one pair: the lower entry is a left
    child still waiting for its sibling, and the stack only ever holds such
    left children at strictly increasing depths, so the next entry at the
    same depth can only be that sibling.  Fold them into one entry a level
    up.  A well-formed number ends as a single entry at depth 0.
    """
    stack: list[tuple[T, int]] = []
    for value, depth in number:
        item = leaf(value)
        while stack and stack[-1][1] == depth:
            left, _ = stack.pop()
            item, depth = pair(left, item), depth - 1
        stack.append((item, depth))
    if len(stack) != 1 or stack[0][1] != 0:
        raise ValueError("leaf depths do not describe a single pair")
    return stack[0][0]


def render(number: Sequence[Leaf]) -> str:
    """Back to `[x,y]` text: the inverse of parse_number, for comparing with the statement."""
    return fold(number, str, lambda a, b: f"[{a},{b}]")


def magnitude(number: Sequence[Leaf]) -> int:
    """3*left + 2*right, recursively, without materialising the tree."""
    return fold(number, int, lambda a, b: 3 * a + 2 * b)


def explode(number: Number) -> bool:
    """Explode the leftmost depth-5 pair in place.  False if there is none."""
    for i, (left, depth) in enumerate(number):
        if depth < EXPLODE_DEPTH:
            continue
        if depth > EXPLODE_DEPTH or number[i + 1][1] != depth:
            raise ValueError(f"leaf nested {depth} deep without a leaf sibling: inputs must be reduced")
        right = number[i + 1][0]
        if i > 0:
            value, d = number[i - 1]
            number[i - 1] = (value + left, d)
        if i + 2 < len(number):
            value, d = number[i + 2]
            number[i + 2] = (value + right, d)
        number[i : i + 2] = [(0, depth - 1)]
        return True
    return False


def split(number: Number) -> bool:
    """Split the leftmost leaf >= 10 in place.  False if there is none."""
    for i, (value, depth) in enumerate(number):
        if value >= 10:
            number[i : i + 1] = [(value // 2, depth + 1), (value - value // 2, depth + 1)]
            return True
    return False


def add(a: Sequence[Leaf], b: Sequence[Leaf]) -> Number:
    """Snailfish a + b, fully reduced.  Neither argument is modified."""
    total = [(value, depth + 1) for value, depth in (*a, *b)]
    # `or` short-circuits: split runs only when there was nothing to explode.
    while explode(total) or split(total):
        pass
    return total


def parse_input(raw: str) -> list[Number]:
    """Every line as a leaf list.  Refuses a line that is not already reduced."""
    numbers = [parse_number(line) for line in raw.splitlines() if line.strip()]
    for number in numbers:
        if any(depth > MAX_INPUT_DEPTH or value >= 10 for value, depth in number):
            raise ValueError(f"input number is not reduced: {render(number)}")
    if not numbers:
        raise ValueError("no snailfish numbers in input")
    return numbers


def total(numbers: Sequence[Number]) -> Number:
    """Left fold of add over the list, in order (addition is not associative)."""
    acc = numbers[0]
    for number in numbers[1:]:
        acc = add(acc, number)
    return acc


def part1(numbers: list[Number]) -> int:
    return magnitude(total(numbers))


def part2(numbers: list[Number]) -> int:
    """Largest magnitude of a + b over two different lines, both orders (a + b != b + a).

    "Different" is by position, so a line that happens to appear twice could pair with its copy.
    """
    return max(magnitude(add(a, b)) for a, b in permutations(numbers, 2))


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
