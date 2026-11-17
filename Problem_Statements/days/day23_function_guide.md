# Day 23 Function Guide — Amphipod

Source: [`src/day23.py`](../../src/day23.py) ·
Tests: [`tests/test_day23.py`](../../tests/test_day23.py) ·
Statement: [`day23.md`](day23.md)

Answers (accepted): **16244** / **43226**.

## 1. The problem

A burrow is an 11-cell hallway with four side rooms hanging off it, at
hallway indices 2, 4, 6 and 8:

```
#############
#...........#        hallway index 0..10
###B#C#B#D###        rooms 0..3, top cell
  #A#D#C#A#          bottom cell
  #########
```

That's the statement's example. (The real input isn't reproduced here,
for the same reason `inputs/` is gitignored.) Each room is full of amphipods of four kinds,
A–D, and the job is to sort them: all the As in room 0, Bs in room 1, and
so on. A step costs 1 / 10 / 100 / 1000 energy for A / B / C / D. The
answer is the least total energy.

The rules:

1. Nobody stops on a hallway cell directly above a room (the "doorway").
2. Nobody walks from the hallway into a room unless it is their own room
   and that room holds no other kind.
3. Once an amphipod stops in the hallway, it stays put until it can walk
   all the way into its room.

- **Part 1.** Rooms are two deep, as in the input.
- **Part 2.** The diagram was folded. Unfold it by inserting two fixed
  rows, `DCBA` and `DBAC`, between the two room rows, making the rooms
  four deep. Same question.

## 2. Representation: trips, not steps

The rules mean nobody wanders. Every amphipod makes at most two **trips**:

- **out**: from the top of a room to one of the seven non-doorway hallway
  cells (0, 1, 3, 5, 7, 9, 10);
- **home**: from the hallway into its own room.

A trip is atomic. Under rule 3, nobody else moves while an amphipod is
mid-trip, and nobody moves from one hallway cell to another. So a
**state** is just who is where, and a trip is an edge whose weight is
steps × energy. The cheapest plan is the shortest path from the input
state to the sorted state. That's Dijkstra.

A state is a `Burrow(hall, rooms)` NamedTuple: `hall` is an 11-tuple of
`'A'..'D'` or `'.'`, and `rooms[r]` is room r's cells, top first. It is
hashable, so it serves directly as the `best` dict key, and it is ordered,
so `(cost, state)` heap entries never need a tiebreaker.

### Concrete trace: the cost of one trip

The statement's first move: the B at the top of room 2 goes out to
hallway 3.

```
steps = (top index + 1)          # climb to the doorway: 0 + 1 = 1
      + |stop − door|            # walk the hallway:     |3 − 6| = 3
      = 4                        # × 10 (B)  =  40 energy
```

The statement says "taking 4 steps and using 40 energy". A home trip is
the same formula in reverse, `|hall − door| + (slot + 1)`, where `slot` is
the deepest empty cell in the room.

### Concrete trace: why it's a search and not a greedy rule

Swap the tops of rooms A and B, with everything else sorted:

```
#############
#...........#
###B#A#C#D###
  #A#B#C#D#
  #########
```

The obvious plan is to park the B at hallway 3 and send the A home. But
the parked B now sits between the A and door 2: rule 3 says B can't move
until it can go home, and its home is blocked by the A. That's a
deadlock. The cheapest plan steps the A *aside* first:

| trip                     | steps | energy |
| ------------------------ | ----: | -----: |
| A out of room 1 → hall 5 |     2 |      2 |
| B out of room 0 → hall 3 |     2 |     20 |
| B hall 3 → room 1 top    |     2 |     20 |
| A hall 5 → room 0 top    |     4 |      4 |
| **total**                |       | **46** |

The lower bound, if each amphipod walked straight room to room, is
40 + 4 = 44. The extra 2 is the A stepping out of the B's way. (I first
wrote 43 for this case in the tests. The solver said 46, and the literal
reference below agreed with the solver. This case is pinned in the tests
for exactly that reason.)

## 3. Function walkthrough

### `parse_input(raw) -> Burrow`

Reads the diagram by text column. A room's cells sit at column
`door + 1`, because the leading `#` shifts everything by one. Lines are
`rstrip`ped, never `strip`ped: the room rows' leading spaces are what put
the letters in the right columns. `rstrip` also removes a CRLF file's
`\r`.

