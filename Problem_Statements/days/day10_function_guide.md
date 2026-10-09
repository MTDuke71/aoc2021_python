# Day 10 Function Guide — Syntax Scoring

Source: [`src/day10.py`](../../src/day10.py) ·
Tests: [`tests/test_day10.py`](../../tests/test_day10.py) ·
Statement: [`day10.md`](day10.md)

Answers (accepted): **323613** / **3103006161**.

## 1. The problem

Each input line is a run of nested chunks built from four bracket pairs:
`()`, `[]`, `{}`, `<>`. Every line is broken in one of two ways. A
*corrupted* line closes a chunk with the wrong kind of bracket; an
*incomplete* line just ends with chunks still open. Part 1 scores the
corrupted lines by their first wrong closer. Part 2 scores the incomplete
lines by the closers it would take to finish them, and takes the median.

Trace on one corrupted line from the statement:

```text
{([(<{}[<>[]}>{[]{[(<()>
         ^^^      stack before the }: { ( [ ( < [     (top is [)
            }     a } cannot close a [  ->  illegal character }, 1197 points
```

And one incomplete line:

```text
<{([{{}}[<[[[<>{}]]]>[]]
                          end of line, stack: < { ( [     (top is [)
                          completion: ] ) } >           (top of stack first)
                          score: 0 -> 2 -> 11 -> 58 -> 294
```

## 2. Representation

`parse_input` returns one `Scan(illegal, unclosed)` per non-blank line.
`illegal` is the first wrong closer or `None`; `unclosed` is the stack as a
string, outermost opener first, frozen wherever the scan stopped.

The scan lives in `parse_input` rather than in the parts because its result
is the same whichever part asks: part 1 reads `illegal`, part 2 reads
`unclosed`. That is CLAUDE.md's rule about derived structures, and it is
also why the bench shows part 1 at 0.004 ms: the work has already happened.

Two tables drive the scoring: `ILLEGAL_POINTS` for part 1 (3, 57, 1197,
25137) and `COMPLETION_POINTS` for part 2 (1, 2, 3, 4). `CLOSER` maps each
opener to its closer, and doubles as "is this an opener" via `in`.

Real input: 90 lines of 90–109 characters, 45 corrupted and 45 incomplete,
none legal. Deepest stack on any line is 15.

## 3. Function walkthrough

### `scan(line) -> Scan`

The classic bracket stack. An opener is pushed. A closer is compared with
the top of the stack: a match pops, a mismatch ends the scan with that
character as `illegal`. The stack at that moment is returned either way.

Two inputs the statement never defines raise `ValueError` instead of being
scored: a character that is not one of the eight brackets, and a closer
arriving on an empty stack (`)` on its own, or `()]`). The second one has
no "expected" character to be wrong against. Neither occurs in the real
input, so the checks are there to make a malformed file loud, not to
handle it.

### `parse_input(raw) -> list[Scan]`

`splitlines()` plus a per-line `strip()`, so CRLF input carries no `\r`
into `scan` (where it would raise as a non-bracket). Blank lines skip.

### `part1(scans)`

Sum `ILLEGAL_POINTS[s.illegal]` over scans whose `illegal` is set. Real
input: 8 `)`, 7 `]`, 18 `}`, 12 `>`, total **323613**.

### `completion(unclosed) -> str`

Reverse the stack and map each opener to its closer. Reversal is the whole
trick: the opener on top of the stack is the innermost unclosed chunk, so
it must be closed first.

### `completion_score(closers) -> int`

`score = score * 5 + points` per closer. Starting from 0, that is reading
the closers as the digits of a base-5 number with digit values 1–4 (no
zero digit, so no leading-zero ambiguity: a longer completion always
outscores a shorter one). The statement's trace `])}>` = 0, 2, 11, 58, 294
is pinned in `test_completion_score_is_base_5`.

### `part2(scans)`

