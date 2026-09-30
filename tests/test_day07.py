"""Day 7: The Treachery of Whales."""

import random

import pytest

import day07

LOCKED = (328318, 89791146)

EXAMPLE = "16,1,2,0,4,2,7,1,2,14\n"


def best_by_search(positions):
    """Cheapest alignment by trying every integer target in range."""
    return min(day07.linear_fuel(positions, t) for t in range(min(positions), max(positions) + 1))


def best_triangular_by_search(positions):
    return min(day07.triangular_fuel(positions, t) for t in range(min(positions), max(positions) + 1))


def test_parse():
    assert day07.parse_input(EXAMPLE) == [0, 1, 1, 2, 2, 2, 4, 7, 14, 16]


def test_parse_empty_is_an_error():
    with pytest.raises(ValueError):
        day07.parse_input("\n")


def test_parse_non_number_is_an_error():
    with pytest.raises(ValueError):
        day07.parse_input("1,x,3\n")


def test_part1_example():
    assert day07.part1(day07.parse_input(EXAMPLE)) == 37


@pytest.mark.parametrize("target, expected", [(2, 37), (1, 41), (3, 39), (10, 71)])
def test_statement_fuel_figures(target, expected):
    assert day07.linear_fuel(day07.parse_input(EXAMPLE), target) == expected


def test_statement_per_crab_moves():
    """The statement's move list for target 2, crab by crab."""
    moves = [abs(p - 2) for p in (16, 1, 2, 0, 4, 2, 7, 1, 2, 14)]
    assert moves == [14, 1, 0, 2, 2, 0, 5, 1, 0, 12]


@pytest.mark.parametrize(
    "positions",
    [[5], [3, 3, 3], [0, 10], [0, 1, 10], [0, 4, 6, 10], [1, 1, 1, 100], [0, 0, 0, 7, 7]],
)
def test_median_is_optimal_on_small_cases(positions):
    assert day07.part1(sorted(positions)) == best_by_search(positions)


def test_median_is_optimal_on_random_cases():
    """The standing claim: the median minimises the sum of |x - t|.  Checked
    against trying every target, for odd and even crab counts."""
    rng = random.Random(7)
    for n in range(1, 40):
        positions = sorted(rng.randrange(0, 60) for _ in range(n))
        assert day07.part1(positions) == best_by_search(positions)


def test_even_count_ties_between_the_two_middles():
    """With an even count every target between the middle pair costs the
    same, which is why picking either middle value is fine."""
    positions = [1, 2, 8, 20]
    costs = {t: day07.linear_fuel(positions, t) for t in range(2, 9)}
    assert len(set(costs.values())) == 1


def test_part2_example():
    assert day07.part2(day07.parse_input(EXAMPLE)) == 168


@pytest.mark.parametrize("target, expected", [(5, 168), (2, 206)])
def test_statement_triangular_figures(target, expected):
    assert day07.triangular_fuel(day07.parse_input(EXAMPLE), target) == expected


def test_statement_per_crab_triangular_moves():
    """The statement's move list for target 5, crab by crab."""
    positions = (16, 1, 2, 0, 4, 2, 7, 1, 2, 14)
    assert [day07.triangular_fuel([p], 5) for p in positions] == [66, 10, 6, 15, 1, 6, 3, 10, 6, 45]


@pytest.mark.parametrize("d", range(30))
def test_triangular_cost_is_the_running_sum(d):
    """d * (d + 1) // 2 is the statement's 1 + 2 + ... + d."""
    assert day07.triangular_fuel([0], d) == sum(range(1, d + 1))


@pytest.mark.parametrize(
    "positions",
    [[5], [3, 3, 3], [0, 10], [0, 1, 10], [0, 4, 6, 10], [1, 1, 1, 100], [0, 0, 0, 7, 7]],
)
def test_mean_neighbourhood_is_optimal_on_small_cases(positions):
    assert day07.part2(sorted(positions)) == best_triangular_by_search(positions)


def test_mean_neighbourhood_is_optimal_on_random_cases():
    """The standing claim: the optimum is floor(mean) or floor(mean) + 1.
    Checked against trying every target, including skewed distributions
    where the mean and the median are far apart."""
    rng = random.Random(21)
    for n in range(1, 60):
        positions = sorted(int(rng.expovariate(0.05)) for _ in range(n))
        assert day07.part2(positions) == best_triangular_by_search(positions)


def test_part2_optimum_differs_from_median_target():
    """Part 2 really is a different problem: the part 1 target is worse."""
    positions = day07.parse_input(EXAMPLE)
    assert day07.triangular_fuel(positions, 2) > day07.part2(positions)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day07.parse_input(crlf) == day07.parse_input(EXAMPLE)
    assert day07.solve(crlf) == (37, 168)


def test_real_input_locked(check_locked):
    check_locked(day07, LOCKED)