Depth is the number of room rows, so the same parser reads 1-, 2- and
4-deep diagrams. It also accepts amphipods in the hallway, which is what
lets the tests parse every intermediate diagram in the statement's
walk-throughs. It refuses anything that isn't a valid state:

- wrong walls;
- an unknown letter;
- not exactly `depth` of each kind;
- someone standing in a doorway;
- a gap under an amphipod in a room.

### `Burrow.render()`

The inverse of `parse_input`, used by the tests to check round-trips and
that `unfold(example)` draws exactly the statement's unfolded diagram.

### `moves(state)`

Yields `(energy, next_state)` for every legal trip.

- **Home trips.** Each hallway amphipod whose room holds only its own
  kind, and whose path to the door is clear, goes to the deepest empty
  cell.
- **Out trips.** For each room still holding a foreigner, the top
  amphipod goes to every one of the seven stops it can reach.

`hall_clear(hall, a, b)` checks the cells strictly after `a` up to and
including `b`, so the walker's own cell doesn't count as blocking.

### `least_energy(start)`

Textbook Dijkstra: a `best` dict, a `heapq` of `(cost, state)`, lazy
deletion (a popped entry dearer than `best[state]` is stale and skipped),
and an early exit when the sorted state is popped. If the heap empties
first, it raises, which is how the deadlock test sees an unsolvable
burrow.

### `unfold(burrow)` / `part1` / `part2`

`unfold` splices `FOLDED_ROWS` in after each room's top cell and refuses
anything that isn't two deep. `part1` is `least_energy(burrow)`;
`part2` is `least_energy(unfold(burrow))`.

## 4. Why it is correct

**Dijkstra is exact** because every edge weight is positive (every trip
is at least one step).

**The trip graph loses no plans.** Rules 1–3 force every movement into
an out trip or a home trip, with one exception: an amphipod can go
straight from one room into its own room without stopping. The solver
splits that into out-then-home via a hallway stop between the two doors.
Any two doors have a non-doorway cell between them (3, 5 or 7), and the
direct walk crosses it, so:

- the two-trip version costs exactly the same;
- it is available whenever the direct one is.

**Three shortcuts, each pinned.** The solver omits:

1. direct room → room trips (argued above);
2. entering one's room at any cell except the deepest empty one (a
   shallower stop only blocks one's own kind later and saves nothing);
3. leaving a room that holds only its own kind (nobody under a settled
   amphipod needs to get out).

These are arguments, and arguments can be wrong. So
`literal_least_energy` in the tests solves the puzzle from the rules as
written. It works on the text grid itself and runs a BFS through open
cells for every amphipod. It allows all three moves the solver omits:
room-to-room trips, any free cell of a clean room, and leaving a settled
room. The two solvers agree on:

- the example;
- the three hand-checked cases;
- 20 random 1-deep and 2 random 2-deep layouts;
- the real part 1 input;
- the real part 2 input, as a one-off run: 43226 after 37.7 s (measured).
  It isn't in the suite because of that runtime.

**The statement's own plans.** Each transition in part 1's walk-through
is reachable for exactly the energy the statement gives. Part 2's
walk-through lists states with no energies, so the test checks that the
cheapest route through its 24 checkpoints totals exactly 44169.

## 5. Complexity

The state count is the cost driver. The search space is every
arrangement reachable under the rules, and Dijkstra settles states in
cost order until the goal pops. Measured:

| input   | depth | answer | states expanded | heap pushes | edges generated |
| ------- | ----: | -----: | --------------: | ----------: | --------------: |
| example |     2 |  12521 |          18,943 |      21,353 |          54,829 |
| example |     4 |  44169 |          99,019 |     100,815 |         205,137 |
| real    |     2 |  16244 |          74,845 |      84,347 |         184,036 |
| real    |     4 |  43226 |          83,173 |      83,841 |         173,647 |

Real part 1 expands almost as many states as real part 2 (74,845 vs
83,173), even though its rooms are half as deep. The input layout
matters as much as the depth does: the example goes from 18,943 to
99,019 states when unfolded.

Per state, `moves` costs O(11 + 4·7) checks plus tuple rebuilds. That is
small but very Python-shaped: about 17 µs (part 1) and 26 µs (part 2)
per expanded state, from the bench times below divided by the expansion
counts.

