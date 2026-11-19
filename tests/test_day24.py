"""Day 24: Arithmetic Logic Unit."""

import itertools
import random

import pytest

import day24
from day24 import BLOCK_TEMPLATE, Block, Pair

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (51939397989999, 11717131211195)


def make_program(blocks: list[Block]) -> str:
    """A MONAD-shaped program text from per-block constants."""
    lines = []
    for b in blocks:
        lines += [t.format(div=b.div, check=b.check, offset=b.offset) for t in BLOCK_TEMPLATE]
    return "\n".join(lines) + "\n"


def run(text: str, digits) -> dict[str, int]:
    return day24.run_alu(day24.parse_program(text), digits)


def digits_of(n: int) -> list[int]:
    return [int(c) for c in str(n)]


# --- the statement's example programs (the interpreter is the ground truth) --

NEGATE = "inp x\nmul x -1\n"
TRIPLE = "inp z\ninp x\nmul z 3\neql z x\n"
BINARY = """\
inp w
add z w
mod z 2
div w 2
add y w
mod y 2
div w 2
add x w
mod x 2
div w 2
mod w 2
"""


@pytest.mark.parametrize("v", [0, 1, 7, -5])
def test_negate_example(v):
    assert run(NEGATE, [v])["x"] == -v


@pytest.mark.parametrize("a, b, want", [(2, 6, 1), (2, 5, 0), (0, 0, 1), (-3, -9, 1)])
def test_triple_example(a, b, want):
    assert run(TRIPLE, [a, b])["z"] == want


@pytest.mark.parametrize("v", range(16))
def test_binary_example(v):
    r = run(BINARY, [v])
    assert (r["w"], r["x"], r["y"], r["z"]) == ((v >> 3) & 1, (v >> 2) & 1, (v >> 1) & 1, v & 1)


@pytest.mark.parametrize("a, b, want", [(7, 2, 3), (-7, 2, -3), (7, -2, -3), (-7, -2, 3), (1, 26, 0)])
def test_div_truncates_toward_zero(a, b, want):
    assert run(f"inp z\ndiv z {b}\n", [a])["z"] == want


@pytest.mark.parametrize("prog", ["inp z\ndiv z 0\n", "inp z\nmod z 0\n", "inp z\nmod z -3\n"])
def test_crash_cases_raise(prog):
    with pytest.raises(ValueError):
        run(prog, [5])


def test_mod_of_negative_raises():
    with pytest.raises(ValueError):
        run("inp z\nmod z 26\n", [-1])


# --- one block equals the stack step in the module docstring ----------------


def block_step(b: Block, z: int, w: int) -> int:
    """The docstring's closed form for one block."""
    x = (z % 26 + b.check) != w
    z //= b.div  # z >= 0 throughout, so floor and truncation agree
    return z * 26 + w + b.offset if x else z


@pytest.mark.parametrize("seed", range(5))
def test_block_closed_form_matches_interpreter(seed):
    rng = random.Random(seed)
    for _ in range(300):
        b = Block(rng.choice((1, 26)), rng.randint(-16, 16), rng.randint(0, 16))
        z, w = rng.randint(0, 26**5), rng.randint(1, 9)
        # Start z off by running "inp z" first, then the block on w.
        prog = day24.parse_program("inp z\n" + make_program([b]))
        assert day24.run_alu(prog, [z, w])["z"] == block_step(b, z, w)


def test_block_closed_form_matches_interpreter_real(real_input):
    program = day24.parse_program(real_input(24))
    blocks = day24.read_blocks(program)
    rng = random.Random(24)
    for _ in range(2000):
        ws = [rng.randint(1, 9) for _ in blocks]
        z = 0
        for b, w in zip(blocks, ws, strict=True):
            z = block_step(b, z, w)
        assert day24.run_alu(program, ws)["z"] == z


# --- the pair constraints are exactly the validity condition ---------------


def satisfies(pairs: list[Pair], ws: list[int]) -> bool:
    return all(ws[j] == ws[i] + d for i, j, d in pairs)


def test_valid_iff_pairs_hold_real(real_input):
    """z == 0 exactly when all seven constraints hold -- including near misses."""
    raw = real_input(24)
    program, pairs = day24.parse_program(raw), day24.parse_input(raw)
    rng = random.Random(7)
    hits = 0
    for _ in range(4000):
        ws = [rng.randint(1, 9) for _ in range(14)]
        if rng.random() < 0.5:  # build one that satisfies, then maybe break one digit
            for i, j, d in pairs:
                ws[i] = rng.randint(max(1, 1 - d), min(9, 9 - d))
                ws[j] = ws[i] + d
            if rng.random() < 0.5:
                p = rng.randrange(14)
                ws[p] = rng.choice([v for v in range(1, 10) if v != ws[p]])
        ok = satisfies(pairs, ws)
        hits += ok
        assert (day24.run_alu(program, ws)["z"] == 0) == ok
    assert hits > 500  # both outcomes were actually exercised


