from __future__ import annotations

import json
import os
import re
from typing import Any, Optional, Dict, List, Tuple

import numpy as np

_MEMO_CACHE: Optional[Dict[str, Any]] = None


def _resolve_dir(settings) -> str:
    return settings.memory_dir or os.environ.get("ARC_MEMORY_DIR", "./memory_bank")


def load_memory(settings) -> Dict[str, Any]:
    global _MEMO_CACHE
    if _MEMO_CACHE is not None:
        return _MEMO_CACHE
    directory = _resolve_dir(settings)
    memo: Dict[str, Any] = {}
    for name in ("motifs", "priors", "layouts", "shapes"):
        path = os.path.join(directory, f"{name}.json")
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    memo[name] = json.load(f)
        except Exception:
            continue
    _MEMO_CACHE = memo
    return memo


def fingerprint_layout(grid: List[List[int]]) -> Dict[str, Any]:
    g = np.array(grid)
    if g.ndim != 2:
        return {"H": 0, "W": 0, "divH": [], "divW": [], "sym": {"H": 0, "V": 0, "R180": 0}}
    H, W = g.shape

    def _divs(n: int) -> List[int]:
        return [k for k in range(2, min(7, n + 1)) if n % k == 0]

    sym = {
        "H": int(np.array_equal(g, g[::-1, :])),
        "V": int(np.array_equal(g, g[:, ::-1])),
        "R180": int(np.array_equal(g, np.rot90(g, 2))),
    }
    return {"H": int(H), "W": int(W), "divH": _divs(int(H)), "divW": _divs(int(W)), "sym": sym}


def select_motifs_for_task(memo: Dict[str, Any], fp: Dict[str, Any], max_k: int = 3) -> List[List[str]]:
    motifs = memo.get("motifs", [])
    if not motifs or max_k <= 0:
        return []
    divH = set(fp.get("divH", []) or [])
    divW = set(fp.get("divW", []) or [])
    scored: List[Tuple[float, List[str]]] = []
    for m in motifs:
        ops = m.get("ops", []) or []
        hit = float(m.get("hit", 1))
        bonus = 0.0
        div_hint = m.get("div_hint")
        if isinstance(div_hint, (list, tuple)) and len(div_hint) == 2:
            if div_hint[0] in divH or div_hint[1] in divW:
                bonus += 1.0
        scored.append((hit + 0.5 * bonus, list(ops)))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [ops for _, ops in scored[:max_k]]


_OP_TOKEN_RE = re.compile(r"^\s*([a-zA-Z_]\w*)\s*\((.*)\)\s*$")


def _parse_args(arg_str: str) -> tuple:
    if not arg_str.strip():
        return ()
    parts = [p.strip() for p in arg_str.split(",") if p.strip()]
    args: List[Any] = []
    for p in parts:
        try:
            args.append(int(p))
            continue
        except Exception:
            pass
        if p.lower() in ("true", "false"):
            args.append(p.lower() == "true")
            continue
        args.append(p)
    return tuple(args)


def parse_op_tokens(tokens: List[str]):
    from arc_one import Step  # type: ignore

    steps: List[Step] = []
    for tok in tokens:
        tok = tok.strip()
        match = _OP_TOKEN_RE.match(tok)
        if not match:
            if "(" not in tok:
                steps.append(Step(tok, ()))
            continue
        name, arg_str = match.group(1), match.group(2)
        steps.append(Step(name, _parse_args(arg_str)))
    return steps