| phase  |       ms |
| ------ | -------: |
| parse  |    0.007 |
| part 1 | 1289.412 |
| part 2 | 2194.422 |
| total  | 3483.841 |

`bench.py 23`, best of 5 on the real input. This is the slowest day so
far.

## 6. If I were writing this in Rust

A sketch; it was not compiled for this guide.

```rust
// 11 hallway + 4×4 room cells = 27 cells; 3 bits each (0 = empty, 1..4 = A..D)
// = 81 bits, so a state is a u128 and hashes/compares as one integer.
#[derive(Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct State(u128);

impl State {
    fn get(self, cell: usize) -> u8 { ((self.0 >> (3 * cell)) & 0b111) as u8 }
    fn set(self, cell: usize, v: u8) -> State {
        let mask = !(0b111u128 << (3 * cell));
        State((self.0 & mask) | ((v as u128) << (3 * cell)))
    }
}

const ENERGY: [u32; 5] = [0, 1, 10, 100, 1000];
const DOORS: [usize; 4] = [2, 4, 6, 8];
const STOPS: [usize; 7] = [0, 1, 3, 5, 7, 9, 10];

fn least_energy(start: State, depth: usize) -> Option<u32> {
    use std::{cmp::Reverse, collections::{BinaryHeap, HashMap}};
    let goal = goal_for(depth);
    let mut best: HashMap<State, u32> = HashMap::from([(start, 0)]);
    let mut heap = BinaryHeap::from([Reverse((0u32, start))]);
    while let Some(Reverse((cost, s))) = heap.pop() {
        if s == goal { return Some(cost); }
        if cost > best[&s] { continue; }
        for (e, n) in moves(s, depth) {           // same two loops as the Python
            let c = cost + e;
            if best.get(&n).map_or(true, |&b| c < b) {
                best.insert(n, c);
                heap.push(Reverse((c, n)));
            }
        }
    }
    None
}
```

The bridge points:

- **The state packs into a register.** Python builds fresh tuples for
  every successor. Rust does a mask-and-or on a `u128`, and the
  `HashMap` key is one 16-byte integer. Room cell `(r, d)` lives at
  index `11 + r * depth + d`.
- **`BinaryHeap` is a max-heap**, so `Reverse` makes it a min-heap.
  That's the same lazy-deletion pattern as `heapq`.
- **`moves` returns an iterator or fills a reused `Vec`.** At most
  4 home trips + 4 × 7 out trips = 32 successors, so a
  `SmallVec<[_; 32]>` avoids allocation altogether.
- I'd expect two orders of magnitude over the Python, but that hasn't
  been measured.

## 7. Possible optimization

**A\* with an admissible heuristic** (measured, not shipped). Use h =
the energy every misplaced amphipod must still spend at minimum:

- a hallway amphipod: walk to its door, then one step in;
- a room amphipod that is foreign, or sits above a foreigner: climb out,
  walk to its door, then one step in. The hallway walk counts as at
  least 2 even when it is already in its own room, since it has to step
  aside and back.

This never overestimates, so A\* still returns the optimum. Same states
and same move generator, three runs each, best:

| variant                        | real p1 expanded | real p1 ms | real p2 expanded | real p2 ms |
| ------------------------------ | ---------------: | ---------: | ---------------: | ---------: |
| Dijkstra (shipped)             |           74,844 |      2,115 |           83,172 |      2,296 |
| + "go home first" pruning      |           50,408 |      1,107 |           79,594 |      2,426 |
| A\*                            |            6,190 |        155 |           62,707 |      2,090 |
| A\* + "go home first"          |            5,081 |        146 |           60,535 |      2,192 |

(These timings come from the scratch harness, which ran slower than
`bench.py` in absolute terms. Compare within the table, not against
section 5.)

A\* is a 13× win on part 1 and close to nothing on part 2. Part 2's
answer is mostly made of D moves, where the heuristic is far below the
true cost. "Go home first" means: if any home trip is available, take
only that one. The argument for safety: a home trip clears a hallway
cell and fills a room slot nobody else can use, so taking it now never
makes a plan worse. All four variants returned the same answers on the
example and the real input, both parts. It pays on part 1 only.

Neither is shipped, because the plain Dijkstra is the version whose
correctness is a one-line argument. The A\* heuristic adds a
per-amphipod case analysis that has to be right for the answer to be
right.

