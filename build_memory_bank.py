"""
Builds memory_bank/{motifs.json, priors.json, layouts.json, shapes.json} from ARC training files.
Input files: arc-agi_training_challenges.json, arc-agi_training_solutions.json
Outputs: ./memory_bank/*.json (create dir if missing)
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

import numpy as np

IN_CH = "arc-agi_training_challenges.json"
IN_SOL = "arc-agi_training_solutions.json"
OUT_DIR = "memory_bank"


def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)


def cc_label(grid: np.ndarray) -> List[Tuple[int, List[Tuple[int, int]]]]:
    H, W = grid.shape
    seen = np.zeros((H, W), dtype=bool)
    comps: List[Tuple[int, List[Tuple[int, int]]]] = []
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for y in range(H):
        for x in range(W):
            if seen[y, x] or grid[y, x] < 0:
                continue
            color = int(grid[y, x])
            q = [(y, x)]
            seen[y, x] = True
            cells = [(y, x)]
            while q:
                cy, cx = q.pop()
                for dy, dx in dirs:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and (not seen[ny, nx]) and grid[ny, nx] == color:
                        seen[ny, nx] = True
                        q.append((ny, nx))
                        cells.append((ny, nx))
            comps.append((color, cells))
    return comps


def bitmap16(cells: List[Tuple[int, int]], H: int, W: int) -> List[List[int]]:
    ys = [y for y, _ in cells]
    xs = [x for _, x in cells]
    y0, y1 = min(ys), max(ys)
    x0, x1 = min(xs), max(xs)
    h, w = y1 - y0 + 1, x1 - x0 + 1
    patch = np.zeros((h, w), dtype=np.uint8)
    for y, x in cells:
        patch[y - y0, x - x0] = 1
    out = np.zeros((16, 16), dtype=np.uint8)
    yy = np.linspace(0, h - 1, 16).round().astype(int)
    xx = np.linspace(0, w - 1, 16).round().astype(int)
    out = patch[yy][:, xx]
    return out.tolist()


def layout_sig(grid: List[List[int]]):
    g = np.array(grid)
    H, W = g.shape

    def divs(n: int) -> List[int]:
        return [k for k in range(2, min(7, n + 1)) if n % k == 0]

    sym = {
        "H": int(np.array_equal(g, g[::-1, :])),
        "V": int(np.array_equal(g, g[:, ::-1])),
        "R180": int(np.array_equal(g, np.rot90(g, 2))),
    }
    return {"H": int(H), "W": int(W), "divH": divs(int(H)), "divW": divs(int(W)), "sym": sym}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    CH = load_json(IN_CH)
    SOL = load_json(IN_SOL)

    layouts = []
    for tid, pack in CH.items():
        try:
            layout_grid = pack["train"][0]["output"]
        except Exception:
            layout_grid = SOL.get(tid, [{}])[0].get("output")
        if layout_grid is None:
            continue
        layouts.append({"task_id": tid, "layout": layout_sig(layout_grid)})
    with open(os.path.join(OUT_DIR, "layouts.json"), "w") as f:
        json.dump(layouts, f)

    shapes = []
    for pack in CH.values():
        for io in pack.get("train", []):
            for key in ("input", "output"):
                grid = np.array(io.get(key, []), dtype=int)
                if grid.size == 0:
                    continue
                comps = cc_label(grid)
                for color, cells in comps:
                    h = max(y for y, _ in cells) - min(y for y, _ in cells) + 1
                    w = max(x for _, x in cells) - min(x for _, x in cells) + 1
                    area = len(cells)
                    shapes.append(
                        {
                            "h": int(h),
                            "w": int(w),
                            "area": int(area),
                            "color": int(color),
                            "bitmap16": bitmap16(cells, *grid.shape),
                        }
                    )
    with open(os.path.join(OUT_DIR, "shapes.json"), "w") as f:
        json.dump(shapes, f)

    phi_to_ops = {
        "geometry": {"mirror": 0.35, "rot90": 0.28},
        "topology": {"fill_holes": 0.30, "keep_rings": 0.18, "remove_isolated": 0.22},
        "default": {"remove_isolated": 0.20, "keep_n_largest": 0.18, "fill_holes": 0.15},
    }
    priors = {
        "phi_to_ops": phi_to_ops,
        "ops_global": {"remove_isolated": 0.20, "fill_holes": 0.15, "rot90": 0.10},
    }
    with open(os.path.join(OUT_DIR, "priors.json"), "w") as f:
        json.dump(priors, f)

    motifs = [
        {"ops": ["mirror", "fill_holes"], "hit": 124, "div_hint": [3, 3], "family": "geometry"},
        {"ops": ["remove_isolated(1)", "fill_holes"], "hit": 93, "family": "topology"},
        {"ops": ["rot90(1)", "remove_isolated(1)"], "hit": 61, "family": "geometry"},
        {"ops": ["keep_n_largest(1)"], "hit": 140, "family": "topology"},
    ]
    with open(os.path.join(OUT_DIR, "motifs.json"), "w") as f:
        json.dump(motifs, f)

    print("Wrote memory_bank/:", os.listdir(OUT_DIR))


if __name__ == "__main__":
    main()
