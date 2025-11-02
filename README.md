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
Memory: `--use_memory/--no_use_memory`, `--memory_dir`, `--priors_alpha`, `--motif_topk`, `--no_memory_motifs`, `--no_memory_priors`
Diversity guard: `--diversity_guard/--no_diversity_guard`, `--diversity_b_force_first`, `--attemptB_beam_scale`, `--attemptB_time_scale`

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
* Memory v1.0 loads read-only motifs/priors; missing files simply disable the feature.

### Memory v1.0 (read-only) & Diversity Guard

**Enable/disable:** `--use_memory` / `--no_use_memory` (default ON)  
**Location:** `--memory_dir ./memory_bank` (or set `ARC_MEMORY_DIR`)  
**Strength:** `--priors_alpha 1.0` (soft, log1p-scaled)  
**Motifs:** `--motif_topk 1` (seed ≤1 short motif when layout match is strong)

**Two attempts with Diversity Guard** (default ON):
* `--diversity_guard` / `--no_diversity_guard`
* `--diversity_b_force_first` (force Attempt‑B to open with a different family when Attempt‑A was align-first)
* `--attemptB_beam_scale`, `--attemptB_time_scale` (heuristic scaling for alternates/debate)

The guard inspects Attempt‑A’s first ops (`ops_tokens`) to infer a family (align/object/color/tiling) and biases Attempt‑B away from it by trimming same-family alternates, injecting complementary motifs (e.g., `keep_n_largest`), and tagging telemetry with `diversity_family`.

### Preparing the memory bank (offline)

Use `build_memory_bank.py` locally on the ARC training JSONs:

```bash
python build_memory_bank.py \
  --train_challenges ./arc-agi_training_challenges.json \
  --train_solutions ./arc-agi_training_solutions.json \
  --out_dir ./memory_bank
# writes: memory_bank/{priors.json,motifs.json,layouts.json,shapes.json}
```

Upload `memory_bank/` as a Kaggle dataset (or bundle in your private dataset). Runtime loads the JSONs read-only; if they’re absent the solver falls back to baseline behaviour.

Quick start (two attempts + memory + guard):

```bash
python arc_one.py --tasks_dir ./arc_tasks \
  --two_attempts \
  --use_memory --memory_dir ./memory_bank \
  --priors_alpha 1.0 --motif_topk 1 \
  --diversity_guard --diversity_b_force_first \
  --out submission.json
```
