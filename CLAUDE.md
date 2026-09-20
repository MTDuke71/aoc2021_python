# CLAUDE.md -- Advent of Code 2021, in Python

This is **Matt LaDuke's** AoC 2021 repo. Read this file before helping on a
first request in a new session.

## History

AoC 2021 began in `C:\Users\m_lad\Repos\aoc2021_OCaml` as the OCaml leg of a
language-rotation experiment. **That rotation is over** (decided 2026-09-19;
the same call was made earlier for `aoc2020_Prolog`). Learning a new language
per year was getting in the way, and Advent of Code itself is the point.

Do not propose reviving the rotation, and do not propose porting solutions to
OCaml or back-filling the OCaml repo. It got as far as day 00 and is left as
it is.

The conventions below are the ones that settled in `aoc2020_Prolog`'s Python
era. The only deliberate differences: solutions live in `src/` rather than
`python/` (no legacy tree to fence off), `LOCKED` may be half-filled, and
`main()` prints one part per line.

## Language

**Python only.** Solutions live in `src/dayNN.py`.

Every day exposes the same five names:

- `parse_input(raw) -> structure` -- the **full** parse. Not a line split
  with the real work deferred into `part1`. If both parts need a derived
  structure that does not depend on which part is asking, it is built here.
  The stub's `list[str]` return type is a placeholder; change it.
- `part1(parsed) -> int`
- `part2(parsed) -> int`
- `solve(raw) -> (part1, part2)`
- `main() -> None` -- reads `INPUT`, prints `part1=...` then `part2=...`

`INPUT` is resolved from `__file__`, not the working directory, so
`python src/day07.py` works from anywhere.

An unsolved part raises `NotImplementedError`. `tests/conftest.py` and
`bench.py` both key on that, so leave the stub raising until the part is
really written.

## Environment

Windows, **not WSL**. Virtualenv executables are in `Scripts\`, not `bin/`.

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install pytest ruff
.venv\Scripts\python.exe -m pytest
.venv\Scripts\ruff.exe format .
.venv\Scripts\ruff.exe check .
.venv\Scripts\python.exe bench.py
```

Inputs downloaded on Windows can carry CRLF, so parsing must tolerate a
trailing `\r`. A per-line `.strip()` or `.splitlines()` handles it --
`block.split("\n")` does not, and that caused a real bug in the 2020 repo
(day06, where the surviving `\r` counted as a 27th customs answer). Every
solved day has a CRLF test case.

## Testing

Tests are **pytest**, one module per day at `tests/test_dayNN.py`.

- Statement worked examples via `@pytest.mark.parametrize`, plus the edge
  cases the statement implies.
- A CRLF case.
- `LOCKED` and the `check_locked` fixture for real-input answers.

`LOCKED = (part1, part2)` asserts. A `None` slot -- or `LOCKED = None` --
reports what the code currently produces and skips; `(1234, None)` is the
normal state between the two stars. Never close that gap by pasting in
whatever the code printed -- the whole point is that an unverified answer
cannot masquerade as a verified one. A slot is filled when adventofcode.com
has accepted that answer, and Matt is the one who submits.

The `real_input` fixture **skips** when a gitignored input is missing, so a
fresh clone stays green.

`tests/test_day00.py` is the worked model for a finished test module.

## Two standing rules

1. **If a solution leans on a non-obvious identity or shortcut, pin it as a
   test, not a claim in prose.** A claim no test checks is a claim that can
   rot.
2. **Anything stated as fact gets run and verified.** A timing, a language
   behaviour, an arithmetic result -- measure it or execute it. Do not
   recall it from memory and write it down as though it were checked.

## Per-day deliverable

1. `src/dayNN.py` with the five names above.
2. `tests/test_dayNN.py`.
3. `Problem_Statements/days/dayNN_function_guide.md`.
4. Row in `Problem_Statements/days/summary_2021.md`.
5. Bench timings when interesting.

Part 2 of a statement only exists once part 1 is accepted; the README has the
two commands that refresh `dayNN.md`.

## Function guides are the durable artifact

Write them for a reader who is cold after 12+ months.
`day00_function_guide.md` shows the section order at its smallest; the
day 14+ guides in `aoc2020_Prolog` show it at full size.

Each guide should include:

- Problem framing and representation choices.
- Function-by-function walkthrough.
- Why the algorithm is correct.
- Complexity discussion.
- An "if I were writing this in Rust" bridge section. Rust is the anchor
  language for comparisons and the corpus Matt returns to
  (`C:\Users\m_lad\Repos\rust_study`).
- Optional "possible optimization" sidebar, without forcing a rewrite.

## About the user

- 20+ year engineer, Software Program Manager; senior-level depth.
- EE by training, embedded C daily, Python for scripting.
- Bit/register/machine framings land well.
- Rust is the anchor for comparisons.
- **Matt reads code; the assistant writes it.** Pitch explanations at
  lead/PM altitude -- what and why and tradeoffs over syntax drills.
- Lead with a concrete numeric trace before stating an invariant
  abstractly.

`src/dayNN_mtl.py` files are Matt's own independent attempts. Do not let
them anchor a solution, and do not treat them as day modules.

## Optimization policy

Shipping source is readable Python first. Document faster alternatives in
the function guide as sidebars rather than replacing clear code with clever
opaque code.

## What not to do

- Do not suggest reviving the language rotation.
- Do not skip guides to increase day throughput.
- Do not assert an unverified answer as though it were confirmed.
