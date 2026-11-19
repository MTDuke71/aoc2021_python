# Day 24 Function Guide — Arithmetic Logic Unit

Source: [src/day24.py](../../src/day24.py) · Tests:
[tests/test_day24.py](../../tests/test_day24.py) · Statement:
[day24.md](day24.md)

## 1. The problem

The input is a straight-line program for a toy 4-register machine
(`w x y z`, six opcodes, no jumps). It reads 14 digits, each 1..9, and
a digit string is a valid model number when `z == 0` at the end.
Part 1 asks for the largest valid model number and part 2 for the
smallest.

Brute force is out. There are 9^14 = 22,876,792,454,961 candidates,
and the literal interpreter takes 53.6 µs per run (measured). That
comes to about 39 years.

This is a reverse-engineering puzzle, not a programming one: the
statement explicitly says *figure out what MONAD does*. Read the
program the way you'd read a disassembly listing, find the structure,
and the answer drops out by hand.

## 2. Representation: decompile the block

The 252 instructions are 14 copies of one 18-instruction block. Only
three immediates change from block to block (`BLOCK_TEMPLATE` in the
source):

```
inp w            
mul x 0          x = 0
add x z          
mod x 26         x = z % 26              <- peek at top of stack
div z {div}      z = z / div             <- div ∈ {1, 26}: keep or pop
add x {check}    
eql x w          
eql x 0          x = (z%26 + check) != w
mul y 0
add y 25
mul y x
add y 1          y = 25*x + 1            <- 26 if x else 1
mul z y          z *= y                  <- shift left one base-26 digit, or not
mul y 0
add y w
add y {offset}
mul y x          y = (w + offset) * x
add z y          z += y                  <- push w+offset into the new low digit, or not
```

Collapsed:

```
x = (z % 26 + check) != w
z = z // div
if x: z = z * 26 + w + offset
```

Think of `z` as a **stack of base-26 digits**, with `z % 26` on top.
`*26 + v` is a push, `//26` is a pop, and `%26` is a peek. It's a
shift register with a radix of 26 instead of 2.

Your input's constants:

| block | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| div    | 1 | 1 | 1 | 1 | 26 | 26 | 1 | 26 | 1 | 26 | 1 | 26 | 26 | 26 |
| check  | 13 | 13 | 10 | 15 | −8 | −10 | 11 | −3 | 14 | −4 | 14 | −5 | −8 | −11 |
| offset | 15 | 16 | 4 | 14 | 1 | 5 | 1 | 3 | 3 | 7 | 5 | 13 | 3 | 10 |

There are two kinds of block:

- **div 1 → push.** `check` is always ≥ 10, so `z%26 + check ≥ 10 > w`.
  The comparison can never match, so `x = 1` and the block
  unconditionally pushes `w + offset`.
- **div 26 → pop, then maybe push.** The block pops the top value `t`.
  If `w == t + check`, then `x = 0` and nothing more happens. Otherwise
  it pushes `w + offset`, which replaces the popped value.

### Concrete trace: the part 1 answer, `51939397989999`

| block | w | kind | z | stack (bottom → top) |
|--:|--:|---|--:|---|
| 0 | 5 | push 5+15 | 20 | 20 |
| 1 | 1 | push 1+16 | 537 | 20 17 |
| 2 | 9 | push 9+4 | 13975 | 20 17 13 |
| 3 | 3 | push 3+14 | 363367 | 20 17 13 17 |
| 4 | 9 | pop 17; 17−8 = 9 = w ✓ | 13975 | 20 17 13 |
| 5 | 3 | pop 13; 13−10 = 3 = w ✓ | 537 | 20 17 |
| 6 | 9 | push 9+1 | 13972 | 20 17 10 |

…and so on down to `z = 0`.

Now change digit 4 from 9 to 8 (`51938397989999`). Block 4 pops 17 and
finds 17 − 8 = 9 ≠ 8, so it pushes 8 + 1 = 9 in its place
(`z = 363359`, stack `20 17 13 9`). The stack is now one level too
deep for good. Block 5 also mismatches, and the run ends with
`z = 363369`.

### The pairing

Pushes and pops nest like parentheses. Pop `j` checks the value pushed
by its matching push `i`, which is `w[i] + offset[i]`. So pop `j`
matches exactly when:

```
w[j] = w[i] + offset[i] + check[j]  =  w[i] + delta
```

For your input:

| push i | pop j | delta | largest (w[i], w[j]) | smallest |
|--:|--:|--:|---|---|
| 3 | 4 | +6 | 3, 9 | 1, 7 |
| 2 | 5 | −6 | 9, 3 | 7, 1 |
| 6 | 7 | −2 | 9, 7 | 3, 1 |
| 8 | 9 | −1 | 9, 8 | 2, 1 |
| 10 | 11 | 0 | 9, 9 | 1, 1 |
| 1 | 12 | +8 | 1, 9 | 1, 9 |
| 0 | 13 | +4 | 5, 9 | 1, 5 |

