# Day 02 Function Guide — Dive!

Source: [`src/day02.py`](../../src/day02.py) ·
Tests: [`tests/test_day02.py`](../../tests/test_day02.py) ·
Statement: [`day02.md`](day02.md)

Answers (accepted): **2070300** / **2078985210**.

## 1. The problem

Each input line is a submarine command: `forward X`, `down X` or `up X`.
Position is a pair (horizontal, depth), both starting at 0. Depth grows
*downward*, so `down` adds and `up` subtracts.

- **Part 1:** `down`/`up` change depth directly. Follow the course, then
  multiply final horizontal by final depth.
- **Part 2:** `down`/`up` change a third value, *aim*, instead. `forward X`
  still adds `X` to horizontal, and now also adds `aim * X` to depth. Same
  final multiplication.

Part 1 trace on the statement's example:

```text
command     horizontal  depth
forward 5        5        0
down 5           5        5
forward 8       13        5
up 3            13        2
down 8          13       10
forward 2       15       10      -> 15 * 10 = 150
```

Read the two columns separately. Horizontal is `5 + 8 + 2 = 15`; depth is
`5 - 3 + 8 = 10`. No command reads the other column, so the order of the
commands does not matter -- each column is just a sum.

Part 2 trace, same commands:

```text
command     horizontal  depth  aim
forward 5        5        0     0     aim is 0, so depth stays put
down 5           5        0     5
forward 8       13       40     5     depth += 5 * 8
up 3            13       40     2
down 8          13       40    10
forward 2       15       60    10     depth += 10 * 2   -> 15 * 60 = 900
```

Now `forward` *reads* aim, so order matters. In register terms, aim is a
rate and `forward X` integrates it for `X` ticks: depth is the running
integral of aim over horizontal distance.

Two things carry over unchanged from part 1. Horizontal is the same 15. And
the aim column here (0, 5, 5, 2, 10, 10) is exactly part 1's depth column:
`down`/`up` do to aim what they used to do to depth.

## 2. Representation

`parse_input` returns `list[tuple[int, int]]`: each command as a
`(forward, dive)` pair of signed deltas.

```text
forward 5 -> (5, 0)
down 5    -> (0, 5)
up 3      -> (0, -3)
```

The second element is deliberately named `dive`, not `depth`: what it is a
delta *of* is the caller's reading -- depth in part 1, aim in part 2. The
parse does not depend on which part is asking.

The command word is resolved at parse time, including the sign flip for
`up`, so nothing downstream compares strings. An unrecognised command raises
`ValueError` rather than being skipped (`test_unknown_command_is_an_error`)
-- a silently dropped line would give a plausible wrong answer.

`line.split()` splits on any whitespace, which also discards a trailing
`\r`, and lines come from `splitlines()`; CRLF is harmless either way
(`test_crlf_input`).

The real input is 1000 commands -- 407 `down`, 402 `forward`, 191 `up` --
with every amount between 1 and 9.

## 3. Function walkthrough

### `parse_input(raw) -> list[tuple[int, int]]`

Described above. One `if/elif` chain over the three command words.

### `part1(moves) -> int`

One pass, accumulating both columns, then the product. On the real input
that is horizontal 2010, depth 1030.

It is `steer` with the `aim` line removed, and that is the point of writing
it as a loop rather than as two `sum()` calls over the columns: side by side,
the two parts are the same loop with one line different, which is exactly
what part 2 changed.

### `steer(moves) -> (horizontal, depth, aim)`

Part 2's walk. The loop body has no branch:

```python
aim += dive
horizontal += forward
depth += aim * forward
```

Every pair has a zero in it. For a `down`/`up`, `forward` is 0, so the last
two lines add nothing. For a `forward`, `dive` is 0, so aim is untouched and
the depth update uses the aim already in force. Because the two cases never
overlap, the order of the three lines does not matter either.

It returns aim as well as the position, only so the tests can see it.

### `part2(moves) -> int`

`steer`, then horizontal times depth. On the real input: horizontal 2010,
depth 1,034,321, final aim 1030.

## 4. Why it is correct

Part 1's three commands are each "add a constant to one coordinate". Integer
addition is commutative and associative, and no command's effect depends on
the current state, so the final position is the column sums regardless of
order.

