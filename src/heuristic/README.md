# V3 — Heuristic (A*)

Phần code Việc 3: giải Star Battle và Light Up bằng A*, kèm bộ kiểm tra lời giải,
script chạy hàng loạt và script vẽ hình cho báo cáo.

## Cấu trúc

```
src/heuristic/
├── heuristic_star_battle.py       # A* cho Star Battle
├── heuristic_light_up.py          # A* cho Light Up
├── test_heuristic_star_battle.py  # check(problem, solution) -> (ok, lý do)
├── test_heuristic_light_up.py     # check(problem, solution) -> (ok, lý do)
├── run_test.py                    # đọc output/, chấm mọi lời giải
├── run_heuristic.py               # data/ -> output/ (kèm thời gian, số node)
├── run_viz.py                     # lõi vẽ (dùng chung cho 2 file dưới)
├── viz_puzzle.py                  # vẽ đề bài
├── viz_solution.py                # vẽ đề + lời giải
└── output/                        # <kind>/<tên đề>.json, <kind>.md
```

Hai module thuật toán trả về cùng một dict:

```python
{"solution": [[row, col], ...], "expanded": int, "generated": int, "frontier_peak": int}
```

## Chạy

Từ gốc repo:

```bash
python3 src/heuristic/run_heuristic.py --timeout 60          # cả 2 bài
python3 src/heuristic/run_heuristic.py --kind light_up       # một bài
python3 src/heuristic/run_test.py                            # chấm output/
python3 src/heuristic/viz_puzzle.py data/star_battle         # figs/star_battle/puzzle
python3 src/heuristic/viz_solution.py src/heuristic/output/star_battle
```

`run_heuristic.py` giới hạn mỗi đề bằng `--timeout` (giây) và `--cap` (số node),
cái nào tới trước thì dừng và ghi `timeout` / `het nut`.

## Định dạng output

Mỗi file trong `output/` là **bản sao nguyên văn** file tương ứng trong `data/`,
chỉ thay giá trị `known_solution`. Đề không giải được giữ nguyên `known_solution`
của file gốc (thường là `[]`).

## Kết quả hiện tại (timeout 60 s/đề)

| Bài | Giải được | Thời gian | Không giải được |
|---|---:|---|---|
| Star Battle | 20/27 | 0,00–2,4 s (tới 10×10) | 14×14 trở lên |
| Light Up | 8/24 | 0,02–1,04 s (7×7) | 10×10 trở lên |

`run_test.py`: 29/29 lời giải thoả luật chơi.

Light Up 10×10 là điểm yếu: ít gợi ý nên sau lan truyền vẫn còn nhiều ô chưa sáng,
branching lớn. Hướng cải thiện: thêm tập ô bị cấm đặt bóng vào trạng thái tìm kiếm.
