"""Chay heuristic tren bo de trong data/, in mot dong cho moi de khi xong.

    python3 -m src.run_heuristic --timeout 60
    python3 -m src.run_heuristic --kind light_up --timeout 30
    python3 -m src.run_heuristic --out-dir /tmp/kq

Moi de chay toi da `timeout` giay; qua han thi dung va ghi `timeout`.
"""

from __future__ import annotations

import argparse
import json
import re
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.heuristic_light_up import heuristic_light_up
from src.heuristic_star_battle import heuristic_star_battle
from src.light_up import LightUpProblem
from src.solver import solve
from src.star_battle import StarBattleProblem

RUNNERS = {
    "light_up": (LightUpProblem, heuristic_light_up),
    "star_battle": (StarBattleProblem, heuristic_star_battle),
}


def _format_solution(solution) -> str:
    if not solution:
        return "[]"
    rows = ",\n".join(f"    [{int(r)}, {int(c)}]" for r, c in solution)
    return "[\n" + rows + "\n  ]"


def _with_solution(raw: str, solution) -> str:
    """Chi thay gia tri cua known_solution, giu nguyen moi thu khac trong file."""
    key = '"known_solution"'
    new_value = _format_solution(solution)

    at = raw.find(key)
    if at < 0:
        end = raw.rindex("}")
        head = raw[:end].rstrip()
        if not head.endswith("{"):
            head += ","
        return head + f"\n  {key}: {new_value}\n}}" + raw[end + 1 :]

    start = raw.index(":", at) + 1
    while raw[start] in " \t\n\r":
        start += 1

    if raw.startswith("null", start):
        end = start + 4
    else:
        depth = 0
        i = start
        while i < len(raw):
            ch = raw[i]
            if ch == '"':
                i += 1
                while raw[i] != '"':
                    i += 1
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            i += 1
        end = i

    return raw[:start] + new_value + raw[end:]


class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout


def _order(path: Path) -> tuple[int, int, str]:
    rank = {"easy": 0, "normal": 1, "hard": 2, "daily": 3, "weekly": 4, "monthly": 5}
    data = json.loads(path.read_text(encoding="utf-8"))
    level = rank.get(path.stem.split("-")[-2], 1) if "-" in path.stem else 1
    return (data["rows"], level, path.stem)


def run(kind: str, path: Path, timeout: float) -> dict:
    cls, fn = RUNNERS[kind]
    problem = cls.from_json(path)
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    started = time.perf_counter()
    try:
        result = solve(problem, fn)
        status = "xong" if result["solution"] is not None else "khong co loi giai"
    except _Timeout:
        result, status = {"expanded": -1, "solution": None}, "timeout"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)
    return {
        "file": path.stem,
        "size": f"{problem.rows}x{problem.cols}",
        "expanded": result.get("expanded", -1),
        "seconds": round(time.perf_counter() - started, 2),
        "status": status,
        "solution": result.get("solution"),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Chay heuristic tren bo de")
    ap.add_argument("--data", default="data")
    ap.add_argument("--kind", choices=sorted(RUNNERS), help="chi chay mot bai")
    ap.add_argument("--timeout", type=float, default=60.0, help="giay toi da moi de")
    ap.add_argument(
        "--out-dir",
        default=str(ROOT / "data" / "heuristic_output"),
        help="thu muc ghi ket qua (mac dinh data/heuristic_output)",
    )
    args = ap.parse_args(argv)

    kinds = [args.kind] if args.kind else ["star_battle", "light_up"]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for kind in kinds:
        rows = []
        files = sorted((Path(args.data) / kind).glob("*.json"), key=_order)
        print(f"== {kind}: {len(files)} de ==", flush=True)
        out_kind = out_dir / kind
        out_kind.mkdir(parents=True, exist_ok=True)
        for path in files:
            row = run(kind, path, args.timeout)
            rows.append(row)
            raw = path.read_text(encoding="utf-8")
            if row["solution"]:
                raw = _with_solution(raw, row["solution"])
            (out_kind / path.name).write_text(raw, encoding="utf-8")
            print(
                f"{row['file']:28} {row['size']:>7} "
                f"mo rong={row['expanded']:>7} {row['seconds']:6.2f}s {row['status']}",
                flush=True,
            )

        lines = ["| De | Kich thuoc | Mo rong | Thoi gian (s) | Ket qua |", "|---|---|---:|---:|---|"]
        for row in rows:
            lines.append(
                f"| `{row['file']}` | {row['size']} | {row['expanded']} | "
                f"{row['seconds']:.2f} | {row['status']} |"
            )
        md = out_dir / f"{kind}.md"
        md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"da ghi {len(rows)} file vao {out_kind} va bang {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
