# Day 03 Function Guide — Binary Diagnostic

Source: [`src/day03.py`](../../src/day03.py) ·
Tests: [`tests/test_day03.py`](../../tests/test_day03.py) ·
Statement: [`day03.md`](day03.md)

Answers (accepted): **2648450** / **2845944**.

## 1. The problem

Each input line is a fixed-width binary number.

- **Part 1:** build *gamma* from the most common bit in each column and
  *epsilon* from the least common bit, then multiply them.
- **Part 2:** find two single rows by repeated filtering, then multiply them.
  Starting from the leftmost bit, keep only the rows whose bit matches a
  criterion, and move one bit right until one row is left. The *oxygen*
  rating keeps the most common bit (1 on a tie); the *CO2* rating keeps the
  least common bit (0 on a tie).

Part 1 trace on the statement's example, 12 rows of 5 bits. Count the 1s in
each column, leftmost first:

```text
column (MSB -> LSB)     4    3    2    1    0
ones out of 12          7    5    8    7    5
most common bit         1    0    1    1    0    gamma   = 10110 = 22
least common bit        0    1    0    0    1    epsilon = 01001 =  9
                                                 22 * 9 = 198
```

Read the last two rows as registers. Every epsilon bit is the complement of
the gamma bit above it, so epsilon is gamma with all five bits inverted:
`22 XOR 0b11111 = 9`. Only one of the two rates ever needs counting.

Part 2 trace, same report. The key change from part 1 is that each column is
counted over the **survivors**, not over all 12 rows:

```text
oxygen (most common, 1 on tie)
bit  survivors  ones:zeros  keep  left
 4      12         7:5       1      7
 3       7         3:4       0      4
 2       4         3:1       1      3
 1       3         2:1       1      2
 0       2         1:1       1      1   -> 10111 = 23

CO2 (least common, 0 on tie)
bit  survivors  ones:zeros  keep  left
 4      12         7:5       0      5
 3       5         2:3       1      2
 2       2         1:1       0      1   -> 01010 = 10     23 * 10 = 230
```

Two things to notice. CO2 finishes after three bits and never looks at the
last two. And at bit 4 the two searches keep **opposite halves** of the
report (the 7 ones versus the 5 zeros), so the two ratings can never be the
same row.

## 2. Representation

`parse_input` returns a `Report(width, values)` named tuple: every line as
an `int`, plus the bit width. Both parts work on the ints with shifts and
masks; neither ever looks at a string again.

The width is carried separately because the ints cannot give it back.
`00100` parses to 4, and nothing about 4 says it was five bits wide. Both
parts need it: part 1 for the XOR mask, part 2 to know which bit is "the
first bit". If every row happened to start with 0, a width inferred from the
largest value would be too narrow. Epsilon would lose its top 1 bit
(`test_width_comes_from_the_text_not_the_values`), and part 2 would start
filtering one column too far right.

The parse is strict about what it accepts:

- every line must be the same width as the first;
- every character must be `0` or `1`.

The second check exists because `int(s, 2)` is more forgiving than a
diagnostic report should be: `int("1_0", 2)` is 2 and `int("+101", 2)` is 5.
Both were run to confirm, and both are rejected as `ValueError`
(`test_malformed_input_is_an_error`). An empty report is also an error.

The real input is 1000 rows of 12 bits, all distinct.

## 3. Function walkthrough

### `parse_input(raw) -> Report`

Strips and drops blank lines, validates, converts. `strip()` is what makes
CRLF harmless (`test_crlf_input`).

### `ones_in_column(values, bit) -> int`

`sum((v >> bit) & 1 for v in values)`: shift the column of interest down to
bit 0, mask it off, add. Bit 0 is the least significant, the *rightmost*
column in the text. Both parts use it: part 1 on the whole report, part 2
on the current survivors.

### `gamma_rate(report) -> int`

For each bit position, sets that bit of `gamma` when the 1s are a strict
majority (`2 * ones > n`). Comparing `2 * ones` with `n` rather than
`ones` with `n / 2` keeps everything in integers.

A tied column (`2 * ones == n`) raises `ValueError`. Part 1 defines "most
common" and never says what happens on a tie, so a guess would be a silent
assumption. (Part 2 *does* define its ties, which is a hint the puzzle
author knew they could happen.) 1000 rows is an even count, so a tie was
possible on the real input; counting showed it does not happen -- the
closest column is 505 ones to 495 zeros.

### `part1(report) -> int`

