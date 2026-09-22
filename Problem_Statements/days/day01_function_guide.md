# Day 01 Function Guide — Sonar Sweep

Source: [`src/day01.py`](../../src/day01.py) ·
Tests: [`tests/test_day01.py`](../../tests/test_day01.py) ·
Statement: [`day01.md`](day01.md)

Answers (accepted): **1791** / **1822**.

## 1. The problem

Each input line is one sonar depth reading, in sweep order.

- **Part 1:** count the readings that are larger than the reading before.
- **Part 2:** slide a three-reading window along the list, sum each window,
  and count the sums that are larger than the sum before.

Trace on the statement's example, first five readings only:

```text
readings:        199  200  208  210  200
part 1 compares: 200>199 yes, 208>200 yes, 210>208 yes, 200>210 no

window A = 199+200+208 = 607
window B =     200+208+210 = 618      B > A: yes
window C =         208+210+200 = 618  C > B: no  (equal is not an increase)
```

Now look at what B - A actually is. The `200` and `208` are in both windows,
so they cancel: `B - A = 210 - 199`. Likewise `C - B = 200 - 200 = 0`. The
window comparison is a comparison of two single readings three places apart.
That is the whole day.

## 2. Representation

`parse_input` returns `list[int]`, one depth per line. Neither part needs
anything derived beyond that. The real input is 2000 readings ranging from
198 to 10,931.

Lines go through `splitlines()` and blank ones are dropped, so CRLF and a
trailing newline are both harmless (`test_crlf_input`).

## 3. Function walkthrough

### `count_increases(depths, gap) -> int`

Counts positions where `depths[i + gap] > depths[i]`. It is written as a
`zip` of the list against itself shifted by `gap`:

```text
depths      : 199 200 208 210 200 207 ...
depths[3:]  : 210 200 207 240 ...
pairs       : (199,210) (200,200) (208,207) (210,240) ...
```

`zip` stops at the shorter sequence, so the pairs run out exactly when there
is no reading `gap` places later. A list shorter than `gap + 1` gives an
empty slice, no pairs, and a count of 0 -- no length check needed
(`test_part1_edges`, `test_part2_edges`).

`sum(later > earlier ...)` adds up booleans; `True` is 1.

### `part1` / `part2`

`count_increases(depths, 1)` and `count_increases(depths, 3)`. Part 1 and
part 2 are the same function at two gaps.

## 4. Why it is correct

Part 1 is the statement applied as written.

Part 2 rests on one identity. For adjacent windows starting at `i` and
`i + 1`:

```text
sum(d[i+1 .. i+3]) - sum(d[i .. i+2])
  = (d[i+1] + d[i+2] + d[i+3]) - (d[i] + d[i+1] + d[i+2])
  = d[i+3] - d[i]
```

So the later sum is strictly larger exactly when `d[i+3] > d[i]`, and ties
map to ties. The number of comparisons also agrees: `n - 2` windows give
`n - 3` adjacent pairs, and `zip(d, d[3:])` yields `n - 3` pairs.

Per the standing rule, this is pinned rather than asserted:
`test_gap3_matches_window_sums` checks `part2` against a literal
build-the-sums implementation on 40 seeded random lists with values 0-9, a
range narrow enough to force many ties. `test_example_window_sums` anchors
that reference implementation to the eight sums the statement prints
(607, 618, 618, 617, 647, 716, 769, 792). The literal version was also run
once against the real input and agrees with `part2`.

Strict `>` matters on the real data. Part 1 has no equal neighbours at all,
but at gap 3 there are 16 tied pairs; `>=` would report 16 more than `>`.

## 5. Complexity

One pass, O(n) time. `depths[gap:]` copies the list, so O(n) extra space --
2000 ints, irrelevant here. The general point: a window of width `w` costs
the same as a window of width 1, because the window is never summed.

`bench.py 1`, best of 5 on the real input:

| phase | ms |
| --- | ---: |
| parse | 0.175 |
| part 1 | 0.087 |
| part 2 | 0.083 |
| total | 0.346 |

Parsing 2000 ints is the most expensive step of the day.

## 6. If I were writing this in Rust

Two spellings, both compiled and run against the example (7 and 5) while
writing this guide:

```rust
fn count_increases(depths: &[u32], gap: usize) -> usize {
    depths.iter().zip(depths.iter().skip(gap)).filter(|(a, b)| b > a).count()
}

fn count_windows(depths: &[u32], gap: usize) -> usize {
    depths.windows(gap + 1).filter(|w| w[gap] > w[0]).count()
}
```

The first is the Python line for line, and `skip` is lazy, so the O(n) copy
that `depths[gap:]` makes disappears. The second uses slice `windows`, which
reads closest to the statement: look at four readings, compare the ends. Both
return 0 on a slice shorter than `gap + 1` without a guard -- `zip` runs dry,
and `windows` yields nothing when the slice is shorter than the window.

`u32` is safe: nothing is subtracted, so there is no underflow to think about
(unlike day 00), and even the literal window sum tops out near 3 x 10,931.

For parsing, `str::lines()` strips `\r\n` as well as `\n`; `split('\n')`
leaves the `\r` on, the same trap as Python's `split("\n")`.

## 7. Possible optimization

None worth having; the day is 0.35 ms and parse-dominated. The memory-tidy
variant is `itertools.islice(depths, gap, None)` in place of `depths[gap:]`
to avoid the copy -- not adopted, since the slice reads better and 2000 ints
is nothing.
