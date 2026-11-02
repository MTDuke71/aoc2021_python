# Day 16 Function Guide — Packet Decoder

Source: [`src/day16.py`](../../src/day16.py) ·
Tests: [`tests/test_day16.py`](../../tests/test_day16.py) ·
Statement: [`day16.md`](day16.md)

Answers (accepted): **1012** / **2223947372407**.

## 1. The problem

The input is one line of hex, 1412 digits. Read as bits (four per digit,
MSB first), it is a serialised expression tree in a format the puzzle calls
BITS. It holds one outermost packet; the hex may add a few 0 bits of padding
after it.

Every packet starts with a header: a 3-bit **version**, then a 3-bit
**type ID**.

- **Type 4, literal.** A number sent in 5-bit groups. Each group is a
  continue flag (1 = more groups follow, 0 = last) and 4 data bits. The
  number is the data nibbles concatenated.
- **Any other type, operator.** One **length type** bit, then either
  - `0`: a 15-bit count of the *bits* the sub-packets occupy, or
  - `1`: an 11-bit count of the *sub-packets* themselves,

  followed by the sub-packets.

- **Part 1:** the sum of every packet's version number.
- **Part 2:** evaluate the tree. Operators 0–3 are sum, product, min and
  max over any number of operands. 5, 6, 7 are greater than, less than and
  equal, each producing 1 or 0 from exactly two operands.

If you've written a TLV decoder or parsed a CAN frame by hand, this is that
job: fixed-width header fields, a type field that selects the layout, and a
length field that bounds the payload.

## 2. Representation

`parse_input` returns the root `Packet`, a `NamedTuple`:

| field      | literal          | operator              |
| ---------- | ---------------- | --------------------- |
| `version`  | 0–7              | 0–7                   |
| `type_id`  | 4                | 0–3, 5–7              |
| `value`    | the number       | `None`                |
| `children` | `()`             | tuple of `Packet`     |

One record type rather than two classes keeps equality and the test
fixtures simple (`lit(6, 2021)`, `op(1, 6, ...)`). The length type is
**not** stored: it's framing, and neither part depends on it. The tests show
the same tree re-encoded either way decodes identically (§4).

The bit stream itself is a Python `str` of `'0'`/`'1'`, with a plain integer
cursor `pos` passed along. A string of characters is wasteful compared with
real bits, but it makes every field read a slice plus `int(..., 2)`, and a
bit position can be printed and compared against the statement's diagrams.

**The whole decode happens in `parse_input`**, so both parts are pure tree
walks. Real input: **268 packets**, 169 literals and 99 operators. The
operators split 51 length-type-0 and 48 length-type-1. The tree is 21 levels
deep. The stream is 5648 bits, the packet ends at bit 5645, and the last 3
bits are padding.

## 3. Function walkthrough

### `hex_to_bits(hex_text) -> str`

`bin(int(hex_text, 16))[2:]`, zero-padded to `4 * len(hex_text)`. The
padding matters: `bin()` drops leading zeros, and the real input starts with
`2` = `0010`. Without `zfill`, every field would be read two bits early.
`test_hex_to_bits_keeps_leading_zeros` pins it.

### `take(bits, pos, n) -> (value, pos + n)`

Reads an n-bit unsigned field, MSB first. Python slices quietly stop at the
end of a string, so `take` checks bounds itself and raises `ValueError` if a
field would run off the end of the stream. Every bit read goes through it:
**1792 calls** on the real input.

### `read_packet(bits, pos) -> (Packet, end)`

Recursive descent. Here is a trace of the statement's `38006F45291200`,
56 bits:

```
00111000000000000110111101000101001010010001001000000000
VVVTTTILLLLLLLLLLLLLLLAAAAAAAAAAABBBBBBBBBBBBBBBB
```