def test_answer_is_valid_real(real_input):
    raw = real_input(24)
    pairs = day24.parse_input(raw)
    for ans in (day24.part1(pairs), day24.part2(pairs)):
        assert len(str(ans)) == 14 and "0" not in str(ans)
        assert day24.run_alu(day24.parse_program(raw), digits_of(ans))["z"] == 0


# --- brute force on small synthetic MONADs ----------------------------------


def brute_force(text: str, n: int) -> list[int]:
    """Every n-digit model number (digits 1..9) the interpreter accepts, ascending."""
    program = day24.parse_program(text)
    return [
        int("".join(map(str, ws)))
        for ws in itertools.product(range(1, 10), repeat=n)
        if day24.run_alu(program, ws)["z"] == 0
    ]


def random_blocks(rng: random.Random, n_pairs: int) -> list[Block]:
    """A random balanced push/pop sequence with plausible constants."""
    while True:
        shape = [1] * n_pairs + [26] * n_pairs
        rng.shuffle(shape)
        depth = itertools.accumulate(1 if d == 1 else -1 for d in shape)
        if min(depth) >= 0:
            break
    return [
        Block(1, rng.randint(10, 16), rng.randint(0, 16))
        if d == 1
        else Block(26, rng.randint(-16, 0), rng.randint(0, 16))
        for d in shape
    ]


@pytest.mark.parametrize("seed", range(12))
def test_matches_brute_force_4_digits(seed):
    blocks = random_blocks(random.Random(seed), 2)
    text = make_program(blocks)
    valid = brute_force(text, 4)
    pairs = day24.parse_input(text)
    if not valid:
        with pytest.raises(ValueError, match="cannot differ"):
            day24.model_number(pairs, largest=True)
        return
    assert day24.model_number(pairs, largest=True) == valid[-1]
    assert day24.model_number(pairs, largest=False) == valid[0]
    # And the constraint set describes the valid set exactly, not just its ends.
    want = [n for n in range(1111, 10000) if "0" not in str(n) and satisfies(pairs, digits_of(n))]
    assert valid == want


def test_nested_and_sequential_shapes_both_covered():
    shapes = {tuple(b.div for b in random_blocks(random.Random(s), 2)) for s in range(12)}
    assert (1, 1, 26, 26) in shapes and (1, 26, 1, 26) in shapes


def test_hand_checked_two_digit():
    # push w0 + 3, then pop with check -5: w1 == w0 + 3 - 5 = w0 - 2.
    text = make_program([Block(1, 12, 3), Block(26, -5, 7)])
    assert day24.parse_input(text) == [Pair(0, 1, -2)]
    assert day24.model_number(day24.parse_input(text), largest=True) == 97
    assert day24.model_number(day24.parse_input(text), largest=False) == 31
    assert brute_force(text, 2) == [31, 42, 53, 64, 75, 86, 97]


def test_nesting_pairs_like_parentheses():
    blocks = [Block(1, 10, 1), Block(1, 10, 2), Block(26, -1, 0), Block(26, -3, 0)]
    assert day24.pair_blocks(blocks) == [Pair(1, 2, 1), Pair(0, 3, -2)]


# --- guide section 8: William Y. Feng's push-digit search ------------------
# https://www.youtube.com/watch?v=Eswmo7Y7C4U -- only push digits are free,
# pop digits are forced, the first survivor in order is the answer.


def push_digit_search(blocks: list[Block], *, largest: bool) -> int | None:
    order = range(9, 0, -1) if largest else range(1, 10)
    n_push = sum(b.div == 1 for b in blocks)
    for free in itertools.product(order, repeat=n_push):
        z, k, digits = 0, 0, []
        for b in blocks:
            if b.div == 1:
                w = free[k]
                k += 1
                z = z * 26 + w + b.offset
            else:
                w = z % 26 + b.check
                z //= 26
                if not 1 <= w <= 9:
                    break
            digits.append(w)
        else:
            return int("".join(map(str, digits)))
    return None


@pytest.mark.parametrize("seed", range(12))
def test_push_digit_search_matches_brute_force(seed):
    blocks = random_blocks(random.Random(seed), 2)
    valid = brute_force(make_program(blocks), 4)
    assert push_digit_search(blocks, largest=True) == (valid[-1] if valid else None)
    assert push_digit_search(blocks, largest=False) == (valid[0] if valid else None)


def test_push_digit_search_agrees_on_real_input(real_input):  # ~2 s: walks 2.6M candidates for the max
    blocks = day24.read_blocks(day24.parse_program(real_input(24)))
    pairs = day24.pair_blocks(blocks)
    assert push_digit_search(blocks, largest=True) == day24.model_number(pairs, largest=True)
    assert push_digit_search(blocks, largest=False) == day24.model_number(pairs, largest=False)


