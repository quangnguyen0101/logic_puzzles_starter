"""Ve de bai (khong co loi giai).

    python3 src/heuristic/tools/viz_puzzle.py data/star_battle
    python3 src/heuristic/tools/viz_puzzle.py data/light_up/lu-7x7-normal-01.json -o hinh.png
"""

from __future__ import annotations

import sys

from run_viz import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], with_solution=False))
