"""Shared fixtures for the day test modules.

Two problems this file exists to solve:

1. Puzzle inputs are gitignored (AoC asks that they not be redistributed), so
   a fresh clone has no inputs/ at all.  Tests that need one must *skip*, not
   fail -- otherwise the suite is red for everybody who did not personally
   download 25 files.  That is `real_input`.

2. An answer nobody has submitted is not an answer.  If a test asserted
   whatever the code happened to print, it would pass by construction and
   prove nothing.  That is `check_locked`: it asserts only against a value a
   human has confirmed, and otherwise reports.  See LOCKED below.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "inputs"


@pytest.fixture(scope="session")
def real_input():
    """Return `load(day) -> str`, skipping the test when the input is absent.

    Reads with newline="" left at the default, i.e. universal newlines: a
    CRLF file arrives as \n-separated text.  Solutions must still tolerate a
    stray \r on their own (see the crlf test in every day module) because
    input can also reach parse_input from a string literal or a byte read that
    did no translation.
    """

    def load(day: int) -> str:
        path = INPUT_DIR / f"day{day:02d}.txt"
        if not path.exists():
            pytest.skip(f"no {path.relative_to(REPO_ROOT)} (inputs are gitignored)")
        return path.read_text()

    return load


@pytest.fixture
def check_locked(real_input):
    """Return `check(module, LOCKED)` -- assert confirmed answers, report the rest.

    LOCKED is a (part1, part2) tuple of answers accepted by adventofcode.com.
    Either slot may be None, and LOCKED itself may be None, meaning "not
    accepted yet".  AoC hands out part 2 only after part 1 is accepted, so
    `LOCKED = (1234, None)` is a normal state for a day to be in.

    - A slot holding a value: assert.  A refactor that changes the answer fails.
    - A slot holding None:    report what the code currently produces (or that
                              the part still raises NotImplementedError), then
                              skip.

    The asymmetry is the point.  There is no third path where an unverified
    number gets asserted against itself, so a green suite never implies more
    confidence than somebody actually has.  Turning a day green means pasting
    a real answer into LOCKED by hand.
    """

    def attempt(part, parsed):
        try:
            return part(parsed)
        except NotImplementedError:
            return NotImplemented

    def check(module, locked):
        name = module.__name__
        raw = real_input(int(name.removeprefix("day")))
        locked = (None, None) if locked is None else tuple(locked)

        parsed = module.parse_input(raw)
        got = (attempt(module.part1, parsed), attempt(module.part2, parsed))

        # Confirmed slots are asserted first, so a regression in an accepted
        # part 1 fails even while part 2 is unfinished.
        for label, want, have in zip(("part1", "part2"), locked, got, strict=True):
            if want is not None:
                assert have == want, f"{name} {label}: expected {want}, got {have}"

        if None not in locked:
            # solve() is the public entry point; make sure it agrees.
            assert module.solve(raw) == locked
            return

        report = []
        for label, want, have in zip(("part1", "part2"), locked, got, strict=True):
            if want is not None:
                report.append(f"{label}={have} (locked)")
            elif have is NotImplemented:
                report.append(f"{label} not implemented")
            else:
                report.append(f"{label}={have} (unconfirmed -- submit it, then set LOCKED)")
        pytest.skip(f"{name}: " + ", ".join(report))

    return check
