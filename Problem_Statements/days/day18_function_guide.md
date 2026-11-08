# Day 18 Function Guide — Snailfish

Source: [`src/day18.py`](../../src/day18.py) ·
Tests: [`tests/test_day18.py`](../../tests/test_day18.py) ·
Statement: [`day18.md`](day18.md)

Answers (accepted): **4176** / **4633**.

## 1. The problem

A snailfish number is a binary tree with small integers at the leaves,
written as nested pairs: `[[1,2],[[3,4],5]]`. Adding two numbers makes them
the two halves of a new pair, `[a,b]`, then **reduces** the result. Each
round of reduction does the first of these that applies:

1. **Explode** the leftmost pair nested inside four pairs. Its left value
   goes into the nearest leaf to its left, its right value into the nearest
   leaf to its right (if those exist), and the pair becomes `0`.
2. **Split** the leftmost leaf `n ≥ 10` into `[⌊n/2⌋, ⌈n/2⌉]`.

When neither applies, the number is reduced. The **magnitude** of a pair is
`3·left + 2·right`, recursively, and that's what the answers are.

- **Part 1:** add the 100 input lines in order (a left fold) and take the
  magnitude of the result.
- **Part 2:** the largest magnitude of `a + b` over any two different lines.
  Addition isn't commutative, so both orders count.

## 2. The key observation: every operation is about neighbouring leaves

"The first regular number to the left of the exploding pair" can be a long
way away in the tree: up some levels, then down the far side of another
subtree. But in the **left-to-right sequence of leaves**, it's just the
previous leaf. Every operation in the puzzle is either a neighbour update or
a depth bump. So drop the tree and store each leaf with its **depth**
(how many pairs enclose it):

```
[[1,2],3]            ->  (1,2) (2,2) (3,1)
[7,[6,[5,[4,[3,2]]]]] ->  (7,1) (6,2) (5,3) (4,4) (3,5) (2,5)
```

Here's the statement's explode `[7,[6,[5,[4,[3,2]]]]] → [7,[6,[5,[7,0]]]]`
on that list:

| step | list |
| --- | --- |
| start | (7,1) (6,2) (5,3) (4,4) **(3,5) (2,5)** |
| left 3 into index 3 | (7,1) (6,2) (5,3) **(7,4)** (3,5) (2,5) |
| right 2: no leaf to the right, so it's dropped | — |
| the pair becomes (0, 4) | (7,1) (6,2) (5,3) (7,4) **(0,4)** |

The `index − 1` / `index + 2` neighbours are the whole "nearest regular
number" rule. Think of it as a shift register of leaves, with the tree
structure kept as a depth tag on each cell instead of in pointers.

| operation | on the flat list |
| --- | --- |
| add `a + b` | concatenate, depth + 1 on every leaf |
| explode | leaves `i`, `i+1` at depth 5 → add into `i−1` and `i+2`, replace both with `(0, 4)` |
| split | `(n, d)` → `(n//2, d+1)`, `(n − n//2, d+1)` |
| magnitude, render | `fold()`, a stack pass that rebuilds pairs bottom-up (§4) |

## 3. Representation

- `Leaf = (value, depth)`, `Number = list[Leaf]`.
- `parse_input(raw) -> list[Number]`: every line parsed, plus a check that
  each line is **already reduced** (depth ≤ 4, values ≤ 9). The real input
  has max depth exactly 4 and max value exactly 9 (pinned in
  `test_real_input_is_reduced`). That check is what keeps depth bounded at
  5, which `explode` relies on (§5).
- `parse_number` is a small recursive-descent parser, not a character scan.
  Flattening throws the bracket structure away, so the parser is the last
  place a malformed line like `[1,2,3]` can be caught.

## 4. Function walkthrough

### `parse_number(text) -> Number`

`element(depth)` reads either `[ element , element ]` at `depth + 1` or a
run of digits, and appends `(value, depth)` for each leaf it hits. `expect`
refuses anything else. A bare number, unbalanced brackets, a third element
and trailing text all raise `ValueError` (parametrized test).

### `fold(number, leaf, pair) -> T`