**Pack the state** into an int (3 bits × 27 cells), as in the Rust
sketch. In Python the tuple rebuilds are the main cost. An int key with
shift/mask updates would cut allocation, but it makes `moves` harder to
read. Not implemented or measured.

## 8. Sidebar: it's FreeCell

If the rules have gone cold, think FreeCell solitaire. The pieces map
almost one to one:

| FreeCell                                                  | Day 23                                                     |
| --------------------------------------------------------- | ---------------------------------------------------------- |
| Cascades: only the top card is playable                   | Rooms: only the top amphipod can leave                     |
| Free cells: a few temporary parking slots                 | The 7 hallway stops                                        |
| Foundations: a card goes up only onto its own suit        | Home rooms: enter only when the room holds just your kind  |
| A card in a free cell clogs it until it can go somewhere  | Rule 3: a parked amphipod stays put until it can go home   |
| Losing by filling the free cells with stuck cards         | Deadlock: D at hallway 3 and A at 5 each block the other   |

Two of the solver's choices have FreeCell counterparts:

- **A supermove is a series of single moves.** FreeCell programs move a
  run of cards in one go, but it's really single moves through the free
  cells. The solver treats a direct room → room walk the same way, as
  out + home (section 4).
- **"Go home first" is auto-play to the foundations.** FreeCell
  auto-plays a card only when that's safe, because a low card might
  still be needed on a cascade. Amphipods have no such catch, since a
  settled amphipod is never needed anywhere else. The pruning in
  section 7 is therefore always safe, and it cut real part 1 from 74,844
  to 50,408 expanded states.

**Where the analogy breaks.** FreeCell asks whether a deal can be solved,
or at most how few moves it takes. Every move counts the same, so
breadth-first search fits. Here a D step costs 1000× an A step, which
makes it a weighted shortest path, so Dijkstra. The weighting is also
why A\* barely helps part 2: that answer is dominated by D moves, which
the heuristic underestimates badly.

## 9. Sidebar: it's also Tower of Hanoi

Look at a plan's diagrams and the stacks show up everywhere.

**Rooms are stacks.** Only the top piece moves, and a bottom piece is
stuck until everything above it has been parked somewhere. That's the
core of Hanoi. Rule 2 (enter only a room holding nothing but your kind)
plays the part of "no large disk on a small one": every move into a room
has to keep that room in order.

**The hallway is stacks too.** The dead-end corners (cells 0–1 and 9–10)
are last-in, first-out pegs. So is any run of parked amphipods waiting
for the same door. The solver's plan for the example's part 2, written
`X>h` for out to cell h and `X<h` for home from cell h:

```
D>10 A>0 B>9 B>7 A>1 C>5 C<5 C>5 C<5 B>5 D>3 B<5 B<7 B<9 C>7 A>9 C<7
D<3 B>3 B<3 D>5 D>3 A<1 A<0 D<5 D<3 A<9 D<10
```

- `A>0 … A>1 … A<1 A<0`: the A at 0 can't leave until the A at 1 has.
- `B>9 B>7 … B>5 … B<5 B<7 B<9`: three Bs parked in a row, heading for
  door 4, go home nearest-first, a three-disk peg.
- `D>5 D>3 … D<5 D<3`: the D at 3 can't pass the D at 5 to reach door 8.

**Where it breaks: the move count is fixed.** In Hanoi the number of
moves is the whole question (2ⁿ − 1 for n disks). Here rules 2 and 3 cap
every amphipod at two trips, out once and home once. An amphipod already
settled (its own kind, with only its own kind below it) makes none, and
every other one must make both. So every plan in the solver's trip model
(direct room → room counted as two trips) has exactly

```
trips = 2 × (amphipods not already settled)
```

| input           | not settled | trips |
| --------------- | ----------: | ----: |
| example, part 1 |    6 of 8   |    12 |
| example, part 2 |   14 of 16  |    28 |
| real, part 1    |    8 of 8   |    16 |
| real, part 2    |   16 of 16  |    32 |

All four counts are measured from the solver's plans, and the two example
rows are pinned in the tests. The search never decides *how many* moves
to make. It decides their order and where to park, which is where
1/10/100/1000 weighting turns it into a search. Hanoi has a fixed order
and a growing count; Day 23 has a fixed count and an order that has to be
searched for.
