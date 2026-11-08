"""Day 18: Snailfish."""

import json
import random

import pytest

import day18
from day18 import add, explode, magnitude, parse_number, render, split

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (4176, 4633)


# ---------------------------------------------------------------------------
# Independent reference: a real tree (nested Python lists), reduced the way
# the statement words it.  Shares no code with day18's flat leaf list.
# ---------------------------------------------------------------------------


def tree_explode(tree):
    """Explode the leftmost pair nested inside four pairs.  Returns (new_tree, exploded?)."""

    def walk(node, depth):
        # Returns (replacement, carry_left, carry_right, done)
        if isinstance(node, int):
            return node, None, None, False
        if depth == 4:
            left, right = node
            assert isinstance(left, int) and isinstance(right, int)
            return 0, left, right, True
        left, right = node
        new_left, carry_l, carry_r, done = walk(left, depth + 1)
        if done:
            if carry_r is not None:
                right = add_leftmost(right, carry_r)
            return [new_left, right], carry_l, None, True
        new_right, carry_l, carry_r, done = walk(right, depth + 1)
        if done:
            if carry_l is not None:
                left = add_rightmost(left, carry_l)
            return [left, new_right], None, carry_r, True
        return node, None, None, False

    new, _, _, done = walk(tree, 0)
    return new, done


def add_leftmost(node, n):
    return node + n if isinstance(node, int) else [add_leftmost(node[0], n), node[1]]


def add_rightmost(node, n):
    return node + n if isinstance(node, int) else [node[0], add_rightmost(node[1], n)]


def tree_split(node):
    if isinstance(node, int):
        return ([node // 2, (node + 1) // 2], True) if node >= 10 else (node, False)
    left, done = tree_split(node[0])
    if done:
        return [left, node[1]], True
    right, done = tree_split(node[1])
    return [node[0], right], done


def tree_add(a, b):
    tree = [a, b]
    while True:
        tree, done = tree_explode(tree)
        if done:
            continue
        tree, done = tree_split(tree)
        if not done:
            return tree


def tree_magnitude(node):
    return node if isinstance(node, int) else 3 * tree_magnitude(node[0]) + 2 * tree_magnitude(node[1])


def tree_text(tree):
    return json.dumps(tree, separators=(",", ":"))


def random_tree(rng, depth=0, max_depth=4):
    if depth == max_depth or (depth > 0 and rng.random() < 0.35):
        return rng.randint(0, 9)
    return [random_tree(rng, depth + 1, max_depth), random_tree(rng, depth + 1, max_depth)]


def apply_once(text, action):
    number = parse_number(text)
    assert action(number)
    return render(number)


# ---------------------------------------------------------------------------
# Parsing and the flat representation
# ---------------------------------------------------------------------------


def test_parse_is_leaves_with_depth():
    assert parse_number("[[1,2],3]") == [(1, 2), (2, 2), (3, 1)]
    assert parse_number("[9,[8,7]]") == [(9, 1), (8, 2), (7, 2)]


STATEMENT_NUMBERS = [
    "[1,2]",
    "[[1,2],3]",
    "[9,[8,7]]",
    "[[1,9],[8,5]]",
    "[[[[1,2],[3,4]],[[5,6],[7,8]]],9]",
    "[[[9,[3,8]],[[0,9],6]],[[[3,7],[4,9]],3]]",
    "[[[[1,3],[5,3]],[[1,3],[8,7]]],[[[4,9],[6,9]],[[8,2],[7,3]]]]",
]


@pytest.mark.parametrize("text", STATEMENT_NUMBERS)
def test_render_round_trips_statement(text):
    """render is fold() building text, so this also pins fold's re-pairing of adjacent equal depths."""
    assert render(parse_number(text)) == text


def test_render_round_trips_random():
    rng = random.Random(18)
    for _ in range(500):
        text = tree_text(random_tree(rng, max_depth=7))
        assert render(parse_number(text)) == text


@pytest.mark.parametrize("bad", ["", "5", "[1]", "[1,2,3]", "[1,2", "[1,2]]", "[[1,2],]", "[1;2]", "[1,2] x"])
def test_malformed_number_is_an_error(bad):
    with pytest.raises(ValueError):
        parse_number(bad)


@pytest.mark.parametrize("bad", ["[[[[[1,2],3],4],5],6]", "[10,1]"])
def test_unreduced_input_is_an_error(bad):
    """The depth <= 5 argument in the module docstring needs reduced inputs."""
    with pytest.raises(ValueError):
        day18.parse_input(bad + "\n[1,1]\n")


def test_real_input_is_reduced(real_input):
    numbers = day18.parse_input(real_input(18))
    assert len(numbers) == 100
    assert max(d for n in numbers for _, d in n) == 4
    assert max(v for n in numbers for v, _ in n) == 9


# ---------------------------------------------------------------------------
# Explode, split, add -- the statement's worked examples
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("[[[[[9,8],1],2],3],4]", "[[[[0,9],2],3],4]"),
        ("[7,[6,[5,[4,[3,2]]]]]", "[7,[6,[5,[7,0]]]]"),
        ("[[6,[5,[4,[3,2]]]],1]", "[[6,[5,[7,0]]],3]"),
        ("[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]", "[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]"),
        ("[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]", "[[3,[2,[8,0]]],[9,[5,[7,0]]]]"),
    ],
)
def test_explode_examples(before, after):
    assert apply_once(before, explode) == after


