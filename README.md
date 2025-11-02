# ARC‑ONE (Octonion‑guided ARC solver)

**What this is (one lungful).**  
An ARC solver built around a tiny DSL (ops like `tile`, `rot90`, `keep_n_largest`, …), an octonion task embedding **φ** that nudges search, and a staged beam-search pipeline (**skim → main → polish**) that emits two diverse attempts with palette safety and blockwise/align finishers. Telemetry is threaded through so you can see why the search did what it did.

## Quick start
Requires Python, `numpy`, `scipy` (for connected components).
```bash
pip install numpy scipy

# Two-attempts schema (ARC 2025)
python arc_one.py --tasks_dir ./arc_tasks --two_attempts --out submission.json

# Classic single-output schema
python arc_one.py --tasks_dir ./arc_tasks --out submission.json

# Faster dev loop
python arc_one.py --tasks_dir ./arc_tasks --two_attempts --max_tasks 5 --no_polish --jsonl telemetry.jsonl
```

### Handy flags (abridged)
Search: `--beam`, `--depth`, `--seconds`
OCO costs: `--lambda_len`, `--lambda1`, `--lambda2`
Two attempts: `--two_attempts`, `--attempt2_strategy` (e.g., `flipH`, `oco_auto`)
Octonion prior: `--no_octo_prior`, `--octo_alpha`, `--octo_clip`
Stage/diversity: `--no_polish`, `--stop_if_diversity`
Rails/identity: `--no_block_identity`, `--no_rails_scale_hard`, thresholds/steps knobs
Memory: `--no_use_memory`, `--no_memory_motifs`, `--no_memory_priors`, `--memory_dir`, `--memory_max_seeded`, `--memory_prior_alpha`

### Map of the beast
* **DSL & interpreter.** Ops registry + `interpret_program`.  
* **Search.** Staged beam search with φ-aware priors, live ρ, bounded debate.  
* **OCO guidance.** 8-D φ vectors, tension, palette difficulty, time scaling.  
* **Two attempts & diversity.** Automatic 2nd attempt with IoU diversity & palette safety.  
* **Finishers.** Align (learned (dy,dx)), block masks, blockwise dominant color, denoising.  
* **Telemetry.** Stage times, ops tokens, rails settings in `_telemetry`.  
* **API shim.** `SearchSettings`, `solve_task(...)` for notebooks.

### Footguns fixed
* Refused ops no longer propagate `None`—they act as identity inside the interpreter.
* Wrappers no longer assume `depth=0` when depth is unknown; early bans only at real depth 0.
* Memory v0.1 loads read-only motifs/priors; missing files simply disable the feature.
