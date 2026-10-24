"""A* cho Light Up (co lan truyen rang buoc).

Trang thai la tuple bitmask (moi phan tu mot hang, bit = co bong den), dung
chung dinh dang voi `LightUpProblem`.

Moi buoc mo rong: chon mot o trang **chua duoc chieu sang**, thu dat bong den
vao mot trong cac o cung hang/cot nhin thay duoc no (ke ca chinh no). Moi loi
giai hop le deu phai chieu sang o nay bang mot trong cac o do, nen khong bo sot
nghiem.

Truoc khi mo rong, moi trang thai duoc lan truyen:
  (1) o chua sang khong con cho dat bong den nao  -> nhanh vo nghiem;
  (2) o chua sang chi con dung mot cho            -> dat luon (buoc bat buoc);
  (3) tuong so con thieu n bong va con dung n o   -> dat het cac o do.
Cac buoc bat buoc khong lam mat tinh toi uu vi chung la he qua cua rang buoc.

h(n) = ceil(so o trang chua sang / 5): mot bong den chieu sang toi da 5 o nen
con it nhat h(n) bong phai dat -> chan duoi hop le.

    from src.light_up import LightUpProblem
    from src.solver import solve
    from src.heuristic.heuristic_light_up import heuristic_light_up

    problem = LightUpProblem.from_json("data/light_up/lu-7x7-normal-01.json")
    result = solve(problem, heuristic_light_up)
"""

from __future__ import annotations

import heapq

from src.light_up import LightUpProblem

_NEIGHBOURS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _segments(problem: LightUpProblem) -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Voi moi o trang: cac o trang cung hang/cot nhin thay no (ke ca no)."""
    out: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for r in range(problem.rows):
        for c in range(problem.cols):
            if problem.grid[r][c] != ".":
                continue
            cells = [(r, c)]
            for dr, dc in _NEIGHBOURS:
                rr, cc = r + dr, c + dc
                while (
                    0 <= rr < problem.rows
                    and 0 <= cc < problem.cols
                    and problem.grid[rr][cc] == "."
                ):
                    cells.append((rr, cc))
                    rr += dr
                    cc += dc
            out[(r, c)] = cells
    return out


def _free_choices(problem, segments, state, cell):
    """Cac o co the dat bong den de chieu sang `cell` ma khong dung bong khac."""
    out = []
    for r, c in segments[cell]:
        if (state[r] >> c) & 1:
            continue
        if any(
            0 <= r + dr < problem.rows
            and 0 <= c + dc < problem.cols
            and (state[r + dr] >> (c + dc)) & 1
            for dr, dc in _NEIGHBOURS
        ):
            continue
        out.append((r, c))
    return out


def _place(state, r, c):
    return state[:r] + (state[r] | (1 << c),) + state[r + 1:]


def _propagate(problem, segments, whites, state):
    """Ap dung cac buoc bat buoc. Tra ve (state, ok)."""
    while True:
        lit = problem.illuminated_cells(state)
        unlit = whites - lit

        forced = None
        for cell in unlit:
            choices = _free_choices(problem, segments, state, cell)
            if not choices:
                return state, False
            if len(choices) == 1:
                forced = choices[0]
                break

        if forced is None:
            for r in range(problem.rows):
                for c in range(problem.cols):
                    clue = problem.grid[r][c]
                    if clue not in "01234":
                        continue
                    adj = [
                        (r + dr, c + dc)
                        for dr, dc in _NEIGHBOURS
                        if 0 <= r + dr < problem.rows
                        and 0 <= c + dc < problem.cols
                        and problem.grid[r + dr][c + dc] == "."
                    ]
                    placed = [(rr, cc) for rr, cc in adj if (state[rr] >> cc) & 1]
                    free = [p for p in adj if p not in placed]
                    need = int(clue) - len(placed)
                    if need < 0:
                        return state, False
                    if free and need == len(free):
                        forced = free[0]
                        break
                if forced is not None:
                    break

        if forced is None:
            return state, True

        state = _place(state, *forced)
        if not problem.is_valid_state(state):
            return state, False


def heuristic_light_up(problem: LightUpProblem, *, max_expanded: int | None = None):
    whites = {
        (r, c)
        for r in range(problem.rows)
        for c in range(problem.cols)
        if problem.grid[r][c] == "."
    }
    segments = _segments(problem)

    start: tuple[int, ...] = tuple([0] * problem.rows)
    start, ok = _propagate(problem, segments, whites, start)
    if not ok:
        return {"solution": None, "expanded": 0, "steps": [], "generated": 0, "frontier_peak": 0}

    def h_of(state):
        return -(-len(whites - problem.illuminated_cells(state)) // 5)

    counter = 0
    heap = [(h_of(start), 0, counter, start)]
    seen = {start}
    expanded = 0
    generated = 1
    peak = 1

    while heap:
        if max_expanded is not None and expanded >= max_expanded:
            return {
                "solution": None, "expanded": expanded, "steps": [],
                "generated": generated, "frontier_peak": peak, "timeout": True,
            }
        _, g, _, state = heapq.heappop(heap)
        expanded += 1

        unlit = whites - problem.illuminated_cells(state)
        if not unlit:
            if problem.is_goal(state):
                coords = problem.coords_from_state(state)
                return {
                    "solution": coords,
                    "expanded": expanded,
                    "steps": [{"row": r, "col": c} for r, c in coords],
                    "generated": generated,
                    "frontier_peak": peak,
                }
            continue

        # MRV: uu tien o chua sang co it lua chon nhat.
        target, choices = min(
            ((cell, _free_choices(problem, segments, state, cell)) for cell in unlit),
            key=lambda x: len(x[1]),
        )

        for r, c in choices:
            nxt, ok = _propagate(problem, segments, whites, _place(state, r, c))
            if not ok or nxt in seen:
                continue
            seen.add(nxt)
            generated += 1
            ng = g + sum(m.bit_count() for m in nxt) - sum(m.bit_count() for m in state)
            counter += 1
            heapq.heappush(heap, (ng + h_of(nxt), ng, counter, nxt))
            peak = max(peak, len(heap))

    return {
        "solution": None, "expanded": expanded, "steps": [],
        "generated": generated, "frontier_peak": peak,
    }