# --- CP-SAT on the literal instruction list (independent of the block analysis)


def cpsat_model_number(program, *, largest: bool, bound: int = 26**8) -> int:
    """Translate every instruction into a CP-SAT constraint and optimise.

    Knows nothing about blocks or stacks.  Constant-valued registers are
    folded in Python, so `mul x 0` costs no variable.  Every other register
    write is a fresh variable in [-bound, bound].
    """
    cp_model = pytest.importorskip("ortools.sat.python.cp_model")
    m = cp_model.CpModel()
    reg: dict = dict.fromkeys("wxyz", 0)
    digits = []

    def fresh():
        return m.new_int_var(-bound, bound, "")

    for op, a, *rest in program:
        if op == "inp":
            reg[a] = m.new_int_var(1, 9, f"d{len(digits)}")
            digits.append(reg[a])
            continue
        x = reg[a]
        y = reg[rest[0]] if rest[0] in reg else int(rest[0])
        if isinstance(x, int) and isinstance(y, int):
            reg[a] = day24.run_alu([("inp", "w"), (op, "w", str(y))], [x])["w"]
            continue
        t = fresh()
        if op == "add":
            m.add(t == x + y)
        elif op == "mul":
            if isinstance(x, int) or isinstance(y, int):
                m.add(t == x * y)  # linear
            else:
                m.add_multiplication_equality(t, [x, y])
        elif op == "div":
            m.add_division_equality(t, x, y)  # CP-SAT truncates toward zero, as the ALU does
        elif op == "mod":
            m.add(x >= 0)  # the statement's crash case is excluded, not modelled
            m.add_modulo_equality(t, x, y)
        elif op == "eql":
            t = m.new_bool_var("")
            m.add(x == y).only_enforce_if(t)
            m.add(x != y).only_enforce_if(~t)
        reg[a] = t
    m.add(reg["z"] == 0)
    objective = sum(d * 10 ** (len(digits) - 1 - k) for k, d in enumerate(digits))
    m.maximize(objective) if largest else m.minimize(objective)
    solver = cp_model.CpSolver()
    assert solver.solve(m) == cp_model.OPTIMAL
    return int("".join(str(solver.value(d)) for d in digits))


def test_cpsat_on_hand_checked_program():
    program = day24.parse_program(make_program([Block(1, 12, 3), Block(26, -5, 7)]))
    assert cpsat_model_number(program, largest=True) == 97
    assert cpsat_model_number(program, largest=False) == 31


def test_cpsat_agrees_on_real_input(real_input):
    raw = real_input(24)
    program, pairs = day24.parse_program(raw), day24.parse_input(raw)
    assert cpsat_model_number(program, largest=True) == day24.model_number(pairs, largest=True)
    assert cpsat_model_number(program, largest=False) == day24.model_number(pairs, largest=False)


# --- malformed programs -----------------------------------------------------

GOOD = [Block(1, 12, 3), Block(26, -5, 7)]


@pytest.mark.parametrize(
    "text, match",
    [
        (make_program(GOOD).replace("mod x 26", "mod x 25", 1), "expected mod x 26"),
        (make_program(GOOD).replace("div z 26", "div z 13"), "div 13"),
        (make_program([Block(1, 9, 3), Block(26, -5, 7)]), "check 9 < 10"),
        (make_program([Block(1, 12, 17), Block(26, -5, 7)]), "offset 17"),
        (make_program([Block(1, 12, -1), Block(26, -5, 7)]), "offset -1"),
        (make_program([Block(26, -5, 7), Block(1, 12, 3)]), "empty stack"),
        (make_program([Block(1, 12, 3), Block(1, 12, 3)]), "never popped"),
        ("\n".join(make_program(GOOD).splitlines()[:-1]), "whole number"),
        ("", "whole number"),
    ],
)
def test_malformed_program_is_an_error(text, match):
    with pytest.raises(ValueError, match=match):
        day24.parse_input(text)


def test_impossible_pair_is_an_error():
    # Offset 0 and check -9: the popped digit would have to be w0 - 9 < 1.
    pairs = day24.parse_input(make_program([Block(1, 12, 0), Block(26, -9, 0)]))
    with pytest.raises(ValueError, match="cannot differ by -9"):
        day24.part1(pairs)


# --- CRLF / locked ---------------------------------------------------------


def test_crlf_input():
    text = make_program([Block(1, 12, 3), Block(1, 15, 0), Block(26, -2, 4), Block(26, -5, 7)])
    crlf = text.replace("\n", "\r\n")
    assert day24.parse_input(crlf) == day24.parse_input(text)
    assert day24.solve(crlf) == day24.solve(text) == (9977, 3311)


def test_real_input_locked(check_locked):
    check_locked(day24, LOCKED)
