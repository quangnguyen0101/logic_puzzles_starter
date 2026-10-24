"""Ve de bai kem loi giai (known_solution).

    python3 src/heuristic/tools/viz_solution.py src/heuristic/output/star_battle
    python3 src/heuristic/tools/viz_solution.py data/light_up/lu-7x7-normal-sample.json -o hinh.png
"""

from __future__ import annotations

import sys

from run_viz import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:], with_solution=True))