Score every incomplete line (`illegal is None` and a non-empty stack), sort,
take the middle element. The statement promises an odd count; an even one
raises rather than silently picking one of two middles. Real input: 45
scores, index 22 after sorting, **3103006161**. The scores range from
11786 to 29606925973.

## 4. Why it is correct

**Part 1.** A line is corrupted exactly when some closer fails to match the
innermost open chunk, and the innermost open chunk is by construction the
top of the stack. Chunks are adjacent or nested, never overlapping, so
nothing a closer could legally match is anywhere but the top. Stopping at
the first mismatch is what the statement asks for.

**Part 2.** For an incomplete line, no closer ever mismatched, so the stack
holds exactly the chunks still open, innermost on top. Closing them in
stack order is the only sequence that forms nothing but legal pairs, which
makes the completion unique and `completion(unclosed)` the answer, not a
guess. The five example completions are pinned against the statement.

**Median.** The shortcut is "take `sorted(scores)[len // 2]`", which is a
real line's score only when the count is odd. The puzzle promises that;
`test_real_input_has_odd_incomplete_count` checks it on the input actually
solved (45), and `part2` raises otherwise.

## 5. Complexity

One pass over every character, with O(1) work per character; the stack
never exceeds the line length. Part 2 adds a sort of 45 integers. Total
input is about 9 KB.

| phase | ms |
| --- | ---: |
| parse | 0.403 |
| part 1 | 0.004 |
| part 2 | 0.067 |
| total | 0.473 |

`bench.py -n 5 10`, best of 5 on the real input. Parse carries the scan, so
the parts are lookups; part 2's 0.067 ms is building 45 completion strings
and sorting them.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
enum Scan { Corrupted(u8), Incomplete(Vec<u8>) }

fn scan(line: &[u8]) -> Scan {
    let mut stack = Vec::new();
    for &c in line {
        match c {
            b'(' | b'[' | b'{' | b'<' => stack.push(c),
            _ => match stack.pop() {
                Some(open) if closer(open) == c => {}
                _ => return Scan::Corrupted(c),
            },
        }
    }
    Scan::Incomplete(stack)
}
```

- **An enum instead of `(Option, str)`.** `Scan::Corrupted(ch)` versus
  `Scan::Incomplete(stack)` says the two outcomes are exclusive, which
  the Python `NamedTuple` only documents.
- **Bytes, not chars.** The input is ASCII, so `&[u8]` and `u8` literals
  avoid UTF-8 decoding entirely. `closer` is a four-arm `match`.
- **Score width.** The biggest real-input completion score is 29606925973,
  35 bits, so `u32` overflows; `u64` holds any completion up to 27
  closers (5^27 ≈ 7.5e18 < u64::MAX ≈ 1.8e19; 5^28 does not fit). The
  deepest stack here is 15. Python's int makes the question invisible.
- **Median.** `scores.sort_unstable(); scores[scores.len() / 2]`, or
  `select_nth_unstable` for O(n) if it mattered. It does not at n = 45.

Embedded framing: `scan` is a push-down automaton with a fixed alphabet,
and the stack could be a `u8` array of the maximum line length. The
completion score is a base-5 shift-and-add, the same shape as building a
number from decimal digits as they arrive on a UART.

## 7. Possible optimization

None of these were measured; they are ideas, not facts.

**Skip the completion string.** `completion_score` could walk `unclosed`
in reverse and look up `COMPLETION_POINTS[CLOSER[opener]]` directly, with
a combined opener-to-points table. Saves one small string per line.

**Score during the scan.** The part 2 score of an incomplete line is
determined by the final stack, so it could be accumulated in `scan`. That
would move part 2's 0.067 ms into parse, but it ties the parse to one
part's scoring rule, which the current split deliberately avoids.

**`statistics.median_low`.** Does the sort-and-index in one call, but hides
the odd-count assumption that `part2` now checks explicitly.