That independence is an assumption about *part 1's rules*, so it is pinned
rather than asserted: `test_column_sums_match_step_by_step` checks `part1`
against a literal one-command-at-a-time walk on 39 seeded random courses, and
`test_example_running_totals` anchors that walk to the six running positions
the statement narrates. (`part1` is itself a walk now; the test dates from
when it was two column sums and still earns its keep, because it is what
licenses the column-sum reading in section 1 and the order test below.)

Part 2 is the statement's rules executed in order, so the only thing to
argue is the branch-free loop, and that is pinned too:
`test_steer_matches_the_manual` checks `steer` against a three-branch
implementation that works from the raw command text, on 39 seeded random
courses (aim going negative included). `test_part2_example_running_totals`
anchors that reference to the statement's narration, and
`test_part2_depends_on_order` shows the part 1 shortcut really is dead:
`down 5, forward 8` and `forward 8, down 5` agree in part 1 (40) and differ
in part 2 (320 vs 0).

The carry-over noted in section 1 -- final aim equals part 1's depth, with
horizontal shared -- is `test_part2_aim_is_part1_depth`. On the real input
both are 1030.

The statement never says depth cannot go negative, and neither part clamps:
`forward 3, up 4` gives -12 in part 1 (`test_part1_edges`). On the real input
the question does not arise -- in both parts the lowest depth reached en
route is 0, and in part 2 aim stays within 0..1036.

## 5. Complexity

One pass over the list for each part, O(n) time and O(1) extra space
beyond the parse.

`bench.py 2`, best of 5 on the real input:

| phase | ms |
| --- | ---: |
| parse | 0.186 |
| part 1 | 0.036 |
| part 2 | 0.056 |
| total | 0.278 |

As on day 01, parsing costs more than both parts together. Part 1 was
0.065 ms as two `sum()` generator expressions over the columns; the single
loop halved it, which is the cost of walking 1000 tuples a second time.

## 6. If I were writing this in Rust

Compiled and run while writing this guide, edition 2021: both functions on
the example with CRLF line endings (150 and 900) and on the real input
(2070300 and 2078985210).

```rust
enum Command {
    Forward(i64),
    Down(i64),
    Up(i64),
}

fn part1(course: &[Command]) -> i64 {
    let (horizontal, depth) = course.iter().fold((0, 0), |(h, d), c| match c {
        Command::Forward(x) => (h + x, d),
        Command::Down(x) => (h, d + x),
        Command::Up(x) => (h, d - x),
    });
    horizontal * depth
}

fn part2(course: &[Command]) -> i64 {
    let (horizontal, depth, _aim) = course.iter().fold((0, 0, 0), |(h, d, aim), c| match c {
        Command::Forward(x) => (h + x, d + aim * x, aim),
        Command::Down(x) => (h, d, aim + x),
        Command::Up(x) => (h, d, aim - x),
    });
    horizontal * depth
}
```

Where Python flattens the command into a delta pair, Rust would more
naturally keep an `enum` and `match` on it: the compiler then checks that all
three commands are handled, which is the job the `else: raise ValueError` does
by hand in Python. Parsing is `split_once(' ')` plus a `match` on the word,
with the unknown-word arm as the error path.

With the `enum` there is no reason for the branch-free trick `steer` uses;
the `match` arms *are* the three branches, and the two parts differ only in
what `Down`/`Up` write to.

The integer width is the real decision, and it is closer than it looks. The
values must be signed, since `up` subtracts and nothing promises aim or depth
stay non-negative. Part 1's product is about 2.07 million, comfortable in
`i32`. Part 2's is 2,078,985,210 against an `i32` maximum of 2,147,483,647 --
it fits with about 3% to spare. `2010i32.checked_mul(1034321)` is `Some`, but
the same call with a depth of 1,100,000 is `None`. A different account's
input could easily land on the wrong side, where a release build wraps
silently, so `i64` is the honest choice. Python never raises the question.

## 7. Possible optimization

None worth having; the day is 0.28 ms and parse-dominated.

One structural note rather than a speed-up: part 2 subsumes part 1. `steer`
already returns the aim, and part 1's answer is `horizontal * aim`
(`test_part2_aim_is_part1_depth`), so a single walk could produce both
answers. Not adopted -- `part1` as its own loop says what part 1 means, and
deriving it from part 2's aim would make it depend on a coincidence of the
two rule sets.
