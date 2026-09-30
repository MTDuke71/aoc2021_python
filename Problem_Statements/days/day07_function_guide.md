# Day 07 Function Guide — The Treachery of Whales

Source: [`src/day07.py`](../../src/day07.py) ·
Tests: [`tests/test_day07.py`](../../tests/test_day07.py) ·
Statement: [`day07.md`](day07.md)

Answers (accepted): **328318** / **89791146**.

## 1. The problem

Each crab sits at a horizontal position. Pick one target for all of them and
pay fuel for the distance each crab travels. Part 1 charges 1 per step, so
distance d costs d. Part 2 charges 1 for the first step, 2 for the second,
and so on, so distance d costs 1 + 2 + ... + d.

Trace the example, `16,1,2,0,4,2,7,1,2,14`:

```text
part 1, target 2:  14 + 1 + 0 + 2 + 2 + 0 + 5 + 1 + 0 + 12           = 37
part 2, target 5:  66 + 10 + 6 + 15 + 1 + 6 + 3 + 10 + 6 + 45        = 168
part 2, target 2:  the part 1 winner now costs                         206
```

Same crabs, different price list, different best target. The design question
is whether the target has to be searched for. It does not: each price list
has a closed-form answer.

## 2. Representation

`parse_input` returns the positions as a sorted `list[int]`. That is the
full parse. Sorting lives here because part 1's median needs it and part 2
does not mind; it is paid once for both. Empty input raises `ValueError`
rather than letting `part1` index an empty list.

The real input is 1000 crabs, positions 0 to 1862, 646 distinct values.
Median 339, mean 467.55. The positions skew right, so the two parts land on
very different targets (339 and 467), and using the part 1 target for part 2
would cost 98,047,232 instead of 89,791,146.

## 3. Function walkthrough

### `parse_input(raw) -> list[int]`

Commas become spaces, then split on whitespace. That tolerates the trailing
newline and a CRLF `\r` alike (`test_crlf_input`). Junk raises from `int`.

### `linear_fuel(positions, target) -> int`

`sum(abs(p - target))`. Part 1's cost as a named function so the tests can
evaluate any target: the statement's 37 / 41 / 39 / 71 figures and the
brute-force comparison both use it.

### `triangular_fuel(positions, target) -> int`

Per crab, `d * (d + 1) // 2`, the closed form of 1 + 2 + ... + d. The
division is exact because d * (d + 1) is always even.
`test_triangular_cost_is_the_running_sum` checks it against the literal sum
for d = 0..29, and the statement's per-crab list (66, 10, 6, 15, ...) is
pinned in `test_statement_per_crab_triangular_moves`.

### `part1(positions)`

`linear_fuel(positions, positions[n // 2])`: the median.

### `part2(positions)`

```python
low = sum(positions) // len(positions)          # floor(mean)
return min(triangular_fuel(positions, low), triangular_fuel(positions, low + 1))
```

Real input: sum 467550, n 1000, floor(mean) 467. Costs are 89,791,146 at 467
and 89,791,190 at 468, so 467 wins by 44 fuel.

## 4. Why it is correct

Both shortcuts are claims, so both are pinned against a full search over
every target (`best_by_search`, `best_triangular_by_search`). On the real
input the same full search gives the same answers (measured while writing
this guide; best part 2 target 467).

**Part 1: the median.** Move the target one step right. Every crab at or left
of the old target pays 1 more; every crab strictly to its right pays 1 less.
The total falls while more crabs are to the right than at or left of the
target, and rises once that flips. The turn is at the median. With an even
count every target between the two middle values costs the same
(`test_even_count_ties_between_the_two_middles`), so either middle works and
`sorted[n // 2]` is one of them. It is the absolute-error counterpart of
"the mean minimises squared error".

**Part 2: the mean, give or take half.** The cost splits as

```text
f(t) = sum( d(d+1)/2 ),  d = |t - p|
     = sum( (t - p)^2 ) / 2  +  sum( |t - p| ) / 2
```

The first sum is a parabola bottoming at the mean, with slope n * (t - mean).
The second has slope somewhere in [-n/2, n/2]. The slopes can only cancel
where |t - mean| <= 1/2, so the integer optimum is floor(mean) or
floor(mean) + 1, which are the two candidates `part2` tries.
`test_mean_neighbourhood_is_optimal_on_random_cases` draws exponentially
distributed positions (mean and median well apart) for n = 1..59.

The trap is rounding the mean: `round(mean)` can pick the wrong neighbour, so
the code evaluates both and takes the minimum instead of choosing.

## 5. Complexity

Parse is O(n log n) for the sort. Each part is O(n): part 1 one pass, part 2
two passes.

| phase | ms |
| --- | ---: |
| parse | 0.138 |
| part 1 | 0.046 |
| part 2 | 0.198 |
| total | 0.382 |

`bench.py -n 5 7`, best of 5 on the real input. Part 2 is about 4x part 1:
two passes, and a multiply and shift per element instead of an `abs`.

Part 2's answer is 27 bits, so nothing is near an overflow.

## 6. If I were writing this in Rust

Compiled and run while writing this guide (rustc 1.93.1, `-O`). It gives
37 / 168 on the example and 328318 / 89791146 on the real input, the same as
the Python.

```rust
fn triangular(p: &[i64], t: i64) -> i64 {
    p.iter().map(|x| { let d = (x - t).abs(); d * (d + 1) / 2 }).sum()
}

// p: Vec<i64>, sorted with p.sort_unstable()
let low = p.iter().sum::<i64>().div_euclid(p.len() as i64);
let part2 = triangular(&p, low).min(triangular(&p, low + 1));
```

- **`div_euclid`, not `/`.** Rust's `/` truncates toward zero, Python's `//`
  floors. They agree here because the sum is non-negative, but `div_euclid`
  says what is meant and stays right if a position could be negative.
- **`i64`.** The real answer (about 9e7) would fit `i32`, but the cost grows
  with distance squared times n, so there is no reason to rely on that.
- **`select_nth_unstable` for the median.** It gives an O(n) median without
  a full sort. Python would need a hand-written quickselect, and the sort is
  already too cheap to bother.
- **Iterator chains** replace the generator expressions one for one, with no
  intermediate list in either language.

Embedded framing: part 1 is a balance point, the target where crabs to the
left and right weigh the same, like a scale. Part 2 is a spring (energy grows
with the square of the stretch), and a spring network's rest point is the
centre of mass: the mean. The half-step correction is the leftover linear term.

## 7. Possible optimization

The whole day takes 0.4 ms, so none is needed. One measured alternative:

**Brute force over every target.** Try each integer from min to max and keep
the cheapest. On the real input that is 92 ms for part 1 and 184 ms for
part 2 (best of 5), against 0.046 and 0.198 ms for the shortcuts: roughly
2000x and 900x slower. It is O(n x range), fine at 1000 crabs over a 1863-wide
range and painful as either grows. It is what the tests use as ground truth,
which is the role it is good for.

**Prefix sums** would make the cost at every target O(1) each, so a full scan
becomes O(n + range). It would only matter if a variation asked for the whole
cost curve. Not measured, not needed.