Reading down the "largest" column by position gives
`5 1 9 3 9 3 9 7 9 8 9 9 9 9`. Reading the "smallest" column gives
`1 1 7 1 7 1 3 1 2 1 1 1 9 5`.

## 3. Function walkthrough

### `parse_program(raw)` / `run_alu(program, inputs)`

These are the literal machine. `run_alu` executes the statement's
semantics as written. Two details:

- **Division truncates toward zero.** Python's `//` floors, so `div` is
  done on magnitudes and the sign is fixed up afterwards (−7/2 = −3, not
  −4; pinned).
- **The statement's crash cases raise `ValueError`.** Those are `div` by
  0 and `mod` with a negative left operand or a non-positive right one.

The solution never calls `run_alu`. It's the ground truth that the
tests check the decompilation against.

### `read_block(lines)` / `read_blocks(program)`

These match each 18-line chunk token by token against
`BLOCK_TEMPLATE`. The three `{placeholder}` slots must keep their
opcode and register, and their integer is captured into a
`Block(div, check, offset)`. Then the preconditions that section 4
relies on are checked:

- `div ∈ {1, 26}`;
- a push block has `check ≥ 10`, so it really is unconditional;
- `0 ≤ offset ≤ 16`, so a pushed `w + offset` lies in 1..25. It's
  never zero (so a non-empty stack means `z ≠ 0`) and never 26 or more
  (so it stays a single base-26 digit).

### `pair_blocks(blocks) -> list[Pair]`

This is a parenthesis matcher. A push puts its index on a stack. A pop
takes the most recent unmatched push and emits
`Pair(i, j, offset[i] + check[j])`. It raises if a pop finds the stack
empty or a push is left unmatched.

`parse_input = pair_blocks ∘ read_blocks ∘ parse_program`. Both parts
use the pair list and don't depend on which part is asking, so per
house rules it's built in the parse.

### `model_number(pairs, largest)` / `part1` / `part2`

For each pair, `w[i]` and `w[i] + delta` must both be in 1..9, so
`w[i] ∈ [max(1, 1−delta), min(9, 9−delta)]`. Take the top of that range
for part 1 and the bottom for part 2, and set `w[j] = w[i] + delta`. If
the range is empty (|delta| ≥ 9), no valid model number exists, and
the function raises.

## 4. Why it is correct

**One block = the collapsed form.** Each step is plain algebra on the
18 lines in section 2. It's also pinned:
`test_block_closed_form_matches_interpreter` runs 1,500 random
(block, z, w) cases, and the `_real` variant chains 2,000 random digit
strings through your 14 blocks. Both compare against `run_alu`.

**`z == 0` ⇔ every pop matches.**

- *If every pop matches:* there are 7 pushes and 7 pops, and each pop
  removes exactly one value without pushing. The stack ends empty, so
  `z = 0`.
- *If some pop mismatches:* that block pops one value and pushes one,
  so the depth doesn't change. Then at most 6 of the 7 pops remove
  anything against 7 pushes, so at least one value remains. Every
  pushed value is in 1..25, a non-zero base-26 digit, so `z > 0`.

Matching is a property of *which* push a pop sees, and that's the
parenthesis pairing only while all earlier pops matched. That's fine:
on any string where some pop mismatches, `z ≠ 0` already, whichever
pairs "hold". Pinned two ways:

- `test_valid_iff_pairs_hold_real`: 4,000 strings, half built to
  satisfy all seven constraints and then a random half of those broken
  by one digit. Interpreter `z == 0` agrees with "all pairs hold" on
  every one, and more than 500 of them are valid, so both outcomes are
  exercised.
- `test_matches_brute_force_4_digits`: 12 random 4-block MONADs, with
  both the nested shape (`push push pop pop`) and the sequential one
  (`push pop push pop`) present. Every one of the 6,561 digit strings
  goes through `run_alu`, and the accepted set equals the set
  satisfying the pairs exactly, not just at its ends. Seeds with no
  valid number confirm that `model_number` raises.

**Per-pair extremes give the global extreme.** The pairs partition the
14 positions, so each digit belongs to exactly one pair and the
constraints never interact. For the largest number, compare positions
left to right. In each pair the push `i` comes before the pop `j`, so
`w[i]` is the more significant digit, and maximizing it (with `w[j]`
then forced) is right. Each pair's leftmost position is its `i`, and
no other pair touches it, so greedy is optimal.

**An independent check that knows nothing about blocks.**
`test_cpsat_agrees_on_real_input` translates the raw 252 instructions
into a CP-SAT model and asks for the provable optimum (section 7). It
gets the same two answers.

## 5. Complexity

The parse is O(n) in instructions with a constant-size template
compare per line. `pair_blocks` is O(blocks), and `model_number` is
O(pairs). The parts are a few dozen integer operations.

| phase  |    ms |
| ------ | ----: |
| parse  | 0.095 |
| part 1 | 0.003 |
| part 2 | 0.003 |
| total  | 0.101 |