| bits    | field                | value | `pos` after |
| ------- | -------------------- | ----: | ----------: |
| 0–2     | version              |     1 |           3 |
| 3–5     | type ID              |     6 |           6 |
| 6       | length type          |     0 |           7 |
| 7–21    | sub-packet bit count |    27 |          22 |
|         | → `end = 22 + 27`    |    49 |             |
| 22–32   | child A: `110 100 01010` → v6, literal, one group `1010` | 10 | 33 |
| 33–48   | child B: `010 100 10001 00100` → v2, literal, `0001 0100` | 20 | 49 |
|         | `pos == end`, stop   |       |             |
| 49–55   | padding, all 0       |       |             |

Result: `Packet(1, 6, None, (Packet(6, 4, 10, ()), Packet(2, 4, 20, ())))`.

The three branches:

- **Literal:** loop `take 1` (continue flag), `take 4` (nibble), and
  `value = value << 4 | nibble` until the flag is 0. That's a shift
  register filling one nibble at a time.
- **Length type 0:** compute `end = pos + length`, read children while
  `pos < end`, then require `pos == end`. A child that runs past the
  declared length raises rather than being quietly accepted.
- **Length type 1:** read exactly `count` children.

Either way, an operator with **no** children raises. The statement says an
operator "contains one or more packets", and refusing an empty one at parse
time means `min` and `max` in `evaluate` never see an empty list.

### `parse_input(raw) -> Packet`

`strip()` (so a trailing `\r\n` is gone), then require non-empty and all
hex digits, either case. Decode from bit 0, then require everything after
the root packet to be `0`. The statement allows "a few extra 0 bits", and a
`1` there means the stream wasn't what we thought.

### `version_sum(packet)` — part 1

`packet.version + sum(version_sum(c) for c in packet.children)`. A
pre-order fold. Real input: **1012**.

### `evaluate(packet)` — part 2

Post-order: evaluate the children, then combine.

| type | operation | operands  |
| ---: | --------- | --------- |
|    0 | `sum`     | 1 or more |
|    1 | `math.prod` | 1 or more |
|    2 | `min`     | 1 or more |
|    3 | `max`     | 1 or more |
|    5 | `int(a > b)`  | exactly 2 |
|    6 | `int(a < b)`  | exactly 2 |
|    7 | `int(a == b)` | exactly 2 |

A comparison with other than two operands raises `ValueError`. Real input:
**2223947372407**.

Trace of `9C0141080250320F1802104A08` ("1 + 3 = 2 × 2"):

```
equal(7)
├── sum(0)      ── 1, 3   → 4
└── product(1)  ── 2, 2   → 4
                            → int(4 == 4) = 1
```

## 4. Why it is correct

**The format is prefix-decodable.** At every point the decoder knows
exactly what comes next: the header fixes the layout, a literal's flag bit
says whether another group follows, and an operator's length field says
where its children stop. So there is never a choice to make and no
backtracking: one left-to-right pass with a cursor is the whole algorithm.
That's why recursive descent fits. Each call consumes exactly one packet and
returns the position just past it, which is where the caller's next field
starts.

**The two framings agree.** Length type 0 checks `pos == end` after its
children, so a malformed length can't make the parser silently start
reading the parent's next field in the middle of a child.
`test_same_tree_either_length_type` decodes the statement's two encodings of
`((10, 11), (12, 13))`, one per length type, to the same shape.

**Checked against an independent encoder.** The tests have their own BITS
*writer* (`encode`), which shares no code with the decoder. Two checks use
it:

- 50 random trees (literals up to 40 bits, including 0, operators of 1–4
  children, nested up to 4 deep) are encoded, with each operator's length
  type chosen at random, and decoded back. The result must equal the
  original tree.
- The real tree is re-encoded twice (all length type 0, then mixed) and
  decodes back unchanged.

A decoder bug would have to have an exactly matching bug in the encoder to
pass both.

**Part 2 checked against a second evaluator.** `to_python` in the tests
renders a tree as a Python expression string, such as
`int((1 + 3) == (2 * 2))`, and `eval`s it. It agrees with `evaluate` on 50
random well-formed expressions and on the real input.

