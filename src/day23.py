"""Day 23: Amphipod.

Four kinds of amphipod (A, B, C, D) sit in four side rooms off an 11-cell
hallway, and each must end up in its own room (A leftmost .. D rightmost).
One step costs 1 / 10 / 100 / 1000 energy for A / B / C / D.  The answer is
the least total energy that sorts them.

The statement's rules reduce every legal plan to a sequence of whole
*trips*, each one of two kinds:

  * room -> hallway: the top amphipod of a room walks out and stops on one
    of the seven hallway cells that is not directly above a room door;
  * hallway -> room: an amphipod parked in the hallway walks into its own
    room, which must hold nothing but its own kind.

A trip is atomic (rule 3: once an amphipod stops in the hallway it stays put
until it can go home), so a state is just "who is where", and a trip is an
edge weighted by steps * energy.  The least-energy plan is a shortest path
in that state graph: Dijkstra from the input to the sorted burrow.

Three shortcuts keep the graph small; each is exact, and each is pinned in
the tests against a reference that takes the rules literally:

  * no direct room -> room trip.  It costs exactly what room -> hallway ->
    room costs through the hallway cell between the doors, and that cell is
    on the direct path anyway, so the two-trip version is always available
    when the direct one is;
  * an amphipod entering its room goes to the deepest free cell;
  * a room that holds only its own kind is never left (nothing below a
    settled amphipod needs to get out).

Part 2 unfolds the diagram: two fixed rows (DCBA, DBAC) are inserted
between the two room rows, making the rooms four deep.  Nothing in the
search assumes a depth (it is read from the state), so part 2 is the same
Dijkstra on the unfolded burrow.
"""

import heapq
from pathlib import Path
from typing import NamedTuple

INPUT = Path(__file__).resolve().parent.parent / "inputs" / "day23.txt"

TYPES = "ABCD"
ENERGY = {"A": 1, "B": 10, "C": 100, "D": 1000}
HALL_LEN = 11
DOORS = (2, 4, 6, 8)  # hallway index above room 0..3
STOPS = tuple(i for i in range(HALL_LEN) if i not in DOORS)  # 0 1 3 5 7 9 10
EMPTY = "."

# Part 2: the diagram was folded.  These rows go between its two room rows.
FOLDED_ROWS = ("DCBA", "DBAC")


class Burrow(NamedTuple):
    """One arrangement.  hall: 11 cells.  rooms[r]: room r's cells, top first."""

    hall: tuple[str, ...]
    rooms: tuple[tuple[str, ...], ...]

    def render(self) -> str:
        """The statement's diagram for this arrangement."""
        depth = len(self.rooms[0])
        lines = ["#" * (HALL_LEN + 2), "#" + "".join(self.hall) + "#"]
        for d in range(depth):
            cells = "#".join(room[d] for room in self.rooms)
            lines.append(("###" if d == 0 else "  #") + cells + ("###" if d == 0 else "#"))
        lines.append("  " + "#" * 9)
        return "\n".join(lines)


def parse_input(raw: str) -> Burrow:
    # rstrip, not strip: the room rows' leading spaces fix the columns.  It
    # also drops a CRLF file's trailing \r.
    lines = [line.rstrip() for line in raw.splitlines() if line.strip()]
    if len(lines) < 4:
        raise ValueError("too few lines for a burrow diagram")
    top, hall_row, *room_rows, floor = lines
    if top != "#" * (HALL_LEN + 2) or floor.strip() != "#" * 9:
        raise ValueError("burrow walls are not the expected shape")
    if len(hall_row) != HALL_LEN + 2 or hall_row[0] != "#" or hall_row[-1] != "#":
        raise ValueError(f"not a hallway row: {hall_row!r}")
    hall = tuple(hall_row[1:-1])

    room_cols = [door + 1 for door in DOORS]  # text column = hallway index + 1 (the wall)
    rows = []
    for row in room_rows:
        if len(row) < room_cols[-1] + 2:
            raise ValueError(f"room row too short: {row!r}")
        rows.append(tuple(row[c] for c in room_cols))
    rooms = tuple(zip(*rows, strict=True))

    depth = len(rooms[0])
    cells = list(hall) + [c for room in rooms for c in room]
    if set(cells) - set(TYPES) - {EMPTY}:
        raise ValueError(f"unexpected cell in diagram: {sorted(set(cells) - set(TYPES) - {EMPTY})}")
    for t in TYPES:
        if cells.count(t) != depth:
            raise ValueError(f"{cells.count(t)} amphipods of type {t}, rooms are {depth} deep")
    if any(hall[d] != EMPTY for d in DOORS):
        raise ValueError("an amphipod is standing in a doorway")
    for room in rooms:
        # Nothing floats above an empty cell: a room fills from the bottom.
        first = next((i for i, c in enumerate(room) if c != EMPTY), depth)
        if EMPTY in room[first:]:
            raise ValueError(f"room has a gap under an amphipod: {room}")
    return Burrow(hall, rooms)