This is the one place the tree comes back. Leaves are pushed left to right;
whenever the top of the stack is at the same depth as the incoming item, the
two are siblings, so they combine with `pair` and move up a level, possibly
cascading. Trace for `[[9,1],[1,9]]`, with magnitude as `pair`:

| push | stack after (value, depth) |
| --- | --- |
| (9,2) | (9,2) |
| (1,2) | matches → `3·9+2·1 = 29` at depth 1: (29,1) |
| (1,2) | (29,1) (1,2) |
| (9,2) | matches → 21 at depth 1, matches again → `3·29+2·21 = 129` at depth 0: (129,0) |

A well-formed list ends as exactly one entry at depth 0; anything else
raises. Two uses:

- `magnitude(number) = fold(number, int, λa,b: 3a + 2b)`
- `render(number) = fold(number, str, λa,b: f"[{a},{b}]")`

Because `render` and `magnitude` share `fold`, the render round-trip tests
(all statement numbers, plus 500 random trees up to depth 7) also check the
pairing logic magnitude uses.

### `explode(number) -> bool`

Finds the first leaf at depth 5. It checks that the next leaf is also depth 5
(its sibling) and raises if not, or if anything is deeper than 5. Then it
adds into the neighbours and splices the pair down to `(0, 4)`. It returns
whether it did anything.

### `split(number) -> bool`

Finds the first leaf ≥ 10 and splices in the two halves one level deeper.

### `add(a, b) -> Number`

Concatenates with depth + 1, then `while explode(total) or split(total)`.
The `or` short-circuit is the priority rule: `split` only runs on a round
where `explode` found nothing. It builds a new list, so the inputs aren't
mutated. That matters for part 2, which reuses every line 198 times
(pinned).

### `total(numbers)`, `part1`, `part2`

`total` is the in-order left fold; `part1` is its magnitude. `part2` tries
`max(magnitude(add(a, b)))` over `itertools.permutations(numbers, 2)`, which
gives every ordered pair of **different positions**: 100 · 99 = 9,900
additions.

## 5. Why it is correct

**Depth never exceeds 5.** Inputs are reduced (≤ 4, enforced at parse).
Adding pushes everything down one level, so ≤ 5. A split only happens on a
round with no depth-5 leaf, so it creates leaves at depth ≤ 5 too. Explode
only removes depth. So any depth-5 leaf is half of a pair whose other half
can't be a pair (that would be depth 6), and the first depth-5 leaf and the
one after it are exactly the leftmost exploding pair. `explode` raises
instead of guessing if this ever fails.

**The fold re-pairs correctly.** Every entry on the stack is a finished left
child waiting for its right sibling, one per ancestor of the current
position. So their depths strictly increase toward the top. The next
finished subtree at the top's depth can only be that sibling.

**Pinned against an independent tree implementation.** The test file has a
reference that does what the statement says on nested Python lists:
recursive explode with left/right carries, recursive split. It shares no
code with the flat list. The two agree on:

- 1,000 random sums of reduced numbers;
- every one of the 99 running sums of the real input, plus the part 1
  magnitude;
- the part 2 maximum over all 9,900 real-input ordered pairs.

**And against the statement.** Each explode and split example; the
five-action reduction trace, step by step; every one of the nine partial
sums in the larger example; all nine magnitude examples; 4140 for part 1;
and 3993 for part 2, including the winning pair (line 9 + line 1) and its
reduced text.

**Pinned edge behaviour:**

- One order per pair (i < j) gives less than 3993 on the example, so both
  orders are needed.
- Part 2 never pairs a line with itself: with input `[9,9]`, `[0,0]`, `a + a`
  scores higher than either cross sum, and isn't chosen.

## 6. Complexity

Each reduction action is a linear scan plus a list splice, both O(L) in the
number of leaves. L is small: input lines have 2–16 leaves and a reduced
sum can't have more than 16 (a full depth-4 tree; the real part 1 total has
exactly 16). Measured action counts (instrumented run on the real input):

| | additions | explodes | splits | per addition |
| --- | ---: | ---: | ---: | --- |
| part 1 | 99 | 9,177 | 8,349 | ~93 explodes, ~84 splits |
| part 2 | 9,900 | 134,973 | 99,486 | ~14 explodes, ~10 splits |