`gamma_rate`, then epsilon as `gamma ^ ((1 << width) - 1)`, then the
product. On the real input:

```text
gamma   = 001100100101 =  805
epsilon = 110011011010 = 3290      805 * 3290 = 2648450
```

### `filter_rating(report, keep_majority) -> int`

Part 2's search, one function for both ratings. `keep_majority=True` is
oxygen and `False` is CO2.

The loop runs `bit` from `width - 1` down to 0. That is the one place where
the order of the columns matters. Part 1 could visit its columns in any
order; part 2's statement starts at "the first bit", the leftmost character,
which is the most significant bit. Each pass:

1. stops if one candidate is left;
2. counts ones and zeros among the candidates;
3. picks the bit to keep: oxygen takes 1 when `ones >= zeros`, and CO2
   takes 0 when `zeros <= ones`; the `=` in each is the statement's tie rule;
4. keeps the candidates with that bit.

After the loop there must be exactly one candidate, or it raises. The
statement's process has two ways to go wrong that it never mentions:

- **Duplicate rows.** Identical rows agree on every bit, so they survive to
  the end together (`101, 101`).
- **An emptied list, CO2 only.** If every survivor shares a bit, the least
  common value is the other bit, which *nobody* has, and keeping it keeps
  nothing (`110, 111` at bit 2). Oxygen cannot empty the list, because the
  most common value always has at least one row.

Neither happens on the real input: the rows are distinct, and a trace of
both searches found no column where the survivors were unanimous
(`test_filter_with_no_single_survivor_is_an_error` pins both cases).

On the real input oxygen needs all 12 bits and finishes on `001101001001` =
841. CO2 is down to one row after 8 bits and finishes on `110100111000` =
3384.

### `part2(report) -> int`

Both ratings, multiplied: 841 * 3384 = 2845944.

## 4. Why it is correct

Gamma is the statement applied column by column.

Epsilon rests on one identity: *in a column with no tie, the least common bit
is the complement of the most common bit*. With only two symbols, if 1 is
not the majority and it is not a tie, 0 is. That makes each epsilon bit
`NOT` the gamma bit, and XOR with an all-ones mask of the right width is
`NOT` applied to exactly those bits.

That covers the corner where a column is unanimous. If every row has a 1
there, the least common bit is 0, a bit that appears zero times, and the XOR
produces 0. The first draft of the test reference got this wrong, not the
solution: it asked `Counter` for the two most common characters, and a
unanimous column only has one.

Pinned rather than asserted, per the standing rule:
`test_epsilon_is_gamma_with_every_bit_flipped` checks `part1` against a
literal string-based implementation that counts both digits in each column
and picks most and least common separately. It runs 200 seeded random
reports of 1 to 12 bits and an odd number of rows, from 1 to 39. The odd row
count guarantees no ties, which is the identity's precondition, and a single
row makes every column unanimous. `test_example_rates` anchors the reference
to the statement's 22 and 9.

Part 2 is the statement executed in order, so what needs arguing is that
the int version matches the character version: that "leftmost character"
and "bit `width - 1`, counting down" are the same walk. That is pinned by
`test_filter_rating_matches_the_statement`, which runs a character-by-
character reference against `filter_rating` on 500 seeded random reports.
The reports are 1 to 6 bits wide with 1 to 20 rows, which is narrow enough
that duplicate rows and emptied lists turn up often. Where the reference
says the statement has no answer, `filter_rating` must raise, and the test
asserts that this path was actually hit. `test_part2_example_narration`
anchors the reference to every survivor list the statement prints, for both
ratings.

The "opposite halves at the first bit" observation from section 1 follows
from the two tie rules being mirror images. Oxygen keeps 1 exactly when
`ones >= zeros`, and CO2 keeps 0 exactly then, so at every column the two
rules would keep complementary groups. At the first bit they see the same
rows, so they split the report. `test_ratings_split_on_the_first_bit` checks
that the two ratings differ in their top bit on 200 random reports.

## 5. Complexity

Part 1 is `width` passes over all `n` values: O(n · width), which is 12,000
value visits on the real input.

Part 2 roughly halves the candidates at each bit, so each search costs about
`n + n/2 + n/4 + ...`, under 2n, and each pass visits its candidates twice:
once to count, once to filter. Measured on the real input, oxygen examines
2,086 values over 12 steps (1000, 513, 266, 139, ...) and CO2 examines 1,909
over 8. That is 3,995 values, or 7,990 visits, against part 1's 12,000. The
halving is not guaranteed -- a lopsided column keeps most of the rows -- so
the worst case is O(n · width) like part 1, but it does not happen here.

