# ARC‑ONE (Octonionic Control Overlay ARC solver)

**What this is (one lungful).**
ARC‑ONE v2.10.4 couples a compact ARC DSL (ops like `tile`, `rot90`, `keep_n_largest`, …) with octonion task embeddings **φ** that steer a staged beam-search pipeline (**skim → main → polish**). The solver now drives two diverse attempts via a strict confidence-minus-IoU chooser, protects them with the GOF-9000 self-monitor + HFP health gates, and lands solutions with palette-safe finishers. Telemetry (JSONL + optional CSVs) keeps the entire run explainable.

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
Two attempts: `--two_attempts`, `--attempt2_strategy`, `--div_lambda`, `--iou_cap`, `--max_bounces`
Octonion prior: `--no_octo_prior`, `--octo_alpha`, `--octo_clip`
Stage/diversity: `--no_polish`, `--stop_if_diversity`, `--no_bounce`, `--lowdiv_thr`, `--octo_z_min_for_bounce`
Rails/identity: `--no_block_identity`, `--no_rails_scale_hard`, `--scale_hard_thresh`, `--scale_hard_steps`, `--early_palette_block_steps`
Self-monitor: `--no_monitor`, `--monitor_pressure_thresh`, `--monitor_plateau_N`, `--monitor_visited_cap`, `--no_monitor_inject_underused`, `--no_monitor_drop_dupe_sigs`
HFP × GOF health: `--no_hfp`, `--hfp_alpha`, `--hfp_rho_hi`, `--hfp_rho_lo`, `--hfp_break_R_min`, `--no_hfp_gate_by_health`, `--no_hfp_gate_keep`
Memory: `--use_memory/--no_use_memory`, `--memory_dir`, `--priors_alpha`, `--motif_topk`, `--no_memory_motifs`, `--no_memory_priors`
Diversity guard: `--diversity_guard/--no_diversity_guard`, `--diversity_b_force_first`, `--attemptB_beam_scale`, `--attemptB_time_scale`
Telemetry: `--jsonl`, `--exact_wins_csv`, `--octo_stats_csv`, `--public_mode`

### Map of the beast
* **DSL & interpreter.** Ops registry + `interpret_program` with guardrails (identity ejection, directional rails, safe refusals).
* **Search.** Staged beam search with φ-aware priors, live ρ, bounded debate, and GOF-9000 self-monitor pressure relief.
* **OCO guidance.** 8-D φ vectors, tension, palette difficulty, time scaling, bounce heuristics.
* **Two attempts & diversity.** Confidence-minus-IoU Attempt-B chooser, diversity guardrails, micro-debate repairs, and a restored stack search space (`stack(grid, axis)` enumerates correctly again with optional `ARC_DEBUG_STACK=1` logging).
* **Health gating (HFP × GOF).** Hidden-factor ρ health bands gate successors and break futile loops while logging `hfp_gof` telemetry. Defaults now calibrate to the analytic maximum of the heptad kernel so “healthy” stretches are realistically attainable, with overrides available via `ARC_R_GOOD` / `ARC_R_BREAK`.
* **Finishers.** Align (learned (dy,dx)), block masks, blockwise dominant color, denoising, palette snap + micro-shifts.
* **Telemetry.** Stage times, ops tokens, rails settings, memory/diversity notes, and optional CSVs for exact wins & octonion stats.
* **API shim.** `SearchSettings`, `solve_task(...)` for notebooks.

### Footguns fixed (v2.10.x)
* Refused ops act as identity inside the interpreter, so guardrails cannot crash search.
* Early-step wrappers respect true depth, enforcing opening bans only when appropriate.
* Exact-match exits are hardened (no NameErrors) and pixel IoU guards tolerate empty grids.
* SciPy is optional—connected components falls back to a pure NumPy implementation.
* Memory v1.0 loads read-only motifs/priors; missing files simply disable the feature. Motif tokens are deduplicated and, if the memory shard yields no steps, the solver falls back to its local parser so seeds never silently disappear.
* Stack candidates are enumerated again (axis guard fixed in v2.10.4). Set `ARC_DEBUG_STACK=1` to print sample combinations during search debugging.

### Memory v1.0 (read-only) & Diversity Guard

**Enable/disable:** `--use_memory` / `--no_use_memory` (default ON)  
**Location:** `--memory_dir ./memory_bank` (or set `ARC_MEMORY_DIR`)  
**Strength:** `--priors_alpha 1.0` (soft, log1p-scaled)  
**Motifs:** `--motif_topk 1` (seed ≤1 short motif when layout match is strong)

**Two attempts with Diversity Guard** (default ON):
* `--diversity_guard` / `--no_diversity_guard`
* `--diversity_b_force_first` (force Attempt‑B to open with a different family when Attempt‑A was align-first)
* `--attemptB_beam_scale`, `--attemptB_time_scale`, `--div_lambda`, `--iou_cap`, `--max_bounces`

Attempt-B is picked by score = confidence − λ·IoU(Attempt-A) with a hard IoU cap. The guard inspects Attempt‑A’s first ops (`ops_tokens`) to infer a family (align/object/color/tiling), trims same-family alternates, injects complementary motifs (e.g., `keep_n_largest`), and tags telemetry with `diversity_family`.

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