def goal_for(depth: int) -> Burrow:
    return Burrow((EMPTY,) * HALL_LEN, tuple((t,) * depth for t in TYPES))


def hall_clear(hall: tuple[str, ...], a: int, b: int) -> bool:
    """True when every hallway cell strictly after a, up to and including b, is empty."""
    step = 1 if b > a else -1
    return all(hall[i] == EMPTY for i in range(a + step, b + step, step))


def moves(state: Burrow):
    """Yield (energy, next_state) for every trip allowed from `state`."""
    hall, rooms = state

    # hallway -> own room
    for h, a in enumerate(hall):
        if a == EMPTY:
            continue
        r = TYPES.index(a)
        room = rooms[r]
        if any(c not in (EMPTY, a) for c in room):
            continue  # room still holds a foreigner
        door = DOORS[r]
        if not hall_clear(hall, h, door):
            continue
        slot = max(i for i, c in enumerate(room) if c == EMPTY)  # deepest free cell
        steps = abs(h - door) + slot + 1
        new_hall = hall[:h] + (EMPTY,) + hall[h + 1 :]
        new_room = room[:slot] + (a,) + room[slot + 1 :]
        new_rooms = rooms[:r] + (new_room,) + rooms[r + 1 :]
        yield steps * ENERGY[a], Burrow(new_hall, new_rooms)

    # room top -> hallway stop
    for r, room in enumerate(rooms):
        if all(c in (EMPTY, TYPES[r]) for c in room):
            continue  # settled (or empty): nobody here needs to leave
        top = next(i for i, c in enumerate(room) if c != EMPTY)
        a = room[top]
        door = DOORS[r]
        new_room = room[:top] + (EMPTY,) + room[top + 1 :]
        new_rooms = rooms[:r] + (new_room,) + rooms[r + 1 :]
        for s in STOPS:
            # The door cell itself is always empty: nobody may stop there.
            if not hall_clear(hall, door, s):
                continue
            steps = top + 1 + abs(s - door)
            new_hall = hall[:s] + (a,) + hall[s + 1 :]
            yield steps * ENERGY[a], Burrow(new_hall, new_rooms)


def least_energy(start: Burrow) -> int:
    """Dijkstra over arrangements from `start` to the sorted burrow."""
    goal = goal_for(len(start.rooms[0]))
    best = {start: 0}
    heap = [(0, start)]
    while heap:
        cost, state = heapq.heappop(heap)
        if state == goal:
            return cost
        if cost > best[state]:
            continue  # stale entry: a cheaper route here was already expanded
        for energy, nxt in moves(state):
            c = cost + energy
            if c < best.get(nxt, c + 1):
                best[nxt] = c
                heapq.heappush(heap, (c, nxt))
    raise ValueError("the amphipods cannot be organized")


def unfold(burrow: Burrow) -> Burrow:
    """Insert the two folded rows between the first and second room rows."""
    if len(burrow.rooms[0]) != 2:
        raise ValueError("only a two-deep diagram can be unfolded")
    rooms = tuple(
        (room[0], *(row[r] for row in FOLDED_ROWS), *room[1:]) for r, room in enumerate(burrow.rooms)
    )
    return Burrow(burrow.hall, rooms)


def part1(burrow: Burrow) -> int:
    return least_energy(burrow)


def part2(burrow: Burrow) -> int:
    return least_energy(unfold(burrow))


def solve(raw: str) -> tuple[int, int]:
    parsed = parse_input(raw)
    return part1(parsed), part2(parsed)


def main() -> None:
    # Printed one part at a time so part 1's answer is on screen to submit
    # while part 2 is still raising NotImplementedError.
    parsed = parse_input(INPUT.read_text())
    print(f"part1={part1(parsed)}")
    print(f"part2={part2(parsed)}")


if __name__ == "__main__":
    raise SystemExit(main())
