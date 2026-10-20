# Day 12 Function Guide — Passage Pathing

Source: [`src/day12.py`](../../src/day12.py) ·
Tests: [`tests/test_day12.py`](../../tests/test_day12.py) ·
Statement: [`day12.md`](day12.md)

Answers (accepted): **5104** / **149220**.

## 1. The problem

The input is an undirected graph of caves, one edge per line (`A-b`).
Upper-case caves are big, lower-case caves are small. Count every distinct
path from `start` to `end` where:

- **Part 1:** each small cave is visited at most once; big caves any
  number of times.
- **Part 2:** one small cave per path may be visited twice; `start` and
  `end` are visited exactly once each.

Trace on the statement's first example:

```text
    start
    /   \
c--A-----b--d
    \   /
     end
```

Part 1 counts 10 paths: 7 that leave `start` through `A` and 3 through `b`.
`d` is on none of them. Reaching `d` means entering `b`, and the only way
back out of `d` is through `b` again, which is a second visit. In part 2
that second visit is allowed, so `start,b,d,b,end` becomes legal, and the
count rises to 36.

## 2. Representation

`parse_input` returns `Graph = dict[str, tuple[str, ...]]`, which maps each
cave to its neighbours in sorted order. Two kinds of edge are removed while
the map is built:

- **Edges into `start`.** The walk begins at `start`, so `start` is
  already on every path. Re-entering it would be a second visit to a small
  cave in part 1, and the statement forbids it outright in part 2.
- **Edges out of `end`.** A path finishes when it reaches `end`, so `end`'s
  neighbour tuple is empty.

Removing these edges in the parser saves the search from checking for
`start` and `end` on every step. It also means part 2 needs no special
case: `start` cannot be the cave visited twice when no edge leads back
into it. Section 4 covers how that is checked.

The parser also refuses an **edge between two big caves**. `A-B` would let a
walk go `A,B,A,B,...` without ever visiting a small cave, so the number of
paths would be infinite. `test_real_input_has_no_big_big_edge` checks that
the real input has no such edge.

Real input: 12 caves (9 small including `start` and `end`, 3 big: `QF`,
`US`, `XL`) and 23 edges.

## 3. Function walkthrough

### `parse_input(raw) -> Graph`

`splitlines()` plus a per-line `strip()`, so CRLF input leaves no `\r`.
Blank lines are skipped. Each line splits on the first `-`.

`ValueError` on any of:

- a missing `-`;
- a cave name that isn't a single-case ASCII word (`Ab`, or `end-x` left
  over from `start-end-x`);
- a self-loop;
- two big caves linked;
- no `start` or no `end`.

### `is_small(cave)`

`cave.islower()`. Valid names are all upper or all lower case, so this is
the whole small/big test.

### `count_paths(graph, spare) -> int`

The number of paths from `start` to `end`. It defines an inner function,
`paths_from(cave, visited, spare)`, wrapped in `functools.cache`, and calls
it once from `start`. The cache is created inside each `count_paths` call,
so it only ever holds results for one graph, and it is dropped when the
count is done.

`paths_from` returns the number of ways to finish from `cave`.

- `visited` is a `frozenset` of the small caves already on the path. Big
  caves never go into it.
- `spare` is True while the one allowed second visit is still unused.

All three arguments are hashable, so the triple works as the cache key.

For each neighbour:

- not in `visited`: recurse into it, adding it to `visited` if it is
  small;
- in `visited` and `spare` is set: recurse into it with `spare=False`.
  The cave is already in `visited`, so a third visit is refused;
- otherwise: skip it.

`end` returns 1. A cave with no usable neighbour returns 0: a dead end
contributes nothing.

Each call builds its own `visited | {nxt}`, so returning from a call
needs no undo step.

### `part1(parsed)` / `part2(parsed)`

Both call `count_paths(parsed, spare)`, with `spare=False` for part 1 and
`spare=True` for part 2.

Real input: **5104** and **149220**.

## 4. Why it is correct

**The count is the number of paths.** Without the cache, the search
follows each path step by step, and each step chooses a neighbour. Two
different paths differ at some first step, and from there they are counted
in different recursive calls. So each legal path is counted exactly once,
and only legal moves are ever made.

**The memo is sound.** Which moves are legal from here on depends only on
three things: the current cave, which small caves are already used, and
whether the spare visit is spent. It does not depend on the order the
small caves were used in, or on how often big caves were passed through.

Example from the real input: `start,lo,nu,XL` and `start,nu,lo,XL`. Both
stand on `XL` with `{start, lo, nu}` used and the spare unchanged, so they
have exactly the same completions. The cache counts those completions once
and reuses the result for the second path.

This is checked by a test, not just argued. `brute_paths` in the tests
enumerates every path with no caching at all, and its count matches the
memoised `part1` and `part2` on the real input (5104 and 149220).