`bench.py 3`, best of 5 on the real input:

| phase | ms |
| --- | ---: |
| parse | 0.337 |
| part 1 | 0.527 |
| part 2 | 0.323 |
| total | 1.187 |

So the harder-sounding part is the cheaper one, and the visit counts explain
it. Part 2 also builds a new list per step, but the lists shrink fast
enough that the allocation does not show.

## 6. If I were writing this in Rust

Compiled and run while writing this guide, edition 2021. Part 1 gives 198 on
the example and 2648450 on the real input. Part 2 gives 23 and 10 on the
example, 841 and 3384 (product 2845944) on the real input, and `None` on
both undefined cases.

```rust
fn part1(values: &[u32], width: u32) -> u64 {
    let n = values.len();
    let mut gamma = 0u32;
    for bit in 0..width {
        let ones = values.iter().filter(|&&v| (v >> bit) & 1 == 1).count();
        assert!(2 * ones != n, "bit {bit} is tied");
        if 2 * ones > n {
            gamma |= 1 << bit;
        }
    }
    let epsilon = !gamma & ((1 << width) - 1);
    u64::from(gamma) * u64::from(epsilon)
}

fn filter_rating(values: &[u32], width: u32, keep_majority: bool) -> Option<u32> {
    let mut candidates = values.to_vec();
    for bit in (0..width).rev() {
        if candidates.len() == 1 {
            break;
        }
        let ones = candidates.iter().filter(|&&v| (v >> bit) & 1 == 1).count();
        let zeros = candidates.len() - ones;
        let wanted = if keep_majority == (ones >= zeros) { 1 } else { 0 };
        candidates.retain(|&v| (v >> bit) & 1 == wanted);
    }
    match candidates.as_slice() {
        [only] => Some(*only),
        _ => None,
    }
}
```

**Part 1** is the embedded-C version of the idea, and Rust says it more
directly than Python does. `!gamma` inverts all 32 bits of the `u32` and the
mask keeps the low `width` of them. Python's `int` has no fixed width, so
`~gamma` is `-gamma - 1`, a negative number, not an inverted register; that
is why the Python uses XOR with the mask instead of `~`. `!805u32 & 4095` is
3290, which matches the Python epsilon.

**Part 2** has three differences from the Python worth noting:

- `keep_majority == (ones >= zeros)` folds both rules into one line. It is
  the mirror-image property from section 4 written as code: oxygen wants 1
  exactly when `ones >= zeros`, and CO2 wants 1 exactly when that is false.
  The Python keeps two explicit branches because each one reads like its
  sentence in the statement; the Rust line reads like the proof.
- `Vec::retain` filters in place, reusing one allocation, where the Python
  builds a new list per step.
- The undefined cases return `None` instead of raising. The
  `match candidates.as_slice() { [only] => ... }` slice pattern says
  "exactly one element" in the type-checked way.

The part 1 product is widened to `u64` before multiplying. With 12 bits both
rates are below 4096 and the product fits `u32` easily, but the width is an
input property. Since gamma + epsilon is always `2^width - 1`, the product
peaks when the two are about equal. Checked by brute force over every gamma:
at 17 bits the worst case is 4,294,901,760, just under `u32::MAX`, and at 18
bits it is 17,179,738,112, which overflows. Part 2's two ratings are
unrelated rows, so its worst case at `width` bits is `(2^width - 1)^2`, and
that overflows `u32` from 17 bits.

For parsing, `u32::from_str_radix(line, 2)` is stricter than Python's `int`
in one way and not the other. Both were run while writing this guide:
`u32::from_str_radix("1_0", 2)` is an error, but `u32::from_str_radix("+101", 2)`
is `Ok(5)`. So a Rust port wants the same explicit `0`/`1` check the Python
parse does.

## 7. Possible optimization

None worth having; the day is 1.2 ms.

A sidebar for the curious: part 2 can be done without filtering at all.
Sort the values. The candidates at every step are then one contiguous range
of the sorted list, because rows sharing their top bits are adjacent. The
split point inside a range, between those with a 0 at the current bit and
those with a 1, is a binary search. Each step becomes O(log n) with no
counting pass, since the two sides' sizes are just the two sub-range
lengths. The whole of part 2 is then O(n log n) for the sort plus
O(width · log n) for the searches. This is the same idea as walking a binary
trie of the values. Not adopted: the filter is the statement, read
directly, and 0.32 ms leaves nothing to win.
