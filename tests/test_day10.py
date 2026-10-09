"""Day 10: Syntax Scoring."""

import pytest

import day10
from day10 import Scan

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (323613, 3103006161)

EXAMPLE = """\
[({(<(())[]>[[{[]{<()<>>
[(()[<>])]({[<{<<[]>>(
{([(<{}[<>[]}>{[]{[(<()>
(((({<>}<{<{<>}{[]{[]{}
[[<[([]))<([[{}[[()]]]
[{[{({}]{}}([{[{{{}}([]
{<[[]]>}<{[{[{[]{()[[[]
[<(<(<(<{}))><([]([]()
<{([([[(<>()){}]>(<<{{
<{([{{}}[<[[[<>{}]]]>[]]
"""


def test_parse_example_shape():
    scans = day10.parse_input(EXAMPLE)
    assert len(scans) == 10
    assert [s.illegal for s in scans] == [None, None, "}", None, ")", "]", None, ")", ">", None]


@pytest.mark.parametrize(
    "line, expected, found",
    [
        ("{([(<{}[<>[]}>{[]{[(<()>", "]", "}"),
        ("[[<[([]))<([[{}[[()]]]", "]", ")"),
        ("[{[{({}]{}}([{[{{{}}([]", ")", "]"),
        ("[<(<(<(<{}))><([]([]()", ">", ")"),
        ("<{([([[(<>()){}]>(<<{{", "]", ">"),
    ],
)
def test_corrupted_example_lines(line, expected, found):
    """The statement's five 'Expected X, but found Y instead' lines."""
    assert line in EXAMPLE.splitlines()
    result = day10.scan(line)
    assert result.illegal == found
    assert day10.CLOSER[result.unclosed[-1]] == expected


def test_part1_example():
    """2 * 3 + 57 + 1197 + 25137."""
    assert day10.part1(day10.parse_input(EXAMPLE)) == 26397


@pytest.mark.parametrize(
    "line",
    ["()", "[]", "([])", "{()()()}", "<([{}])>", "[<>({}){}[([])<>]]", "(((((((((())))))))))"],
)
def test_legal_chunks_scan_clean(line):
    """The statement's valid chunks: nothing illegal, nothing left open."""
    assert day10.scan(line) == Scan(None, "")


@pytest.mark.parametrize(
    "line, illegal",
    [("(]", "]"), ("{()()()>", ">"), ("(((()))}", "}"), ("<([]){()}[{}])", ")")],
)
def test_corrupted_chunks(line, illegal):
    """The statement's corrupted chunks."""
    assert day10.scan(line).illegal == illegal


@pytest.mark.parametrize("closer, points", [(")", 3), ("]", 57), ("}", 1197), (">", 25137)])
def test_points_table(closer, points):
    opener = "(" if closer != ")" else "["
    assert day10.part1(day10.parse_input(opener + closer + "\n")) == points


def test_scan_stops_at_first_illegal_character():
    """Only the first wrong closer counts: the later > is never reached."""
    assert day10.scan("(]>") == Scan("]", "(")
    assert day10.part1(day10.parse_input("(]>\n")) == 57


def test_incomplete_line_keeps_its_open_chunks():
    """Outermost first; the closed <> in the middle leaves no trace."""
    assert day10.scan("([<>{") == Scan(None, "([{")


def test_adjacent_chunks_on_one_line():
    assert day10.scan("()[]{}<>") == Scan(None, "")
    assert day10.scan("()[]{}<)") == Scan(")", "<")


def test_incomplete_and_legal_lines_score_nothing():
    assert day10.part1(day10.parse_input("(((\n()\n<{\n")) == 0


def test_parse_skips_blank_lines():
    assert day10.parse_input("\n()\n\n(]\n\n") == [Scan(None, ""), Scan("]", "(")]


@pytest.mark.parametrize("bad", ["(a)\n", "( )\n", "(1]\n"])
def test_non_bracket_is_an_error(bad):
    with pytest.raises(ValueError):
        day10.parse_input(bad)


@pytest.mark.parametrize("bad", [")\n", "()]\n", "(())>(\n"])
def test_closer_with_nothing_open_is_an_error(bad):
    """The statement only defines 'wrong closer'; a closer with no open chunk
    has no 'expected' character, so it raises rather than being scored."""
    with pytest.raises(ValueError):
        day10.parse_input(bad)


@pytest.mark.parametrize(
    "line, closers, score",
    [
        ("[({(<(())[]>[[{[]{<()<>>", "}}]])})]", 288957),
        ("[(()[<>])]({[<{<<[]>>(", ")}>]})", 5566),
        ("(((({<>}<{<{<>}{[]{[]{}", "}}>}>))))", 1480781),
        ("{<[[]]>}<{[{[{[]{()[[[]", "]]}}]}]}>", 995444),
        ("<{([{{}}[<[[[<>{}]]]>[]]", "])}>", 294),
    ],
)
def test_completion_example_lines(line, closers, score):
    """The statement's five incomplete lines, their completions and scores."""
    assert line in EXAMPLE.splitlines()
    result = day10.scan(line)
    assert result.illegal is None
    assert day10.completion(result.unclosed) == closers
    assert day10.completion_score(closers) == score


def test_completion_score_is_base_5():
    """The statement's worked trace for ])}> : 0 -> 2 -> 11 -> 58 -> 294."""
    assert [day10.completion_score("])}>"[:n]) for n in range(5)] == [0, 2, 11, 58, 294]


@pytest.mark.parametrize("closer, points", [(")", 1), ("]", 2), ("}", 3), (">", 4)])
def test_completion_points_table(closer, points):
    assert day10.completion_score(closer) == points


def test_longer_completion_always_outscores_shorter():
    """No zero digit in the base-5 reading, so the weakest n+1 closers beat the strongest n."""
    for n in range(1, 16):
        assert day10.completion_score(")" * (n + 1)) > day10.completion_score(">" * n)


def test_part2_example():
    """Sorted: 294, 5566, 288957, 995444, 1480781; the middle one."""
    assert day10.part2(day10.parse_input(EXAMPLE)) == 288957


def test_part2_ignores_corrupted_and_complete_lines():
    """Only the incomplete line scores; the corrupted (] and the complete () do not."""
    assert day10.part2(day10.parse_input("(]\n()\n[\n")) == 2


def test_part2_even_count_is_an_error():
    with pytest.raises(ValueError):
        day10.part2(day10.parse_input("(\n[\n"))


def test_part2_no_incomplete_lines_is_an_error():
    with pytest.raises(ValueError):
        day10.part2(day10.parse_input("()\n"))


def test_real_input_has_odd_incomplete_count(real_input):
    """The median shortcut's premise, checked on the input actually solved."""
    scans = day10.parse_input(real_input(10))
    assert sum(s.illegal is None and bool(s.unclosed) for s in scans) % 2 == 1


def test_real_input_has_no_legal_lines(real_input):
    """'Syntax error on line: all of them' -- every line is corrupted or incomplete."""
    scans = day10.parse_input(real_input(10))
    assert all(s.illegal is not None or s.unclosed for s in scans)


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    crlf = EXAMPLE.replace("\n", "\r\n")
    assert day10.parse_input(crlf) == day10.parse_input(EXAMPLE)
    assert day10.part1(day10.parse_input(crlf)) == 26397
    assert day10.part2(day10.parse_input(crlf)) == 288957


def test_real_input_locked(check_locked):
    check_locked(day10, LOCKED)