`bench.py 24`, best of 5 on the real input. Nearly all of it is
tokenizing 252 lines. The fastest day since the early ones, after the
slowest (day 23, 3.5 s).

## 6. If I were writing this in Rust

The shape maps one to one. A `Block` is a `Copy` struct of three
`i64`s, and the pairing is a `Vec<usize>` used as a stack:

```rust
#[derive(Clone, Copy)]
struct Block { div: i64, check: i64, offset: i64 }

struct Pair { i: usize, j: usize, delta: i64 }

fn pair_blocks(blocks: &[Block]) -> Result<Vec<Pair>, String> {
    let mut stack = Vec::new();
    let mut pairs = Vec::new();
    for (j, b) in blocks.iter().enumerate() {
        if b.div == 1 {
            stack.push(j);
        } else {
            let i = stack.pop().ok_or(format!("block {j} pops an empty stack"))?;
            pairs.push(Pair { i, j, delta: blocks[i].offset + b.check });
        }
    }
    if stack.is_empty() { Ok(pairs) } else { Err("unmatched push".into()) }
}

fn model_number(pairs: &[Pair], largest: bool) -> Option<u64> {
    let mut d = [0i64; 14];
    for p in pairs {
        let (lo, hi) = (1.max(1 - p.delta), 9.min(9 - p.delta));
        if lo > hi { return None; }
        d[p.i] = if largest { hi } else { lo };
        d[p.j] = d[p.i] + p.delta;
    }
    Some(d.iter().fold(0, |n, &x| n * 10 + x as u64))
}
```

Two Rust-specific notes:

- **Division semantics come free.** Rust's `/` and `%` on signed
  integers already truncate toward zero, matching the ALU, so a Rust
  `run_alu` doesn't need the magnitude-and-sign fixup that Python's
  flooring `//` forces. (Rust's `%` sign follows the dividend; the ALU
  never reaches that case, because negative `mod` is a crash.)
- **The decompiled block is branch-free.** `z = z / div * (25*x + 1) +
  (w + offset) * x`, with `x` a 0/1 compare, is exactly how the input
  is written. Someone hand-compiled a conditional push into
  multiply-by-flag, the way you'd write it in embedded C to avoid a
  branch.

## 7. Sidebar: CP-SAT on the raw program

Google OR-Tools' CP-SAT solver can do this without any decompiling.
Each instruction becomes one constraint on a fresh integer variable
(the program is in SSA form already, since every write is a new
value):

| ALU | CP-SAT |
|---|---|
| `inp a` | new var in 1..9 (a decision digit) |
| `add a b` | `t == a + b` |
| `mul a b` | `t == a * k` if either side is constant (linear); else `add_multiplication_equality` |
| `div a b` | `add_division_equality` (truncates toward zero, like the ALU) |
| `mod a b` | `a >= 0`, then `add_modulo_equality` |
| `eql a b` | bool `t`, with `a == b` enforced if `t` and `a != b` if not `t` |

Then `z_final == 0`, and the objective is to maximize (or minimize)
Σ dₖ·10^(13−k). Registers holding a known constant are folded in
Python, so `mul x 0` and the like make no variables. The model is
`cpsat_model_number` in the test module.

Measured with ortools 9.15, default solver settings:

| | answer | best / median of 5 |
|---|---|---|
| max | 51939397989999 | 14.9 / 15.6 ms |
| min | 11717131211195 | 14.8 / 15.8 ms |

Both solves report `OPTIMAL`, a proof that nothing better exists, not
just a feasible point.

**The one assumption is a bound.** CP-SAT needs finite domains, and
every intermediate value is given [−26⁸, 26⁸]. If the true optimum
needed an intermediate outside that range, the model would miss it.
For this input, `z` peaks at 363,367 (< 26⁴) on the part 1 answer.
Re-running with bounds of 2⁴⁰, 10¹², and 10¹⁵ gave the same answers
(measured during development, not pinned).

**Why it isn't the shipped solution.** It's two orders of magnitude
slower than the decompiled version, and it adds a binary dependency.
It also explains nothing: you get the number without learning that
MONAD is a stack machine. Its value is as a witness that shares no
reasoning with the main solution. The pairing argument in section 4
and the solver agree from opposite directions. In the tests it's
behind `pytest.importorskip`, so a clone without ortools still passes.

When to reach for it in general: a puzzle where you can write down the
rules but can't see the structure. It's the integer-programming
counterpart of handing a netlist to a SAT-based equivalence checker
instead of reasoning about the gates.

## 8. Possible optimization

None worth having. The 0.1 ms is parse-dominated. A generic
alternative that doesn't depend on the template is a depth-first
search over digits, memoized on `(block index, z)` and pruned when `z`
exceeds 26^(pops remaining). It would survive a MONAD that broke the
template, but it's much slower and it still leans on the stack insight
for its pruning. Not implemented or measured here.