Part 1's additions are about 7× busier than part 2's, because the
accumulator is a big saturated number and folding in each new line sets off
a long explode/split cascade. Part 2 does 100× more additions of
fresh two-line sums, and that's where the time goes.

| phase  |      ms |
| ------ | ------: |
| parse  |   0.540 |
| part 1 |  12.613 |
| part 2 | 212.492 |
| total  | 225.644 |

`bench.py 18`, best of 5 on the real input.

For comparison, the test suite's nested-list tree reference takes
**705.1 ms** best of 5 for part 2 against **211.6 ms** for the shipped flat
list (measured in the same run), about 3.3× slower. Recursion and rebuilding
lists on every explode cost more than a flat scan over a list that averages
about 15 tuples (31 at most) during reduction.

## 7. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
#[derive(Clone, Copy, PartialEq)]
struct Leaf { value: u8, depth: u8 }

fn add(a: &[Leaf], b: &[Leaf]) -> Vec<Leaf> {
    let mut n: Vec<Leaf> = a.iter().chain(b)
        .map(|l| Leaf { depth: l.depth + 1, ..*l }).collect();
    while explode(&mut n) || split(&mut n) {}
    n
}

fn explode(n: &mut Vec<Leaf>) -> bool {
    let Some(i) = n.iter().position(|l| l.depth == 5) else { return false };
    let (l, r) = (n[i].value, n[i + 1].value);
    if i > 0 { n[i - 1].value += l; }
    if i + 2 < n.len() { n[i + 2].value += r; }
    n.splice(i..i + 2, [Leaf { value: 0, depth: 4 }]);
    true
}

fn magnitude(n: &[Leaf]) -> u32 {
    let mut stack: Vec<(u32, u8)> = Vec::with_capacity(5);
    for l in n {
        let (mut v, mut d) = (l.value as u32, l.depth);
        while let Some(&(lv, ld)) = stack.last() {
            if ld != d { break; }
            stack.pop();
            v = 3 * lv + 2 * v;
            d -= 1;
        }
        stack.push((v, d));
    }
    stack[0].0
}
```

- **Two bytes per leaf.** Depth ≤ 5 is proven (§5). The value bound is only
  measured: the largest leaf seen anywhere during reduction on the real
  input is 55 (part 1; 39 in part 2). Several explodes can pile into one
  leaf before a split gets a turn. `u8` has ample headroom for that, but it's
  an empirical bound, so use `u16` if that feels too thin. Either way it's `u8`
  for depth. That's a 2-byte struct, and a whole number
  fits in a cache line or two. It's the embedded-friendly shape: a packed
  array plus a depth tag instead of a `Box`-linked tree, which in Rust would
  also mean fighting the borrow checker for parent/sibling access.
- **The stack never gets deeper than 5.** One entry per pending ancestor,
  so `magnitude` could use a fixed `[(u32, u8); 5]` with no allocation.
- **Part 2 is embarrassingly parallel.** With `rayon`, a `par_iter` over
  the 9,900 ordered pairs plus `max()` is a one-line change, because `add`
  takes slices and owns its output.

## 8. Possible optimization

**Explode the whole addition in one pass. Measured, not worth it.** Right
after an addition, every depth-5 pair comes from the operands' depth-4
pairs. Exploding the leftmost one never creates another, so one left-to-right
pass could do them all instead of rescanning from index 0 each time. The
catch, found while prototyping: when two exploding pairs are adjacent, the
first one's right value has to be carried into the second one's left value
**before** that one explodes, or the result is wrong. With the carry, the
prototype matched `add` on all 9,900 real-input pairs, and part 2 took
**214.4 ms** against 211.6 ms. No gain: about 14 explodes per addition over
a list that averages about 15 leaves (31 at most, measured) leaves nothing
to save. The splice and the Python
loop overhead dominate, not the rescans.

**Where time actually goes.** If part 2 ever needed to be faster, the
leverage is in the constant factor (Rust, or packed values with numpy-style
vectorisation), or in parallelising over pairs. Not in the algorithm: every
pair has to be reduced, and each reduction is already linear in a list of about
15 leaves.
