from __future__ import annotations

import json
import math
import os
import re  # needed by _OP_TOKEN_RE
from typing import Any, Dict, List, Optional

import numpy as np

MEMORY_VERSION = "1.0"


def _load_json(path: str) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def load_all(memory_dir: str) -> Dict[str, Any]:
    """Load all memory shards; missing files are treated as empty."""
    out: Dict[str, Any] = {}
    try:
        out["priors"] = _load_json(os.path.join(memory_dir, "priors.json"))
    except Exception:
        out["priors"] = {}
    try:
        out["motifs"] = _load_json(os.path.join(memory_dir, "motifs.json"))
    except Exception:
        out["motifs"] = {}
    try:
        out["layouts"] = _load_json(os.path.join(memory_dir, "layouts.json"))
    except Exception:
        out["layouts"] = {}
    try:
        out["shapes"] = _load_json(os.path.join(memory_dir, "shapes.json"))
    except Exception:
        out["shapes"] = {}
    out["_version"] = MEMORY_VERSION
    return out


# -------- Layout fingerprint (fast, approximate) --------

def _symmetry_flags_np(grid: np.ndarray) -> Dict[str, int]:
    Hsym = int(np.all(grid == np.flip(grid, axis=1)))
    Vsym = int(np.all(grid == np.flip(grid, axis=0)))
    R180 = int(np.all(grid == np.rot90(grid, 2)))
    return {"H": Hsym, "V": Vsym, "R180": R180}


def _periodicity(grid: np.ndarray) -> List[int]:
    H, W = grid.shape

    def period1d(lines: np.ndarray) -> int:
        for k in range(2, min(10, len(lines) // 2 + 1)):
            if all(np.array_equal(lines[i], lines[i - k]) for i in range(k, len(lines))):
                return k
        return 0

    return [period1d(grid), period1d(grid.T)]


def _layout_fp_from_train(train: List[dict]) -> Dict[str, Any]:
    if not train:
        return {"sym": {"H": 0, "V": 0, "R180": 0}, "period": [0, 0], "div": [0, 0]}

    Hs, Ws = set(), set()
    symH = symV = symR = 0
    perR = perC = 0

    for ex in train:
        if not isinstance(ex, dict):
            continue
        grid = ex.get("output") or ex.get("input")
        if grid is None:
            continue
        arr = np.array(grid)
        if arr.ndim != 2:
            continue
        Hs.add(arr.shape[0])
        Ws.add(arr.shape[1])
        s = _symmetry_flags_np(arr)
        symH |= int(s.get("H", 0))
        symV |= int(s.get("V", 0))
        symR |= int(s.get("R180", 0))
        pr, pc = _periodicity(arr)
        perR = max(perR, int(pr))
        perC = max(perC, int(pc))

    if not Hs or not Ws:
        return {"sym": {"H": symH, "V": symV, "R180": symR}, "period": [perR, perC], "div": [0, 0]}

    div = [0, 0]
    minH = min(Hs)
    minW = min(Ws)
    if perR and minH % perR == 0:
        div[0] = int(perR)
    if perC and minW % perC == 0:
        div[1] = int(perC)

    return {
        "sym": {"H": int(symH), "V": int(symV), "R180": int(symR)},
        "period": [int(perR), int(perC)],
        "div": div,
    }


def fingerprint_layout(task_json: Dict[str, Any]) -> Dict[str, Any]:
    train = task_json.get("train") or []
    if not isinstance(train, list):
        return {"sym": {"H": 0, "V": 0, "R180": 0}, "period": [0, 0], "div": [0, 0]}
    try:
        return _layout_fp_from_train(train)
    except Exception:
        return {"sym": {"H": 0, "V": 0, "R180": 0}, "period": [0, 0], "div": [0, 0]}


def detect_family(layout_fp: Dict[str, Any]) -> str:
    if not layout_fp:
        return "unknown"
    sym = layout_fp.get("sym", {})
    period = layout_fp.get("period", [0, 0])
    if any(int(sym.get(flag, 0)) for flag in ("H", "V", "R180")):
        return "geometry"
    if any(period) or any(layout_fp.get("div", [0, 0])):
        return "tiling"
    return "objectness"


# -------- Priors & motifs --------

def op_prior_for_task(phi_family: str, priors: Dict[str, Any], alpha: float = 1.0) -> Dict[str, float]:
    """Return op->weight dict; weights are soft-bounded in [0, 1]."""
    ops_freq = dict(priors.get("ops_freq", {}) or priors.get("ops_global", {}))
    phi_map = dict(priors.get("phi_to_ops", {}))
    out: Dict[str, float] = {}
    for op, freq in ops_freq.items():
        out[op] = min(1.0, max(0.0, math.log1p(max(alpha, 0.0) * float(freq))))
    for op in phi_map.get(phi_family, []):
        out[op] = max(out.get(op, 0.0), 0.6)
    # Provide some safe defaults
    out.setdefault("keep_n_largest", 0.4)
    out.setdefault("remove_isolated", 0.3)
    return out


def _flatten_motif_bucket(bucket: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if isinstance(bucket, dict):
        items.append(bucket)
    elif isinstance(bucket, (list, tuple)):
        for item in bucket:
            if isinstance(item, dict):
                items.append(item)
    return items


def choose_motifs(layout_fp: Dict[str, Any], motifs: Any, topk: int = 1) -> List[List[str]]:
    fam = detect_family(layout_fp)

    if isinstance(motifs, dict):
        primary_bucket = _flatten_motif_bucket(motifs.get(fam, []))
        alternate_buckets: List[Dict[str, Any]] = []
        for key, bucket in motifs.items():
            if key == fam:
                continue
            alternate_buckets.extend(_flatten_motif_bucket(bucket))
    else:
        flat = _flatten_motif_bucket(motifs or [])
        primary_bucket = [m for m in flat if m.get("family") == fam]
        alternate_buckets = [m for m in flat if m.get("family") != fam]

    try:
        k = max(1, int(topk))
    except Exception:
        k = 1

    primary = sorted(primary_bucket, key=lambda m: -int(m.get("hit", 1)))
    alternates = sorted(alternate_buckets, key=lambda m: -int(m.get("hit", 1)))

    bag = primary[:k] + alternates[: max(0, k - 1)]
    chosen: List[List[str]] = []
    for motif in bag:
        ops = motif.get("ops", [])
        if isinstance(ops, list) and ops:
            chosen.append([str(t) for t in ops if isinstance(t, str)])

    return chosen[:k] if chosen else []


# ---- token parsing ----------------------------------------------------------

_OP_TOKEN_RE = re.compile(r"^\s*([a-zA-Z_]\w*)\s*\((.*)\)\s*$")


def parse_op_tokens(tokens: List[str]):
    from arc_one import Step  # type: ignore

    steps: List[Step] = []
    for tok in tokens:
        tok = str(tok).strip()
        match = _OP_TOKEN_RE.match(tok)
        if not match:
            if "(" not in tok:
                steps.append(Step(tok, ()))
            continue
        name, arg_str = match.group(1), match.group(2)
        if not arg_str.strip():
            steps.append(Step(name, ()))
            continue
        parts = [p.strip() for p in arg_str.split(",") if p.strip()]
        args: List[Any] = []
        for part in parts:
            try:
                args.append(int(part))
                continue
            except Exception:
                pass
            if part.lower() in ("true", "false"):
                args.append(part.lower() == "true")
            else:
                args.append(part)
        steps.append(Step(name, tuple(args)))
    return steps
