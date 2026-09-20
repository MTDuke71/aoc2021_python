# Day 00 Function Guide — The Tyranny of the Rocket Equation

> Tutorial dry run, not an AoC 2021 puzzle: this is AoC 2019 day 1, reused
> because its answers were already known. It exists to prove the pipeline end
> to end -- module, tests, locked answers, bench, guide -- and to show the
> section order every later guide follows, at its smallest.

Source: [`src/day00.py`](../../src/day00.py) ·
Tests: [`tests/test_day00.py`](../../tests/test_day00.py) ·
Statement: [`day00.md`](day00.md)

Answers (accepted): **3481005** / **5218616**.

## 1. The problem

Each input line is the mass of one spacecraft module. Fuel for a module is
`floor(mass / 3) - 2`.

- **Part 1:** sum that over all modules.
- **Part 2:** fuel has mass too, so it needs its own fuel, which needs its
  own, and so on until a step asks for zero or less. Sum the whole chain per
  module, then over all modules.

Trace for a mass of 1969, the statement's own example:

```text
1969 -> 654 -> 216 -> 70 -> 21 -> 5 -> -1 (stop, not counted)
part 1 contribution: 654
part 2 contribution: 654 + 216 + 70 + 21 + 5 = 966
```

## 2. Representation

`parse_input` returns `list[int]`, one mass per line. There is nothing to
derive that both parts share, so the parse is the whole structure. The real
input is 100 modules with masses from 51,187 to 149,855.

Lines go through `splitlines()` and blank ones are dropped, which is what
makes a CRLF input and a trailing newline both harmless (`test_crlf_input`).

## 3. Function walkthrough

### `fuel(mass) -> int`

The base equation, `mass // 3 - 2`. It is allowed to go negative -- `fuel(2)`
is `-2` -- and deliberately does not clamp. Deciding what a non-positive
result *means* is the caller's job, and the two callers disagree: part 1 never
sees one, part 2 treats it as "stop".

### `total_fuel(mass) -> int`

Part 2's chain as a loop: compute a step, add it while it is positive, feed it
back in. The check is `f > 0` *before* the add, so the first non-positive step
ends the chain without being counted. `test_small_masses_never_go_negative`
pins the two boundary cases: a mass of 6 (step is exactly 0) and a mass of 2
(step is -2) both contribute nothing.

### `part1` / `part2`

`sum` of `fuel` and of `total_fuel` over the list.

## 4. Why it is correct

Part 1 is the formula applied as written.

For part 2 the only thing to argue is termination and the stop condition.
For any `f > 0`, `f // 3 - 2 < f`, so the chain strictly decreases and must
reach a non-positive value. The statement says a negative requirement counts
as zero fuel, and that the chain continues "until a fuel requirement is zero
or negative". Adding a 0 changes nothing and adding a negative would be wrong,
so stopping at the first `f <= 0` without adding it covers both.

## 5. Complexity

Each step divides by 3, so a chain from mass `m` is about `log3(m)` steps; the
longest on the real input is 9. Both parts are linear in the number of
modules with a tiny constant.

Measured with `bench.py` (best of 5): parse 0.018 ms, part 1 0.013 ms,
part 2 0.113 ms.

## 6. If I were writing this in Rust

The loop ports line for line. The one decision Rust forces that Python does
not is the integer type. With `u32` masses, `mass / 3 - 2` underflows for a
mass below 6 -- a panic in debug, a wraparound to four billion in release.
Two honest ways out:

- Use `i64` and keep the Python shape, `while f > 0`.
- Stay unsigned and write `(mass / 3).saturating_sub(2)`. Both the "exactly
  0" and the "would be negative" cases collapse to 0, which is precisely the
  statement's "treat as zero", and the loop condition is unchanged.

`std::iter::successors(Some(fuel(m)), |&f| Some(fuel(f))).take_while(|&f| f > 0).sum()`
is the iterator spelling of `total_fuel`.

Python's `//` floors and Rust's `/` truncates. They differ only for negative
operands, and nothing negative is ever divided here -- `fuel` is only fed
masses and positive steps -- so the port needs no adjustment for it.

## 7. Possible optimization

None worth having. The whole day is 0.14 ms.