**Part 1 terminates.** This is where the big-big ban matters. Between two
small-cave visits a walk can only sit on one big cave, because big caves
are never adjacent to each other. Every second step is therefore into a
small cave. Each small cave can be used once (twice in part 2, for one of
them), so the path length is bounded. The longest legal path on the real
input is 16 caves in part 1 and 18 in part 2.

**The trimmed edges are equivalent to the statement's rules.** This is
the one shortcut, so it is checked by a test. `brute_paths` in the test
module walks the **untrimmed** edge list and applies the statement's rules
literally:

- no small cave a third time;
- at most one small cave twice;
- never back into `start`;
- stop at `end`.

It reproduces the statement's full path lists (10 and 19 paths in part 1,
36 in part 2). Its path count matches `part1` and `part2` on all three
examples and on the real input, 149220 paths included.

`test_part2_start_is_not_the_double` pins the failure the trimming
prevents: with `start-A`, an untrimmed graph plus a spare visit would
count `start,A,start,A,end`.

**Only one cave doubles.** `spare` is a single flag, not one per cave.
`test_part2_only_one_cave_doubles` checks the count on a hand-countable
graph: `start-A, A-x, A-y, A-end`. Every path is a word over `{x, y}`
with `A` between letters:

- 5 words in part 1: `""`, `x`, `y`, `xy`, `yx`.
- 13 words in part 2: those 5, plus `xx` and `yy`, plus the 3
  arrangements each of `xxy` and `yyx`.
- `xxyy` is excluded because it doubles both caves.

## 5. Complexity

With the memo, the work grows with the number of distinct states
`(cave, visited, spare)`, not with the number of paths. Measured on the
real input (the plain search is the same recursion with no cache):

| | paths | distinct states | memoised calls | plain calls |
| --- | ---: | ---: | ---: | ---: |
| part 1 | 5104 | 605 | 1166 | 19137 |
| part 2 | 149220 | 1356 | 3544 | 545150 |

"Memoised calls" counts every call, cache hits included: in part 2 there
are 1356 misses (each state worked out once) and 2188 hits.

| phase | ms |
| --- | ---: |
| parse | 0.020 |
| part 1 | 0.401 |
| part 2 | 1.150 |
| total | 1.571 |

`bench.py -n 5 12`, best of 5 on the real input. Before the memo, the
plain search measured 4.119 ms for part 1 and 112.528 ms for part 2
(116.662 ms total). With the memo, part 2 is 98× faster, and it costs
2.9× part 1 instead of 27×. That tracks the state counts rather than the
path counts.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
struct Graph {
    adj: Vec<Vec<usize>>,   // cave index -> neighbour indices, start/end trimmed
    small: u16,             // bit i set when cave i is small
    start: usize,
    end: usize,
}

fn count(g: &Graph, cave: usize, visited: u16, spare: bool) -> u64 {
    if cave == g.end { return 1; }
    let mut total = 0;
    for &nxt in &g.adj[cave] {
        let bit = 1u16 << nxt;
        if visited & bit != 0 {
            if spare { total += count(g, nxt, visited, false); }
        } else {
            let v = if g.small & bit != 0 { visited | bit } else { visited };
            total += count(g, nxt, v, spare);
        }
    }
    total
}
```

- **Intern the names.** Parse each name once to an index, so the search
  never compares or hashes a string.
- **`visited` is a register.** The real input has 12 caves, so the
  visited set fits in a `u16` bitmask. Union is `|`, membership is `&`,
  and copying it into the next call is free. It replaces the frozenset
  that the Python allocates on every small-cave step.
- **Memo as a flat array.** The sketch above leaves the cache out. The
  state is `(cave, visited, spare)`, at most 12 × 2¹² × 2 = 98,304
  combinations, so a `Vec<Option<u64>>` indexed by
  `(cave << 13) | (visited << 1) | spare` would replace the Python's
  hash-keyed `functools.cache`.
- **Big-big edges.** Reject them in the parser, as the Python does.
  Otherwise the recursion overflows the stack instead of returning an
  error.

Embedded framing: `visited` is a status register with one bit per small
cave, and `spare` is a single sticky bit. A revisit is allowed only while
`spare` is set, and the first revisit clears it.

## 7. Possible optimization

**Plain recursion (the earlier version).** The same `paths_from` without
`@cache` is the most literal reading of the statement, and it was the
first version written. It costs 116.7 ms against 1.6 ms (section 5). It
does no worse on correctness, but memoising a path count is standard
practice for Advent of Code, so the cached version ships.

**Bitmask instead of frozenset.** Number the small caves at parse time and
carry `visited` as an int. That makes the cache key three small ints, and
the set union a single `|`. This was not measured. With only 1356 states
left after memoising, there is little left to gain.

**Diagram.** [`day12_graph.py`](day12_graph.py) renders the real map with
Graphviz (`dot` on PATH) to `day12_graph.jpg`, which is gitignored like the
day 9 heat map because it is a picture of the puzzle input. Big caves are
boxes. The map shows why the counts are finite: `QF`, `US` and `XL` never
touch each other, and `US` and `xb` are dead-end branches that a path can
only enter and leave through one neighbour.
