"""Day 16: Packet Decoder."""

import random

import pytest

import day16
from day16 import Packet

# (part1, part2) once adventofcode.com has accepted both; None until then.
LOCKED = (1012, 2223947372407)


def lit(version, value):
    return Packet(version, 4, value, ())


def op(version, type_id, *children):
    return Packet(version, type_id, None, tuple(children))


def encode(packet, rng=None):
    """Independent writer for the BITS format; returns a bit string.

    With rng, each operator picks its length type at random; without, every
    operator uses length type 0.
    """
    head = f"{packet.version:03b}{packet.type_id:03b}"
    if packet.type_id == 4:
        nibbles = f"{packet.value:x}"
        groups = [f"{int(n, 16):04b}" for n in nibbles]
        return head + "".join(("1" if i < len(groups) - 1 else "0") + g for i, g in enumerate(groups))
    body = "".join(encode(child, rng) for child in packet.children)
    if rng is not None and rng.random() < 0.5:
        return head + "1" + f"{len(packet.children):011b}" + body
    return head + "0" + f"{len(body):015b}" + body


def to_hex(bits):
    bits += "0" * (-len(bits) % 4)
    return "".join(f"{int(bits[i : i + 4], 2):X}" for i in range(0, len(bits), 4))


def random_tree(rng, depth=0):
    version = rng.randrange(8)
    if depth >= 4 or rng.random() < 0.4:
        return lit(version, rng.choice([0, 1, 15, 16, 2021, rng.randrange(2**40)]))
    type_id = rng.choice([0, 1, 2, 3, 5, 6, 7])
    return op(version, type_id, *(random_tree(rng, depth + 1) for _ in range(rng.randint(1, 4))))


def test_literal_d2fe28():
    """The statement's literal: version 6, groups 0111 1110 0101 -> 2021, three padding zeros."""
    assert day16.hex_to_bits("D2FE28") == "110100101111111000101000"
    packet, end = day16.read_packet(day16.hex_to_bits("D2FE28"))
    assert packet == lit(6, 2021)
    assert end == 21


def test_operator_length_type_0():
    """38006F45291200: 15-bit length 27 holding literals 10 (11 bits) and 20 (16 bits)."""
    assert day16.parse_input("38006F45291200") == op(1, 6, lit(6, 10), lit(2, 20))


def test_operator_length_type_1():
    """EE00D40C823060: 11-bit count 3 holding literals 1, 2, 3."""
    assert day16.parse_input("EE00D40C823060") == op(7, 3, lit(2, 1), lit(4, 2), lit(1, 3))


@pytest.mark.parametrize(
    ("hex_text", "want"),
    [
        ("D2FE28", 6),
        ("8A004A801A8002F478", 16),
        ("620080001611562C8802118E34", 12),
        ("C0015000016115A2E0802F182340", 23),
        ("A0016C880162017C3686B18A3D4780", 31),
    ],
)
def test_part1_examples(hex_text, want):
    assert day16.part1(day16.parse_input(hex_text)) == want


def test_nested_example_shape():
    """8A004A801A8002F478 is a chain: operator v4 > operator v1 > operator v5 > literal v6."""
    p = day16.parse_input("8A004A801A8002F478")
    versions = []
    while True:
        versions.append(p.version)
        if p.type_id == 4:
            break
        (p,) = p.children
    assert versions == [4, 1, 5, 6]


def test_same_tree_either_length_type():
    """620080001611562C8802118E34 and C0015000016115A2E0802F182340 differ only in framing (and versions)."""
    a = day16.parse_input("620080001611562C8802118E34")
    b = day16.parse_input("C0015000016115A2E0802F182340")

    def shape(p):
        return p.value if p.type_id == 4 else tuple(shape(c) for c in p.children)

    assert shape(a) == shape(b) == ((10, 11), (12, 13))


@pytest.mark.parametrize(
    ("hex_text", "bits"),
    [
        ("0", "0000"),
        ("00F", "000000001111"),
        ("2", "0010"),
        ("f", "1111"),
    ],
)
def test_hex_to_bits_keeps_leading_zeros(hex_text, bits):
    """bin(int(h, 16)) drops leading zeros; the real input starts with 2 = 0010, so they matter."""
    assert day16.hex_to_bits(hex_text) == bits


def test_literal_zero_is_one_group():
    # version 0, type 4, group 00000 -> "000100" + "00000"
    assert day16.read_packet("00010000000")[0] == lit(0, 0)


def test_lowercase_hex():
    assert day16.parse_input("d2fe28") == day16.parse_input("D2FE28")


@pytest.mark.parametrize("seed", range(50))
def test_round_trip_random_trees(seed):
    """decode(encode(tree)) == tree, with the length type chosen at random per operator."""
    rng = random.Random(seed)
    tree = random_tree(rng)
    assert day16.parse_input(to_hex(encode(tree, rng))) == tree


def test_round_trip_real_input(real_input):
    """Re-encode the real tree both ways (all type 0, mixed types) and decode it back unchanged."""
    tree = day16.parse_input(real_input(16))
    assert day16.parse_input(to_hex(encode(tree))) == tree
    assert day16.parse_input(to_hex(encode(tree, random.Random(16)))) == tree


