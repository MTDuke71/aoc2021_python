# Day 08 Function Guide — Seven Segment Search

Source: [`src/day08.py`](../../src/day08.py) ·
Tests: [`tests/test_day08.py`](../../tests/test_day08.py) ·
Statement: [`day08.md`](day08.md)

Answers (accepted): **274** / **1012089**.

## 1. The problem

A four-digit seven-segment display has its seven wires `a`-`g` hooked to the
segments in an unknown order, and the order differs per display. Each input
line gives the ten patterns the display shows (one per digit 0-9, order
unknown) and then four output patterns to read.

Trace the statement's single entry:

```text
patterns:  acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab
outputs:   cdfeb fcadb cdfeb cdbaf

by length:  ab=1   dab=7   eafb=4   acedgfb=8          (2, 3, 4, 7 wires)
5 wires:    cdfbe gcdfa fbcad      -> 5, 2, 3
6 wires:    cefabd cdfgeb cagedb   -> 9, 6, 0
outputs:    cdfeb=5  fcadb=3  cdfeb=5  cdbaf=3   ->  5353
```

Part 1 only needs the first line of that trace: count outputs whose length
singles out a digit. Part 2 needs all of it. The design question is whether
the wire-to-segment map has to be recovered. It does not: the digit can be
read straight off set sizes.

## 2. Representation

`parse_input` returns `list[(patterns, outputs)]`, each pattern a
`frozenset[str]` of its lit wires. Wire order inside a pattern means nothing
(`cdfeb` and `bcdef` are the same pattern), so a set is the honest type, and
it makes the decoder's questions one-liners: `len(s)`, `s & other`,
`one <= s` (is `one` contained in `s`). Frozen so a pattern can be a dict key.

A malformed line (no `|`, not 10 patterns, not 4 outputs) raises
`ValueError`. Blank lines are skipped.

The real input is 200 entries. Output digit lengths: 6 wires 270, 5 wires 256,
2 wires 78, 7 wires 70, 4 wires 65, 3 wires 61. Every line's ten patterns are
distinct.

## 3. Function walkthrough

### `parse_input(raw) -> list[Entry]`

`splitlines()` (CRLF-safe, `test_crlf_input`), then `partition("|")` and
`split()` on each side; `split()` also drops any stray `\r`.

### `part1(entries) -> int`

Count output signals whose length is in `UNIQUE_LENGTHS = {2, 3, 4, 7}`. The
scramble moves wires between segments but never changes how many are lit, so
length is scramble-proof. Only outputs count; the left side is ignored.
Real input: 78 + 61 + 65 + 70 = **274**.

### `decode_patterns(patterns) -> dict[Signal, int]`

Groups the ten patterns by length. 2, 3, 4, 7 give 1, 7, 4, 8 (each of those
lengths must occur exactly once, else `ValueError`). The ambiguous groups are
then split by overlap with the known 1 and 4:

| length | digits | test | result |
| --- | --- | --- | --- |
| 5 | 2, 3, 5 | contains all of 1 | 3 |
| 5 | | shares 3 wires with 4 | 5 |
| 5 | | otherwise | 2 |
| 6 | 0, 6, 9 | contains all of 4 | 9 |
| 6 | | contains all of 1 | 0 |
| 6 | | otherwise | 6 |

Numeric trace on the statement entry, where 1 = `ab` and 4 = `eafb`:

```text
fbcad  contains a and b                     -> 3
cdfbe  lacks a; shares {b, e, f} with eafb  -> 5   (3 wires)
gcdfa  lacks b; shares {a, f} with eafb     -> 2   (the leftover)
```

That matches the statement's `fbcad: 3`, `cdfbe: 5`, `gcdfa: 2`.

### `decode_entry(entry) -> int`

Build the lookup, then fold the four outputs into a number
(`value * 10 + digit`). A leading zero output such as `0007` simply gives 7
(`test_leading_zero_output_is_a_number`).

### `part2(entries)`

Sum of `decode_entry`. Real input: 200 values from 58 to 9994 (20 of them
under 1000, i.e. with a leading 0), sum **1012089**.

## 4. Why it is correct

The standing claim is that (length, overlap with 1, overlap with 4) identifies
every digit under any scramble. Two reasons it holds:

- **The signature is invariant.** A scramble is a relabelling of wires, and a
  relabelling cannot change the size of a set or of an intersection. So the
  sizes computed on scrambled patterns equal the sizes on a true display.
- **The signature is unique.** On a true display the ten triples
  `(len, |s & 1|, |s & 4|)` are all different
  (`test_each_digit_has_a_distinct_overlap_signature`). The decoder's table
  is a minimal subset of those distinctions.

Both are pinned by running, not asserted in prose:
`test_overlap_rule_decodes_every_wiring` decodes all 5040 possible wirings and
checks every digit, and
`test_overlap_rule_matches_brute_force_on_random_displays` compares end to end
against a solver that never uses the rule (try every permutation, keep the
one that explains the ten patterns). On the real input that brute-force solver
also gives 1012089 (measured, section 7).

## 5. Complexity

Parse is O(n) in entries (14 small sets each). Part 1 is O(n). Part 2 is O(n)
with a constant of ten classifications plus four lookups per entry. Set
operations are over at most 7 elements.

| phase | ms |
| --- | ---: |
| parse | 0.721 |
| part 1 | 0.041 |
| part 2 | 0.611 |
| total | 1.373 |

`bench.py -n 5 8`, best of 5 on the real input. Parse dwarfs part 1 because
building 2800 frozensets costs far more than counting lengths.

## 6. If I were writing this in Rust

Compiled and run while writing this guide (rustc 1.93.1, `-O`). It gives
26 / 61229 on the statement example and 274 / 1012089 on the real input, the
same as the Python.

```rust
fn mask(s: &str) -> u8 {
    s.bytes().fold(0, |m, b| m | 1 << (b - b'a'))
}

let digit = |p: u8| match (p.count_ones(), (p & one).count_ones(), (p & four).count_ones()) {
    (2, _, _) => 1, (3, _, _) => 7, (4, _, _) => 4, (7, _, _) => 8,
    (5, 2, _) => 3, (5, _, 3) => 5, (5, _, _) => 2,
    (6, _, 4) => 9, (6, 2, _) => 0, _ => 6,
};
```

- **A pattern is a `u8`.** Seven wires fit in seven bits, so `frozenset`
  becomes a bitmask: size is `count_ones()`, intersection is `&`, "contains"
  is `p & one == one`. No hashing, no allocation, `Copy`.
- **The decoder is one `match` on a tuple.** It reads like the table in
  section 3. Python needs an if/elif chain.
- **`find` for 1 and 4** replaces the `by_length` dict: scan the ten masks for
  `count_ones() == 2` and `== 4`.

Embedded framing: this is a register-level problem. Each display is a 7-bit
register, the scramble is a bit permutation, and popcount and AND are the two
operations a permutation cannot disturb. That invariance is the whole solution.

## 7. Possible optimization

The whole day takes 1.4 ms, so none is needed. One measured alternative:

**Brute force over wirings.** For each entry try all 5040 permutations until
one reproduces the ten patterns. On the real input that is 2718 ms (best of 3),
about 4400x slower than part 2's 0.611 ms, and it gives the same 1012089. It is
the test suite's ground truth, which is the role it suits.

**Bitmask patterns in Python.** Parsing to ints (`1 << (ord(c) - 97)`) and
using `int.bit_count()` would avoid building frozensets, which is where the
parse time goes. Not measured, and it would trade the readable set operations
for bit tricks.
