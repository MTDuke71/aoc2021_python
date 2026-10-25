# Day 14 Function Guide — Extended Polymerization

Source: [`src/day14.py`](../../src/day14.py) ·
Tests: [`tests/test_day14.py`](../../tests/test_day14.py) ·
Statement: [`day14.md`](day14.md)

Answers (accepted): **2745** / **3420801168962**.

## 1. The problem

The input is a polymer template, a string of element letters, and a list of
rules `AB -> C`: wherever `A` and `B` are adjacent, insert `C` between them.
Every adjacent pair is rewritten at the same time, and the inserted letters
don't count as part of a pair until the next step.

The answer is the count of the most common letter minus the count of the
least common one:

- **Part 1:** after 10 steps.
- **Part 2:** after 40 steps.

Trace on the statement's example: template `NNCB`. Its pairs are `NN`, `NC`,
`CB`, with rules `NN -> C`, `NC -> B`, `CB -> H`. One step inserts all three
at once:

```text
N   N   C   B
  C   B   H
N C N B C H B     (NCNBCHB)
```

Four letters became seven. In general **n letters become 2n − 1**, because
one letter goes into each of the n − 1 gaps. So the length after k steps is
(n − 1)·2ᵏ + 1. The real template has 20 letters, so the polymer would be
19,457 letters after 10 steps and **20,890,720,927,745** (about 2·10¹³)
after 40. Building the string works for part 1 but cannot work for part 2.

## 2. Representation

`parse_input` returns `Polymer`, a `NamedTuple` of:

- **`pairs`**: a `Counter` of the template's adjacent pairs. `NNCB` gives
  `{NN: 1, NC: 1, CB: 1}`.
- **`last`**: the template's last letter.
- **`rules`**: each pair mapped to the two pairs it turns into.
  `CH -> B` is stored as `CH: ("CB", "BH")`.

The polymer is stored as **how many times each pair occurs**, not where.
Where a pair sits makes no difference to what it becomes: every `CH`
anywhere in the polymer becomes a `CB` and a `BH`. So the counts alone are
enough to compute the next step's counts.

Storing each rule as its two output pairs, rather than as the inserted
letter, means the step does no string building. It reads two keys and adds
twice.

Real input: a 20-letter template over 10 letters (B C F H K N O P S V), and
100 rules, one for each of the 10 × 10 possible pairs.

## 3. Function walkthrough

### `parse_input(raw) -> Polymer`

`splitlines()` plus a per-line `strip()`, so CRLF input leaves no `\r`.
Blank lines are dropped. The first line is the template; every later line
must be `AB -> C`, in upper-case letters.

`ValueError` on:

- an empty input, or a template that is shorter than 2 letters or not
  upper-case letters;
- a malformed rule, or two rules for the same pair;
- **a pair with no rule.** The parser collects every letter in play (from
  the template and the rules) and requires a rule for each ordered pair of
  them. The statement doesn't say what happens to a pair with no rule, so
  the parser refuses rather than guessing that the pair is left alone.
  `test_real_input_rules_cover_every_pair` checks the real input: all 100
  pairs have a rule.

### `step(pairs, rules) -> Counter`

For each pair `AB` with count n, add n to each of its two output pairs,
`AC` and `CB`. The result is a fresh `Counter`. It is never updated in
place, because a pair's own output can be a pair that hasn't been processed
yet in the same step. Building a new `Counter` is how "all at once" is
enforced.

Trace on `NNCB`, step 1:

| pair | n | becomes |
| --- | ---: | --- |
| NN | 1 | NC + CN |
| NC | 1 | NB + BC |
| CB | 1 | CH + HB |

The result, `{NC, CN, NB, BC, CH, HB}`, one of each, is exactly the pairs of
`NCNBCHB`.

### `element_counts(pairs, last) -> Counter`

Count the **first letter** of every pair, then add 1 for `last`.

Why that works: in `NCNBCHB`, the pairs are `NC CN NB BC CH HB`. Their first
letters are `N C N B C H`, which is every letter of the polymer except the
final `B`. Each letter starts exactly one pair, except the last letter,
which starts none.

The last letter never changes. Insertions only go *between* two letters, so
nothing is ever added after the end. The template's last letter is the
polymer's last letter forever.

### `spread(polymer, steps) -> int`

Runs `step` `steps` times, converts to letter counts, and returns max − min.

### `part1(parsed)` / `part2(parsed)`

`spread(parsed, 10)` and `spread(parsed, 40)`. Real input: **2745** and
**3420801168962**.

After 40 steps on the real input, the most common letter is B
(4,399,405,361,139) and the least common is P (978,604,192,177).

## 4. Why it is correct

**The pair counts after a step depend only on the pair counts before it.**
Every pair of the new polymer comes from exactly one pair of the old one:
`AB` with rule `C` produces the two adjacent pairs `AC` and `CB`, and
nothing else. No new pair spans the boundary between two old pairs, because
neighbouring old pairs share their middle letter. In `NNCB`, the `N` in the
middle of `NN | NC` is the end of one pair's output (`CN`) and the start of
the next one's (`NB`). So summing each old pair's two outputs gives exactly
the new pair counts.

**The letter counts are recovered exactly.** This is the identity in
`element_counts`: first letter of each pair, plus the fixed last letter.

**Both claims are checked by tests against the literal string.** `grow` in
the tests builds the actual polymer string step by step with no pair
counting. It reproduces the statement's strings for steps 1–4, the lengths
97 and 3073, and the step-10 letter counts (B 1749, C 298, H 161, N 865).
Then:

- `test_pair_counts_match_literal_string`: after every one of 10 steps, on
  the example and on the real input, `step`'s counts equal the pairs read
  off the literal string.
- `test_element_counts_match_literal_string`: the same 10 steps; the
  first-letter-plus-last rule equals the literal string's letter counts.
- `test_length_doubles_less_one`: for every step up to 40, the total letter
  count equals (n − 1)·2ᵏ + 1, on both inputs.
- `test_example_counts_after_40_steps`: B = 2192039569602 and
  H = 3849876073, the statement's own part 2 numbers.

## 5. Complexity

A step costs one pass over the live pairs. There are at most L² of them for
L letters, 100 here, however long the polymer gets. The run is
O(steps · L²): constant per step, where the string would double.

Measured on the real input, the number of distinct pairs alive after each
step:

| step | 0 | 1 | 2 | 3 | 5 | 10 | 40 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| live pairs | 18 | 29 | 47 | 64 | 79 | 81 | 81 |
| polymer length | 20 | 39 | 77 | 153 | 609 | 19,457 | 20,890,720,927,745 |

It levels off at 81 live pairs; across all 40 steps, 85 of the 100 possible
pairs ever appear.

| phase | ms |
| --- | ---: |
| parse | 0.057 |
| part 1 | 0.186 |
| part 2 | 0.893 |
| total | 1.136 |

`bench.py -n 5 14`, best of 5 on the real input. Part 2 runs 4× the steps of
part 1 and takes 4.8× the time. That fits the table above: part 1's 10 steps
include the warm-up, where only 18–79 pairs are alive, while part 2's extra
30 steps all have 81.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
// Letters interned to 0..L at parse time; a pair is a * L + b.
struct Polymer {
    pairs: Vec<u64>,          // length L*L, count per pair index
    last: usize,
    rules: Vec<(usize, usize)>, // pair index -> its two output pair indices
}

fn step(pairs: &[u64], rules: &[(usize, usize)]) -> Vec<u64> {
    let mut next = vec![0u64; pairs.len()];
    for (p, &n) in pairs.iter().enumerate() {
        if n == 0 { continue; }
        let (l, r) = rules[p];
        next[l] += n;
        next[r] += n;
    }
    next
}
```

- **Arrays, not hash maps.** With letters numbered 0..10, a pair is an index
  0..100, and both the counts and the rules become flat arrays. A step is a
  100-entry loop with two indexed adds and no hashing.
- **`u64` is enough.** The real polymer after 40 steps is 45 bits long, so
  no count can exceed that. Python's integers never overflow, so the
  question never comes up there; in Rust it's worth a `checked_add` in
  debug builds, or a note.
- **Double-buffer.** Allocate two arrays once and swap them each step,
  instead of building a new `Vec` per step.

Embedded framing: the pair counts are a 100-entry state vector, and a step
is a fixed linear map applied to it. Each pair's count is routed to two
output slots, the same every step. That is a sparse 100 × 100 matrix whose
columns each sum to 2: usually two 1s, or a single 2 for a rule like
`AA -> A`, whose outputs are both `AA` (the real input has no such rule). It's the day 6 lanternfish idea again: don't
track individuals, track a histogram, and advance the histogram.

## 7. Possible optimization

**Matrix power.** Since a step is a fixed linear map M, 40 steps is M⁴⁰
applied to the starting vector. Repeated squaring gets M⁴⁰ in 6 matrix
products (40 = 32 + 8). That is the right tool when the step count is in
the millions. At 40, each dense 100 × 100 product is 10⁶ multiply-adds,
so 6 of them is far more work than 40 sparse passes over 81 pairs. This
was not measured; the step loop is under a millisecond.

**Memoised recursion per pair (implemented and measured; 17× slower).**
Another common solution recurses on `(pair, depth)`. `spread_memo` in the
source is that version, kept for comparison only; `part1` and `part2` don't
use it.

`inside(AB, d)` is the letters that d steps put *between* A and B. After
one step, AB is A C B, so:

```text
inside(AB, 0) = {}
inside(AB, d) = {C: 1} + inside(AC, d − 1) + inside(CB, d − 1)
```

The answer is the template's own letters plus `inside` of each template
pair. `test_memo_recursion_matches_histogram` checks that it agrees with
`spread` at every step count from 0 to 40, on both inputs.

Measured on the real input (best / median of 20 runs, cold cache every run,
same method as `bench.py`):

| steps | histogram ms | memo ms | memo ÷ histogram |
| ---: | ---: | ---: | ---: |
| 10 | 0.181 / 0.183 | 2.563 / 2.680 | 14× |
| 40 | 0.873 / 0.892 | 15.749 / 16.315 | 18× |

A second run gave 12× and 17×.

Both versions do about the same amount of work: 3147 distinct
`(pair, depth)` states in the memo at 40 steps (6150 calls, 3003 of them
cache hits), against roughly 40 × 81 ≈ 3,000 pair updates in the histogram.
The difference is the cost of each unit:

- The histogram's unit is two integer additions into one `Counter`.
- The memo's unit builds a new `Counter` from two child `Counter`s plus the
  inserted letter, merging up to 10 letter keys every time.

The recursion is the natural shape when the question is about one pair in
isolation ("what does `CH` grow into?"). For the total over the whole
polymer, the histogram shares that work for free: every `CH` in the polymer
is advanced by one addition, however many there are.
