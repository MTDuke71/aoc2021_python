# Day 06 Function Guide — Lanternfish

Source: [`src/day06.py`](../../src/day06.py) ·
Tests: [`tests/test_day06.py`](../../tests/test_day06.py) ·
Statement: [`day06.md`](day06.md)

Answers (accepted): **373378** / **1682576647495**.

## 1. The problem

Each lanternfish is a countdown timer. A fish at 0 resets to 6 and spawns a
new fish at 8. Every other fish drops by 1. How many fish exist after
80 days (part 1)? The example, `3,4,3,1,2`, gives 5934.

Trace the first two days of the example as a histogram, `counts[t]` = how
many fish have timer t:

```text
day 0:  3,4,3,1,2          counts = [0, 1, 1, 2, 1, 0, 0, 0, 0]
day 1:  2,3,2,0,1          counts = [1, 1, 2, 1, 0, 0, 0, 0, 0]   shift left
day 2:  1,2,1,6,0,8        counts = [1, 2, 1, 0, 0, 0, 1, 0, 1]
```

Day 1 is a pure shift: no fish was at 0. Day 2 has one fish at 0. It wraps
to slot 8 as the newborn, and the same fish also lands in slot 6 as the
reset parent. So slot 6 gains 1 and slot 8 gains 1, from one fish.

The fish-per-entry simulation is exponential in population. The statement
hints at this ("maybe *exponentially* quickly?"). The histogram doesn't
care: 9 slots regardless of how many fish there are.

## 2. Representation

`parse_input` returns `list[int]` of length 9, the histogram. That is the
full parse: the histogram doesn't depend on which part asks, so it is
built once here. The stub's `list[str]` placeholder is gone.

Fish are interchangeable. Two fish with the same timer behave identically
forever, so which fish is which carries no information. The list order in
the statement's day-by-day listings is not preserved (a `0` becomes a `6`
in place and its child is appended), and no answer depends on it.

The real input is 300 fish with timers only 1 through 5:

```text
counts = [0, 145, 39, 53, 33, 30, 0, 0, 0]
```

The register framing: it is a 9-stage shift register with one feedback tap.
Slot 0's output feeds slot 8 (the newborn stage) and is also added into
slot 6.

## 3. Function walkthrough

### `parse_input(raw) -> list[int]`

Replaces commas with spaces and splits on whitespace. That tolerates the
trailing newline and a CRLF `\r` alike (`test_crlf_input`). Each field is
converted with `int`, which raises on junk like `x`. A timer outside 0..8
raises `ValueError` too, since it would index off the end or silently
wrap from the front of the list.

### `step(counts) -> list[int]`

One day:

```python
spawning = counts[0]
nxt = counts[1:] + [spawning]   # shift left; the wrapped fish are the newborns at 8
nxt[CYCLE - 1] += spawning      # the same fish, reset, land on 6
```

It returns a new list rather than mutating, so `parse_input`'s result is
never disturbed and `part1` and `part2` can both start from it.

`CYCLE = 7` and `NEWBORN = 8` name the two constants from the statement.
Slot 6 is `CYCLE - 1` because a fish that spawns has timer 0 and comes out
at 6: it counts 7 days through 6, 5, 4, 3, 2, 1, 0.

### `population(counts, days) -> int`

Applies `step` that many times and sums the histogram. Negative `days`
raises instead of quietly returning the day-0 population.

### `part1` and `part2`

`population(counts, 80)` and `population(counts, 256)`. Same code, longer
loop.

## 4. Why it is correct

**Grouping by timer is lossless.** A fish's future depends only on its own
timer, and the rule is applied to each fish independently. So the number of
fish at each timer after a day is a function of the number at each timer
before it, which is exactly what `step` computes: slot t after the day is
slot t+1 before, for t = 0..7 except t = 6, which also gets the parents.
Slot 8 after the day is slot 0 before.