@pytest.mark.parametrize(
    "bad",
    [
        "",
        "\n",
        "D2FE2G",  # not hex
        "D2 FE28",
        "D2FE28\nD2FE28\n",  # two lines
        "D2FE",  # literal cut off mid-group
        "D2FE29",  # a 1 in the padding after the packet
        "38006F4529",  # length-type-0 operator cut off
        # length type 0 declares 10 bits, but its first child is an 11-bit literal
        to_hex("001110" + "0" + f"{10:015b}" + "11010001010"),
        to_hex("000000" + "0" + f"{0:015b}"),  # operator with 0 bits of sub-packets
        to_hex("000000" + "1" + f"{0:011b}"),  # operator with 0 sub-packets
    ],
)
def test_malformed_input_is_an_error(bad):
    with pytest.raises(ValueError):
        day16.parse_input(bad)


@pytest.mark.parametrize(
    ("hex_text", "want"),
    [
        ("C200B40A82", 3),
        ("04005AC33890", 54),
        ("880086C3E88112", 7),
        ("CE00C43D881120", 9),
        ("D8005AC2A8F0", 1),
        ("F600BC2D8F", 0),
        ("9C005AC2F8F0", 0),
        ("9C0141080250320F1802104A08", 1),
    ],
)
def test_part2_examples(hex_text, want):
    assert day16.part2(day16.parse_input(hex_text)) == want


@pytest.mark.parametrize(
    ("tree", "want"),
    [
        (op(0, 0, lit(0, 7)), 7),  # one-operand sum is its operand
        (op(0, 1, lit(0, 7)), 7),  # one-operand product is its operand
        (op(0, 2, lit(0, 7)), 7),
        (op(0, 3, lit(0, 7)), 7),
        (op(0, 5, lit(0, 3), lit(0, 3)), 0),  # ties: neither greater nor less
        (op(0, 6, lit(0, 3), lit(0, 3)), 0),
        (op(0, 7, lit(0, 3), lit(0, 3)), 1),
        (op(0, 5, lit(0, 4), lit(0, 3)), 1),  # operand order matters
        (op(0, 6, lit(0, 4), lit(0, 3)), 0),
    ],
)
def test_operator_edge_cases(tree, want):
    assert day16.evaluate(tree) == want


@pytest.mark.parametrize("type_id", [5, 6, 7])
@pytest.mark.parametrize("arity", [1, 3])
def test_comparison_needs_two_operands(type_id, arity):
    tree = op(0, type_id, *(lit(0, 1) for _ in range(arity)))
    with pytest.raises(ValueError):
        day16.evaluate(tree)


def to_python(packet):
    """Render the tree as a Python expression -- a reference evaluator sharing no code with evaluate()."""
    if packet.type_id == 4:
        return str(packet.value)
    args = [to_python(child) for child in packet.children]
    if packet.type_id == 0:
        return "(" + " + ".join(args) + ")"
    if packet.type_id == 1:
        return "(" + " * ".join(args) + ")"
    if packet.type_id in (2, 3):
        # min()/max() of one argument needs an iterable, so always pass a list.
        return ("min" if packet.type_id == 2 else "max") + "([" + ", ".join(args) + "])"
    a, b = args
    return f"int({a} {({5: '>', 6: '<', 7: '=='})[packet.type_id]} {b})"


def random_expr(rng, depth=0):
    """Like random_tree, but comparisons always get exactly two operands."""
    version = rng.randrange(8)
    if depth >= 4 or rng.random() < 0.4:
        return lit(version, rng.choice([0, 1, 2, 3, 2021, rng.randrange(2**12)]))
    type_id = rng.choice([0, 1, 2, 3, 5, 6, 7])
    arity = 2 if type_id >= 5 else rng.randint(1, 4)
    return op(version, type_id, *(random_expr(rng, depth + 1) for _ in range(arity)))


@pytest.mark.parametrize("seed", range(50))
def test_evaluate_matches_reference_random(seed):
    tree = random_expr(random.Random(seed))
    assert day16.evaluate(tree) == eval(to_python(tree))


def test_evaluate_matches_reference_real(real_input):
    tree = day16.parse_input(real_input(16))
    assert day16.evaluate(tree) == eval(to_python(tree))


def test_real_input_values_fit_u64(real_input):
    """Every intermediate value on the real input fits in 42 bits, so a Rust u64 evaluator cannot overflow."""
    tree = day16.parse_input(real_input(16))

    def walk(p):
        yield p
        for c in p.children:
            yield from walk(c)

    assert max(day16.evaluate(p).bit_length() for p in walk(tree)) == 42


def test_crlf_input():
    """Windows-downloaded inputs carry \r; parse_input must not keep it."""
    for hex_text, want in [("8A004A801A8002F478", 16), ("A0016C880162017C3686B18A3D4780", 31)]:
        assert day16.part1(day16.parse_input(hex_text + "\r\n")) == want
    assert day16.part2(day16.parse_input("9C0141080250320F1802104A08\r\n")) == 1


def test_real_input_locked(check_locked):
    check_locked(day16, LOCKED)