**Real-input shape, for the curious.** The root is a sum of 53 terms. 26 of
them are products, and 20 of those multiply a comparison by a literal,
e.g. `(a > b) * 4980268524`. That's an `if` written as arithmetic: the term
counts only when its comparison is 1. 8 of the 20 fire. The 21-level depth
comes from a chain of 20 single-child operators wrapping one value, the same
trick as the statement's `8A004A801A8002F478`. A one-operand sum, product,
min or max is just its operand (`test_operator_edge_cases`).

## 5. Complexity

Everything is linear in the input. Every bit is read exactly once, through
`take`, and each packet is visited once by each walk. Recursion depth equals
tree depth, 21 here, nowhere near Python's default limit of 1000.

| phase  |    ms |
| ------ | ----: |
| parse  | 0.489 |
| part 1 | 0.051 |
| part 2 | 0.032 |
| total  | 0.572 |

`bench.py -n 5 16`, best of 5 on the real input.

Parse is 85% of the total: 1792 `take` calls, each one a string slice plus
an `int(s, 2)`. The two walks touch 268 nodes each and are noise.

## 6. If I were writing this in Rust

A sketch of the shape; it was not compiled for this guide.

```rust
enum Packet {
    Literal { version: u8, value: u64 },
    Operator { version: u8, op: u8, children: Vec<Packet> },
}

struct Bits<'a> { bytes: &'a [u8], pos: usize }   // pos in bits

impl Bits<'_> {
    fn take(&mut self, n: usize) -> Result<u64, Error> {
        let mut v = 0;
        for _ in 0..n {
            let byte = *self.bytes.get(self.pos / 8).ok_or(Error::Truncated)?;
            v = v << 1 | ((byte >> (7 - self.pos % 8)) & 1) as u64;
            self.pos += 1;
        }
        Ok(v)
    }
}

fn evaluate(p: &Packet) -> u64 {
    match p {
        Packet::Literal { value, .. } => *value,
        Packet::Operator { op, children, .. } => {
            let mut vals = children.iter().map(evaluate);
            match op {
                0 => vals.sum(),
                1 => vals.product(),
                2 => vals.min().unwrap(),
                3 => vals.max().unwrap(),
                _ => {
                    let (a, b) = (vals.next().unwrap(), vals.next().unwrap());
                    match op { 5 => (a > b) as u64, 6 => (a < b) as u64, _ => (a == b) as u64 }
                }
            }
        }
    }
}
```

- **An enum, not a record with optional fields.** Python's `value: int |
  None` plus `children: ()` becomes two variants, so "a literal with
  children" can't even be written down.
- **Decode the hex into bytes, keep a bit cursor.** `Bits` is a read
  pointer over a byte buffer, the way you'd pull fields out of a received
  frame in firmware. A faster version keeps a 64-bit window and refills it
  a byte at a time instead of looping bit by bit.
- **`u64` is enough.** The largest literal is 40 bits (10 groups), and the
  largest intermediate value anywhere in the real tree is 42 bits.
  `test_real_input_values_fit_u64` pins that, so the Rust version doesn't
  need `checked_mul` for this input. A hostile input could overflow it.
- **`?` replaces the Python `ValueError`s** for truncation, overrun and bad
  padding: `read_packet` returns `Result<Packet, Error>` and the
  recursion just propagates it.

## 7. Possible optimization

**The whole stream as one integer (measured: slower).** The
register-minded approach is `N = int(hex, 16)` and
`(N >> (W - pos - n)) & ((1 << n) - 1)` per field, with no string at all.
Swapped in for `take` and timed best of 5: **0.523 ms** against the string
version's **0.472 ms**. In C or Rust a shift is one instruction, but here
`N` is a 5648-bit bignum and every shift builds a new ~700-byte integer, so
each field read costs O(stream length). The string slice copies at most 15
characters. It would win back if the window were bounded (shift a small
int that's refilled from the hex as the cursor advances), at the cost of
more code than this 0.5 ms day deserves.

**Fold during the decode.** Both answers could be computed inside
`read_packet` without building a tree: return `(version_sum, value, pos)`
from each call. That's one pass instead of three, and allocates no
`Packet`s. It was left out on purpose: the repo's rule is that
`parse_input` does the full parse and the parts consume its result, and the
tree is what lets the tests compare structures directly.