@pytest.mark.parametrize(("n", "pair"), [(10, "[5,5]"), (11, "[5,6]"), (12, "[6,6]")])
def test_split_examples(n, pair):
    assert apply_once(f"[{n},0]", split) == f"[{pair},0]"


def test_nothing_to_do_returns_false():
    number = parse_number("[[1,2],[3,4]]")
    assert not explode(number)
    assert not split(number)
    assert render(number) == "[[1,2],[3,4]]"


def test_reduction_trace():
    """The statement's step-by-step reduction of [[[[4,3],4],4],[7,[[8,4],9]]] + [1,1]."""
    number = [(v, d + 1) for v, d in parse_number("[[[[4,3],4],4],[7,[[8,4],9]]]") + parse_number("[1,1]")]
    assert render(number) == "[[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]"
    trace = [
        (explode, "[[[[0,7],4],[7,[[8,4],9]]],[1,1]]"),
        (explode, "[[[[0,7],4],[15,[0,13]]],[1,1]]"),
        (split, "[[[[0,7],4],[[7,8],[0,13]]],[1,1]]"),
        (split, "[[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]"),
        (explode, "[[[[0,7],4],[[7,8],[6,0]]],[8,1]]"),
    ]
    for action, want in trace:
        assert not (action is split and explode(number[:]))  # split only when nothing explodes
        assert action(number)
        assert render(number) == want
    assert not explode(number) and not split(number)


def test_add_does_not_mutate_arguments():
    a, b = parse_number("[[[[4,3],4],4],[7,[[8,4],9]]]"), parse_number("[1,1]")
    a0, b0 = a[:], b[:]
    assert render(add(a, b)) == "[[[[0,7],4],[[7,8],[6,0]]],[8,1]]"
    assert (a, b) == (a0, b0)


SMALL_SUMS = [
    (4, "[[[[1,1],[2,2]],[3,3]],[4,4]]"),
    (5, "[[[[3,0],[5,3]],[4,4]],[5,5]]"),
    (6, "[[[[5,0],[7,4]],[5,5]],[6,6]]"),
]


@pytest.mark.parametrize(("n", "want"), SMALL_SUMS)
def test_small_list_sums(n, want):
    raw = "\n".join(f"[{i},{i}]" for i in range(1, n + 1))
    assert render(day18.total(day18.parse_input(raw))) == want


LARGER = """\
[[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]
[7,[[[3,7],[4,3]],[[6,3],[8,8]]]]
[[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]
[[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]
[7,[5,[[3,8],[1,4]]]]
[[2,[2,2]],[8,[8,1]]]
[2,9]
[1,[[[9,3],9],[[9,0],[0,7]]]]
[[[5,[7,4]],7],1]
[[[[4,2],2],6],[8,7]]
"""

# The statement's running sums for LARGER, one per addition.
LARGER_PARTIALS = [
    "[[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]",
    "[[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]",
    "[[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]",
    "[[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]",
    "[[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]",
    "[[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]",
    "[[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]",
    "[[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]",
    "[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]",
]


def test_larger_example_partial_sums():
    numbers = day18.parse_input(LARGER)
    acc = numbers[0]
    for number, want in zip(numbers[1:], LARGER_PARTIALS, strict=True):
        acc = add(acc, number)
        assert render(acc) == want


# ---------------------------------------------------------------------------
# Magnitude
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "want"),
    [
        ("[9,1]", 29),
        ("[1,9]", 21),
        ("[[9,1],[1,9]]", 129),
        ("[[1,2],[[3,4],5]]", 143),
        ("[[[[0,7],4],[[7,8],[6,0]]],[8,1]]", 1384),
        ("[[[[1,1],[2,2]],[3,3]],[4,4]]", 445),
        ("[[[[3,0],[5,3]],[4,4]],[5,5]]", 791),
        ("[[[[5,0],[7,4]],[5,5]],[6,6]]", 1137),
        ("[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]", 3488),
    ],
)
def test_magnitude_examples(text, want):
    assert magnitude(parse_number(text)) == want


