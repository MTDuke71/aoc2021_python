"""Day 6: Lanternfish."""

import pytest

import day06

LOCKED = (373378, 1682576647495)

EXAMPLE = "3,4,3,1,2\n"

# The statement's day-by-day listings, as fish lists (order is not tracked
# by the histogram, so they are compared as sorted timers).
STATEMENT_DAYS = {
    0: "3,4,3,1,2",
    1: "2,3,2,0,1",
    2: "1,2,1,6,0,8",
    3: "0,1,0,5,6,7,8",
    4: "6,0,6,4,5,6,7,8,8",
    5: "5,6,5,3,4,5,6,7,7,8",
    9: "1,2,1,6,0,1,2,3,3,4,8",
    10: "0,1,0,5,6,0,1,2,2,3,7,8",
    11: "6,0,6,4,5,6,0,1,1,2,6,7,8,8,8",
    18: "6,0,6,4,5,6,0,1,1,2,6,0,1,1,1,2,2,3,3,4,6,7,8,8,8,8",
}


def expand(counts):
    return sorted(t for t, n in enumerate(counts) for _ in range(n))


def naive_fish(timers, days):
    """One list entry per fish, exactly as the statement describes it."""
    fish = list(timers)
    for _ in range(days):
        born = fish.count(0)
        fish = [6 if t == 0 else t - 1 for t in fish] + [8] * born
    return fish


def test_parse():
    assert day06.parse_input(EXAMPLE) == [0, 1, 1, 2, 1, 0, 0, 0, 0]


def test_parse_counts_repeats_and_covers_every_slot():
    assert day06.parse_input("0,0,8,8,8,5\n") == [2, 0, 0, 0, 0, 1, 0, 0, 3]


@pytest.mark.parametrize("day, listing", STATEMENT_DAYS.items())
def test_statement_listing(day, listing):
    counts = day06.parse_input(EXAMPLE)
    for _ in range(day):
        counts = day06.step(counts)
    assert expand(counts) == sorted(map(int, listing.split(",")))


@pytest.mark.parametrize("days, expected", [(0, 5), (18, 26), (80, 5934), (256, 26984457539)])
def test_example_population(days, expected):
    assert day06.population(day06.parse_input(EXAMPLE), days) == expected


def test_part1_example():
    assert day06.part1(day06.parse_input(EXAMPLE)) == 5934


def test_part2_example():
    assert day06.part2(day06.parse_input(EXAMPLE)) == 26984457539


def test_histogram_matches_one_entry_per_fish():
    """The rotate-and-add-to-6 step is a claim about the statement's rules;
    check it against the literal fish-list simulation on every timer."""
    timers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 3, 3, 0]
    counts = day06.parse_input(",".join(map(str, timers)))
    for days in range(40):
        assert expand(counts) == sorted(naive_fish(timers, days))
        counts = day06.step(counts)


def test_step_conserves_nothing_but_spawns():
    """Population grows by exactly the number of fish at timer 0."""
    counts = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    assert sum(day06.step(counts)) == sum(counts) + counts[0]


def test_lone_fish_timeline():
    """A single 3: it spawns on day 4, and the newborn's first spawn is 9
    days later (8 -> 0 is 8 days, then the reset day), as in the statement."""
    assert day06.population([0, 0, 0, 1, 0, 0, 0, 0, 0], 3) == 1
    assert day06.population([0, 0, 0, 1, 0, 0, 0, 0, 0], 4) == 2


def transition_matrix():
    """One day as a 9x9 matrix acting on the column vector of counts:
    new[t] = old[t + 1] for t < 8, new[6] also gains old[0], new[8] = old[0]."""
    m = [[0] * 9 for _ in range(9)]
    for t in range(8):
        m[t][t + 1] = 1
    m[6][0] += 1
    m[8][0] = 1
    return m


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(9)) for j in range(9)] for i in range(9)]


def matrix_power(m, n):
    """m**n by repeated squaring: O(log n) multiplies."""
    result = [[int(i == j) for j in range(9)] for i in range(9)]
    while n:
        if n & 1:
            result = matmul(result, m)
        m = matmul(m, m)
        n >>= 1
    return result


def population_by_matrix(counts, days):
    p = matrix_power(transition_matrix(), days)
    return sum(p[i][j] * counts[j] for i in range(9) for j in range(9))


def test_matrix_step_is_the_same_step():
    """The matrix is a second statement of the rule: one multiply by it must
    equal `step` on every unit histogram and on a mixed one."""
    m = transition_matrix()
    for counts in [*([int(i == j) for j in range(9)] for i in range(9)), [3, 1, 4, 1, 5, 9, 2, 6, 5]]:
        assert [sum(m[i][j] * counts[j] for j in range(9)) for i in range(9)] == day06.step(counts)


@pytest.mark.parametrize("days", [0, 1, 2, 7, 18, 80, 256, 1000])
def test_matrix_power_matches_the_loop(days):
    """Raising the day matrix to the n-th power by squaring gives the same
    population as n applications of `step`, on the example and a mixed start."""
    for counts in (day06.parse_input(EXAMPLE), [3, 1, 4, 1, 5, 9, 2, 6, 5]):
        assert population_by_matrix(counts, days) == day06.population(counts, days)


def test_matrix_power_reaches_the_part_two_example():
    assert population_by_matrix(day06.parse_input(EXAMPLE), 256) == 26984457539


def test_negative_days_is_an_error():
    with pytest.raises(ValueError, match="non-negative"):
        day06.population([0] * 9, -1)


@pytest.mark.parametrize("raw", ["9\n", "-1,2\n", "3,x\n"])
def test_malformed_input_is_an_error(raw):
    with pytest.raises(ValueError):
        day06.parse_input(raw)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day06.parse_input(crlf) == day06.parse_input(EXAMPLE)
    assert day06.solve(crlf) == (5934, 26984457539)


def test_real_input_locked(check_locked):
    check_locked(day06, LOCKED)