**The rule is pinned against the literal simulation.**
`test_histogram_matches_one_entry_per_fish` runs a fish-per-entry
simulation transcribed straight from the statement (`0 -> 6` plus an
appended 8, everything else minus 1) alongside `step`, for 40 days, starting
from a mix that includes every timer 0..8 and repeats. The two agree as
sorted multisets every day. `test_statement_listing` also compares against
ten of the statement's own day-by-day lines (days 0-5, 9-11 and 18).

**The example totals** are 26 at day 18, 5934 at day 80
(`test_example_population`) and 26984457539 at day 256. All three come from the statement.

**Spawn timing.** `test_lone_fish_timeline` starts one fish at 3: it is
still 1 fish after 3 days and 2 after 4, matching the statement's opening
walkthrough (`3 -> 2 -> 1 -> 0 -> 6`, with an 8 born on that last day).

## 5. Complexity

O(days x 9) time and O(9) space, independent of the population. Only the
values grow.

| phase | ms |
| --- | ---: |
| parse | 0.057 |
| part 1 | 0.028 |
| part 2 | 0.074 |
| total | 0.159 |

`bench.py 5`, best of 5 on the real input. Part 2 takes about 2.6x part 1
for 3.2x the days. Parse (300 `int` calls) costs about twice as much as 80 days
of simulation.

Magnitude: the real input's part 2 total is 1,682,576,647,495, which needs
41 bits. It fits `i64` and `u64` with room to spare. In Python it is
irrelevant, but it is the reason the Rust version uses `u64`.

## 6. If I were writing this in Rust

Compiled and run while writing this guide (rustc 1.93.1, `-O`). It gives
5934 / 26984457539 on the example and 373378 / 1682576647495 on the real
input, the same as the Python.

```rust
fn parse(raw: &str) -> [u64; 9] {
    let mut counts = [0u64; 9];
    for f in raw.split(|c: char| c == ',' || c.is_whitespace()).filter(|s| !s.is_empty()) {
        counts[f.parse::<usize>().unwrap()] += 1;
    }
    counts
}

fn population(mut counts: [u64; 9], days: u32) -> u64 {
    for _ in 0..days {
        counts.rotate_left(1); // slot 0 wraps to 8: the newborns
        counts[6] += counts[8]; // the parents reset to 6
    }
    counts.iter().sum()
}
```

- **`[u64; 9]` is the histogram.** A fixed array on the stack: no
  allocation, `Copy`, so `population(ex, 80)` and `population(ex, 256)` can
  both start from the same value without a clone. Python's list is
  heap-allocated and step returns a new one each day.
- **`rotate_left(1)` is the shift.** It works in place on the array, so the
  Rust step needs no temporary.
- **The order of the two lines matters.** After the rotate, slot 8 holds the
  old slot 0, so `counts[6] += counts[8]` reuses the newborn count as the
  parent count. There is no `spawning` local, but it is the same fact.
- **`u64`, not `u32`.** 1.68e12 does not fit in `u32` (max about 4.29e9),
  so the type has to be 64-bit. Same shape as the day 2 `i32` headroom note.
- **`parse::<usize>()` doubles as the range check** for indexing, except
  that a timer of 9 or more would panic on the index rather than return a
  clean error as the Python does.

Embedded framing: this is a circular buffer of 9 counters. Instead of
moving 9 words each day, keep a head index that advances by 1 mod 9, and
add `buf[head]` into `buf[(head + 7) % 9]` before advancing. That is
constant work per day with no data movement.

## 7. Possible optimization

The day runs in about 0.16 ms, so none is needed. One measured
alternative:

**`collections.deque` with `rotate`.** `q.rotate(-1); q[6] += q[8]` is the
Rust step written in Python. It gives the same part 2 answer and takes
0.035 ms against 0.082 ms for `step` in the same run (best of 5 repeats of
200), roughly 2.3x faster. It is not used because the list version reads
as the statement does, and the whole day is already under a fifth of a
millisecond.

The other route is to treat one day as a 9x9 matrix and raise it to the
256th power by squaring, which turns O(days) into O(log days). Nothing
here needs it, and I did not implement or measure it.