def test_magnitude_matches_tree_random():
    rng = random.Random(1818)
    for _ in range(500):
        tree = random_tree(rng, max_depth=7)
        assert magnitude(parse_number(tree_text(tree))) == tree_magnitude(tree)


@pytest.mark.parametrize("bad", [[(1, 1)], [(1, 1), (2, 1), (3, 1)], [(1, 1), (2, 2)]])
def test_fold_refuses_impossible_depths(bad):
    with pytest.raises(ValueError):
        magnitude(bad)


# ---------------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------------

HOMEWORK = """\
[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
[[[5,[2,8]],4],[5,[[9,9],0]]]
[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
[[[[5,4],[7,7]],8],[[8,3],8]]
[[9,3],[[9,9],[6,[4,9]]]]
[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
"""


def test_part1_example():
    numbers = day18.parse_input(HOMEWORK)
    assert render(day18.total(numbers)) == "[[[[6,6],[7,6]],[[7,7],[7,0]]],[[[7,7],[7,7]],[[7,8],[9,9]]]]"
    assert day18.part1(numbers) == 4140


def test_add_matches_tree_random():
    """Flat-list add == nested-list add on random reduced numbers (depth <= 4, values 0..9)."""
    rng = random.Random(2021)
    for _ in range(1000):
        a, b = random_tree(rng), random_tree(rng)
        got = render(add(parse_number(tree_text(a)), parse_number(tree_text(b))))
        assert got == tree_text(tree_add(a, b))


def test_running_sum_matches_tree_real(real_input):
    """Every partial sum of the real input, flat vs tree."""
    lines = [line for line in real_input(18).splitlines() if line.strip()]
    flat = parse_number(lines[0])
    tree = json.loads(lines[0])
    for line in lines[1:]:
        flat = add(flat, parse_number(line))
        tree = tree_add(tree, json.loads(line))
        assert render(flat) == tree_text(tree)
    assert day18.part1(day18.parse_input(real_input(18))) == tree_magnitude(tree)


def test_addition_is_not_commutative():
    """Why part 1's order matters: a + b and b + a are different numbers in general."""
    a, b = parse_number("[[[[4,3],4],4],[7,[[8,4],9]]]"), parse_number("[1,1]")
    assert render(add(a, b)) != render(add(b, a))


# ---------------------------------------------------------------------------
# Part 2
# ---------------------------------------------------------------------------


def test_part2_example():
    numbers = day18.parse_input(HOMEWORK)
    assert day18.part2(numbers) == 3993
    best = add(numbers[8], numbers[0])  # the statement's winning pair, in that order
    assert render(best) == "[[[[7,8],[6,6]],[[6,0],[7,7]]],[[[7,8],[8,8]],[[7,9],[0,6]]]]"
    assert magnitude(best) == 3993


def test_part2_needs_both_orders():
    """Restricting to i < j (one order per pair) loses the example's answer, so both orders are tried."""
    numbers = day18.parse_input(HOMEWORK)
    one_order = max(
        magnitude(add(numbers[i], numbers[j]))
        for i in range(len(numbers))
        for j in range(i + 1, len(numbers))
    )
    assert one_order < 3993


def test_part2_never_pairs_a_line_with_itself():
    """Two lines: the only candidates are a+b and b+a, even though a+a would score higher here."""
    numbers = day18.parse_input("[9,9]\n[0,0]\n")
    assert day18.part2(numbers) == max(
        magnitude(add(numbers[0], numbers[1])), magnitude(add(numbers[1], numbers[0]))
    )
    assert magnitude(add(numbers[0], numbers[0])) > day18.part2(numbers)


def test_part2_matches_tree_real(real_input):
    trees = [json.loads(line) for line in real_input(18).splitlines() if line.strip()]
    want = max(
        tree_magnitude(tree_add(a, b)) for i, a in enumerate(trees) for j, b in enumerate(trees) if i != j
    )
    assert day18.part2(day18.parse_input(real_input(18))) == want


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = HOMEWORK.replace("\n", "\r\n")
    assert day18.parse_input(crlf) == day18.parse_input(HOMEWORK)
    assert day18.part1(day18.parse_input(crlf)) == 4140
    assert day18.part2(day18.parse_input(crlf)) == 3993


def test_real_input_locked(check_locked):
    check_locked(day18, LOCKED)
